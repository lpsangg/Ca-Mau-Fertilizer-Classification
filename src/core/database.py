"""
Database Manager for Ca Mau Fertilizer Classification System.
Built with SQLite3 (Zero-Config, no external server required).
Manages users, authentication, orders, order items, and counting sessions.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from src.config import DATABASE_PATH
from src.core.security import hash_password, verify_password

class DatabaseManager:
    def __init__(self, db_path: Path = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
        self.seed_default_data()

    def get_connection(self) -> sqlite3.Connection:
        """Create and return a new SQLite database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Create tables if they do not exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Users Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    role TEXT DEFAULT 'operator',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 2. Orders Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_name TEXT NOT NULL,
                    status TEXT CHECK(status IN ('PENDING', 'PROCESSING', 'COMPLETED')) DEFAULT 'PENDING',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)

            # 3. Order Items Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    product_name TEXT NOT NULL,
                    quantity_ordered INTEGER NOT NULL,
                    quantity_counted INTEGER DEFAULT 0,
                    FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE
                )
            """)

            # 4. Counting Session History Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS counting_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER,
                    video_source TEXT,
                    count_urea_bio_xanh INTEGER DEFAULT 0,
                    count_npk_22_5_6 INTEGER DEFAULT 0,
                    count_urea_hat_duc INTEGER DEFAULT 0,
                    start_time TEXT,
                    end_time TEXT,
                    exported_file TEXT,
                    FOREIGN KEY (order_id) REFERENCES orders (id)
                )
            """)
            conn.commit()

    def seed_default_data(self):
        """Seed default admin accounts if users table is empty."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM users")
            if cursor.fetchone()["count"] == 0:
                # Add default admin
                h1, s1 = hash_password("123456")
                cursor.execute(
                    "INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, ?)",
                    ("admin", h1, s1, "admin")
                )
                # Add legacy fallback account for compatibility
                h2, s2 = hash_password("123")
                cursor.execute(
                    "INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, ?)",
                    ("phanloaisp", h2, s2, "operator")
                )
                conn.commit()

    # --- User Management Methods ---

    def register_user(self, username: str, password: str, role: str = "operator") -> tuple[bool, str]:
        """Register a new user."""
        username = username.strip()
        if not username or not password:
            return False, "Tên đăng nhập và mật khẩu không được để trống."

        pwd_hash, salt = hash_password(password)
        try:
            with self.get_connection() as conn:
                conn.cursor().execute(
                    "INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, ?)",
                    (username, pwd_hash, salt, role)
                )
                conn.commit()
            return True, "Đăng ký tài khoản thành công!"
        except sqlite3.IntegrityError:
            return False, f"Tài khoản '{username}' đã tồn tại trong hệ thống."
        except Exception as e:
            return False, f"Lỗi cơ sở dữ liệu: {e}"

    def authenticate_user(self, username: str, password: str) -> tuple[bool, dict | None]:
        """Authenticate user credentials."""
        username = username.strip()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, password_hash, salt, role FROM users WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
            if not row:
                return False, None

            if verify_password(password, row["password_hash"], row["salt"]):
                user_info = {
                    "id": row["id"],
                    "username": row["username"],
                    "role": row["role"]
                }
                return True, user_info
            return False, None

    # --- Order Management Methods ---

    def create_order(self, customer_name: str, items: dict[str, int]) -> tuple[bool, int | None]:
        """
        Create a new order with items.
        items: {"Urea Bio xanh": 50, "NPK 22-5-6": 30}
        """
        customer_name = customer_name.strip()
        if not customer_name:
            return False, None
        if not items:
            return False, None

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO orders (customer_name, status) VALUES (?, 'PENDING')",
                (customer_name,)
            )
            order_id = cursor.lastrowid

            for product, qty in items.items():
                if qty > 0:
                    cursor.execute(
                        "INSERT INTO order_items (order_id, product_name, quantity_ordered) VALUES (?, ?, ?)",
                        (order_id, product, qty)
                    )
            conn.commit()
            return True, order_id

    def get_all_orders(self) -> list[dict]:
        """Fetch all orders with their summary."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.id, o.customer_name, o.status, o.created_at, o.completed_at
                FROM orders o
                ORDER BY o.id DESC
            """)
            orders = [dict(row) for row in cursor.fetchall()]

            for order in orders:
                cursor.execute(
                    "SELECT product_name, quantity_ordered, quantity_counted FROM order_items WHERE order_id = ?",
                    (order["id"],)
                )
                order["items"] = [dict(r) for r in cursor.fetchall()]
            return orders

    def get_order_by_id(self, order_id: int) -> dict | None:
        """Fetch a specific order by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
            row = cursor.fetchone()
            if not row:
                return None
            order = dict(row)
            cursor.execute(
                "SELECT product_name, quantity_ordered, quantity_counted FROM order_items WHERE order_id = ?",
                (order_id,)
            )
            order["items"] = [dict(r) for r in cursor.fetchall()]
            return order

    def update_order_counted_qty(self, order_id: int, counts: dict[str, int]):
        """Update actual counted quantities for an order."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for product, qty in counts.items():
                cursor.execute(
                    "UPDATE order_items SET quantity_counted = ? WHERE order_id = ? AND product_name = ?",
                    (qty, order_id, product)
                )
            cursor.execute("UPDATE orders SET status = 'PROCESSING' WHERE id = ? AND status = 'PENDING'", (order_id,))
            conn.commit()

    def complete_order(self, order_id: int):
        """Mark an order as COMPLETED."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "UPDATE orders SET status = 'COMPLETED', completed_at = ? WHERE id = ?",
                (now_str, order_id)
            )
            conn.commit()

    def delete_order(self, order_id: int) -> bool:
        """Delete an order and its items."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
            conn.commit()
            return True

    def record_counting_session(self, order_id: int | None, video_source: str,
                                counts: dict[str, int], start_time: str,
                                end_time: str, exported_file: str = "") -> int:
        """Record an audit trail of an AI video counting session."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO counting_history (
                    order_id, video_source,
                    count_urea_bio_xanh, count_npk_22_5_6, count_urea_hat_duc,
                    start_time, end_time, exported_file
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                order_id,
                video_source,
                counts.get("Urea_Bio_xanh", 0),
                counts.get("NPK_22-5-6", 0),
                counts.get("Urea_hat_duc", 0),
                start_time,
                end_time,
                exported_file
            ))
            conn.commit()
            return cursor.lastrowid
