import pexpect
import subprocess
import paramiko
from pathlib import Path
import os
from config import *
import socket


def expect(i, p, ssh_newkey, password):
    if i == 0:
        print("I say yes")
        p.sendline('yes')
        i = p.expect([ssh_newkey, 'password:', pexpect.EOF, pexpect.TIMEOUT])
        # expect(i=i, ssh_newkey=ssh_newkey, password=password,p=p)
    elif i == 1:
        print("I give password")
        p.sendline(password)
        p.expect(pexpect.EOF)
    elif i == 2:
        print("I got key \n")
        pass
    elif i == 3:
        print("connection timeout\n")
        pass
    output = p.before.decode('utf-8', 'ignore')
    # print(output)
    return output


def ssh_login(userName, hostName, password, cmd):
    ssh_newkey = 'Are you sure you want to continue connecting'
    p = pexpect.spawn("ssh " + userName + "@" + hostName + " " + cmd)

    i = p.expect([ssh_newkey, 'password:', pexpect.EOF, pexpect.TIMEOUT])
    # expect(i=i, ssh_newkey=ssh_newkey, password=password, p=p)
    if i == 0:
        print("I say yes")
        p.sendline('yes')
        i = p.expect([ssh_newkey, 'password:', pexpect.EOF])
    if i == 1:
        print("I give password")
        p.sendline(password)
        p.expect(pexpect.EOF)
    elif i == 2:
        print("I either got key\n")

        pass
    output = p.before.decode('utf-8', 'ignore')
    # print(output)
    return output


def paramiko_login(username, hostname, password, cmd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=hostname, port=22, username=username, password=password)

    stdin, stdout, stderr = ssh.exec_command(cmd)
    lines = stdout.readlines()

    return lines


