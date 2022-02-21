import uvicorn
from fastapi import FastAPI, Body
import sqlite3

app = FastAPI()


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
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()

    cursor.execute('''
        select * from users where username = ? and password = ?
    ''', (username, password))
    user = cursor.fetchone()
    print(user)

    cursor.close()
    conn.close()
    return user


@app.post('/test')
def test():
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()

    cursor.execute('''
        insert into users (username, password) values ('test', 'password')
    ''')
    conn.commit()

    cursor.close()
    conn.close()
    return None


uvicorn.run(app)