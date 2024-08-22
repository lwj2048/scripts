import os
import json
from datetime import datetime, timedelta
import pymysql

# 数据库连接信息
DB_HOST = 'xxxxx'
DB_USER = 'xxxxx'
DB_PASSWORD = 'xxxxx'
DB_DATABASE = 'xxxxx'
DB_CHARSET = 'utf8'
DB_PORT = 38152

def insert_mysql(DB_table, data_list):
    # 创建连接
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_DATABASE,
        charset=DB_CHARSET
    )
    # 创建游标
    cur = conn.cursor()

    # 检查表是否存在
    cur.execute(f"SHOW TABLES LIKE '{DB_table}'")
    result = cur.fetchone()
    if result is None:
        # 表不存在，执行create函数
        create_table(DB_table)

    keys = ', '.join(data_list[0].keys())
    values = ', '.join(['%s'] * len(data_list[0]))
    update = ', '.join([f"{key} = VALUES({key})" for key in data_list[0]])

    insert = f'INSERT INTO {DB_table} ({keys}) VALUES ({values}) ON DUPLICATE KEY UPDATE {update}'

    try:
        # 批量插入数据
        cur.executemany(insert, [tuple(data.values()) for data in data_list])
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def add_hours_to_time(time_str, hours=8):
    if time_str:
        # Convert the string to a datetime object and add 8 hours
        time_obj = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%SZ')
        time_obj += timedelta(hours=hours)
        return time_obj
    return None

def get_json_info(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    result = []
    for item in data:
        create_time = add_hours_to_time(item.get("create_time", ""))
        complete_time = add_hours_to_time(item.get("complete_time", ""))
        job_id = item.get("id", "")

        labels = item.get("labels", {})
        roces_num = int(labels.get("roces_num", 16))
        training_job_replicas = int(labels.get("training_job_replicas", 1))

        if training_job_replicas == 1:
            roces_num = 16
        gpu_num = roces_num * training_job_replicas

        gpu_series = labels.get("diamond.xxx.com/gpu-series")
        start_time = add_hours_to_time(item.get("start_time", ""))
        status_phase = item.get("status_phase", "")
        submit_time = add_hours_to_time(item.get("submit_time", ""))

        user = item.get("user", {})
        user_name = user.get("user_name", "")

        workspace_name = item.get("workspace_name", "")

        result.append({
            "workspace_name": workspace_name,
            "id": job_id,
            "user_name": user_name,
            "gpu_num": gpu_num,
            "gpu_series": gpu_series,
            "status_phase": status_phase,
            "create_time": create_time,
            "start_time": start_time,
            "submit_time": submit_time,
            "complete_time": complete_time
        })

    return result

# 大批量数据插入数据库
if __name__ == "__main__":
    # 获取当前目录下所有 JSON 文件
    current_directory = os.getcwd()
    json_files = [file for file in os.listdir(current_directory) if file.endswith('.json')]

    all_data = []
    # 遍历每个 JSON 文件并处理
    for json_file in json_files:
        file_path = os.path.join(current_directory, json_file)
        info = get_json_info(file_path) # info数据类似：{'workspace_name': 'xxx-dev', 'id': 'pt-w9r5q5zx', 'user_name': 'liuwei10', ... 'complete_time': None}
        all_data.extend(info)
    insert_mysql('get_sco_srun_info', all_data)
