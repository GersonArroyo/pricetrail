import connection


def get_products(cur, limit: int = 20, offset: int = 0):
    cur.execute("""
        SELECT product_pk, product_id, title, category
        FROM products
        ORDER BY product_id
        LIMIT %s OFFSET %s
    """, (limit, offset))
    
    return cur.fetchall()


def get_price_history(cur, limit: int = 20, offset: int = 0):
    cur.execute("""
        SELECT histoy_pk, product_pk, price, stock, available, discount_percentage, price_with_discount, warranty, date_insert
        FROM price_history                ORDER BY date_insert DESC
        LIMIT %s OFFSET %s
    """, (limit, offset))
    
    return cur.fetchall()


def get_products_with_history(cur, department: str, limit: int = 20, offset: int = 0):
    cur.execute("""
        SELECT p.product_pk, p.product_id, p.title, p.category, ph.price, ph.stock, ph.available, ph.discount_percentage, ph.price_with_discount, ph.warranty, ph.date_insert, ph.history_pk, ph.product_pk
        FROM products p
        JOIN price_history ph ON p.product_pk = ph.product_pk
        WHERE p.category = %s
        ORDER BY ph.date_insert DESC
        LIMIT %s OFFSET %s
    """, (department, limit, offset))
    
    return cur.fetchall()