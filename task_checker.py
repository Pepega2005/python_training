import json

from utils import db_action, DBAction, run_code


class Task:
    id: int
    name: str
    description: str
    tests: str

    def __init__(self, task_id: int, name: str, description: str, tests: str):
        self.id = task_id
        self.name = name
        self.description = description
        self.tests = tests

    @staticmethod
    def create(name: str, description: str, tests: str) -> 'Task':
        task_id = db_action(
            '''
                insert into tasks (name, description, tests) values (?, ?, ?)
            ''',
            (name, description, tests),
            DBAction.commit,
        )
        task = Task(task_id, name, description, tests)
        return task

    def save(self):
        db_action(
            '''
                update tasks set name = ?, description = ?, tests = ? where id = ?
            ''',
            (self.name, self.description, self.tests, self.id),
            DBAction.commit,
        )

    @staticmethod
    def get(task_id: int) -> 'Task':
        db_task = db_action(
            '''
                select * from tasks where id = ?
            ''',
            (task_id,),
            DBAction.fetchone,
        )

        task = Task(db_task[0], db_task[1], db_task[2], db_task[3])
        return task

    @staticmethod
    def all():
        db_tasks = db_action(
            '''
                select * from tasks
            ''',
            (),
            DBAction.fetchall,
        )

        tasks = []
        for db_task in db_tasks:
            task = Task(db_task[0], db_task[1], db_task[2], db_task[3])
            tasks.append(task)
        return tasks

    def check_solution(self, code: str) -> dict:
        tests = json.loads(self.tests)

        tests_completed = 0
        for test in tests:
            program_input = test['input']
            expected_output = test['output']

            output = run_code(code, program_input)
            output = output.replace('\r', '')
            if len(output) != 0 and output[-1] == '\n':
                output = output[:-1]

            if output != expected_output:
                return {
                    'status': False,
                    'user_output': output,
                    'expected_output': expected_output,
                    'tests_completed': tests_completed,
                }

            tests_completed += 1

        return {
            'status': True,
        }