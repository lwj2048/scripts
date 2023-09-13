import requests
import sys
import time
import pymysql
from datetime import datetime


max_retries = 3  # 最大重试次数
retry_delay = 10  # 重试延迟时间（秒）
token = 'xxxxxxxxxxxxxx'
api_url = "https://api.github.com"
owners = ['Test1','Test2']
now = datetime.now().replace(microsecond=0)
#now = '2023-04-25 11:00:00'
headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"Bearer {token}"
}

def insert_Mysql(owner,runner_label,idle,online_num,repo=None):
    db = pymysql.connect(host='sh.paas.xxxxxx.com', user='github', password='xxxxxx', charset='utf8',
                          db='GitHub', port=38152)
    cursor = db.cursor()

    if repo is None:
        #获取数据库runner_label的数量
        select_total_query = "SELECT total_count FROM GitHub_runners WHERE owner = %s AND runner_label = %s AND datetime = %s"
        cursor.execute(select_total_query, (owner, runner_label, now))
        total_count = cursor.fetchone()
        if  total_count is None or total_count[0] == 0:
            total_count = 1
        else:
            total_count = int(total_count[0]) + 1
        #获取online runner数量
        select_online_query = "SELECT online_num FROM GitHub_runners WHERE owner = %s AND runner_label = %s AND datetime = %s"
        cursor.execute(select_online_query, (owner, runner_label, now))
        online_count = cursor.fetchone()
        if not online_count is None:
            online_num = int(online_count[0]) + online_num
        # 获取数据库runner_label的空闲数量
        select_idle_query = "SELECT idle_count FROM GitHub_runners WHERE owner = %s AND runner_label = %s AND datetime = %s"
        cursor.execute(select_idle_query, (owner, runner_label, now))
        idle_count = cursor.fetchone()
        print("debug1")
        if idle_count is None or idle_count[0] == '':   #如果过滤不到符合的数据，判断idle_count is None；如果过滤到数据，但查找的列没数据，判断runner_queued[0] is None
            idle_count = idle
        else:
            idle_count = int(idle_count[0]) + idle
        REPLACE_sql = "REPLACE INTO GitHub_runners(owner,runner_label,total_count,idle_count,online_num,datetime) VALUES ('%s', '%s', '%s', '%s', '%s','%s')" \
                 %(owner,runner_label,total_count,idle_count,online_num,now)
    else:
        #获取数据库runner_label的数量
        select_total_query = "SELECT total_count FROM GitHub_runners WHERE owner = %s AND runner_label = %s AND repo = %s AND datetime = %s"
        cursor.execute(select_total_query, (owner, runner_label, repo, now))
        total_count = cursor.fetchone()
        print("debug2")
        if total_count is None:
            total_count = 1
        else:
            total_count = int(total_count[0]) + 1
        # 获取online runner数量
        select_online_query = "SELECT online_num FROM GitHub_runners WHERE owner = %s AND runner_label = %s AND repo = %s AND datetime = %s"
        cursor.execute(select_online_query, (owner, runner_label, repo,now))
        online_count = cursor.fetchone()
        print(online_count)
        if not online_count is None:
            online_num = int(online_count[0]) + online_num
        # 获取数据库runner_label的空闲数量
        select_idle_query = "SELECT idle_count FROM GitHub_runners WHERE owner = %s AND runner_label = %s AND repo = %s AND datetime = %s"
        cursor.execute(select_idle_query, (owner, runner_label, repo, now))
        idle_count = cursor.fetchone()
        print("debug3")
        if idle_count is None or idle_count[0] == '':
            idle_count = idle
        else:
            idle_count = int(idle_count[0]) + idle
        REPLACE_sql = "REPLACE INTO GitHub_runners(owner,repo,runner_label,total_count,idle_count,online_num,datetime) VALUES ('%s', '%s', '%s', '%s', '%s', '%s','%s')" \
                 %(owner,repo,runner_label,total_count,idle_count,online_num,now)
    print(REPLACE_sql)
    cursor = db.cursor()
    cursor.execute(REPLACE_sql)
    db.commit()
def insert_Mysql_queued(owner,runner_label):
    db = pymysql.connect(host='sh.paas.xxxxxx.com', user='github', password='xxxxxx', charset='utf8',
                          db='GitHub', port=38152)
    cursor = db.cursor()
    #获取数据库runner_queued的数量
    select_queued_query = "SELECT runner_queued FROM GitHub_runners WHERE owner = %s AND runner_label = %s AND datetime = %s"
    cursor.execute(select_queued_query, (owner, runner_label, now))
    runner_queued = cursor.fetchone()
    print("debug4")
    if runner_queued is None or runner_queued[0] == 0:
        runner_queued = 1
    else:
        runner_queued = int(runner_queued[0]) + 1
    update_query = "UPDATE GitHub_runners SET runner_queued = %s WHERE owner = %s AND  runner_label = %s AND datetime = %s"
    cursor.execute(update_query, (runner_queued, owner,  runner_label, now))
    db.commit()
    db.close()
