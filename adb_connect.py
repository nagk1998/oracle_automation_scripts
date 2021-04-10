import pexpect
import subprocess
from config import *
from pathlib import Path
import socket
from cluster_map import *
from datetime import datetime


#
# USAGE
#    python3 adb_connect.py
# Requirements
#    python3
# PYTHON-MODULES
#    Pexpect
# DESCRIPTION
#    This script can be used to connect to ADB clusters 1209,1211,220 or  directly connect to the adb databases
#    from the client machine
#    Make sure that adb_connect.py and config.py are in the same directory
# OPTIONS
#  1 : Connect to ADBD server from Local Host/Client Machine
#  2 : Connect to ADBD Database from Local Host/Client Machine
# EXAMPLES
#    python3 adb_connect.py
#
#  HISTORY
#     2021/04/06 : Nagarjun Reddy Kalli(nkalli) : Script creation
#

# Before running this script you need to source all the path of Oracle Database
def expect(i, p, ssh_new_key, password):
    if i == 0:
        print("I say yes")
        p.sendline('yes')
        i = p.expect([ssh_new_key, 'password:', pexpect.EOF, pexpect.TIMEOUT])
        expect(i=i, ssh_new_key=ssh_new_key, password=password, p=p)
    elif i == 1:
        print("I give password")
        p.sendline(password)
        p.expect(pexpect.EOF, )
    elif i == 2:
        print("I got key \n")
        pass
    elif i == 3:
        print("connection timeout\n")
        pass
    output = p.before.decode('utf-8', 'ignore')
    print(output)
    return output


# ----------------------------------------------------------
#  to say yes to hosts when logged in first time recursively
# ----------------------------------------------------------
def login_to_unknown_hosts(user_name, host_name, password):
    ssh_new_key = 'Are you sure you want to continue connecting'
    p = pexpect.spawn("ssh " + user_name + "@" + host_name + " whoami")

    i = p.expect([ssh_new_key, 'password:', pexpect.EOF, pexpect.TIMEOUT])
    expect(i=i, ssh_new_key=ssh_new_key, password=password, p=p)


# ------------------------------------
# To Scp files from the remote Machine
# ------------------------------------
def scp_transfer(user_name, host_name, password, file_name, path):
    ssh_new_key = 'Are you sure you want to continue connecting'
    p = pexpect.spawn("scp " + user_name + "@" + host_name + ":" + file_name + " " + path)

    i = p.expect([ssh_new_key, 'password:', pexpect.EOF])
    if i == 0:
        print("I say yes")
        p.sendline('yes')
        i = p.expect([ssh_new_key, 'password:', pexpect.EOF])
    if i == 1:
        print("I give password")
        p.sendline(password)
        p.expect(pexpect.EOF)
    elif i == 2:
        print("I either got key or connection timeout\n")
        pass
    print(p.before.decode('utf-8', 'ignore'))


# ---------------------------------------------------------------------------------------
# To change files permission to 600 after downloading private keys from the remote server
# ---------------------------------------------------------------------------------------
def change_file_permission(client_machine_ssh_path, files_to_change_permission):
    private_key_files = files_to_change_permission
    for file in private_key_files:
        print(file)
        file_local = client_machine_ssh_path + "/" + file
        subprocess.call(['chmod', '0600', file_local])
    print("keys permissions changed to 600")


