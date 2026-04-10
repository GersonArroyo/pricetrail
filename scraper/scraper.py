import requests
import time
import psycopg

params = {
    "page_number":1,
    "page_size":20,
    "facet_filters":"",
    "sort":"most_searched",
}

conn = psycopg.connect(  
                dbname="sales_db",  
                user="postgres",  
                password="437766",  
                host="localhost",  
                port=5432  
            )

departments = ["hardware", "perifericos", "computadores", "projetores", "escritorio"]

# https://servicespub.prod.api.aws.grupokabum.com.br/catalog/v2/products-by-category/perifericos?page_number=1&page_size=20&facet_filters=&sort=most_searched&is_prime=false&payload_data=products_category_filters&include=gift

for department in departments:
    url = f"https://servicespub.prod.api.aws.grupokabum.com.br/catalog/v2/products-by-category/{department}"
    
    response = requests.get(url, params=params)
    
    # total pages in the retrived json
    total_pages = response.json()['meta']['total_pages_count']
    
    # will loop until the last page is reached
    while True:
        response = requests.get(url, params=params)
        data = response.json()
        total_pages = data['meta']['total_pages_count']
    #while total_pages >= params["page_number"]:
        
        # response from the api for each page
    #    response = requests.get(url, params=params)
        
        # pause 1 sec for the server
        time.sleep(1)
        
        # total numbers of items(products) in the retrived json
        total_items = response.json()['meta']['total_items_count']
        
        # data to be stored in the database
        data = response.json()['data']
        
        for size in range(len(data)):
            
            # lists to store the data for products and price history tables
            products_list = []
            products_history_list = []
            
            # attributes of each product
            products = data[size]["attributes"]
            
            # data for products table
            id=data[size]["id"]
            title=products["title"]
            category=department
            discount_percentage=products["discount_percentage"]
            price_with_discount=products["price_with_discount"]
            warrant=products["warranty"]
            
            # data for history table
            price=products["price"]
            stock=products["stock"]
            available=products["available"]
            
            # creating a dictionary to store the data for products table
            products_data = {
                "id": id,
                "title": title,
                "category": category,
                "discount_percentage": discount_percentage,
                "price_with_discount": price_with_discount,
                "warranty": warrant
            }
            
            products_list.append(products_data)
            
            price_history_data = {
                "id": id,
                "price": price,
                "stock": stock,
                "available": available
            }
            
            
            with conn.cursor() as cur:
                try:
                    
                    cur.execute('INSERT INTO products (product_id, title, category, discount_percentage, price_with_discount, warranty) VALUES (%s, %s, %s, %s, %s, %s) RETURNING product_pk',
                                (products_data["id"], products_data["title"], products_data["category"], products_data["discount_percentage"], products_data["price_with_discount"], products_data["warranty"]))
                    product_pk = cur.fetchone()[0]
                    
                    cur.executemany('INSERT INTO price_history (product_pk, price, stock, available) VALUES (%s, %s, %s, %s)',
                                [(product_pk, history["price"], history["stock"], history["available"]) for history in products_history_list])
                    conn.commit()
                    
                except Exception as e:
                    print(f"Error inserting data: {e}")
                    conn.rollback()
            
        if params["page_number"] >= total_pages:
            break

        params["page_number"] += 1
