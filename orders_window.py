import tkinter as tk
from tkinter import ttk, messagebox
import database
from add_edit_order import AddEditOrderWindow


class OrdersWindow:
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Управление заказами - СтройМатериалы")
        self.window.geometry("1000x500")
        self.window.grab_set()

        self.create_table()
        self.load_orders()

        btn_frame = tk.Frame(self.window)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Добавить заказ", command=self.add_order, bg="#B8860B", fg="white").pack(side=tk.LEFT,
                                                                                                           padx=5)
        tk.Button(btn_frame, text="Редактировать", command=self.edit_order, bg="#B8860B", fg="white").pack(side=tk.LEFT,
                                                                                                           padx=5)
        tk.Button(btn_frame, text="Удалить", command=self.delete_order, bg="#B8860B", fg="white").pack(side=tk.LEFT,
                                                                                                       padx=5)
        tk.Button(btn_frame, text="Обновить", command=self.load_orders, bg="#DAA520", fg="black").pack(side=tk.LEFT,
                                                                                                       padx=5)

    def create_table(self):
        frame = tk.Frame(self.window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ('ID', 'Артикул', 'Статус', 'Адрес пункта выдачи', 'Дата заказа', 'Дата выдачи', 'Клиент')
        self.tree = ttk.Treeview(frame, columns=columns, show='headings')

        col_widths = {'ID': 50, 'Артикул': 120, 'Статус': 100, 'Адрес пункта выдачи': 200,
                      'Дата заказа': 100, 'Дата выдачи': 100, 'Клиент': 150}
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_widths.get(col, 100))

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def load_orders(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        orders = database.get_all_orders()
        for order in orders:
            self.tree.insert('', tk.END, values=order)

    def add_order(self):
        AddEditOrderWindow(self.window, parent_callback=self.load_orders)

    def edit_order(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите заказ для редактирования")
            return
        order_id = self.tree.item(selected[0])['values'][0]
        AddEditOrderWindow(self.window, order_id, self.load_orders)

    def delete_order(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите заказ для удаления")
            return

        if messagebox.askyesno("Подтверждение", "Удалить заказ?"):
            order_id = self.tree.item(selected[0])['values'][0]
            database.delete_order(order_id)
            self.load_orders()
            messagebox.showinfo("Успех", "Заказ удален")