def clean_table(TABLE):
    db = pymysql.connect(host='sh.paas.xxxxxx.com', user='github', password='xxxxxx', charset='utf8',
                         db='GitHub', port=38152)

    CLEAN_sql = f"TRUNCATE TABLE {TABLE}"
    cursor = db.cursor()
    cursor.execute(CLEAN_sql)
    db.commit()
def clean_now_data():
    db = pymysql.connect(host='sh.paas.xxxxxx.com', user='github', password='xxxxxx', charset='utf8',
                         db='GitHub', port=38152)

    CLEAN_sql = "DELETE from GitHub_runners WHERE datetime = %s "
    cursor = db.cursor()
    cursor.execute(CLEAN_sql, (now))
    db.commit()
def get_repo(owner):
    repo_url = f"{api_url}/orgs/{owner}/repos"
    repo_response = requests.get(repo_url, headers=headers)
    if repo_response.status_code == 200:
        repos = repo_response.json()
        repo_names = [repo["name"] for repo in repos]
        return repo_names
    else:
        print(repo_response.status_code)
        print(repo_response)
        sys.exit(1)

def get_runners(owner,repo_names):
    for item_repo in repo_names:
        time.sleep(1)
        print("======================= " + owner + " 组织 " + item_repo + " 仓库下runner信息=========================")
        runners_url = f"{api_url}/repos/{owner}/{item_repo}/actions/runners"
        runners_response = requests.get(runners_url, headers=headers)
        if runners_response.status_code == 503:
            time.sleep(3)
            runners_response = requests.get(runners_url, headers=headers)
        if runners_response.status_code != 200:
            sys.exit(1)
        if runners_response.json()['total_count'] != 0:
            runners = runners_response.json()
            for item_runner in runners['runners']:
                print(item_runner)
                idle = 1
                online_num = 0
                if item_runner['busy']:
                    idle = 0
                if item_runner['status'] == "online":
                    online_num = 1
                for label in item_runner['labels']:
                    if label['name'] not in ['self-hosted', 'Linux', 'X64']:
                        runner_label = label['name']
                        insert_Mysql(owner, runner_label, idle, online_num,repo=item_repo)

def get_runners_owner(owner):
    print("=======================" + owner + "组织下runner信息=========================")
    #默认显示30个runner，如果超过30个就需要添加per_page指定每一页数量
    runners_url = f"{api_url}/orgs/{owner}/actions/runners?per_page=70"
    print(runners_url)
    runners_response = requests.get(runners_url, headers=headers)
    if runners_response.status_code == 503:
        time.sleep(3)
        runners_response = requests.get(runners_url, headers=headers)
    if runners_response.status_code != 200:
        sys.exit(1)
    if runners_response.json()['total_count'] != 0:
        runners = runners_response.json()
        for item_runner in runners['runners']:
            print(item_runner)
            idle = 1
            online_num = 0
            if item_runner['busy']:
                idle = 0
            if item_runner['status'] == "online":
                online_num = 1
            for label in item_runner['labels']:
                if label['name'] not in ['self-hosted', 'Linux', 'X64']:
                    runner_label = label['name']
                    insert_Mysql(owner, runner_label, idle, online_num)

def get_runner_queued(owner,repo_names):
    for repo in repo_names:
        workflow_runs_url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
        response = requests.get(workflow_runs_url, headers=headers)
        if response.status_code == 503:
            time.sleep(3)
            response = requests.get(workflow_runs_url, headers=headers)
        workflow_runs = response.json()["workflow_runs"][:20]  #获取最近多少个run的信息,可能需要变动
        if len(workflow_runs) == 0:
            continue
        for run in workflow_runs:
            run_id = run['id']
            if run['status'] == 'completed':
                continue
            #print("当前正在运行的workflow是 " + run['html_url'])
            workflow_jobs_url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/jobs"
            response = requests.get(workflow_jobs_url, headers=headers)
            jobs = response.json()['jobs']
            for job in jobs:
                if job['status'] == 'queued':
                    print(job)
                    for label in job['labels']:
                        print("当前正在排队的run是 " + run['html_url'])
                        print("当前正在排队的job是 " + job['html_url'] + ' label是: ' +label)
                        #insert_Mysql_queued(owner,label)
            time.sleep(1)

for i in range(max_retries):
    try:
        for owner in owners:
            print("=======================" + owner + "=========================")
            repo_names = get_repo(owner) #获取组织下所有的repo
            get_runners(owner,repo_names) #获取repo下runner的总数
            get_runners_owner(owner)   #获取组织下runner的总数
            get_runner_queued(owner, repo_names) #获取等待runner的job数量
        break  # 如果操作成功，则退出重试循环
    except Exception as e:
        print("Error occurred:", e)
        print('test')
        clean_now_data()
        if i == max_retries - 1:  # 如果达到最大重试次数，则退出
            print(retry_delay)
            sys.exit(1)
        print("Retrying in {} seconds...".format(retry_delay))
        time.sleep(retry_delay)
