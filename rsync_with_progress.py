# https://libbits.wordpress.com/2011/04/09/get-total-rsync-progress-using-python/
import subprocess
import re
import sys
import time

SECONDS_IN_MINUTE = 60
SECONDS_IN_HOUR = 60 * SECONDS_IN_MINUTE


def to_human_elapse_time(seconds):
    hours = int(seconds // SECONDS_IN_HOUR)
    if hours > 0:
        r = seconds % SECONDS_IN_HOUR
        minutes = int(r // SECONDS_IN_MINUTE)
        return f'{hours} hr. {minutes:d} min.'
    else:
        minutes = int(seconds // SECONDS_IN_MINUTE)
        if minutes > 0:
            seconds = int(seconds % SECONDS_IN_MINUTE)
            return f'{minutes} min. {seconds} sec.'
        else:
            return f'{int(seconds)} sec.'

 
def rsync(from_, to, print_=print):
    start = time.time()
    # https://unix.stackexchange.com/questions/48298/can-rsync-resume-after-being-interrupted
    cmd = 'rsync -av  --progress --append-verify ' + from_ + ' ' + to
    print(cmd)
    proc = subprocess.Popen(cmd,
                            shell=True,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
    )
    while True:
        output = proc.stdout.readline().decode('utf-8')
        if not output:
            break    

        if 'to-chk' in output:
            m = re.findall(r'to-chk=(\d+/\d+)', output)
            elapsed = time.time() - start
            print_(f'Elapsed Time:\n    {to_human_elapse_time(elapsed)}\nFile Remaining:\n    {str(m[0])}')
            if int(m[0][0]) == 0:
                break

    print_('\rFinished')