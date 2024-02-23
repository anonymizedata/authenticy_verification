#!/usr/bin python3
import socket
import sys,os
import time
from random import randint
from protocol_phases import enrollment
from utils.utils_vendor import take_csr

def enrollMe(port,csr_enroll_path):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', port))
    data_folder_path = 'results/'
    cases = ['case1', 'case2']
    print('\n[system] -- REQUEST a csr_id --')

    n_ED = str(randint(0, 2 ** 256))

    m1 = 'request'+n_ED
    s.send(m1.encode())
    # data: csr_id, sign(sk_as,csr_id)
    data = s.recv(4096)
    time_enroll0 = time.time()
    csr_id,nonces,time_ver = take_csr(data,n_ED)
    time_enroll = '0'
    if csr_id!= None:
        attempt = csr_enroll_path.split('/')[-2]
        print(f'[system] Signing {attempt} with id {csr_id}')
        # step 2: take images for enrollment
        txt_enr = data_folder_path + 'case1' + 'intra' + ' enrol_information.txt'
        en_rec, time_proc, time_gen, time_Kgen, time_sign = enrollment(csr_id,csr_enroll_path, 'case1', txt_enr,nonces)

        print('[system] Sending record ')
        s.send(en_rec)
        time_enroll = time.time() - time_enroll0
        rec = s.recv(4096)
        print(rec.decode())
    else:
        s.send('None'.encode('utf-8'))
        time_enroll = time.time() - time_enroll0
    
    with open('results/time/time_enroll.txt', 'a') as file:
        file.write(str(attempt) + '\t'
            + str(time_enroll) + '\t'
            + str(time_ver) + '\t'
            + str(time_proc) + '\t'
            + str(time_gen) + '\t'
            + str(time_Kgen) + '\t'
            + str(time_sign)
            + '\n')

    s.close()
    return