def paramiko_config_login(hostname, cmd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    user_config_file = os.path.expanduser("~/.ssh/config")
    config = paramiko.SSHConfig.from_path(user_config_file)
    dict = config.lookup(hostname=hostname)
    print(dict)
    print(dict["hostname"])
    ssh.connect(hostname=dict["hostname"], username=dict["user"], port=22, key_filename=dict["identityfile"],
                sock=dict["proxycommand"])

    stdin, stdout, stderr = ssh.exec_command(cmd)
    lines = stdout.readlines()

    return lines


def scp_transfer(userName, hostName, password, fileName, path):
    ssh_newkey = 'Are you sure you want to continue connecting'
    p = pexpect.spawn("scp " + userName + "@" + hostName + ":" + fileName + " " + path)

    i = p.expect([ssh_newkey, 'password:', pexpect.EOF])
    if i == 0:
        print("I say yes")
        p.sendline('yes')
        i = p.expect([ssh_newkey, 'password:', pexpect.EOF])
    if i == 1:
        print("I give password")
        p.sendline(password)
        p.expect(pexpect.EOF)
    elif i == 2:
        print("I either got key or connection timeout\n")

        pass
    print(p.before.decode('utf-8', 'ignore'))


def get_free_port():
    cmd = "netstat -tulpn | grep LISTEN | grep - | awk '{ print $4 }'| awk 'NR == 1'"
    p1 = subprocess.run([cmd], shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    port = p1.stdout.strip()
    print(port)
    return port


# Port Forwarding
def port_forwarding(fileName, forwardedPort, dbPort, nodeName, nodeIp, isOCIMachine):
    cmd = "ssh -4 -i ~/.ssh/" + fileName + " -f -N -L " + forwardedPort + ":" + nodeIp + ":" + dbPort + " oracle@" + nodeName
    p1 = subprocess.call([cmd], shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    print(p1)
    return p1


# ---------------
# To get FreePort
# ---------------
def get_free_port():
    cmd1 = "netstat -tulpn | grep LISTEN | grep - | awk '{ print $4 }'| awk 'NR == 1'| awk  -F ':'  '{print$1 }'"
    p1 = subprocess.run([cmd1], shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    hostname = p1.stdout.strip()
    print(hostname)
    cmd2 = "netstat -tulpn | grep LISTEN | grep - | awk '{ print $4 }'| awk 'NR == 1'| awk  -F ':'  '{print$2 }'"
    p2 = subprocess.run([cmd2], shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    port = p2.stdout.strip()
    print(port)
    return port


def get_oracle_user_private_key(node):
    c1 = "ssh " + node + " "
    c2 = "'su - oracle -c 'pwd''"
    c3 = "sudo su - oracle -c 'pwd'"
    # p1 = paramiko_config_login(hostname=node, cmd="ls")
    p1 = ssh_login(userName="root", password="", hostName=node, cmd=c2)
    # home_path = p1[0].rstrip()
    home_path = p1
    print(home_path)


def parameters_validation(host_ip, port):
    result = True
    config_files = ["pdbName", "databasePort", "serviceName", "node1", "localPortNumber", "sshPath", "isOCIMachine"]
    for x in config_files:
        if eval(x) == "":
            print(x + " is a Empty Variable")
            result = False
    # To check if the port is free or not
    print(port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((host_ip, int(port)))
    except:
        result = False
        print("Port is in use \nEnter a valid port which is free")
    sock.close()
    # To check the ssh path entered is a directory or not
    if not Path(SSH_PATH).is_dir():
        result = False
        print("Enter a valid sshPath")

        if not Path(TNS_ADMIN).is_file():
            result = False
            print("Enter a valid tns file path")
    return result


def get_scp_batch_file_format(private_keys):
    private_keys.remove("config")
    oracle = "Kalli Nagarjun Reddy"
    private_keys.append(oracle)
    file_format = "~/.ssh/\{"
    file_string = ""
    for x in range(len(private_keys)):
        if x + 1 != len(private_keys):
            file_string = file_string + private_keys[x] + ","
        else:
            file_string = file_string + private_keys[x]
    return file_format + file_string + "\}"


# # print(get_scp_batch_file_format(private_keys=FILES_TO_COPY))
# def gen_connect_string(adb_pdb_name, host_name, port_number, pdb_service_name):
#     pdb_connect_string = """
# %s = (DESCRIPTION=(CONNECT_TIMEOUT=120)(RETRY_COUNT=20)(RETRY_DELAY=3)(TRANSPORT_CONNECT_TIMEOUT=3)(ADDRESS_LIST=(LOAD_BALANCE=on)(ADDRESS=(PROTOCOL=TCP)(HOST=%s)(PORT=%s)))(CONNECT_DATA=(SERVICE_NAME=%s)))
#     """
#     pdb_connect_string = adb_pdb_name + " = (DESCRIPTION=(CONNECT_TIMEOUT=120)(RETRY_COUNT=20)(RETRY_DELAY=3)" \
#                                         "(TRANSPORT_CONNECT_TIMEOUT=3)(ADDRESS_LIST=(LOAD_BALANCE=on)(ADDRESS=(PROTOCOL=TCP)(HOST=" + host_name + "" \
#                                                                                                                                                   "(PORT=" + port_number + ")))(CONNECT_DATA=(SERVICE_NAME=" + pdb_service_name + ")))"
#     updated_connect_string = pdb_connect_string % (adb_pdb_name, host_name, port_number, pdb_service_name)
#     print(updated_connect_string)
#     return updated_connect_string
#
#
# string = gen_connect_string(host_name="127.0.0.1", adb_pdb_name=PDB_NAME, port_number=LOCAL_PORT_TO_FORWARD,
#                             pdb_service_name=PDB_SERVICE_NAME)
# file1 = open(TNS_ADMIN + "/tnsnames.ora", "a")
# file1.write(string)
# file1.close()
def run_sql_plus(sql_plus_script, connect_string):
    p = subprocess.Popen(['sqlplus', '-s', connect_string], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = p.communicate(sql_plus_script.encode('utf-8'))
    stdout_lines = stdout.strip().decode('utf-8')
    print(stdout_lines)
    return stdout_lines


def sanity_test(pdb_name, pdb_password):
    get_pdb_name = """
    set pagesize 0 feedback off verify off heading off echo off;
    show con_name;
    exit
    """
    get_sys_date = """
    set pagesize 0 feedback off verify off heading off echo off;
    select sysdate from v$pdbs;
    exit
    """
    connect_string = "admin/" + pdb_password + "@" + pdb_name
    output1 = run_sql_plus(sql_plus_script=get_pdb_name, connect_string=connect_string)
    print(output1)
    output2 = run_sql_plus(sql_plus_script=get_sys_date, connect_string=connect_string)
    print("PDB Name is " + output1 + "\n", "SYS DATE is " + output2 + "\n")


def check_port(local_host_ip, client_machine_local_port):
    print("Free Port: " + client_machine_local_port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((local_host_ip, int(client_machine_local_port)))
        print(client_machine_local_port + " is Free Port")
    except:
        result = False
        print("Port " + client_machine_local_port + " is in use \nEnter a valid port which is free")
    sock.close()


check_port("127.0.0.1", "5700")
