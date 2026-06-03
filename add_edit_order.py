import tkinter as tk
from tkinter import ttk, messagebox
import database


class AddEditOrderWindow:
    def __init__(self, parent, order_id=None, parent_callback=None):
        self.parent = parent
        self.order_id = order_id
        self.parent_callback = parent_callback

        self.window = tk.Toplevel(parent)
        title = "Редактирование заказа" if order_id else "Добавление заказа"
        self.window.title(title)
        self.window.geometry("500x450")
        self.window.grab_set()

        self.create_widgets()

        if order_id:
            self.load_order_data()

    def create_widgets(self):
        frame = tk.Frame(self.window)
        frame.pack(pady=20)

        fields = [
            ("Артикул заказа:", "order_number_entry"),
            ("Статус:", "status_combo"),
            ("Адрес пункта выдачи:", "address_entry"),
            ("Дата заказа (ГГГГ-ММ-ДД):", "order_date_entry"),
            ("Дата выдачи (ГГГГ-ММ-ДД):", "issue_date_entry"),
        ]

        self.entries = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(frame, text=label).grid(row=i, column=0, pady=5, padx=5, sticky="e")

            if key == "status_combo":
                self.status_combo = ttk.Combobox(frame, width=37)
                self.status_combo['values'] = ['Новый', 'В обработке', 'Отправлен', 'Доставлен', 'Отменен']
                self.status_combo.grid(row=i, column=1, pady=5, padx=5)
                self.entries[key] = self.status_combo
            else:
                entry = tk.Entry(frame, width=40)
                entry.grid(row=i, column=1, pady=5, padx=5)
                self.entries[key] = entry

        btn_frame = tk.Frame(self.window)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Сохранить", command=self.save, bg="#B8860B", fg="white", width=15).pack(side=tk.LEFT,
                                                                                                           padx=10)
        tk.Button(btn_frame, text="Отмена", command=self.window.destroy, bg="#DAA520", fg="black", width=15).pack(
            side=tk.LEFT, padx=10)

    def load_order_data(self):
        order = database.get_order_by_id(self.order_id)
        if order:
            self.entries['order_number_entry'].insert(0, order[1] or '')
            self.status_combo.set(order[2] or '')
            self.entries['address_entry'].insert(0, order[3] or '')
            self.entries['order_date_entry'].insert(0, order[4] or '')
            self.entries['issue_date_entry'].insert(0, order[5] or '')

    def save(self):
        try:
            order_number = self.entries['order_number_entry'].get()
            status = self.status_combo.get()
            address = self.entries['address_entry'].get()
            order_date = self.entries['order_date_entry'].get()
            issue_date = self.entries['issue_date_entry'].get()

            if not order_number:
                messagebox.showerror("Ошибка", "Введите артикул заказа")
                return

            if self.order_id:
                database.update_order(self.order_id, order_number, status, address, order_date, issue_date, 1)
            else:
                database.add_order(order_number, status, address, order_date, issue_date, 1)

            self.window.destroy()
            if self.parent_callback:
                self.parent_callback()
            messagebox.showinfo("Успех", "Заказ сохранен!")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")