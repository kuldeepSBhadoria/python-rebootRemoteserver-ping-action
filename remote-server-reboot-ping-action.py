#Written by Kuldeep
#09/23/2020 
#Version : 1.5

import subprocess
import paramiko
import sys
import platform
import time
import glob
import math
import requests
import threading
from datetime import datetime
import os
# Import smtplib for the actual sending function
import smtplib, ssl


HOST_IP='10.0.128.132'
BMC_IP='10.0.128.128'
list_nvme="nvme list"
run_fio='/root/runfio.sh &'
ssh_run_fio='ssh root@'+HOST_IP+' fio /root/PCIE_SSD_cycle.fio &'
run_fio_cmd='fio /root/PCIE_SSD_cycle.fio &'
iostat_cmd='iostat'
no_ping=True
result_c = ''
pwrcycle= 'power-util slot1 12V-cycle'
ssh_pwrcycle= 'sshpass -p 0penBmc ssh -o StrictHostKeyChecking=no root@'+BMC_IP+' /usr/local/bin/power-util slot1 12V-cycle &'
#ssh_pwrcycle= 'sshpass -p 0penBmc ssh -o StrictHostKeyChecking=no root@'+BMC_IP+' /usr/local/bin/power-util sled-cycle &'
pwrcycle_status= 'power-util slot1 status'
ssh_pwr_status= 'sshpass -p 0penBmc ssh -o StrictHostKeyChecking=no root@'+BMC_IP+' /usr/local/bin/power-util slot1 status'

scp_fio='scp -pr PCIE_SSD_cycle.fio root@'+HOST_IP+':/root'
scp_fio_sh='scp -pr runfio.sh root@'+HOST_IP+':/root'



    

def run_command(HOST, COMMAND):
    p = paramiko.SSHClient()
    p.set_missing_host_key_policy(paramiko.AutoAddPolicy())   # This script doesn't work for me unless this line is added!
    try:
       p.connect(HOST, port=22, username="root", password="facebook")
       stdin, stdout, stderr = p.exec_command(COMMAND, timeout=10)
    except:
       print('oops  ...................')

    opt = stdout.readlines()
    opt = "".join(opt)
    p.close()
    return opt

def run_bmc_command(HOST, COMMAND):
    p = paramiko.SSHClient()
    print("------run bmc -----------")
    p.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        print(COMMAND)
        p.connect(HOST, port=22, username="root", password="0penBmc")
    except:
        print("can not connect")
        return 0
    stdin, stdout, stderr = p.exec_command(COMMAND)
    opt = stdout.readlines()
    opt = "".join(opt)
    p.close()
    print(opt)
    print("------run bmc -----------end")
    return opt


def ping_ip(current_ip_address):
        try:
            output = subprocess.check_output("ping -{} 1 {}".format('n' if platform.system().lower(
            ) == "windows" else 'c', current_ip_address ), shell=True, universal_newlines=True)
            if 'unreachable' in output:
                return False
            else:
                return True
        except Exception:
                return False
 
def message():
	resp = requests.post('https://textbelt.com/text', { 'phone': '+1650xx9401','message': '..Quanta Error ..','key': 'xx6912a6085ca0a06a3852c53e6bf2f8ea24fb40f3MN6HuQlN7dVw0Mshn1pB6P3s',})
	print(resp.json())

def fio_on_host(HOST):
       run_command(HOST_IP, run_fio_cmd)
     	
	
if __name__ == '__main__':
    current_ip_address = [HOST_IP]
    count=1
    while True:
        print(str(datetime.now()))
        print('\n ##### count = %d ' % count)
        while no_ping:          
            for each in current_ip_address:
                if ping_ip(each):
                    print(f"{each} is available")
                    no_ping = False
                    print(str(datetime.now()))
                else:
                    print(f"{each} is not available")
                time.sleep(5)
            	
        try:
            print("Waiting for some seconds so that OS can come up")
            time.sleep(11)
            print(str(datetime.now()))
            result_c = run_command(HOST_IP, list_nvme)
            print (result_c)
            time.sleep(3)
            result_c = run_command(HOST_IP, list_nvme)
            print (result_c)
            if('ERROR' in result_c):
                 print("Y=== ERROR Produced ================== ")
                 message()
                 os.exit(os.EX_OK)

            print('\n scp FIO workload')
            os.system('ssh-keygen -R 10.0.128.132')
            os.system(scp_fio_sh)
            os.system(scp_fio)
            time.sleep(3)
            result_c = run_command(HOST_IP, 'chmod 777 /root/runfio.sh')
            result_c = run_command(HOST_IP, 'chmod 777 /root/*.fio')

            os.system(ssh_run_fio)

            print('\n Waiting 120 seconds for FIO to be completed')
            for io in range(0, 12):           
                print (io * 10)
                time.sleep(10)
            print('\n FIO Completed ')
            result_c = run_command(HOST_IP, list_nvme)
            print (result_c)
            if('ERROR' in result_c):
                 print("Y=== ERROR Produced ================== ")
                 message()
                 os.exit(os.EX_OK)
            print('\n Powering down the system x x x x ')
            print(ssh_pwr_status)
            result_c = run_command(HOST_IP, ssh_pwr_status)
            print (result_c)
            print(ssh_pwrcycle)
            result_c = run_command(HOST_IP, ssh_pwrcycle)
            print (result_c)
            print("\n-----------------")
        except:
            print(" -----xxx-------")
        #result_c = run_bmc_command(BMC_IP, pwrcycle)
        #print (result_c)    
        no_ping=True
        count +=1
        
        
#resp = requests.post('https://textbelt.com/text', { 'phone': '+16504479401','message': '..Quanta Error ..','key': 'x6912a6085ca0a06a3852c53e6bf2f8ea24fb40f3MN6HuQlN7dVw0Mshn1pB6P3s',})
        
# def run_command(HOST, COMMAND):
    # ssh = subprocess.Popen(["ssh", "%s" % HOST, COMMAND],shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    
    # result = ssh.stdout.readlines()
    # if result == []:
        # error = ssh.stderr.readlines()
        # print(sys.stderr, "ERROR: %s" % error)
    # else:
        # print(" Pass \n")
    # return result     
