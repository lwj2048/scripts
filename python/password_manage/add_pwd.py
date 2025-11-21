from __future__ import annotations

from typing import List

from storage import SecureStorage, create_entry_payload

# 批量导入（或更新）数据示例，可根据需要修改/扩展
BULK_ENTRIES = [
    {
        "name": "GitHub",
        "key": "ghp_xxxxxxxx",
        "category": "git",
        "notes": "个人 Access Token",
    },
    {
        "name": "DockerHub",
        "key": "docker_secret_key",
        "category": "docker",
        "notes": "",
    },
]


def upsert_entries(
    original: List[dict],
    new_payloads: List[dict],
) -> List[dict]:
    """同名同分类则更新，否则追加，确保可重复执行。"""
    mapping = {(item["name"], item.get("category", "")): item for item in original}
    for payload in new_payloads:
        key = (payload["name"], payload.get("category", ""))
        if key in mapping:
            payload["id"] = mapping[key]["id"]
        mapping[key] = payload
    return list(mapping.values())


def main() -> None:
    storage = SecureStorage()
    current_entries = storage.load_entries()
    prepared = [
        create_entry_payload(
            name=item["name"],
            key=item["key"],
            category=item.get("category"),
            notes=item.get("notes"),
        )
        for item in BULK_ENTRIES
    ]

    merged = upsert_entries(current_entries, prepared)
    storage.save_entries(merged)
    print(f"已导入/更新 {len(prepared)} 条记录，共 {len(merged)} 条。")


if __name__ == "__main__":
    main()
