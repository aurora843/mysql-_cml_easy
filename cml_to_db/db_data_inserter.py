import sys
import io

# 표준 입출력 인코딩을 UTF-8로 설정 (Windows에서 한글 입력 문제 해결 시도)
if sys.platform == "win32":
    sys.stdin = io.TextIOWrapper(sys.stdin.detach(), encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8')

import mysql.connector
from mysql.connector import Error
import getpass
# ... (나머지 코드는 동일) ...
import mysql.connector
from mysql.connector import Error
import getpass # 비밀번호 입력을 위해 추가

def get_mysql_credentials():
    """사용자로부터 MySQL 접속 정보를 입력받습니다."""
    print("\n--- MySQL 접속 정보 입력 ---")
    host = input("MySQL 호스트 주소를 입력하세요 (예: localhost, 기본값: localhost): ") or "localhost"
    user = input("MySQL 사용자명을 입력하세요 (예: root): ")
    # getpass.getpass는 터미널에서 비밀번호를 입력할 때 화면에 표시되지 않도록 합니다.
    password = getpass.getpass("MySQL 비밀번호를 입력하세요: ")
    database = input("사용할 데이터베이스명을 입력하세요: ")
    print("-" * 28 + "\n")
    return host, user, password, database

def get_table_name():
    """사용자로부터 사용할 테이블명을 입력받습니다."""
    table_name = input("데이터를 저장할 테이블명을 입력하세요 (예: phone_numbers, 기본값: phone_numbers): ") or "phone_numbers"
    # 간단한 유효성 검사 (공백이나 특수문자 포함 여부 등)를 추가할 수 있지만, 여기서는 생략합니다.
    # 테이블명에는 SQL 예약어를 사용하지 않는 것이 좋습니다.
    print("-" * 28 + "\n")
    return table_name

def get_user_data():
    """사용자로부터 삽입할 데이터를 입력받아 리스트 형태로 반환합니다."""
    data_list = []
    print("--- 데이터 입력 시작 ---")
    print("각 항목 입력 후 엔터키를 누르세요.")
    print("첫 번째 '구분' 항목에서 그냥 엔터키를 누르면 입력이 종료됩니다.\n")

    while True:
        category = input("구분 (입력을 마치려면 엔터): ")
        if not category:
            break
        sub_category = input("세부항목: ")
        details = input("상세내용: ")

        data_list.append((category, sub_category, details))
        print("-" * 20)

    print("--- 데이터 입력 종료 ---\n")
    return data_list

def main():
    # 1. MySQL 접속 정보 입력받기
    db_host, db_user, db_password, db_name = get_mysql_credentials()

    # 2. 사용할 테이블명 입력받기
    table_name = get_table_name()

    # 3. 삽입할 데이터 입력받기
    data_to_insert = get_user_data()

    if not data_to_insert:
        print("입력된 데이터가 없어 프로그램을 종료합니다.")
        return

    conn = None
    cursor = None
    try:
        # MySQL 서버에 연결
        conn = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )

        if conn.is_connected():
            print(f"MySQL '{db_name}' 데이터베이스에 '{db_user}' 사용자로 접속 성공")

        cursor = conn.cursor()

        # 4. 테이블 생성 (없을 경우만 생성) - 동적으로 테이블명 사용
        # SQL 인젝션에 주의: 테이블명은 %s로 매개변수화하기 어렵습니다.
        # 여기서는 사용자가 입력한 그대로 사용하지만, 실제 운영 환경에서는
        # 테이블명에 대한 유효성 검사나 허용 문자 제한이 필요합니다.
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS `{table_name}` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            category VARCHAR(255) NOT NULL,
            sub_category VARCHAR(255) NOT NULL,
            details TEXT NOT NULL
        )
        """
        cursor.execute(create_table_query)
        print(f"테이블 '{table_name}' 확인/생성 완료.")

        # 5. 데이터 삽입 쿼리 - 동적으로 테이블명 사용
        insert_query = f"INSERT INTO `{table_name}` (category, sub_category, details) VALUES (%s, %s, %s)"

        # 여러 건의 데이터를 한 번에 삽입
        cursor.executemany(insert_query, data_to_insert)
        conn.commit()

        print(f"총 삽입 레코드 수: {cursor.rowcount} (테이블: '{table_name}')")

    except Error as e:
        print(f"에러 발생: {e}")
        if conn and conn.is_connected():
            try:
                conn.rollback()
                print("데이터 삽입 중 오류가 발생하여 롤백되었습니다.")
            except Error as rb_e:
                print(f"롤백 중 에러 발생: {rb_e}")

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            print("MySQL 연결 종료")

if __name__ == "__main__":
    main()