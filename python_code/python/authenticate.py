#!/usr/bin python3
import os
import random
import glob
import datetime
import sys
import time
from utils.utils_ import numerical_sort
from client import authenticateIntraMe, authenticateInterMe

TODAY = str(datetime.date.today()).replace('-', '')

PORT = sys.argv[1]

if __name__=='__main__':
    base_path = './csr_responses/'+'20230421'+'/Authentication/'
    csrs = sorted(glob.glob(base_path + '/*'), key=numerical_sort)
    try:

        t0 = time.time()
        for csr in csrs:
            attempt = csr.split('/')[-1]
            print(f'-- {attempt} --')

            attempts = sorted(glob.glob(csr + '/*'), key=numerical_sort)
            for att in attempts:
                random_csr = random.choice(csrs)
                while random_csr == csr:
                    random_csr = random.choice(csrs)

                random_attempts = sorted(glob.glob(random_csr + '/*'), key=numerical_sort)
                random_att = random.choice(random_attempts)

                authenticateIntraMe(int(PORT),att)

                time_auth_inter0 = time.time() 
                authenticateInterMe(int(PORT),att,random_att)
                time_auth_inter = round(time.time() - time_auth_inter0,4)

                

        print(f'\nTotal time: {(time.time() - t0) / 60}', 'minutes')
    except KeyboardInterrupt:
        print("\nCaught keyboard interrupt")


