import os
import glob
import datetime
import sys
import time
from vendor import enrollMe
from utils.utils_ import numerical_sort

TODAY = str(datetime.date.today()).replace('-', '')

if sys.argv[1] == 'reset':
    os.system('python3 ./python/vendor.py reset')
    sys.exit(1)


def enrollment(port):
    base_path = './csr_responses/'+'20230421'+'/Enrollment/'
    csrs = sorted(glob.glob(base_path + '/*'), key=numerical_sort)
    t0 = time.time()
    for csr in csrs:
        attempt = csr.split('/')[-1]
        print(f'-- {attempt} --')
        attempts = sorted(glob.glob(csr + '/*'), key=numerical_sort)
        enrollMe(port,attempts[0])
        #os.system('python3 ./python/vendor.py '+port+ ' request ' + attempt[0])
        print('\n')
    print(f'\nTotal time: {(time.time() - t0) / 60}', 'minutes')

    return

if __name__=='__main__':
    enrollment(int(sys.argv[1]))
