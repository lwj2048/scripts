import requests
import sys
import datetime
import json
import codecs
import time
import pymysql

max_retries = 3  # 最大重试次数
retry_delay = 10  # 重试延迟时间（秒）
token = 'xxxxxxxxxxxxxxxxxxxx'
api_url = "https://api.github.com"
owners = ['Test1','Test2']
headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"Bearer {token}"
}


def insert_Mysql(run_id,workflow_id,owner,repo,workflow_name,run_number,conclusion,run_url,run_started_at,updated_at,run_time,user):
    db = pymysql.connect(host='sh.paas.xxxx.com', user='github', password='GitHub123', charset='utf8',
                          db='GitHub', port=38152)
    now = datetime.datetime.now().replace(microsecond=0)
    INSERT_sql = "REPLACE INTO GitHub_workflow(run_id,workflow_id,owner,repo,workflow_name,run_number,conclusion,run_url,run_started_at,updated_at,run_time,user,datetime) " \
                 "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" \
                 %(run_id,workflow_id,owner,repo,workflow_name,run_number,conclusion,run_url,run_started_at,updated_at,run_time,user,now)
    print(INSERT_sql)
    cursor = db.cursor()
    cursor.execute(INSERT_sql)
    db.commit()

def get_delta(time1,time2):
    dt1 = datetime.datetime.strptime(time1, '%Y-%m-%d %H:%M:%S')
    dt2 = datetime.datetime.strptime(time2, '%Y-%m-%d %H:%M:%S')
    delta = dt2 - dt1
    total_seconds = str(delta.total_seconds()).split('.')[0]
    return total_seconds

def get_repo(owner):
    repo_url = f"{api_url}/orgs/{owner}/repos"
    repo_response = requests.get(repo_url, headers=headers)
    if repo_response.status_code == 200:
        repos = repo_response.json()
        repo_names = [repo["name"] for repo in repos]
        return repo_names
    else:
        sys.exit(1)

def get_runs(owner,repo_names):
    for repo in repo_names:
        workflow_runs_url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
        response = requests.get(workflow_runs_url, headers=headers)
        workflow_runs = response.json()["workflow_runs"][:20]  #获取最近多少个run的信息
        if len(workflow_runs) == 0:
            continue
        for run in workflow_runs:
            run_id = run['id']
            workflow_id = run['workflow_id']
            workflow_name = run['name']
            run_number = run['run_number']
            conclusion = run['conclusion']
            run_url = run['html_url']
            run_started_at = run['run_started_at'][:-1].replace('T', ' ')
            updated_at = run['updated_at'][:-1].replace('T', ' ')
            run_time = get_delta(run_started_at,updated_at)
            user = run['triggering_actor']['login']
            print(run_id,workflow_id,owner,repo,workflow_name,run_number,conclusion,run_url,run_started_at,updated_at,run_time,user)
            insert_Mysql(run_id,workflow_id,owner,repo,workflow_name,run_number,conclusion,run_url,run_started_at,updated_at,run_time,user)





for i in range(max_retries):
    try:
        for owner in owners:
            repo_names = get_repo(owner)
            get_runs(owner,repo_names)
        break  # 如果操作成功，则退出重试循环
    except Exception as e:
        print("Error occurred:", e)
        if i == max_retries - 1:  # 如果达到最大重试次数，则退出循环
            print(retry_delay)
            break
        print("Retrying in {} seconds...".format(retry_delay))
        time.sleep(retry_delay)
