import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os
import database
from add_edit_product import AddEditProductWindow
from orders_window import OrdersWindow


class AuthWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Авторизация - ООО СтройМатериалы")
        self.window.geometry("400x300")
        self.window.eval('tk::PlaceWindow . center')

        if os.path.exists('icon.ico'):
            try:
                self.window.iconbitmap('icon.ico')
            except:
                pass

        tk.Label(self.window, text="Добро пожаловать в СтройМатериалы!", font=("Calibri", 14, "bold")).pack(pady=20)
        tk.Label(self.window, text="Войдите в систему или продолжите как гость", font=("Calibri", 10)).pack(pady=5)

        frame = tk.Frame(self.window, bg="#FFFFFF")
        frame.pack(pady=20)

        tk.Label(frame, text="Логин:", font=("Calibri", 10)).grid(row=0, column=0, pady=5, padx=5, sticky="e")
        self.login_entry = tk.Entry(frame, width=25, font=("Calibri", 10))
        self.login_entry.grid(row=0, column=1, pady=5)

        tk.Label(frame, text="Пароль:", font=("Calibri", 10)).grid(row=1, column=0, pady=5, padx=5, sticky="e")
        self.password_entry = tk.Entry(frame, width=25, show="*", font=("Calibri", 10))
        self.password_entry.grid(row=1, column=1, pady=5)

        btn_frame = tk.Frame(self.window)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Войти", command=self.login, width=15, bg="#B8860B", fg="white",
                  font=("Calibri", 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Продолжить как гость", command=self.guest, width=20, bg="#DAA520", fg="black",
                  font=("Calibri", 10)).pack(side=tk.LEFT, padx=5)

        self.window.mainloop()

    def login(self):
        login = self.login_entry.get()
        password = self.password_entry.get()

        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT full_name, role FROM users WHERE login = ? AND password = ?', (login, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            self.window.destroy()
            MainWindow(user[0], user[1])
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль!")

    def guest(self):
        self.window.destroy()
        MainWindow("Гость", "guest")


