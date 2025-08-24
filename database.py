import sqlite3
from models import Product

class Database:
    def __init__(self, db_name='pos.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Tabel produk
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER NOT NULL,
                imei TEXT UNIQUE
            )
        ''')
        # Tabel transaksi
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY,
                total REAL NOT NULL,
                date TEXT NOT NULL
            )
        ''')
        # Tabel items transaksi
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transaction_items (
                id INTEGER PRIMARY KEY,
                transaction_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                subtotal REAL,
                FOREIGN KEY(transaction_id) REFERENCES transactions(id),
                FOREIGN KEY(product_id) REFERENCES products(id)
            )
        ''')
        self.conn.commit()

    def get_product_by_barcode(self, barcode):
        self.cursor.execute("SELECT * FROM products WHERE imei=?", (barcode,))
        product_data = self.cursor.fetchone()
        if product_data:
            product = Product()
            product.id = product_data[0]
            product.name = product_data[1]
            product.price = product_data[2]
            product.stock = product_data[3]
            product.imei = product_data[4]
            return product
        return None

    def add_product(self, product):
        self.cursor.execute("INSERT INTO products (name, price, stock, imei) VALUES (?, ?, ?, ?)",
                            (product.name, product.price, product.stock, product.imei))
        self.conn.commit()

    def add_transaction(self, total, items):
        date = datetime.now().isoformat()
        self.cursor.execute("INSERT INTO transactions (total, date) VALUES (?, ?)", (total, date))
        transaction_id = self.cursor.lastrowid
        for item in items:
            self.cursor.execute("INSERT INTO transaction_items (transaction_id, product_id, quantity, subtotal) VALUES (?, ?, ?, ?)",
                                (transaction_id, item.product.id, item.quantity, item.subtotal))
        self.conn.commit()

    def close(self):
        self.conn.close()
