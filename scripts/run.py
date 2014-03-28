import simple_que
import os.path

BASE_PATH = os.path.normpath('c:/tmp')

def main():
    q = simple_que.FileQue(BASE_PATH)
    q.add_job('just added a new job')
    for j in q:
        print('{}:{}'.format(j.fn, j.cmd))
        if q.is_locked(j):
            print('\tunlocking {}'.format(j.fn))
            q.unlock(j)
        else:
            print('\tlocking {}'.format(j.fn))
            q.lock(j)
    print('deleting job {}'.format(j.fn))
    if q.is_locked(j):
        q.unlock(j)
    try:
        q.delete_job(j)
        q.lock(j)
    except simple_que.FileQueException as e:
        print(e)



if __name__ == '__main__':
    main()
