import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import os

# Ensure DB file path in same folder
DB_PATH = os.path.join(os.path.dirname(__file__), 'inventory.db')

# Database setup
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL
            )''')
conn.commit()

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"

# Low-stock threshold
LOW_STOCK_THRESHOLD = 5

# Main Application
class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("760x520")
        self.root.resizable(True, True)
        self.login_screen()

    #Login
    def login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        login_frame = tk.Frame(self.root, pady=20)
        login_frame.pack(expand=True)

        tk.Label(login_frame, text="🔐 Admin Login", font=("Arial", 20, "bold")).pack(pady=10)
        tk.Label(login_frame, text="Username:", anchor='w').pack(fill='x', padx=50)
        self.username_entry = tk.Entry(login_frame)
        self.username_entry.pack(padx=50, pady=5)

        tk.Label(login_frame, text="Password:", anchor='w').pack(fill='x', padx=50)
        self.password_entry = tk.Entry(login_frame, show="*")
        self.password_entry.pack(padx=50, pady=5)

        btn_frame = tk.Frame(login_frame)
        btn_frame.pack(pady=12)
        tk.Button(btn_frame, text="Login", width=12, command=self.check_login, bg="#4CAF50", fg="white").grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Exit", width=12, command=self.root.quit, bg="#E57373", fg="white").grid(row=0, column=1, padx=5)

    def check_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            self.main_screen()
        else:
            messagebox.showerror("Error", "Invalid username or password!")

    #Main screen
    def main_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        top = tk.Frame(self.root)
        top.pack(fill='x', pady=6, padx=8)
        tk.Label(top, text="📦 Inventory Management System", font=("Arial", 18, "bold")).pack(side='left')
        tk.Button(top, text="Logout", command=self.login_screen, bg="#FFB74D").pack(side='right', padx=6)
        tk.Button(top, text="Export CSV", command=self.export_csv, bg="#90CAF9").pack(side='right', padx=6)

        # Left entry form
        left = tk.Frame(self.root, padx=10, pady=10, bd=1, relief=tk.GROOVE)
        left.place(x=8, y=60, width=320, height=440)

        tk.Label(left, text="Product Name:").grid(row=0, column=0, sticky='w', padx=6, pady=6)
        self.name_entry = tk.Entry(left)
        self.name_entry.grid(row=0, column=1, padx=6, pady=6)

        tk.Label(left, text="Quantity:").grid(row=1, column=0, sticky='w', padx=6, pady=6)
        self.quantity_entry = tk.Entry(left)
        self.quantity_entry.grid(row=1, column=1, padx=6, pady=6)

        tk.Label(left, text="Price (₹):").grid(row=2, column=0, sticky='w', padx=6, pady=6)
        self.price_entry = tk.Entry(left)
        self.price_entry.grid(row=2, column=1, padx=6, pady=6)

        tk.Button(left, text="Add Product", width=14, command=self.add_product, bg="#2196F3", fg="white").grid(row=3, column=0, pady=10, padx=6)
        tk.Button(left, text="Update Product", width=14, command=self.update_product, bg="#FFC107").grid(row=3, column=1, pady=10, padx=6)
        tk.Button(left, text="Delete Product", width=14, command=self.delete_product, bg="#F44336", fg="white").grid(row=4, column=0, pady=6, padx=6)
        tk.Button(left, text="Clear Fields", width=14, command=self.clear_fields, bg="#90A4AE").grid(row=4, column=1, pady=6, padx=6)

        # Search
        tk.Label(left, text="Search (name/category):").grid(row=5, column=0, columnspan=2, sticky='w', padx=6, pady=(12,4))
        self.search_entry = tk.Entry(left, width=25)
        self.search_entry.grid(row=6, column=0, columnspan=2, padx=6, pady=4)
        tk.Button(left, text="Search", width=14, command=self.search_product, bg="#64B5F6").grid(row=7, column=0, columnspan=2, pady=6)

        # Right table area
        columns = ("ID", "Name", "Quantity", "Price")
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings')
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Quantity", text="Quantity")
        self.tree.heading("Price", text="Price (₹)")
        self.tree.place(x=340, y=100, width=400, height=380)
        self.tree.bind("<ButtonRelease-1>", self.select_item)

        # Vertical scrollbar
        vsb = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        vsb.place(x=740, y=100, height=380)
        self.tree.configure(yscrollcommand=vsb.set)

        self.load_products()

    #DB ops
    def load_products(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        c.execute("SELECT * FROM products")
        rows = c.fetchall()
        for row in rows:
            tag = "low" if row[2] < LOW_STOCK_THRESHOLD else ""
            self.tree.insert("", tk.END, values=row, tags=(tag,))
        self.tree.tag_configure("low", background="#FFB6B6")
        #popup low stock alert
        self.check_low_stock(rows)

    def add_product(self):
        name = self.name_entry.get().strip()
        quantity = self.quantity_entry.get().strip()
        price = self.price_entry.get().strip()
        if not name or not quantity.isdigit() or not self.is_number(price):
            messagebox.showerror("Error", "Enter valid name, integer quantity, and numeric price.")
            return
        c.execute("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)",
                  (name, int(quantity), float(price)))
        conn.commit()
        messagebox.showinfo("Success", "Product added.")
        self.load_products()
        self.clear_fields()

    def update_product(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select a product to update.")
            return
        item = self.tree.item(selected)['values']
        prod_id = item[0]
        quantity = self.quantity_entry.get().strip()
        price = self.price_entry.get().strip()
        name = self.name_entry.get().strip()
        if not name or not quantity.isdigit() or not self.is_number(price):
            messagebox.showerror("Error", "Enter valid data to update.")
            return
        c.execute("UPDATE products SET name=?, quantity=?, price=? WHERE id=?",
                  (name, int(quantity), float(price), prod_id))
        conn.commit()
        messagebox.showinfo("Success", "Product updated.")
        self.load_products()
        self.clear_fields()

    def delete_product(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select a product to delete.")
            return
        item = self.tree.item(selected)['values']
        prod_id = item[0]
        if messagebox.askyesno("Confirm", f"Delete '{item[1]}' (ID {prod_id})?"):
            c.execute("DELETE FROM products WHERE id=?", (prod_id,))
            conn.commit()
            messagebox.showinfo("Deleted", "Product removed.")
            self.load_products()

    def search_product(self):
        key = self.search_entry.get().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)
        query = "SELECT * FROM products WHERE name LIKE ?"
        pattern = f"%{key}%"
        c.execute(query, (pattern,))
        rows = c.fetchall()
        for row in rows:
            tag = "low" if row[2] < LOW_STOCK_THRESHOLD else ""
            self.tree.insert("", tk.END, values=row, tags=(tag,))
        self.tree.tag_configure("low", background="#FFB6B6")
        self.check_low_stock(rows)

    def select_item(self, event):
        selected = self.tree.focus()
        if selected:
            item = self.tree.item(selected)['values']
            self.name_entry.delete(0, tk.END); self.name_entry.insert(0, item[1])
            self.quantity_entry.delete(0, tk.END); self.quantity_entry.insert(0, item[2])
            self.price_entry.delete(0, tk.END); self.price_entry.insert(0, item[3])

    def clear_fields(self):
        self.name_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.search_entry.delete(0, tk.END)

    def is_number(self, s):
        try:
            float(s)
            return True
        except:
            return False

    #Low stock alert
    def check_low_stock(self, rows):
        low = [r for r in rows if r[2] < LOW_STOCK_THRESHOLD]
        if low:
            msg = "⚠️ Low stock alert — these items have less than {} units:\n\n".format(LOW_STOCK_THRESHOLD)
            for r in low:
                msg += f"- {r[1]} (Qty: {r[2]})\n"
            # Show messagebox
            messagebox.showwarning("Low Stock", msg)

    #Export CSV
    def export_csv(self):
        import csv
        c.execute("SELECT * FROM products")
        rows = c.fetchall()
        path = os.path.join(os.path.dirname(__file__), "inventory_export.csv")
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Name", "Quantity", "Price"])
            writer.writerows(rows)
        messagebox.showinfo("Exported", f"Exported to {path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
    conn.close()
