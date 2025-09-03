import json
from cryptography.fernet import Fernet

# 批量导入密码，你的明文密码数据，格式：{ "名称": "密码" }
password_data = {
    "key1": "xxxxxxxxxxx",
    "key2": "aaaazzzzzzz",
    "key3": "mmmmmnnnnnnn"
}

# 读取加密密钥
key_file = "key.key"
password_file = "passwords.json"

try:
    with open(key_file, "rb") as f:
        key = f.read()
    cipher = Fernet(key)
except FileNotFoundError:
    print("错误: key.key 文件不存在，请先运行密码管理器生成密钥")
    exit(1)

# 加密密码数据
encrypted_data = cipher.encrypt(json.dumps(password_data).encode())

# 写入加密的 passwords.json
with open(password_file, "wb") as f:
    f.write(encrypted_data)

print("密码数据已成功加密并导入到 passwords.json")