# -------------------------------------------
# To get Ip Address of the of Forwarding node
# -------------------------------------------
def get_ip_address(node):
    cmd = "ssh " + node + " hostname -i"
    p1 = subprocess.run([cmd], shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    ip = p1.stdout.strip()
    print(ip)
    return ip


# -----------------------
# Generate Connect String
# -----------------------
def gen_connect_string(adb_pdb_name, host_name, port_number, pdb_service_name):
    pdb_connect_string = """
%s = (DESCRIPTION=(CONNECT_TIMEOUT=120)(RETRY_COUNT=20)(RETRY_DELAY=3)(TRANSPORT_CONNECT_TIMEOUT=3)(ADDRESS_LIST=(LOAD_BALANCE=on)(ADDRESS=(PROTOCOL=TCP)(HOST=%s)(PORT=%s)))(CONNECT_DATA=(SERVICE_NAME=%s)))
    """
    updated_connect_string = pdb_connect_string % (adb_pdb_name, host_name, port_number, pdb_service_name)
    print(updated_connect_string)
    return updated_connect_string


# --------------------------------------
# Format to download files in batch mode
# --------------------------------------
def get_scp_batch_file_format(private_keys):
    file_format = "~/.ssh/\{"
    file_string = ""
    for x in range(len(private_keys)):
        if x + 1 != len(private_keys):
            file_string = file_string + private_keys[x] + ","
        else:
            file_string = file_string + private_keys[x]
    return file_format + file_string + "\}"


# ---------------------------------------
# To get the node oracle user private key
# ---------------------------------------
def get_oracle_user_private_key(node, client_machine_ssh_path, node_oracle_key_name):
    c1 = "ssh " + node + " "
    c2 = "'su - oracle -c 'pwd''"
    c3 = c1 + c2
    p1 = subprocess.run([c3], shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    home_path = str(p1.stdout.strip())
    print(home_path)
    scp_transfer(user_name="root", host_name=node, password="", file_name=home_path + "/.ssh/id_rsa",
                 path=client_machine_ssh_path + "/" + node_oracle_key_name)


# ---------------
# Port Forwarding
# ---------------
def port_forwarding(file_name, forwarded_port, db_port, remote_node_name, remote_node_ip, client_machine_ssh_path):
    cmd = "ssh -4 -i " + client_machine_ssh_path + "/" + file_name + " -f -N -L " + forwarded_port + ":" + \
          remote_node_ip + ":" + db_port + " oracle@" + remote_node_name
    print(cmd)
    p1 = subprocess.call([cmd], shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    print(p1)
    return p1


# -----------------------------------
# Parameter validation for option TWO
# -----------------------------------
def parameters_validation(client_machine_local_port, local_host_ip):
    result = True
    option_two_parameters = ["PDB_NAME", "PDB_SERVICE_NAME", "NODE_NAME", "TNS_ADMIN"]
    # To check if config file variables are empty or not
    for x in option_two_parameters:
        if eval(x) == "":
            print(x + " is a Empty Variable\n")
            result = False
    # To check if the port is free or not
    print("Port chosen for Forwarding was : " + client_machine_local_port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((local_host_ip, int(client_machine_local_port)))
    except:
        result = False
        print("Port " + client_machine_local_port + " is in use \nEnter a valid port which is free")
    sock.close()
    # To check the ssh path and tns file path entered is valid or not
    if not Path(TNS_ADMIN + "/tnsnames.ora").is_file():
        result = False
        print("Enter a valid TNS ADMIN path")
    return result


# -----------------------------------
# Parameter validation for option one
# -----------------------------------
def connect_to_cluster_validation(client_machine_ssh_path):
    option_one_parameters = ["SOURCE_VM_HOST_ID", "SSH_PATH"]
    result = True
    if len(FILES_TO_COPY) == 0:
        print("FILES_TO_COPY is empty")
        result = False
    value = SOURCE_VM_HOST_ID
    if value != "VMH1" and value != "VMH2":
        print("Mention a valid Machine Name")
        result = False

    # To check if config file variables are empty or not
    for x in option_one_parameters:
        if eval(x) == "":
            print(x + " is a Empty Variable\n")
            result = False
    if not Path(client_machine_ssh_path).is_dir():
        result = False
        print("Enter a valid SSH Path")
    return result


# ----------------------------------------------
# OPTION ONE connect to clusters (1209,1211,220)
# ----------------------------------------------
def connect_to_clusters():
    files = get_scp_batch_file_format(private_keys=FILES_TO_COPY)
    backup_old_keys(files_to_copy=FILES_TO_COPY, ssh_path=SSH_PATH)
    scp_transfer(user_name=SOURCE_VM_USER, host_name=SOURCE_VM_HOST, password=VM_HOST_PASSWORD,
                 file_name=files,
                 path=SSH_PATH)
    keys_without_config = FILES_TO_COPY.copy()
    keys_without_config.remove("config")
    change_file_permission(client_machine_ssh_path=SSH_PATH, files_to_change_permission=keys_without_config)
    print("\nYou can connect to cluster 1209,1211 and 220 directly\n")


# ----------------------------------------------------------------------
# OPTION TWO connect to clusters (1209,1211,220) and to the adb database
# ----------------------------------------------------------------------
def connect_to_server_and_database(node_name):
    LOCAL_HOST_IP = "127.0.0.1"
    LOCAL_PORT_TO_FORWARD = str(get_open_port())
    check_extra_parameters = parameters_validation(client_machine_local_port=LOCAL_PORT_TO_FORWARD,
                                                   local_host_ip=LOCAL_HOST_IP)
    if not check_extra_parameters:
        exit(0)
    cluster_parameter_validation(node_name)
    node_name = cluster_list[node_name]
    oracle_key_name = node_name + "_oracle"
    print("Executing Option Two Connect to both server and database\n")
    connect_to_clusters()
    login_to_unknown_hosts(user_name="root", password="", host_name=node_name)
    get_oracle_user_private_key(node=node_name, client_machine_ssh_path=SSH_PATH,
                                node_oracle_key_name=oracle_key_name)
    change_file_permission(client_machine_ssh_path=SSH_PATH, files_to_change_permission=[oracle_key_name])
    node_ip = get_ip_address(node=node_name)
    port_forwarding(file_name=oracle_key_name, forwarded_port=LOCAL_PORT_TO_FORWARD, db_port=DB_PORT,
                    remote_node_name=node_name, remote_node_ip=node_ip, client_machine_ssh_path=SSH_PATH)
    string = gen_connect_string(host_name=LOCAL_HOST_IP, adb_pdb_name=PDB_NAME, port_number=LOCAL_PORT_TO_FORWARD,
                                pdb_service_name=PDB_SERVICE_NAME)
    file1 = open(TNS_ADMIN + "/tnsnames.ora", "a")
    file1.write(string)
    file1.close()
    print("\nNow you can connect to both cluster and the ADB database directly\n")


# ----------------------------------------------------------------------------------------------
# To check whether the node_name entered in the config file is there in cluster list map or not
# ----------------------------------------------------------------------------------------------
def cluster_parameter_validation(node_name):
    if not (node_name in cluster_list.keys()):
        print(node_name + " that you have entered is invalid")
        exit(0)


def get_vm_cluster_map(value, cluster_list_vm1, cluster_list_vm2):
    if value == "VMH1":
        return cluster_list_vm1
    elif value == "VMH2":
        return cluster_list_vm2


# ------------------------------------------------------
# TO get free port in client machine for port forwarding
# ------------------------------------------------------
def get_open_port():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


def get_vm_map(value):
    VMH1 = {
        "user": "root",
        "password": "WelCome-123#",
        "host_name": "slcoda3061.us.oracle.com"
    }
    VMH2 = {
        "user": "crsusr",
        "password": "cdcora",
        "host_name": "rwsak09.us.oracle.com"
    }
    if value == "VMH1":
        return VMH1
    elif value == "VMH2":
        return VMH2


# ---------------------
# To Run Shell Commands
# ---------------------
def run_shell_cmd(cmd):
    output = subprocess.run([cmd], shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    output = output.stdout.strip()
    print(output)
    return output


# ------------------------------------------------------------------------
# TO Backup the keys and config file if already present in the .ssh folder
# ------------------------------------------------------------------------
def backup_old_keys(files_to_copy, ssh_path):
    new_files = files_to_copy.copy()
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y_%H:%M:%S")
    for x in new_files:
        file = ssh_path + "/" + x
        if Path(file).is_file():
            cmd = "mv " + file + " " + file + "_" + dt_string
            run_shell_cmd(cmd=cmd)
            print(x + " name changed to " + x + "_" + dt_string)


# ------------------
# To Run Sql Scripts
# ------------------
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
    output2 = run_sql_plus(sql_plus_script=get_sys_date, connect_string=connect_string)
    print("PDB Name is " + output1 + "\nSYS DATE is " + output2 + "\n")


# ----------------------------------------------------------------------------------------------------------------------
#                                               Main File
# ----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    current_path = str(Path.cwd())
    check_parameters = connect_to_cluster_validation(client_machine_ssh_path=SSH_PATH)
    if not check_parameters:
        exit(0)
    vm_map = get_vm_map(SOURCE_VM_HOST_ID)
    SOURCE_VM_USER = vm_map["user"]
    SOURCE_VM_HOST = vm_map["host_name"]
    VM_HOST_PASSWORD = vm_map["password"]
    if OPT_TYPE == 1:
        print("Executing Option one Connect to Cluster")
        connect_to_clusters()
    else:
        # CLUSTER MAP --> according to the config file downloaded from the source VM
        cluster_list = get_vm_cluster_map(SOURCE_VM_HOST_ID, cluster_list_vm1=CLUSTER_LIST_VM_1,
                                          cluster_list_vm2=CLUSTER_LIST_VM_2)
        connect_to_server_and_database(node_name=NODE_NAME)
        sanity_test(PDB_NAME, PDB_PASSWORD)
