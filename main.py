import sqlite3

import jose.exceptions
import uvicorn
from fastapi import FastAPI, Body, Header, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from jose import jwt

import config
from utils import db_action, DBAction, run_code
from task_checker import Task

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
    cursor.execute('''
        create table if not exists tasks (
            id integer primary key,
            name varchar not null,
            description varchar,
            output varchar not null
        );
    ''')

    cursor.close()
    conn.close()


def get_user(authorization: str = Header(...)):
    try:
        user_id = jwt.decode(authorization, config.SECRET, algorithms=['HS256'])['id']
    except jose.exceptions.JWTError:
        raise HTTPException(
            status_code=400,
            detail='Неверный токен'
        )

    user = db_action(
        '''
            select * from users where id = ?
        ''',
        (user_id,),
        DBAction.fetchone,
    )
    return user


def send_html(name: str):
    with open(f'html/{name}.html', 'r', encoding='utf-8') as f:
        return HTMLResponse(f.read())


@app.get('/')
def index():
    return send_html('index')

@app.get('/tasks')
def tasks():
    return send_html('tasks')

@app.get('/login')
def login_page():
    return send_html('login')


@app.get('/register')
def register_page():
    return send_html('register')


@app.get('/api/ping')
def ping(user: list = Depends(get_user)):
    return {
        'response': 'Pong',
        'username': user[1],
    }


@app.post('/api/execute')
def execute(
        user: list = Depends(get_user),
        code: str = Body(..., embed=True),
):
    return {
        'result': run_code(code),
    }


@app.post('/api/login')
def login(username: str = Body(...), password: str = Body(...)):
    user = db_action(
        '''
            select * from users where username = ? and password = ?
        ''',
        (username, password),
        DBAction.fetchone,
    )
    if not user:
        raise HTTPException(
            status_code=404,
            detail='Пользователь не найден'
        )

    token = jwt.encode({'id': user[0]}, config.SECRET, algorithm='HS256')
    return {
        'token': token
    }


@app.post('/api/register')
def register(username: str = Body(...), password: str = Body(...)):
    user = db_action(
        '''
            select * from users where username = ?
        ''',
        (username,),
        DBAction.fetchone,
    )
    if user:
        raise HTTPException(
            status_code=400,
            detail='Пользователь уже существует'
        )

    db_action(
        '''
            insert into users (username, password) values (?, ?)
        ''',
        (username, password),
        DBAction.commit,
    )

    return {
        'message': 'Успешная регистрация'
    }

@app.get('/api/tasks')
def get_tasks(user: list = Depends(get_user)):
    return Task.all()

@app.post('/api/send_task')
def send_task(user: list = Depends(get_user),
              task_id: int = Body(..., embed=True),
              code: str = Body(..., embed=True),
              ) -> bool:
    task = Task.get(task_id)
    result = Task.check_solution(code)
    return {
        'result': result
    }


if __name__ == '__main__':
    uvicorn.run('main:app', reload=True)