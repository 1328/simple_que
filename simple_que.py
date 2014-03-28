
'''
This is a very simply job queueing system for Python3
Works by creating job files in a directory (self.base) defined at __init__

job files are named: job_[time]_[pid of creator]

commands:
    load(): loads all queued jobs, drops them in FIFO order
        can also just use the object as a iterator, which calls load and then iterates throguh jobs FIFO
    add_job(cmd_text):  adds new job file
    delete_job(job_record):  deletes job
    load_job(job_file_name): loads text from job_file_name
    lock_job(job_record):   locks a job by adding a file named job_file_name_lck to self.base
    unlock_job(job_record):   removes the lock file
    is_locked(job_record):   tests whether lock file present


'''
import os
import os.path
import time
import collections


class FileQueException(Exception):
    pass

class FileQue(object):
    def __init__(self, basepath):
        self.base = basepath
        self.jobs = None
        self.cur = None
        self.JR = collections.namedtuple('Job','ts, fn, cmd')

    def add_job(self, what):
        '''when called adds a job file to the base directory, with text = what'''
        while True:
            name = '_'.join([
                'job',
                str(int(time.time()*100)),
                str(os.getpid()),
                ])
            name = os.path.join(self.base,name)
            if not os.path.exists(name):
                break
            print('waiting for new timestamp')
            time.sleep(.05)# could also use longer time to avoid
        with open(name,mode = 'w') as fh:
            fh.writelines(what)

    def get_job_filenames(self):
        '''returns valid jobs filenames from self.base'''
        to_check = next(os.walk(self.base))[2]
        fns = {}
        for fn in to_check:
            try:
                name, timestamp, pid = fn.split('_')
                if name == 'job':
                    fns[timestamp] = fn
            except ValueError:
                pass
                #print('skipping {} -> wrong format'.format(fn))
        return fns

    def load_job(self, fn):
        '''loads job file, returns job text'''
        fp = os.path.join(self.base, fn)
        with open(fp, mode='r') as fh:
            return fh.readlines()

    def load(self):
        '''loads all job files in self.base'''
        filenames = self.get_job_filenames()

        self.jobs = [self.JR(k,v,self.load_job(v))for k,v in sorted(filenames.items())]
        return self.jobs

    def __iter__(self):
        self.load()
        self.cur = -1
        return self

    def __next__(self):
        self.cur += 1
        if self.cur>=len(self.jobs):
            raise StopIteration
        return self.jobs[self.cur]

    def _lock_name(self, job):
        return '_'.join([job.fn,'lck'])

    def is_locked(self, job):
        '''returns true if job lockfile present'''
        fn = self._lock_name(job)
        pn = os.path.join(self.base, fn)
        return os.path.isfile(pn)

    def lock(self, job):
        '''locks 'job' by creating file named job.fn_lck in self.base'''
        if self.is_locked(job):
            raise FileQueException('can\'t lock job {}, job already locked'.format(job.fn))
        if job not in self.jobs:
            raise FileQueException('can\'t lock job {}, job has been deleted'.format(job.fn))
        fn = self._lock_name(job)
        pn = os.path.join(self.base, fn)
        with open(pn, mode = 'w') as fh:
            fh.write('locked')


    def unlock(self, job):
        '''unlocks job by deleting file named job.fn_lock in self.base'''
        fn = self._lock_name(job)
        pn = os.path.join(self.base, fn)
        if os.path.isfile(pn):
            os.remove(pn)
        else:
            raise FileQueException('Job {} not locked'.format(job.fn))

    def delete_job(self, job):
        '''deletes the job file specified in job.fn'''
        if self.is_locked(job):
            raise FileQueException('Job {} is locked, can\'t delete locked job'.format(job.fn))
        if job not in self.jobs:
            raise FileQueException('can\'t delete job {}, already deleted'.format(job.fn))
        pn = os.path.join(self.base, job.fn)
        os.remove(pn)
        self.jobs.remove(job)




