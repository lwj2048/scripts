import requests
import sys
import datetime
import json
import codecs
import time
import pymysql

max_retries = 3  # 最大重试次数
retry_delay = 10  # 重试延迟时间（秒）
token = 'xxxxxxxxxxxxxxxx'
api_url = "https://api.github.com"
owners = ['Test1','Test2']
# owners = ['OpenComputeLab']
headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"Bearer {token}"
}
headers = {"Authorization": f"Bearer {token}"}


def insert_Mysql(run_id,job_id,owner,repo,job_name,conclusion,job_url,started_at,completed_at,run_time,workflow_status,total_count):
    db = pymysql.connect(host='sh.paas.xxxx.com', user='github', password='GitHub123', charset='utf8',
                          db='GitHub', port=38152)
    now = datetime.datetime.now().replace(microsecond=0)
    INSERT_sql = "REPLACE INTO GitHub_jobs(run_id,job_id,owner,repo,job_name,conclusion,job_url,started_at,completed_at,run_time,workflow_status,total_count,datetime)" \
                 " VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" \
                 %(run_id,job_id,owner,repo,job_name,conclusion,job_url,started_at,completed_at,run_time,workflow_status,total_count,now)
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

def get_jobs(owner,repo_names):
    for repo in repo_names:
        workflow_runs_url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
        response = requests.get(workflow_runs_url, headers=headers)
        workflow_runs = response.json()["workflow_runs"][:2]  #获取最近多少个run的信息
        if len(workflow_runs) == 0:
            continue
        for run in workflow_runs:
            run_id = run['id']
            workflow_status = run['conclusion']

            workflow_jobs_url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/jobs"
            response = requests.get(workflow_jobs_url, headers=headers)

            total_count = response.json()['total_count']
            jobs = response.json()['jobs']
            created_at = jobs[0]['created_at'][:-1].replace('T', ' ')
            print(total_count,created_at)
            for job in jobs:
                job_id = job['id']
                job_name = job['name']
                conclusion = job['conclusion']
                job_url = job['html_url']
                started_at = job['started_at'][:-1].replace('T', ' ')
                completed_at = job['completed_at'][:-1].replace('T', ' ')
                run_time = get_delta(started_at,completed_at)
                print(run_id,job_id,owner,repo,job_name,conclusion,job_url,started_at,completed_at,run_time,workflow_status,total_count)
                insert_Mysql(run_id,job_id,owner,repo,job_name,conclusion,job_url,started_at,completed_at,run_time,workflow_status,total_count)
            time.sleep(1)
        time.sleep(1)
    time.sleep(1)






for i in range(max_retries):
    try:
        for owner in owners:
            repo_names = get_repo(owner)
            get_jobs(owner,repo_names)
        break  # 如果操作成功，则退出重试循环
    except Exception as e:
        print("Error occurred:", e)
        print('test')
        if i == max_retries - 1:  # 如果达到最大重试次数，则退出循环
            print(retry_delay)
            break
        print("Retrying in {} seconds...".format(retry_delay))
        time.sleep(retry_delay)
