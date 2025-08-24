import sqlite3
import os
from datetime import datetime, timedelta

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('pos.db', check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'cashier'
            )
        ''')

        # Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER DEFAULT 0,
                imei TEXT UNIQUE
            )
        ''')

        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                total REAL NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # Transaction items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transaction_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (transaction_id) REFERENCES transactions (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')

        # Insert default user if not exists
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', 'admin'))
        
        self.conn.commit()

    def get_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        return cursor.fetchone()

    def get_products(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products")
        return cursor.fetchall()

    def get_product_by_imei(self, imei):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products WHERE imei = ?", (imei,))
        return cursor.fetchone()

    def add_product(self, name, price, stock, imei=None):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO products (name, price, stock, imei) VALUES (?, ?, ?, ?)", 
                       (name, price, stock, imei))
        self.conn.commit()

    def update_product(self, product_id, name, price, stock, imei=None):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE products SET name = ?, price = ?, stock = ?, imei = ? WHERE id = ?", 
                       (name, price, stock, imei, product_id))
        self.conn.commit()

    def add_transaction(self, user_id, items):
        cursor = self.conn.cursor()
        total = sum(item['subtotal'] for item in items)
        cursor.execute("INSERT INTO transactions (user_id, total) VALUES (?, ?)", (user_id, total))
        transaction_id = cursor.lastrowid

        for item in items:
            cursor.execute("INSERT INTO transaction_items (transaction_id, product_id, quantity, subtotal) VALUES (?, ?, ?, ?)",
                           (transaction_id, item['product_id'], item['quantity'], item['subtotal']))
            # Update stock
            cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (item['quantity'], item['product_id']))

        self.conn.commit()
        return transaction_id

    def get_transactions(self, period='daily'):
        cursor = self.conn.cursor()
        if period == 'daily':
            date_filter = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT t.id, t.created_at, t.total, u.username 
                FROM transactions t
                JOIN users u ON t.user_id = u.id
                WHERE date(t.created_at) = ?
                ORDER BY t.created_at DESC
            ''', (date_filter,))
        elif period == 'weekly':
            week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT t.id, t.created_at, t.total, u.username 
                FROM transactions t
                JOIN users u ON t.user_id = u.id
                WHERE date(t.created_at) >= ?
                ORDER BY t.createdated_at DESC
            ''', (week_ago,))
        elif period == 'monthly':
            month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            cursor.execute('''
                SELECT t.id, t.created_at, t.total, u.username 
                FROM transactions t
                JOIN users u ON t.user_id = u.id
                WHERE date(t.created_at) >= ?
                ORDER BY t.created_at DESC
            ''', (month_ago,))
        else:
            cursor.execute('''
                SELECT t.id, t.created_at, t.total, u.username 
                FROM transactions t
                JOIN users u ON t.user_id = u.id
                ORDER BY t.created_at DESC
            ''')
        return cursor.fetchall()

    def get_transaction_details(self, transaction_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT p.name, ti.quantity, ti.subtotal
            FROM transaction_items ti
            JOIN products p ON ti.product_id = p.id
            WHERE ti.transaction_id = ?
        ''', (transaction_id,))
        return cursor.fetchall()
