import pymysql

# 数据库连接信息
DB_HOST = 'xxxxx'
DB_USER = 'xxxxx'
DB_PASSWORD = 'xxxxx'
DB_DATABASE = 'xxxxx'
DB_CHARSET = 'utf8'
DB_PORT = 38152

def create_table(DB_table):
    # 创建连接
    conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_DATABASE,
        charset=DB_CHARSET
    )
    cur = conn.cursor()

    # 创建表的 SQL 语句
    create_table_sql = f"""
    CREATE TABLE `{DB_table}` (
        `gpu_series` VARCHAR(50) NULL DEFAULT NULL COLLATE 'latin1_swedish_ci',
        `workspace_name` VARCHAR(50) NOT NULL COLLATE 'latin1_swedish_ci',
        `id` VARCHAR(50) NOT NULL COLLATE 'latin1_swedish_ci',
        `user_name` VARCHAR(50) NULL DEFAULT NULL COLLATE 'latin1_swedish_ci',
        `gpu_num` INT(11) NULL DEFAULT NULL,
        `status_phase` VARCHAR(50) NULL DEFAULT NULL COLLATE 'latin1_swedish_ci',
        `start_time` DATETIME NULL DEFAULT NULL,
        `submit_time` DATETIME NULL DEFAULT NULL,
        `create_time` DATETIME NULL DEFAULT NULL,
        `complete_time` DATETIME NULL DEFAULT NULL,
        PRIMARY KEY (`workspace_name`, `id`) USING BTREE
    )
    COLLATE='latin1_swedish_ci'
    ENGINE=InnoDB;
    """
    try:
        cur.execute(create_table_sql)
        conn.commit()
        print(f"Table `{DB_table}` created successfully.")
    except Exception as e:
        print(f"An error occurred while creating the table: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_table("get_sco_srun_info2")
