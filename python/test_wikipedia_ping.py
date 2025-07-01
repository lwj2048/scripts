import os
import requests
import time

def test_request(use_proxy=False):
    url = 'https://en.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'format': 'json',
        'titles': 'Main Page',
        'prop': 'info'
    }
    
    if use_proxy:
        print("\n=== Testing with proxy ===")
        proxies = {
            'http': 'http://xxx@10.54.0.93:3128',
            # 'https': 'http://xxx@10.54.0.93:3128'
        }
        os.environ['http_proxy'] = proxies['http']
        # os.environ['https_proxy'] = proxies['https']
    else:
        print("\n=== Testing without proxy ===")
        proxies = None
        # 清除代理环境变量
        os.environ.pop('http_proxy', None)
        os.environ.pop('https_proxy', None)
    
    print(f"Current environment variables:")
    print(f"http_proxy: {os.environ.get('http_proxy', 'Not set')}")
    print(f"https_proxy: {os.environ.get('https_proxy', 'Not set')}")
    print(f"REQUESTS_CA_BUNDLE: {os.environ.get('REQUESTS_CA_BUNDLE', 'Not set')}")
    
    try:
        start_time = time.time()
        response = requests.get(url, params=params, proxies=proxies)
        end_time = time.time()
        
        print(f"\nRequest successful!")
        print(f"Status code: {response.status_code}")
        print(f"Time taken: {end_time - start_time:.2f} seconds")
        print(f"Response headers:")
        for key, value in response.headers.items():
            print(f"{key}: {value}")
            
    except requests.exceptions.SSLError as e:
        print(f"\nSSL Error occurred: {e}")
    except requests.exceptions.RequestException as e:
        print(f"\nOther error occurred: {e}")

if __name__ == "__main__":
    # 先测试不使用代理
    test_request(use_proxy=False)
    
    # # 等待一下
    time.sleep(1)
    
    # 再测试使用代理
    test_request(use_proxy=True)
    
    # 最后测试使用代理和证书
    # print("\n=== Testing with proxy and CA bundle ===")
    # os.environ['REQUESTS_CA_BUNDLE'] = '/etc/ssl/certs/ca-certificates.crt'
    # test_request(use_proxy=True) 
