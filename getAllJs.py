#!/usr/bin/env python
from multiprocessing import Process
import os
from subprocess import call
def run_proc(url):
    call(["wget", url.strip()])

with open('./js-file-urls.txt') as f:
    lines = f.readlines()
    procs = []
    os.chdir('./js')
    for line in lines:
        p = Process(target=run_proc, args=(line,))
        procs.append(p)
        p.start()

    for proc in procs:
        proc.join()
