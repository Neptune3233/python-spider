import requests
import re
import json
import time
import tkinter
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
    a = [x for x in range(10)]
    b = [x for x in range(1, len(a) + 1)]
    for aa, bb in zip(a, b):
        print aa, bb
