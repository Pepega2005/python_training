from utils import db_action, DBAction, run_code


class Task:
    id: int
    name: str
    description: str
    output: str

    def __init__(self, task_id: int, name: str, description: str, output: str):
        self.id = task_id
        self.name = name
        self.description = description
        self.output = output

    @staticmethod
    def create(name: str, description: str, output: str) -> 'Task':
        task_id = db_action(
            '''
                insert into tasks (name, description, output) values (?, ?, ?)
            ''',
            (name, description, output),
            DBAction.commit,
        )
        task = Task(task_id, name, description, output)
        return task

    def save(self):
        db_action(
            '''
                update tasks set name = ?, description = ?, output = ? where id = ?
            ''',
            (self.name, self.description, self.output, self.id),
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
            tasks.append(db_task[0], db_task[1], db_task[2], db_task[3])
        return tasks

    def check_solution(self, code: str) -> bool:
        output = run_code(code)
        output = output.replace('\r', '')
        if output[-1] == '\n':
            output = output[:-1]
        return output == self.output