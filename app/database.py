import mysql.connector
from datetime import datetime


now = datetime.now()


class Constants:
    table = 'webEQ'


mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='!nxbTjiPw7@Pb8',
    database='cards'
)
# scheme: webEQ (ID int Primary Key, rawiem String, iem String, target String, processed Datetime)

cursor = mydb.cursor(buffered=True)
cursor.execute('SELECT * FROM webEQ')
result = cursor.fetchall()


def get_all_ids(table='webEQ') -> list:
    ids = []
    cursor.execute(f'SELECT * FROM {table}')
    result = cursor.fetchall()
    for row in result:
        ids.append(row[0])
    return ids


def get_free_id(table=Constants.table) -> int:
    cursor.execute(f'SELECT * FROM {table}')
    result = cursor.fetchall()
    if len(result) == 0:
        return 0
    else:
        lastid = result[-1][0]
        print("lastid:", lastid)
        return lastid+1


def log(rawiem: str, iem: str, target: str, algo: str, filtercount: str, eqres:str, mode: str, results: str='',table:str=Constants.table) -> int:
    cursor.execute(f'SELECT * FROM {table}')
    processed = now.strftime("%Y-%m-%d %H:%M:%S")
    id = get_free_id()
    cursor.execute(
        f'INSERT INTO {table} VALUES ({id},"{rawiem}","{iem}","{target}","{algo}","{processed}","{filtercount}","{eqres}","{mode}","{results}")')
    return id


def getEntity(id: int, table=Constants.table) -> tuple:
    cursor.execute(f'SELECT * FROM {table} WHERE id = {id}')
    entity = cursor.fetchall()[0]
    return entity
