from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from typing import Dict, List, Optional

import pyperclip

from storage import SecureStorage, create_entry_payload

# 打包示例：
# pyinstaller --clean --noconfirm --noconsole --onefile --add-data "storage.py;." PM.py


class PasswordManagerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("密码管理器")
        self.root.geometry("320x480")
        self.root.configure(bg="#f4f5f7")

        self.storage = SecureStorage()
        self.master_password = self._ensure_master_password()
        self.entries: List[Dict[str, str]] = self.storage.load_entries()

        self.selected_entry_id: Optional[str] = None
        self.status_var = tk.StringVar(value="欢迎使用安全密码管理器")
        self._suspend_selection_event = False
        self._status_clear_job: Optional[str] = None

        self._build_styles()
        self.show_login()
    
    # ---------------------------
    # 初始化 & 登录
    # ---------------------------
    def _ensure_master_password(self) -> str:
        existing = self.storage.read_master_password()
        if existing:
            return existing

        while True:
            master = simpledialog.askstring(
                "设置主密码", "首次使用，请设置一个主密码：", show="*", parent=self.root
            )
            if master is None or not master.strip():
                if messagebox.askyesno(
                    "提示", "未设置主密码将无法继续，是否退出？", parent=self.root
                ):
                    self.root.destroy()
                    raise SystemExit
                continue

            confirm = simpledialog.askstring(
                "确认主密码", "请再次输入主密码：", show="*", parent=self.root
            )
            if confirm is None:
                continue
            if confirm != master:
                messagebox.showwarning("提示", "两次输入不一致，请重试。", parent=self.root)
                continue

            self.storage.write_master_password(master)
            messagebox.showinfo("成功", "主密码设置完成。", parent=self.root)
            return master
    
    def show_login(self) -> None:
        self.login_frame = ttk.Frame(self.root, padding=30, style="Card.TFrame")
        self.login_frame.pack(expand=True, fill=tk.BOTH, padx=24, pady=24)

        ttk.Label(
            self.login_frame,
            text="请输入主密码",
            style="Title.TLabel",
        ).pack(pady=(0, 16))

        self.pass_entry = ttk.Entry(self.login_frame, show="*")
        self.pass_entry.pack(fill=tk.X)
        self.pass_entry.focus()

        ttk.Button(
            self.login_frame, text="登录", command=self.verify_password, style="Accent.TButton"
        ).pack(pady=24, fill=tk.X)

    def verify_password(self) -> None:
        if self.pass_entry.get() == self.master_password:
            self.login_frame.destroy()
            self.create_main_window()
        else:
            messagebox.showerror("错误", "主密码不正确，请重试。", parent=self.root)

    # ---------------------------
    # 主界面
    # ---------------------------
    def _build_styles(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Card.TFrame", background="#ffffff")
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))
        style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"), foreground="#1f2933")
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10), foreground="#64748b")
        style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def create_main_window(self) -> None:
        self.root.geometry("480x520")
        self.root.minsize(460, 400)

        self.main_frame = ttk.Frame(self.root, padding=12)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(self.main_frame)
        header.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(header, text="密码管理器", style="Title.TLabel").pack(anchor=tk.W)
        ttk.Label(
            self.main_frame, text="双击条目可复制 Key", style="Subtitle.TLabel"
        ).pack(anchor=tk.W, pady=(0, 8))

        controls = ttk.Frame(self.main_frame)
        controls.pack(fill=tk.X, pady=(0, 12))

        self.category_var = tk.StringVar(value="全部")
        ttk.Label(controls, text="分类").pack(side=tk.LEFT)
        self.category_combo = ttk.Combobox(
            controls,
            textvariable=self.category_var,
            state="readonly",
            width=10,
        )
        self.category_combo.pack(side=tk.LEFT, padx=(6, 24))
        self.category_combo.bind("<<ComboboxSelected>>", lambda _: self._refresh_tree())

        self.search_var = tk.StringVar()
        ttk.Label(controls, text="搜索").pack(side=tk.LEFT)
        search_entry = ttk.Entry(controls, textvariable=self.search_var, width=18)
        search_entry.pack(side=tk.LEFT, padx=(6, 0))
        self.search_var.trace_add("write", lambda *_: self._refresh_tree())

        button_strip = ttk.Frame(self.main_frame)
        button_strip.pack(fill=tk.X, pady=(0, 12))
        ttk.Button(button_strip, text="编辑", command=self.edit_entry, width=10).pack(side=tk.LEFT)
        ttk.Button(button_strip, text="删除", command=self.delete_entry, width=10).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(button_strip, text="刷新", command=self._refresh_category_options, width=10).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(
            button_strip, text="添加", command=self.add_entry, width=10, style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=4)

        list_container = ttk.Frame(self.main_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(
            list_container,
            columns=("name", "key", "category"),
            show="headings",
            selectmode="browse",
        )
        self.tree.heading("name", text="名称")
        self.tree.heading("key", text="Key")
        self.tree.heading("category", text="分类")
        self.tree.column("name", minwidth=80, width=160, stretch=True)
        self.tree.column("key", minwidth=60, width=120, stretch=True)
        self.tree.column("category", minwidth=60, width=90, stretch=True)

        y_scroll = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=y_scroll.set)

        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 6))
        y_scroll.pack(fill=tk.Y, side=tk.RIGHT)

        self.tree.bind("<<TreeviewSelect>>", lambda _: self._handle_selection_change())
        self.tree.bind("<Double-1>", lambda _: self.copy_key())

        status_bar = ttk.Label(
            self.main_frame,
            textvariable=self.status_var,
            foreground="#4b5563",
            anchor=tk.W,
        )
        status_bar.pack(fill=tk.X, pady=(12, 0))

        self._refresh_category_options()
        self._refresh_tree()

    # ---------------------------
    # 数据/树视图
    # ---------------------------
    def _refresh_category_options(self) -> None:
        categories = sorted({entry.get("category", "未分组") for entry in self.entries})
        options = ["全部"] + categories
        self.category_combo["values"] = options
        if self.category_var.get() not in options:
            self.category_var.set("全部")

    def _refresh_tree(self, select_id: Optional[str] = None) -> None:
        current_selection = self.selected_entry_id if select_id is None else select_id
        for item in self.tree.get_children():
            self.tree.delete(item)

        filtered = self._filter_entries()
        for entry in filtered:
            masked_key = self._mask_key(entry.get("key", ""))
            self.tree.insert(
                "",
                tk.END,
                iid=entry["id"],
                values=(entry.get("name", "-"), masked_key, entry.get("category", "-")),
            )

        if current_selection and self.tree.exists(current_selection):
            self.tree.selection_set(current_selection)
            self.tree.see(current_selection)
        else:
            self._clear_selection()

    def _filter_entries(self) -> List[Dict[str, str]]:
        category = self.category_var.get()
        keyword = self.search_var.get().strip().lower()

        filtered = self.entries
        if category and category != "全部":
            filtered = [entry for entry in filtered if entry.get("category") == category]

        if keyword:
            filtered = [
                entry
                for entry in filtered
                if keyword in entry.get("name", "").lower()
                or keyword in entry.get("key", "").lower()
                or keyword in entry.get("notes", "").lower()
            ]

        return filtered

    # ---------------------------
    # 事件 & 状态
    # ---------------------------
    def _handle_selection_change(self) -> None:
        selected = self.tree.selection()
        if self._suspend_selection_event:
            return
        if not selected:
            self._clear_selection()
            return
        entry_id = selected[0]
        self.selected_entry_id = entry_id
        entry = self._get_entry_by_id(entry_id)
        if not entry:
            self._clear_selection()
            return

    def _clear_selection(self) -> None:
        self.selected_entry_id = None
        current = self.tree.selection()
        if not current:
            return
        self._suspend_selection_event = True
        self.tree.selection_remove(current)
        self._suspend_selection_event = False

    def _mask_key(self, key: str) -> str:
        if not key:
            return "-"
        return "*" * min(len(key), 12)

    def toggle_key_visibility(self) -> None:
        if not self.selected_entry_id:
            return
        entry = self._get_entry_by_id(self.selected_entry_id)
        if not entry:
            return
        self.key_visible.set(not self.key_visible.get())
        value = entry.get("key", "")
        self.key_value_label.config(text=value if self.key_visible.get() else self._mask_key(value))
        self.toggle_key_btn.config(text="隐藏 Key" if self.key_visible.get() else "显示 Key")

    def copy_key(self) -> None:
        if not self.selected_entry_id:
            self._update_status("请先选择一个条目。", error=True)
            return
        entry = self._get_entry_by_id(self.selected_entry_id)
        if not entry:
            self._update_status("当前条目不存在。", error=True)
            return
        pyperclip.copy(entry.get("key", ""))
        self._update_status(f"{entry.get('name', '条目')} 的 Key 已复制。")

    # ---------------------------
    # CRUD
    # ---------------------------
    def add_entry(self) -> None:
        dialog = EntryDialog(
            self.root,
            title="添加密码",
            categories=self.category_combo["values"][1:],
        )
        self.root.wait_window(dialog)
        if not dialog.result:
            return

        payload = create_entry_payload(
            name=dialog.result["name"],
            key=dialog.result["key"],
            category=dialog.result["category"],
            notes=dialog.result["notes"],
        )
        self.entries.append(payload)
        self._persist_entries()
        self._refresh_category_options()
        self._refresh_tree(select_id=payload["id"])
        self._update_status("添加成功。")

    def edit_entry(self) -> None:
        if not self.selected_entry_id:
            self._update_status("请先选择一个条目。", error=True)
            return
        entry = self._get_entry_by_id(self.selected_entry_id)
        if not entry:
            self._update_status("当前条目不存在。", error=True)
            return

        dialog = EntryDialog(
            self.root,
            title="编辑密码",
            categories=self.category_combo["values"][1:],
            initial=entry,
        )
        self.root.wait_window(dialog)
        if not dialog.result:
            return

        entry.update(dialog.result)
        self._persist_entries()
        self._refresh_category_options()
        self._refresh_tree(select_id=entry["id"])
        self._update_status("修改成功。")

    def delete_entry(self) -> None:
        if not self.selected_entry_id:
            self._update_status("请先选择一个条目。", error=True)
            return
        entry = self._get_entry_by_id(self.selected_entry_id)
        if not entry:
            self._update_status("当前条目不存在。", error=True)
            return

        if not messagebox.askyesno("确认删除", f"确定删除「{entry.get('name')}」吗？", parent=self.root):
            return

        self.entries = [item for item in self.entries if item["id"] != entry["id"]]
        self._persist_entries()
        self._refresh_category_options()
        self._refresh_tree()
        self._clear_selection()
        self._update_status("已删除。")

    # ---------------------------
    # 工具方法
    # ---------------------------
    def _get_entry_by_id(self, entry_id: str) -> Optional[Dict[str, str]]:
        for entry in self.entries:
            if entry["id"] == entry_id:
                return entry
        return None

    def _persist_entries(self) -> None:
        self.storage.save_entries(self.entries)

    def _update_status(self, message: str, error: bool = False) -> None:
        prefix = "[!] " if error else "[√] "
        self.status_var.set(f"{prefix}{message}")
        if self._status_clear_job:
            self.root.after_cancel(self._status_clear_job)
        self._status_clear_job = self.root.after(
            3500, self._clear_status_message
        )

    def _clear_status_message(self) -> None:
        self.status_var.set("")
        self._status_clear_job = None


