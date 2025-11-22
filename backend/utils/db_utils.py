import pymysql

def get_db():
    conn = pymysql.connect(
		host="127.0.0.1",
		port=3306,
		user="nexcodecs",
		password="sprtmzhemWkd1234!!",
		db="users",
		charset="utf8mb4"
    )
    return conn


def save_update_kakao_user(user_id, nickname, image):
    conn = get_db()
    if not conn:
        return False

    try:
        with conn.cursor() as cursor:
            # 1. users 테이블이 없으면 생성
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS xthon.users (
                user_id BIGINT PRIMARY KEY,
                nickname VARCHAR(100),
                image TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_table_sql)

            # 2. 유저 정보 저장 (이미 존재하면 닉네임과 이미지만 업데이트)
            # INSERT ... ON DUPLICATE KEY UPDATE 구문 사용
            sql = """
            INSERT INTO xthon.users (user_id, nickname, image)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                nickname = VALUES(nickname),
                image = VALUES(image)
            """
            cursor.execute(sql, (user_id, nickname, image))
        
        conn.commit()
        print(f"[DB] User {user_id} saved/updated successfully.")
        return True

    except Exception as e:
        print(f"[DB Error] save_update_kakao_user failed: {e}")
        return False
        
    finally:
        conn.close()

def create_expenses_table(user_id):
    table_name = f'{user_id}_expenses'
    print(f"테이블 '{table_name}' 생성을 시도합니다.")
    
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        sql_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
            merchant VARCHAR(255) NOT NULL,
            category VARCHAR(255),
            price INT NOT NULL,
            hour INT,
            sentiment VARCHAR(50),
            regret_flag TINYINT DEFAULT 0,
            created_at DATETIME NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        
        cursor.execute(sql_query)
        conn.commit()
        print(f"테이블 '{table_name}'이 성공적으로 생성되었거나 이미 존재합니다.")
    except pymysql.Error as e:
        print(f"MySQL 오류 발생: {e}")
    finally:
        if conn:
            conn.close()
            
def create_initial_table(user_id):
    table_name = f'{user_id}_initial'
    print(f"테이블 '{table_name}' 생성을 시도합니다.")

    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()

        sql_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
            item_name VARCHAR(255) NOT NULL,
            category VARCHAR(100),
            price INT NOT NULL,
            time_text INT,
            sentiment VARCHAR(50),
            created_at DATETIME NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """

        cursor.execute(sql_query)
        conn.commit()
        print(f"테이블 '{table_name}'이 성공적으로 생성되었거나 이미 존재합니다.")

    except pymysql.Error as e:
        print(f"MySQL 오류 발생: {e}")
    finally:
        if conn:
            conn.close()

def insert_expenses_data(user_id, merchant, category, price, hour, sentiment, regret_flag, created_at):
    table_name = f'{user_id}_expenses'
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        insert_query = f"""
        INSERT INTO {table_name} 
        (merchant, category, price, hour, sentiment, regret_flag, created_at) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
    
        cursor.execute(
            insert_query, 
            (merchant, category, price, hour, sentiment, regret_flag, created_at)
        )
        conn.commit()
        print(f"테이블 '{table_name}'에 데이터 삽입 성공.")
    except pymysql.Error as e:
        print(f"MySQL 삽입 오류 발생: {e}")
    finally:
        if conn:
            conn.close()

def insert_initial_data(user_id, item_name, category, price, time_text, sentiment, created_at):
    table_name = f'{user_id}_initial'
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        insert_query = f"""
        INSERT INTO {table_name} 
        (item_name, category, price, time_text, sentiment, created_at) 
        VALUES (%s, %s, %s, %s, %s)
        """
        
        cursor.execute(
            insert_query, 
            (item_name, category, price, time_text, sentiment, created_at)
        )
        conn.commit()
        print(f"테이블 '{table_name}'에 데이터 삽입 성공.")
    except pymysql.Error as e:
        print(f"MySQL 삽입 오류 발생: {e}")
    finally:
        if conn:
            conn.close()