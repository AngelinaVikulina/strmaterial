import sqlite3

conn = sqlite3.connect('shop.db')
cursor = conn.cursor()

# Добавляем администратора
cursor.execute("INSERT OR REPLACE INTO users (login, password, full_name, role) VALUES (?, ?, ?, ?)",
               ('admin', 'admin123', 'Тестовый Админ', 'admin'))

conn.commit()
conn.close()
print("✅ Пользователь admin добавлен")