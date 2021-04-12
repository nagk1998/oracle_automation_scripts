# File Type : Config file
#
# This automation script supports :
#   1 : Connect to ADBD server from Local Host
#   2 : Connect to ADBD Database from Local Host
#
# ADBD Cluster Details:
#   220  : 4 Node Half Rack    : atpd-exa-ntlo21 atpd-exa-ntlo22 atpd-exa-ntlo23 atpd-exa-ntlo24
#   1209 : 2 Node Quarter Rack : atpd-exa-8qhsc1 atpd-exa-8qhsc2
#   1211 : 2 Node Quarter Rack : atpd-exa-pfzrz1 atpd-exa-pfzrz2
#
# Source VM hosts:
#   To connect to any ADBD clusters, we need to have the required keys.
#   The keys can be obtained from below hosts:
#    VMH1 = slcoda3061.us.oracle.com
#    VMH2 = rwsak09.us.oracle.com

# OPT_TYPE : Choose the type of operation supported. OPT_TYPE = [1 | 2] DEFAULT OPTION (2)
OPT_TYPE = 2

# --------------------------------------------------------------------
# Parameters for OPT_TYPE - 1 : Connect to ADBD server from Local Host
# --------------------------------------------------------------------
# Source vm host : SOURCE_VM_HOST = [VMH1 | VMH2]
SOURCE_VM_HOST_ID = "VMH1"

# Client machine .ssh folder path
SSH_PATH = "/Users/kalli/.ssh"

# FILES_TO_COPY : List of files required to copy from source VM:(no need to modify)
FILES_TO_COPY = ["atp_rsa", "bastion_rsa", "racteam_rsa", "wecra.rsa", "config"]

# ----------------------------------------------------------------------
# Parameters for OPT_TYPE - 2 : Connect to ADBD Database from Local Host
# ----------------------------------------------------------------------
# PDB_NAME : TNS Alias name for PDB:
PDB_NAME = "oltppdb1_tp"

# PDB ADMIN Password :
PDB_PASSWORD = "WelCome-123#"

# Database Service running Port:
DB_PORT = "1521"

# PDB Service Name:
PDB_SERVICE_NAME = "OLTPPDB1_tp.atp.oraclecloud.com"

# NODE_NAME : Enter the node detail where pdb is running.
# Syntax : NODE_NAME = [Cluster]_[node]. e.g. NODE_NAME = 1209_2
NODE_NAME = "1209_2"

# TNSADMIN PATH to add the connect String $ORACLE_HOME/network/admin
TNS_ADMIN = "/Users/kalli/instantclient_19_8/network/admin"
