import requests
import re
import json
import time

import os

import multiprocessing

class Demo():
    def job(self, i):
        print i
        time.sleep(3)
        print os.getpid()

    def execute(self):
        pool = multiprocessing.Pool(10)
        for i in range(100):
            pool.apply_async(self.job, (i,))
        pool.close()
        pool.join()
        print 'All'

if __name__ == '__main__':
    ll = 'asdfg'
    print ll[1:-1]