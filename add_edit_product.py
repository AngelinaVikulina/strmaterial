import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import shutil
import os
from PIL import Image, ImageTk
import database


class AddEditProductWindow:
    def __init__(self, parent, product_id=None, parent_callback=None):
        self.parent = parent
        self.product_id = product_id
        self.parent_callback = parent_callback
        self.image_path = None

        self.window = tk.Toplevel(parent)
        title = "Редактирование товара" if product_id else "Добавление товара"
        self.window.title(title)
        self.window.geometry("600x700")
        self.window.grab_set()

        self.create_widgets()

        if product_id:
            self.load_product_data()

    def create_widgets(self):
        # Фото
        self.image_label = tk.Label(self.window, text="Фото товара", width=30, height=10, bg="#f0f0f0")
        self.image_label.pack(pady=10)
        tk.Button(self.window, text="Выбрать фото", command=self.select_image).pack()

        # Поля ввода
        frame = tk.Frame(self.window)
        frame.pack(pady=10)

        fields = [
            ("Наименование:", "name_entry"),
            ("Категория:", "category_entry"),
            ("Описание:", "desc_entry"),
            ("Производитель:", "manufacturer_entry"),
            ("Поставщик:", "supplier_entry"),
            ("Цена:", "price_entry"),
            ("Единица измерения:", "unit_entry"),
            ("Количество:", "quantity_entry"),
        ]

        self.entries = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(frame, text=label).grid(row=i, column=0, pady=5, padx=5, sticky="e")
            entry = tk.Entry(frame, width=40)
            entry.grid(row=i, column=1, pady=5, padx=5)
            self.entries[key] = entry

        # Скидка
        tk.Label(frame, text="Скидка:").grid(row=len(fields), column=0, pady=5, padx=5, sticky="e")
        self.discount_combo = ttk.Combobox(frame, width=37)
        discounts = database.get_all_discounts()
        self.discount_list = discounts
        self.discount_combo['values'] = [f"{d[1]} ({d[2]}%)" for d in discounts]
        self.discount_combo.grid(row=len(fields), column=1, pady=5, padx=5)
        self.discount_combo.current(0)

        # Кнопки
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Сохранить", command=self.save, bg="#B8860B", fg="white", width=15).pack(side=tk.LEFT,
                                                                                                           padx=10)
        tk.Button(btn_frame, text="Отмена", command=self.window.destroy, bg="#DAA520", fg="black", width=15).pack(
            side=tk.LEFT, padx=10)

    def select_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if file_path:
            self.image_path = file_path
            img = Image.open(file_path)
            img = img.resize((200, 150), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo)
            self.image_label.image = photo

    def load_product_data(self):
        product = database.get_product_by_id(self.product_id)
        if product:
            self.entries['name_entry'].insert(0, product[1] or '')
            self.entries['category_entry'].insert(0, product[2] or '')
            self.entries['desc_entry'].insert(0, product[3] or '')
            self.entries['manufacturer_entry'].insert(0, product[4] or '')
            self.entries['supplier_entry'].insert(0, product[5] or '')
            self.entries['price_entry'].insert(0, str(product[6] or ''))
            self.entries['unit_entry'].insert(0, product[7] or 'шт')
            self.entries['quantity_entry'].insert(0, str(product[8] or '0'))
            self.image_path = product[10]

    def save(self):
        try:
            name = self.entries['name_entry'].get()
            category = self.entries['category_entry'].get()
            description = self.entries['desc_entry'].get()
            manufacturer = self.entries['manufacturer_entry'].get()
            supplier = self.entries['supplier_entry'].get()
            price = float(self.entries['price_entry'].get())
            unit = self.entries['unit_entry'].get()
            quantity = int(self.entries['quantity_entry'].get())

            discount_index = self.discount_combo.current()
            discount_id = self.discount_list[discount_index][0] if discount_index >= 0 else 1

            saved_image_path = None
            if self.image_path and os.path.exists(self.image_path):
                images_dir = "product_images"
                os.makedirs(images_dir, exist_ok=True)
                filename = f"{name}_{int(price)}.png"
                saved_image_path = os.path.join(images_dir, filename)
                shutil.copy2(self.image_path, saved_image_path)

            if self.product_id:
                database.update_product(self.product_id, name, category, description, manufacturer, supplier, price,
                                        unit, quantity, discount_id, saved_image_path)
                messagebox.showinfo("Успех", "Товар обновлен!")
            else:
                database.add_product(name, category, description, manufacturer, supplier, price, unit, quantity,
                                     discount_id, saved_image_path)
                messagebox.showinfo("Успех", "Товар добавлен!")

            self.window.destroy()

            if self.parent_callback:
                self.parent_callback()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")