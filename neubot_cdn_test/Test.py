import subprocess
import time
cmd="python __main__.py"
for i in range(10):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    time.sleep(60)
    print "sleep"


