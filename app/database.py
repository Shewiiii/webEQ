import mysql.connector
from datetime import datetime


now = datetime.now()


class Constants:
    table = 'webEQ'
# scheme: webEQ (ID int Primary Key, rawiem String, iem String, target String, processed Datetime)


class DB:
    conn = None

    def connect(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='!nxbTjiPw7@Pb8',
            database='cards')

    def query(self, sql):
        try:
            cursor = self.conn.cursor(buffered=True)
            cursor.execute(sql)
        except:
            self.connect()
            cursor = self.conn.cursor(buffered=True)
            cursor.execute(sql)
        return cursor


db = DB()


def get_all_ids(table='webEQ') -> list:
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


def log(rawiem: str, iem: str, target: str, algo: str, filtercount: str, eqres: str, mode: str, results: str = '', table: str = Constants.table) -> int:
    db.query(f'SELECT * FROM {table};')
    processed = now.strftime("%Y-%m-%d %H:%M:%S")
    id = get_free_id()
    db.query(
        f'INSERT INTO {table} VALUES ({id},"{rawiem}","{iem}","{target}","{algo}","{processed}","{filtercount}","{eqres}","{mode}","{results}");')
    return id


def getEntity(id: int, table=Constants.table) -> tuple:
    cursor = db.query(f'SELECT * FROM {table} WHERE id = {id};')
    entity = cursor.fetchall()[0]
    return entity
