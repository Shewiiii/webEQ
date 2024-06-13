import mysql.connector
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()


class Constants:
    table = 'webEQ'
# schema: webEQ (ID int Primary Key, rawiem String, iem String, target String, processed Datetime)


class DB:
    conn = None

    def connect(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password=os.getenv('DB_PASSWORD'),
            database='cards')

    def query(self, sql: str, params: tuple | None = None):
        print(sql)
        try:
            cursor = self.conn.cursor(buffered=True)
        except:
            self.connect()
            cursor = self.conn.cursor(buffered=True)
        cursor.execute(sql, params)
        self.conn.commit()
        return cursor


db = DB()


def get_all_ids(table=Constants.table) -> list:
    ids = []
    cursor = db.query(f'SELECT * FROM {table};')
    result = cursor.fetchall()
    for row in result:
        ids.append(row[0])
    return ids


def get_free_id(table=Constants.table) -> int:
    cursor = db.query(f'SELECT * FROM {table};')
    result = cursor.fetchall()
    if len(result) == 0:
        return 0
    else:
        lastid = result[-1][0]
        print("lastid:", lastid)
        return lastid+1

# log("rawiem","iem","target","algo",10,"eqres","mode",results="",table="webEQ")


def log(
    rawiem: str,
    iem: str,
    target: str,
    algo: str,
    filtercount: str,
    eqres: str,
    mode: str,
    results: str | list = '',
    table: str = Constants.table
) -> int:
    now = datetime.now()
    processed = now.strftime("%Y-%m-%d %H:%M:%S")
    id = get_free_id()
    db.query(
        f'INSERT INTO {table} VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);',
        (
            id,
            rawiem,
            iem,
            target,
            algo,
            processed,
            filtercount,
            eqres,
            mode,
            str(results)
        )
    )
    return id


def getEntity(id: int, table=Constants.table) -> tuple:
    cursor = db.query(f'SELECT * FROM {table} WHERE id = %s;', (id,))
    entity = cursor.fetchall()[0]
    return entity
