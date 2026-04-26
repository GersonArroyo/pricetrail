CREATE schema sales_db;

CREATE TABLE IF NOT EXISTS products (
    product_pk SERIAL PRIMARY KEY,
    product_id INT unique,
    title VARCHAR (250),
    category VARCHAR (150)
);

CREATE TABLE IF NOT EXISTS price_history(
    history_pk SERIAL PRIMARY KEY,
    product_pk INT NOT NULL,
    price NUMERIC (10,2),
    stock INT,
    available BOOLEAN,
    discount_percentage INT,
    price_with_discount NUMERIC (10,2),
    warranty TEXT,
    date_insert TIMESTAMP default now(),
    CONSTRAINT fk_product FOREIGN KEY (product_pk) REFERENCES products(product_pk)
);

CREATE INDEX idx_price_history_product ON price_history(product_pk);
CREATE INDEX idx_price_history_date ON price_history(date_insert);
