import tkinter as tk
from tkinter import ttk, simpledialog
import pyperclip
import json
import os
import threading
from cryptography.fernet import Fernet

# pip install pyperclip cryptography
# pyinstaller --onefile --windowed PM.py
# 密码管理器，双击复制密码。有主密码做全局管理，要在windows的bash中打包

class PasswordManager:
    def __init__(self, root):
        self.root = root
        self.root.title("密码管理器")
        self.root.geometry("300x500")
        self.root.configure(bg="#f0f0f0")
        
        style = ttk.Style()
        style.configure(
            "Blue.TButton",
            background="#FFFFFF",
            foreground="#3f3f3f",
            padding=3,
            relief="flat",
            font=("Arial", 9, "bold")
        )
        style.map("Blue.TButton", background=[("active", "#0056b3")])

        self.key = self.load_or_generate_key()
        self.cipher = Fernet(self.key)
        self.master_password = self.load_master_password()
        self.passwords = self.load_passwords()
        
        self.show_login()
    
    def load_or_generate_key(self):
        if os.path.exists("key.key"):
            with open("key.key", "rb") as f:
                return f.read()
        key = Fernet.generate_key()
        with open("key.key", "wb") as f:
            f.write(key)
        return key

    def load_master_password(self):
        if os.path.exists("master.txt"):
            with open("master.txt", "rb") as f:
                return self.cipher.decrypt(f.read()).decode()
        master = simpledialog.askstring("设置主密码", "首次使用，请设置主密码:", show="*")
        with open("master.txt", "wb") as f:
            f.write(self.cipher.encrypt(master.encode()))
        return master
    
    def load_passwords(self):
        if os.path.exists("passwords.json"):
            with open("passwords.json", "rb") as f:
                encrypted = f.read()
                decrypted = self.cipher.decrypt(encrypted)
                return json.loads(decrypted.decode())
        return {}

    def save_passwords(self):
        encrypted = self.cipher.encrypt(json.dumps(self.passwords).encode())
        with open("passwords.json", "wb") as f:
            f.write(encrypted)
    
    def show_login(self):
        self.login_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.login_frame.pack(pady=50)
        
        tk.Label(self.login_frame, text="输入主密码", bg="#f0f0f0", font=("Arial", 12)).pack()
        self.pass_entry = tk.Entry(self.login_frame, show="*", width=20)
        self.pass_entry.pack(pady=5)
        
        ttk.Button(self.login_frame, text="登录", command=self.verify_password, style="Blue.TButton").pack()
    
    def verify_password(self):
        if self.pass_entry.get() == self.master_password:
            self.login_frame.destroy()
            self.create_main_window()
        else:
            self.show_message("密码错误", "red")
    
    def create_main_window(self):
        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(self.main_frame, text="密码管理器", font=("Arial", 14), bg="#f0f0f0").pack(pady=10)
        
        self.tree = ttk.Treeview(self.main_frame, columns=("Key", "Value", "Copy"), show="headings", height=15)
        self.tree.heading("Key", text="名称")
        self.tree.heading("Value", text="密码")
        self.tree.column("Key", width=150)
        self.tree.column("Value", width=150)
        self.tree.pack(pady=10)
        
        for name in self.passwords.keys():
            self.tree.insert("", "end", values=(name, "********"))
        
        self.tree.bind("<Double-1>", self.copy_password)

        btn_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        # btn_frame.pack(pady=10)
        
        
        # ttk.Button(btn_frame, text="添加密码", command=self.add_password, style="Blue.TButton").grid(row=0, column=0, padx=2)
        # ttk.Button(btn_frame, text="修改密码", command=self.edit_password, style="Blue.TButton").grid(row=0, column=1, padx=2)
        # ttk.Button(btn_frame, text="查看密码", command=self.view_all_passwords, style="Blue.TButton").grid(row=0, column=2, padx=2)

        btn_frame.pack(pady=5, fill=tk.X)
        ttk.Button(btn_frame, text="添加密码", command=self.add_password, style="Blue.TButton", width=10).grid(row=0, column=0, padx=2)
        ttk.Button(btn_frame, text="修改密码", command=self.edit_password, style="Blue.TButton", width=10).grid(row=0, column=1, padx=2)
        ttk.Button(btn_frame, text="查看所有密码", command=self.view_all_passwords, style="Blue.TButton", width=12).grid(row=0, column=2, padx=2)
    
    def copy_password(self, event):
        item = self.tree.selection()
        if item:
            key = self.tree.item(item, "values")[0]
            pyperclip.copy(self.passwords[key])
            self.show_message(f"{key} 密码已复制", "blue")
    
    def add_password(self):
        name = simpledialog.askstring("添加密码", "请输入名称:")
        if name:
            password = simpledialog.askstring("添加密码", "请输入密码:", show="*")
            if password:
                self.passwords[name] = password
                self.save_passwords()
                self.tree.insert("", "end", values=(name, "********"))
    
    def edit_password(self):
        selected_item = self.tree.selection()
        if not selected_item:
            self.show_message("请先选择一个条目", "red")
            return
        key = self.tree.item(selected_item, "values")[0]
        new_password = simpledialog.askstring("修改密码", "请输入新密码:", show="*")
        if new_password:
            self.passwords[key] = new_password
            self.save_passwords()
            self.show_message("修改成功", "green")
    
    def view_all_passwords(self):
        master = simpledialog.askstring("查看所有密码", "输入主密码:", show="*")
        if master == self.master_password:
            for item in self.tree.get_children():
                key = self.tree.item(item, "values")[0]
                self.tree.item(item, values=(key, self.passwords[key]))
            threading.Timer(60, self.hide_passwords).start()
        else:
            self.show_message("密码错误", "red")
    
    def hide_passwords(self):
        for item in self.tree.get_children():
            key = self.tree.item(item, "values")[0]
            self.tree.item(item, values=(key, "********"))
    
    def show_message(self, text, color):
        message_label = tk.Label(self.main_frame, text=text, fg=color, bg="#f0f0f0")
        message_label.pack()
        self.root.after(2000, message_label.destroy)

# style = ttk.Style()
# style.configure(
#     "Blue.TButton",
#     background="#007BFF",  # 蓝色背景
#     foreground="white",  # 白色文字
#     padding=(6, 3),  # 适当增加按钮大小
#     relief="ridge",  # 增加立体感
#     font=("Arial", 10, "bold")
# )
# style.map("Blue.TButton", background=[("active", "#0056b3")])  # 按下变深蓝色    
if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.configure("Blue.TButton", background="#007BFF", foreground="white", padding=5, relief="flat", font=("Arial", 10, "bold"))
    app = PasswordManager(root)
    root.mainloop()
