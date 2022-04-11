from task_checker import Task

def main():
    task = Task.get(1)
    result = task.check_solution('''
print('Hello, world!')
    ''')
    print(result)


if __name__ == '__main__':
    main()