class EntryDialog(tk.Toplevel):
    def __init__(
        self,
        parent: tk.Tk,
        title: str,
        categories: List[str],
        initial: Optional[Dict[str, str]] = None,
    ) -> None:
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.result: Optional[Dict[str, str]] = None

        ttk.Label(self, text="名称").grid(row=0, column=0, sticky=tk.W, pady=(12, 4), padx=12)
        self.name_var = tk.StringVar(value=(initial or {}).get("name", ""))
        ttk.Entry(self, textvariable=self.name_var, width=32).grid(
            row=0, column=1, padx=12, pady=(12, 4)
        )

        ttk.Label(self, text="Key").grid(row=1, column=0, sticky=tk.W, pady=4, padx=12)
        self.key_var = tk.StringVar(value=(initial or {}).get("key", ""))
        ttk.Entry(self, textvariable=self.key_var, width=32).grid(
            row=1, column=1, padx=12, pady=4
        )

        ttk.Label(self, text="分类").grid(row=2, column=0, sticky=tk.W, pady=4, padx=12)
        self.category_var = tk.StringVar(value=(initial or {}).get("category", "未分组"))
        self.category_combo = ttk.Combobox(
            self,
            textvariable=self.category_var,
            values=categories or ["git", "docker", "未分组"],
            width=30,
        )
        self.category_combo.grid(row=2, column=1, padx=12, pady=4)

        ttk.Label(self, text="备注").grid(row=3, column=0, sticky=tk.NW, pady=4, padx=12)
        self.notes_text = tk.Text(self, width=30, height=4)
        self.notes_text.grid(row=3, column=1, padx=12, pady=4)
        if initial:
            self.notes_text.insert("1.0", initial.get("notes", ""))

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(8, 12))
        ttk.Button(btn_frame, text="取消", command=self.destroy).pack(side=tk.RIGHT, padx=6)
        ttk.Button(btn_frame, text="确定", command=self._on_confirm, style="Accent.TButton").pack(
            side=tk.RIGHT
        )

        self.bind("<Return>", lambda _: self._on_confirm())
        self.bind("<Escape>", lambda _: self.destroy())

    def _on_confirm(self) -> None:
        name = self.name_var.get().strip()
        key = self.key_var.get().strip()
        category = self.category_var.get().strip() or "未分组"
        notes = self.notes_text.get("1.0", tk.END).strip()

        if not name or not key:
            messagebox.showwarning("提示", "名称和 Key 不能为空。", parent=self)
            return

        self.result = {
            "name": name,
            "key": key,
            "category": category,
            "notes": notes,
        }
        self.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManagerApp(root)
    root.mainloop()
