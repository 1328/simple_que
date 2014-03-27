import simple_que
import os.path

BASE_PATH = os.path.normpath('c:/tmp')

def main():
    q = simple_que.File_Que(BASE_PATH)
    q.add_job('just added a new job')
    for j in q:
        print('{}:{}'.format(j.fn, j.cmd))
        if q.is_locked(j):
            print('\tunlocking {}'.format(j.fn))
            q.unlock(j)
        else:
            print('\tlocking {}'.format(j.fn))
            q.lock(j)
    if not q.is_locked(j):
        print('deleting job {}'.format(j.fn))
        q.delete_job(j)


if __name__ == '__main__':
    main()
