import pymysql

def get_db():
    conn = pymysql.connect(
			host="secuho.life",
			port=53306,
			user="nexcodecs",
			password="sprtmzhemWkd1234!!",
			db="users",
			charset="utf8mb4",
    )
    
    return conn

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
            category VARCHAR(100),
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
            sentiment VARCHAR(50)
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

def insert_initial_data(user_id, item_name, category, price, time_text, sentiment):
    table_name = f'{user_id}_initial'
    conn = None
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        insert_query = f"""
        INSERT INTO {table_name} 
        (item_name, category, price, time_text, sentiment) 
        VALUES (%s, %s, %s, %s, %s)
        """
        
        cursor.execute(
            insert_query, 
            (item_name, category, price, time_text, sentiment)
        )
        conn.commit()
        print(f"테이블 '{table_name}'에 데이터 삽입 성공.")
    except pymysql.Error as e:
        print(f"MySQL 삽입 오류 발생: {e}")
    finally:
        if conn:
            conn.close()