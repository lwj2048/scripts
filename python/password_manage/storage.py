from __future__ import annotations

import json
import os
import uuid
from typing import Any, Dict, List

from cryptography.fernet import Fernet


class SecureStorage:
    """负责主密码、密钥与加密数据的读写，可供不同脚本复用。"""

    def __init__(
        self,
        key_file: str = "key.key",
        master_file: str = "master.txt",
        data_file: str = "passwords.json",
    ) -> None:
        self.key_file = key_file
        self.master_file = master_file
        self.data_file = data_file
        self.key = self._load_or_create_key()
        self.cipher = Fernet(self.key)

    def _load_or_create_key(self) -> bytes:
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as file:
                return file.read()
        key = Fernet.generate_key()
        with open(self.key_file, "wb") as file:
            file.write(key)
        return key

    def read_master_password(self) -> str | None:
        if not os.path.exists(self.master_file):
            return None
        with open(self.master_file, "rb") as file:
            encrypted = file.read()
        return self.cipher.decrypt(encrypted).decode()

    def write_master_password(self, master_password: str) -> None:
        encrypted = self.cipher.encrypt(master_password.encode())
        with open(self.master_file, "wb") as file:
            file.write(encrypted)

    def load_entries(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.data_file):
            return []
        try:
            with open(self.data_file, "rb") as file:
                encrypted = file.read()
            if not encrypted:
                return []
            decrypted = self.cipher.decrypt(encrypted)
            raw_data = json.loads(decrypted.decode())
            return self._normalize_entries(raw_data)
        except Exception:
            # 文件损坏或密钥不匹配，返回空列表
            return []

    def save_entries(self, entries: List[Dict[str, Any]]) -> None:
        payload = json.dumps(entries, ensure_ascii=False, indent=2).encode()
        encrypted = self.cipher.encrypt(payload)
        with open(self.data_file, "wb") as file:
            file.write(encrypted)

    def _normalize_entries(self, raw_data: Any) -> List[Dict[str, Any]]:
        """兼容旧版字典结构，统一输出带有 id/name/key/category/notes 的列表。"""
        if isinstance(raw_data, dict):
            return [
                {
                    "id": str(uuid.uuid4()),
                    "name": name or "未命名",
                    "key": value or "",
                    "category": "未分组",
                    "notes": "",
                }
                for name, value in raw_data.items()
            ]

        normalized: List[Dict[str, Any]] = []
        if isinstance(raw_data, list):
            for item in raw_data:
                if not isinstance(item, dict):
                    continue
                normalized.append(
                    {
                        "id": item.get("id") or str(uuid.uuid4()),
                        "name": item.get("name") or "未命名",
                        "key": item.get("key") or "",
                        "category": item.get("category") or "未分组",
                        "notes": item.get("notes", ""),
                    }
                )
        return normalized


def create_entry_payload(
    name: str,
    key: str,
    category: str | None = None,
    notes: str | None = None,
) -> Dict[str, Any]:
    """供外部批量导入脚本复用的辅助函数。"""
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "key": key,
        "category": (category or "未分组").strip() or "未分组",
        "notes": (notes or "").strip(),
    }

