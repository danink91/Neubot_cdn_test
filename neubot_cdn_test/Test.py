"""Just a test"""
import subprocess
import time
CMD = "python __main__.py"
for i in range(10):
    print i, "process"
    proc = subprocess.Popen(CMD, stdout=subprocess.PIPE, \
            stderr=subprocess.STDOUT, shell=True)
    time.sleep(60)
    print "sleep"


