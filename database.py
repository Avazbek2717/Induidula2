import sqlite3

DB_NAME = "sport_palaces.db"

def create_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Palaces jadvali - price_per_hour ustuni qo‘shildi
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS palaces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT,
            latitude REAL,
            longitude REAL,
            admin_name TEXT,
            admin_phone TEXT,
            price_per_hour REAL ,
            group_id INTEGER
        )
    """)
    
    # Users jadvali
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            full_name TEXT,
            phone TEXT
        )
    """)
    
    # Bookings jadvali, user_id bilan bog‘langan va yangi ustunlar qo‘shildi
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            palace_id INTEGER,
            user_id INTEGER,
            visit_time TEXT,
            hours REAL,
            payment_amount REAL,
            access_id TEXT,
            FOREIGN KEY (palace_id) REFERENCES palaces(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    conn.commit()
    conn.close()


import sqlite3
import random
from datetime import datetime, timedelta

DB_NAME = "sport_palaces.db"

def add_sample_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Palaces uchun 5 ta namuna ma'lumot
    palaces_data = [
        ("Suv sport saroyi", "Toshkent, Chilonzor", "Suzish havzasi, sauna, trenajyor zallari mavjud.", 41.2995, 69.2401, "Ali aka", "+998901234567", 50000,1002683611651,),
        ("Olimpiya sport majmuasi", "Toshkent, Yunusobod", "Suzish havzalari, sport zallari, tennis kortlari.", 41.3242, 69.2283, "Vali aka", "+998909876543", 70000,1002683611651,),
        ("Yoshlar sport markazi", "Samarqand, Registon ko'chasi", "Basketbol va voleybol zallari, fitnes xonasi.", 39.6544, 66.9597, "Zakir aka", "+998901112233", 30000,1002683611651,),
        ("Shahrisabz sport kompleksi", "Shahrisabz, Markaziy ko‘cha", "Sport zallari va suzish havzasi.", 38.2166, 67.8611, "Jahongir aka", "+998901234890", 45000,1002683611651,),
        ("Buxoro sport saroyi", "Buxoro, Amir Temur ko‘chasi", "Yengil atletika va sport zallari.", 39.7747, 64.4286, "Rustam aka", "+998909876700", 40000,1002683611651,),
    ]
    cursor.executemany("""
        INSERT INTO palaces (name, location, description, latitude, longitude, admin_name, admin_phone, price_per_hour, group_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, palaces_data)

    # Users uchun 5 ta namuna ma'lumot
    users_data = [
        (123456789, "Avazbek Toshtonov", "+998901112233"),
        (987654321, "Nigina Rasulova", "+998909998877"),
        (111222333, "Jasur Qodirov", "+998905551122"),
        (444555666, "Dilshod Akramov", "+998901234567"),
        (777888999, "Sevara Karimova", "+998907777666"),
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO users (telegram_id, full_name, phone)
        VALUES (?, ?, ?)
    """, users_data)

    # Bookings uchun 5 ta namuna ma'lumot
    # palace_id va user_id ni 1-5 orasida random tanlab, visit_time va payment_amount hisoblaymiz
    bookings_data = []
    for i in range(5):
        palace_id = random.randint(1, 5)
        user_id = random.randint(1, 5)
        # Hozirgi vaqtdan tasodifiy keyingi 1-7 kun oralig'ida
        visit_time = (datetime.now() + timedelta(days=random.randint(1,7))).strftime("%Y-%m-%d %H:%M")
        hours = random.choice([1, 2, 3])
        
        # price_per_hour olish uchun palace ni so'raymiz
        cursor.execute("SELECT price_per_hour FROM palaces WHERE id = ?", (palace_id,))
        price_per_hour = cursor.fetchone()[0]
        payment_amount = price_per_hour * hours
        
        # Tasodifiy access_id (oddiy raqam)
        access_id = f"ACCESS{random.randint(1000,9999)}"
        
        bookings_data.append((palace_id, user_id, visit_time, hours, payment_amount, access_id))
    
    cursor.executemany("""
        INSERT INTO bookings (palace_id, user_id, visit_time, hours, payment_amount, access_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, bookings_data)

    conn.commit()
    conn.close()


def get_all_palaces():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM palaces")
    results = cursor.fetchall()
    conn.close()
    return results

def get_palace_by_id(palace_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, location, description, photo FROM palaces WHERE id = ?", (palace_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_palace_details_by_id(palace_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, location, description, latitude, longitude, admin_name, admin_phone, price_per_hour
        FROM palaces WHERE id = ?
    """, (palace_id,))
    result = cursor.fetchone()
    conn.close()
    return result
