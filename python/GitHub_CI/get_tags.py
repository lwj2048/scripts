import requests
import time
import sys
max_retries = 3  # 最大重试次数
retry_delay = 10  # 重试延迟时间（秒）
api_url = "https://api.github.com"
owner = "ParrotsDL"
repo = "parrots"
token = "ghp_1yhmAiuUzLxQxdmEbp2kZUYQtUgmy14LErv"
headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"Bearer {token}"
}


def get_repo():
    repo_url = f"{api_url}/orgs/{owner}/repos"
    repo_response = requests.get(repo_url, headers=headers)
    # print(response.json())
    if repo_response.status_code == 200:
        repos = repo_response.json()
        repo_names = [repo["name"] for repo in repos]
        # print("The names of all repositories in the organization are:", repo_names)
        return repo_names
    else:
        sys.exit(1)

def get_tages(repo_names):
    for item_repo in repo_names:
        tags_url = f"{api_url}/repos/{owner}/{item_repo}/tags"
        tags_response = requests.get(tags_url, headers=headers)
        if tags_response.status_code == 200:
            tags = tags_response.json()
            tag_count = len(tags)
            print( item_repo ,':' ,tag_count)
        else:
            sys.exit(1)


for i in range(max_retries):
    try:
        repo_names = get_repo()
        get_tages(repo_names)
        break  # 如果操作成功，则退出重试循环
    except Exception as e:
        print("Error occurred:", e)
        print('test')
        if i == max_retries - 1:  # 如果达到最大重试次数，则退出循环
            print(retry_delay)
            break
        print("Retrying in {} seconds...".format(retry_delay))
        time.sleep(retry_delay)