class MainWindow:
    def __init__(self, user_name, role):
        self.user_name = user_name
        self.role = role
        self.all_items_cache = []
        self.current_manufacturer_filter = "Все производители"
        self.current_sort_column = None
        self.current_sort_reverse = False

        self.window = tk.Tk()
        self.window.title("СтройМатериалы - Система управления")
        self.window.geometry("1400x750")
        self.window.configure(bg="#FFFFFF")

        if os.path.exists('icon.ico'):
            try:
                self.window.iconbitmap('icon.ico')
            except:
                pass

        top_frame = tk.Frame(self.window, bg="#DAA520", height=50)
        top_frame.pack(fill=tk.X)
        top_frame.pack_propagate(False)

        if os.path.exists('icon.png'):
            try:
                img = Image.open('icon.png')
                img = img.resize((40, 40), Image.Resampling.LANCZOS)
                logo = ImageTk.PhotoImage(img)
                logo_label = tk.Label(top_frame, image=logo, bg="#DAA520")
                logo_label.image = logo
                logo_label.pack(side=tk.LEFT, padx=10)
            except:
                pass

        tk.Label(top_frame, text=f"👤 {user_name} | Роль: {role}", bg="#DAA520", font=("Calibri", 10)).pack(
            side=tk.RIGHT, padx=10, pady=10)

        btn_frame = tk.Frame(top_frame, bg="#DAA520")
        btn_frame.pack(side=tk.LEFT, padx=10)

        tk.Button(btn_frame, text="🚪 Выйти", command=self.logout, bg="#B8860B", fg="white", font=("Calibri", 10)).pack(
            side=tk.LEFT, padx=5)

        if role == 'admin':
            tk.Button(btn_frame, text="➕ Добавить товар", command=self.add_product, bg="#B8860B", fg="white",
                      font=("Calibri", 10)).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="🗑️ Удалить товар", command=self.delete_product, bg="#B8860B", fg="white",
                      font=("Calibri", 10)).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="📥 Импорт Excel", command=self.import_excel_menu, bg="#B8860B", fg="white",
                      font=("Calibri", 10)).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="📦 Заказы", command=self.show_orders, bg="#B8860B", fg="white",
                      font=("Calibri", 10)).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="🔄 Обновить", command=self.load_products, bg="#B8860B", fg="white",
                      font=("Calibri", 10)).pack(side=tk.LEFT, padx=5)
        elif role == 'manager':
            tk.Button(btn_frame, text="📦 Заказы", command=self.show_orders, bg="#B8860B", fg="white",
                      font=("Calibri", 10)).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="🔄 Обновить", command=self.load_products, bg="#B8860B", fg="white",
                      font=("Calibri", 10)).pack(side=tk.LEFT, padx=5)
        else:
            tk.Button(btn_frame, text="🔄 Обновить", command=self.load_products, bg="#B8860B", fg="white",
                      font=("Calibri", 10)).pack(side=tk.LEFT, padx=5)

        filter_frame = tk.Frame(self.window, bg="#FFFFFF")
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(filter_frame, text="Производитель:", font=("Calibri", 10), bg="#FFFFFF").pack(side=tk.LEFT, padx=5)
        self.manufacturer_filter_var = tk.StringVar(value="Все производители")
        self.manufacturer_combo = ttk.Combobox(filter_frame, textvariable=self.manufacturer_filter_var, width=20)
        self.manufacturer_combo.pack(side=tk.LEFT, padx=5)
        self.manufacturer_combo.bind('<<ComboboxSelected>>', self.apply_filters)

        tk.Label(filter_frame, text="🔍 Поиск:", font=("Calibri", 10), bg="#FFFFFF").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(filter_frame, width=40, font=("Calibri", 10))
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', self.apply_filters)
        tk.Label(filter_frame, text="(поиск по всем полям)", fg="gray", bg="#FFFFFF", font=("Calibri", 9)).pack(
            side=tk.LEFT, padx=5)

        self.create_product_table()
        self.load_products()

        self.window.mainloop()

    def create_product_table(self):
        frame = tk.Frame(self.window, bg="#FFFFFF")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scroll_y = tk.Scrollbar(frame)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.columns = ('ID', 'Название', 'Категория', 'Описание', 'Производитель',
                        'Поставщик', 'Цена', 'Ед.изм', 'Кол-во', 'Скидка')

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background="white", foreground="black", rowheight=25, font=("Calibri", 9))
        style.configure("Treeview.Heading", font=("Calibri", 10, "bold"))
        style.map('Treeview', background=[('selected', '#B8860B')])

        self.tree = ttk.Treeview(frame, columns=self.columns, show='headings',
                                 yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        col_widths = {
            'ID': 50, 'Название': 180, 'Категория': 100, 'Описание': 200,
            'Производитель': 120, 'Поставщик': 120, 'Цена': 100, 'Ед.изм': 70,
            'Кол-во': 80, 'Скидка': 70
        }

        for col in self.columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=col_widths.get(col, 100))

        self.tree.pack(fill=tk.BOTH, expand=True)

        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        self.tree.tag_configure('high_discount', background='#F4A460', foreground='black')
        self.tree.tag_configure('no_stock', background='#ADD8E6', foreground='black')

        if self.role == 'admin':
            self.tree.bind('<Double-1>', self.edit_product)

    def load_products(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        manufacturers = database.get_unique_manufacturers()
        self.manufacturer_combo['values'] = ["Все производители"] + manufacturers
        self.manufacturer_filter_var.set("Все производители")

        products = database.get_all_products()

        for p in products:
            product_id, name, category, desc, manufacturer, supplier, price, unit, quantity, discount, final_price, image_path = p

            if discount is None:
                discount = 0

            tag = ''
            if discount > 12:
                tag = 'high_discount'
            elif quantity == 0:
                tag = 'no_stock'

            price_display = f"{price:.2f}₽"
            values = (product_id, name, category, desc[:80] + "..." if len(desc) > 80 else desc,
                      manufacturer, supplier, price_display, unit, quantity, f"{discount}%")

            self.tree.insert('', tk.END, values=values, tags=(tag,))

        self.all_items_cache = self.tree.get_children('')
        print(f"✅ Загружено товаров: {len(self.all_items_cache)}")

    def sort_by_column(self, col):
        if self.current_sort_column == col:
            self.current_sort_reverse = not self.current_sort_reverse
        else:
            self.current_sort_column = col
            self.current_sort_reverse = False
        self.apply_filters()

    def apply_filters(self, event=None):
        search_text = self.search_entry.get().lower().strip()
        manufacturer_filter = self.manufacturer_filter_var.get()

        items = []
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']

            if search_text and search_text not in str(values).lower():
                continue
            if manufacturer_filter != "Все производители" and manufacturer_filter != values[4]:
                continue
            items.append((item, values))

        if self.current_sort_column:
            col_index = self.columns.index(self.current_sort_column)
            if self.current_sort_column in ['Цена', 'Кол-во', 'Скидка']:
                try:
                    items.sort(key=lambda x: float(x[1][col_index].replace('₽', '').replace('%', '').strip()),
                               reverse=self.current_sort_reverse)
                except:
                    items.sort(key=lambda x: str(x[1][col_index]), reverse=self.current_sort_reverse)
            else:
                items.sort(key=lambda x: str(x[1][col_index]), reverse=self.current_sort_reverse)

        for idx, (item, _) in enumerate(items):
            self.tree.move(item, '', idx)

        for col in self.columns:
            if col == self.current_sort_column:
                arrow = " ↓" if self.current_sort_reverse else " ↑"
                self.tree.heading(col, text=col + arrow)
            else:
                self.tree.heading(col, text=col)

    def add_product(self):
        AddEditProductWindow(self.window, parent_callback=self.load_products)

    def edit_product(self, event):
        selected = self.tree.selection()
        if selected:
            product_id = self.tree.item(selected[0])['values'][0]
            AddEditProductWindow(self.window, product_id, self.load_products)

    def delete_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите товар для удаления")
            return

        product_id = self.tree.item(selected[0])['values'][0]
        product_name = self.tree.item(selected[0])['values'][1]

        if messagebox.askyesno("Подтверждение", f"Удалить товар '{product_name}'?"):
            if database.delete_product(product_id):
                messagebox.showinfo("Успех", "Товар удален!")
                self.load_products()
            else:
                messagebox.showerror("Ошибка", "Товар присутствует в заказах, удаление невозможно!")

    def import_excel_menu(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return

        filename = os.path.basename(file_path)

        try:
            if "user" in filename.lower():
                count = database.import_users_from_excel(file_path)
                msg = f"Импортировано пользователей: {count}"
            elif "tovar" in filename.lower() or "product" in filename.lower():
                count = database.import_products_from_excel(file_path)
                msg = f"Импортировано товаров: {count}"
            elif "пункт" in filename.lower() or "delivery" in filename.lower():
                count = database.import_delivery_points_from_excel(file_path)
                msg = f"Импортировано пунктов выдачи: {count}"
            elif "заказ" in filename.lower() or "order" in filename.lower():
                count = database.import_orders_from_excel(file_path)
                msg = f"Импортировано заказов: {count}"
            else:
                msg = "Файл импортирован"

            messagebox.showinfo("Импорт", msg)
            self.load_products()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def show_orders(self):
        OrdersWindow(self.window)

    def logout(self):
        self.window.destroy()
        AuthWindow()


if __name__ == "__main__":
    if not os.path.exists('shop.db'):
        messagebox.showerror("Ошибка", "База данных не найдена!\nСначала запустите create_database.py")
    else:
        AuthWindow()