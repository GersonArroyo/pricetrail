from psycopg.rows import dict_row
from typing import List, cast
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import psycopg
import os

params = {
    "page_number":1,
    "page_size":20,
    "facet_filters":"",
    "sort":"most_searched",
}

# Setup session using retry logic
session = requests.Session()
retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS"],
    backoff_factor=2
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

conn = psycopg.connect(  
                dbname=os.getenv('POSTGRES_DB'),
                user=os.getenv('POSTGRES_USER'),
                password=os.getenv('POSTGRES_PASSWORD'), 
                host=os.getenv('POSTGRES_HOST'), 
                port=os.getenv('POSTGRES_PORT'),
                row_factory=dict_row # type: ignore
            )

departments = ["hardware", "perifericos", "computadores", "projetores", "escritorio"]

# https://servicespub.prod.api.aws.grupokabum.com.br/catalog/v2/products-by-category/perifericos?page_number=1&page_size=20&facet_filters=&sort=most_searched&is_prime=false&payload_data=products_category_filters&include=gift

def save_product(cur, item: dict, department: str):
    
        attributes = item['attributes']
        product_id = item['id']
        
        cur.execute("SAVEPOINT sp")
        try:
            # localizar o product_pk do produto se existir
            cur.execute("""
                INSERT INTO products (product_id, title, category)
                VALUES (%s, %s, %s)
                ON CONFLICT (product_id) DO NOTHING
                RETURNING product_pk
                """, (product_id, attributes["title"], department))
            
            result = cur.fetchone()
            
            if result:
                product_pk = cast(dict, result)["product_pk"]
            else:
                cur.execute("SELECT product_pk FROM products WHERE product_id = %s",(product_id,))
                product_pk = cast(dict, cur.fetchone())["product_pk"]
            
            # buscar o ultimo registro daquele produto
            cur.execute("""SELECT price, stock, available, discount_percentage, price_with_discount, warranty
                        FROM price_history
                        WHERE product_pk = %s
                        ORDER BY date_insert DESC
                        LIMIT 1
                        """, (product_pk,))
            
            result = cur.fetchone()

            # se não tem nenhum registro de preço para aquele produto, insere o primeiro
            if not result:
                cur.execute("""INSERT INTO price_history (product_pk, price, stock, available, discount_percentage, price_with_discount, warranty) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                            (product_pk, attributes["price"], attributes["stock"], attributes["available"], 
                            attributes["discount_percentage"], attributes["price_with_discount"], attributes["warranty"]))
            # se um destes mudou
            else:
                row = cast(dict, result)
                
                db_data = {
                    "price": float(row["price"]),
                    "stock": row["stock"],
                    "available": row["available"],
                    "discount_percentage": row["discount_percentage"],
                    "price_with_discount": float(row["price_with_discount"]),
                    "warranty": row["warranty"]
                }

                api_data = {
                    "price": attributes["price"],
                    "stock": attributes["stock"],
                    "available": attributes["available"],
                    "discount_percentage": attributes["discount_percentage"],
                    "price_with_discount": attributes["price_with_discount"],
                    "warranty": attributes["warranty"]
                }
                
                # compara os dados, banco com a API
                if db_data != api_data:
                    cur.execute("""INSERT INTO price_history (product_pk, price, stock, available, discount_percentage, price_with_discount, warranty) VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                                (product_pk, attributes["price"], attributes["stock"], attributes["available"], 
                                attributes["discount_percentage"], attributes["price_with_discount"], attributes["warranty"]))
        except Exception as e:
            cur.execute("ROLLBACK TO SAVEPOINT sp")
            raise e

for department in departments:
    url = f"https://servicespub.prod.api.aws.grupokabum.com.br/catalog/v2/products-by-category/{department}"
    # flush=True para garantir que as mensagens sejam exibidas em tempo real, mesmo se o output estiver sendo redirecionado para um arquivo
    print(f"\n[INFO] Iniciando scraping da categoria: {department}", flush=True)
    
    params["page_number"] = 1
    
    # will loop until the last page is reached
    while True:
        try:
            response = session.get(url, params=params, timeout=30)
        except requests.exceptions.Timeout:
            print(f"[TIMEOUT] {department} - tentando novamente em 10s", flush=True)
            time.sleep(10)
            continue
        except requests.exceptions.ConnectionError as e:
            print(f"[CONEXÃO] Erro em {department}: aguardando 10s", flush=True)
            time.sleep(10)
            continue
        
        # se a resposta não for 200, loga o erro e tenta novamente depois de 10s
        if response.status_code != 200:
            print(f"[ERRO] Status {response.status_code} na página {params['page_number']} da categoria {department}", flush=True)
            break
        
        data_json = response.json()
        total_pages = data_json['meta']['total_pages_count']
        data = data_json['data']
        
        print(f"[{department.upper()}] Página {params['page_number']} - {len(data)} produtos processados", flush=True)
        
        with conn.cursor() as cur:
            for item in data:
                try:
                    save_product(cur=cur, item=item, department=department)
                except Exception as e:
                    print(f"[ERRO] Erro ao processar produto {item['id']} da categoria {department}: {e}", flush=True)
                    continue

        # commit the transaction after processing each page
        conn.commit()
        print(f"[{department.upper()}] Página {params['page_number']} - Dados salvos no banco", flush=True)
        
        # if the current page number is greater than or equal to the total pages, break the loop
        if params["page_number"] >= total_pages:
            break
        
        # get the next page
        params["page_number"] += 1
        
        # pause 1 sec for the server
        time.sleep(1)

print("\n[INFO] Scraping concluído com sucesso!", flush=True)
