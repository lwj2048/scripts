import requests
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# pip install requests[socks]

# 获取代理列表
def fetch_proxy_list(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        proxies = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}:\d+\b', response.text)
        return list(set(proxies))  # 去重
    except Exception as e:
        print(f"获取代理列表失败: {e}")
        return []


# 验证单个代理
def check_proxy(proxy):
    ip, port = proxy.split(':')
    proxy_dict = {
        'http': f'socks5://{ip}:{port}',
        'https': f'socks5://{ip}:{port}'
    }
    try:
        start = time.time()
        response = requests.get(
            'https://httpbin.org/ip',
            proxies=proxy_dict,
            timeout=10
        )
        if response.status_code == 200:
            return proxy, True, round(time.time() - start, 2)
    except Exception:
        pass
    return proxy, False, None


# 主函数
def main():
    url = "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt"
    print("正在获取代理列表...")
    proxies = fetch_proxy_list(url)
    print(f"共获取 {len(proxies)} 个代理，开始验证...")

    working_proxies = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        future_to_proxy = {executor.submit(check_proxy, p): p for p in proxies}
        for future in as_completed(future_to_proxy):
            proxy, is_ok, latency = future.result()
            if is_ok:
                print(f"[✅] {proxy} 可用，延迟 {latency}s")
                working_proxies.append((proxy, latency))
            else:
                print(f"[❌] {proxy} 不可用")

    # 按延迟升序排序
    working_proxies.sort(key=lambda x: x[1])

    print(f"\n验证完成，共 {len(working_proxies)} 个可用代理：\n")
    for proxy, latency in working_proxies:
        print(f"export https_proxy=http://{proxy}")
        print(f"export http_proxy=http://{proxy}\n")


if __name__ == "__main__":
    main()
