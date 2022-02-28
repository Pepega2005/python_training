from enum import Enum, auto

import uvicorn
from fastapi import FastAPI, Body
import sqlite3

app = FastAPI()


class DBAction(Enum):
    fetchone = auto()
    fetchall = auto()
    commit = auto()


def db_action(sql: str, args: tuple, action: DBAction):
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()

    cursor.execute(sql, args)
    if action == DBAction.fetchone:
        result = cursor.fetchone()
    elif action == DBAction.fetchall:
        result = cursor.fetchall()
    elif action == DBAction.commit:
        conn.commit()
        result = None

    cursor.close()
    conn.close()

    return result


@app.on_event('startup')
def create_db():
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()

    cursor.execute('''
        create table if not exists users (
            id integer primary key,
            username varchar not null,
            password varchar not null
        );
    ''')

    cursor.close()
    conn.close()


@app.get('/')
def index():
    return 'Hello, world!'


@app.post('/login')
def login(username: str = Body(...), password: str = Body(...)):
    return db_action(
        '''
            select * from users where username = ? and password = ?
        ''',
        (username, password),
        DBAction.fetchone,
    )


@app.post('/reg')
def test(username: str = Body(...), password: str = Body(...)):
    resp = db_action(
        '''
            select * from users where username = ?
        ''',
        (username,),
        DBAction.fetchone,
        )
    if resp:
        return "Error"
    return db_action(
        '''
            insert into users (username, password) values (?, ?)
        ''',
        (username, password),
        DBAction.commit,
    )

uvicorn.run(app)