import requests
import sys
import datetime
import time
import pymysql
"""
CREATE TABLE `GitHub_runs` (
        `run_id` VARCHAR(50) NOT NULL DEFAULT '0' COLLATE 'latin1_swedish_ci',
        `workflow_id` VARCHAR(50) NOT NULL DEFAULT '0' COLLATE 'latin1_swedish_ci',
        `owner` VARCHAR(50) NOT NULL DEFAULT '' COLLATE 'latin1_swedish_ci',
        `repo` VARCHAR(50) NOT NULL DEFAULT '' COLLATE 'latin1_swedish_ci',
        `workflow_name` VARCHAR(50) NULL DEFAULT NULL COLLATE 'latin1_swedish_ci',
        `run_number` VARCHAR(50) NULL DEFAULT NULL COLLATE 'latin1_swedish_ci',
        `conclusion` VARCHAR(50) NULL DEFAULT NULL COLLATE 'latin1_swedish_ci',
        `run_url` VARCHAR(255) NULL DEFAULT NULL COLLATE 'latin1_swedish_ci',
        `run_started_at` VARCHAR(50) NULL DEFAULT NULL COLLATE 'latin1_swedish_ci',
        `updated_at` VARCHAR(50) NULL DEFAULT NULL COLLATE 'latin1_swedish_ci',
        `run_time` BIGINT(20) NULL DEFAULT NULL,
        `user` VARCHAR(50) NULL DEFAULT NULL COLLATE 'latin1_swedish_ci',
        `datetime` DATETIME NULL DEFAULT NULL,
        PRIMARY KEY (`run_id`) USING BTREE
)
COLLATE='latin1_swedish_ci'
ENGINE=InnoDB
;


"""

max_retries = 3  # 最大重试次数
retry_delay = 10  # 重试延迟时间（秒）
token = 'xxxxxxxxxxxxxx'
api_url = "https://api.github.com"
owners = ['Test1','Test2']
headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"Bearer {token}"
}


def insert_Mysql(run_id,workflow_id,owner,repo,workflow_name,run_number,conclusion,run_url,run_started_at,updated_at,run_time,user):
    db = pymysql.connect(host='sh.paas.xxxxxx.com', user='github', password='xxxxxx', charset='utf8',
                          db='GitHub', port=38152)
    now = datetime.datetime.now().replace(microsecond=0)
    INSERT_sql = "REPLACE INTO GitHub_runs(run_id,workflow_id,owner,repo,workflow_name,run_number,conclusion,run_url,run_started_at,updated_at,run_time,user,datetime) " \
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

def get_runs_item(repo,workflow_runs):
    for run in workflow_runs:
        print(run)
        run_id = run['id']
        workflow_id = run['workflow_id']
        workflow_name = run['name']
        run_number = run['run_number']
        conclusion = run['conclusion']
        run_url = run['html_url']
        run_started_at = run['run_started_at'][:-1].replace('T', ' ')
        updated_at = run['updated_at'][:-1].replace('T', ' ')
        run_time = get_delta(run_started_at, updated_at)
        user = run['triggering_actor']['login']
        # print(run_id,workflow_id,owner,repo,workflow_name,run_number,conclusion,run_url,run_started_at,updated_at,run_time,user)
        insert_Mysql(run_id, workflow_id, owner, repo, workflow_name, run_number, conclusion, run_url, run_started_at,updated_at, run_time, user)

def get_runs(owner,repo_names):
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    yesterday_date = yesterday.date()
    print(yesterday_date)
    params = {
        "created": f"{yesterday_date}T00:00:00Z..{yesterday_date}T23:59:59Z",
        "status": "completed",
    }

    for repo in repo_names:
        workflow_runs_url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
        response = requests.get(workflow_runs_url, params=params, headers=headers)
        workflow_runs = response.json()["workflow_runs"]  # 获取最近多少个run的信息
        if len(workflow_runs) == 0:
            continue
        get_runs_item(repo,workflow_runs)
        while "next" in response.links:
            next_url = response.links["next"]["url"]
            response = requests.get(next_url, headers=headers)
            workflow_runs = response.json()["workflow_runs"]
            get_runs_item(repo, workflow_runs)

for i in range(max_retries):
    try:
        for owner in owners:
            repo_names = get_repo(owner)
            get_runs(owner,repo_names)
        break  # 如果操作成功，则退出重试循环
    except Exception as e:
        print("Error occurred:", e)
        if i == max_retries - 1:  # 如果达到最大重试次数，则退出
            print(retry_delay)
            sys.exit(1)
        print("Retrying in {} seconds...".format(retry_delay))
        time.sleep(retry_delay)
