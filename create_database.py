import sqlite3

conn = sqlite3.connect('shop.db')
cursor = conn.cursor()

cursor.execute('DROP TABLE IF EXISTS users')
cursor.execute('DROP TABLE IF EXISTS discounts')
cursor.execute('DROP TABLE IF EXISTS products')
cursor.execute('DROP TABLE IF EXISTS delivery_points')
cursor.execute('DROP TABLE IF EXISTS orders')
cursor.execute('DROP TABLE IF EXISTS order_items')

cursor.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE discounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    percentage INTEGER NOT NULL
)
''')

cursor.execute('''
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT,
    manufacturer TEXT,
    supplier TEXT,
    price REAL NOT NULL,
    unit TEXT DEFAULT 'шт',
    quantity INTEGER DEFAULT 0,
    discount_id INTEGER DEFAULT 1,
    image_path TEXT,
    FOREIGN KEY (discount_id) REFERENCES discounts(id)
)
''')

cursor.execute('''
CREATE TABLE delivery_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number TEXT UNIQUE NOT NULL,
    status TEXT DEFAULT 'Новый',
    delivery_address TEXT,
    order_date TEXT,
    issue_date TEXT,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')

cursor.execute('''
CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER DEFAULT 1,
    price_at_time REAL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
)
''')

# Базовые скидки
discounts = [
    ('Без скидки', 0),
]
cursor.executemany('INSERT INTO discounts (name, percentage) VALUES (?, ?)', discounts)

conn.commit()
conn.close()
print("✅ База данных создана (готова к импорту)")