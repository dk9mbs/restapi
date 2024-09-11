import argparse
import sys
import json
import os
import subprocess
import shutil

from clientlib import RestApiClient
from config import CONFIG
from core.log import create_logger

logger=create_logger(__name__)

parser = argparse.ArgumentParser(description='Administrate the restapi.')
parser.add_argument('--path','-p', type=str, help='path to the module folder for example: /tmp/demosolution/restapi/')
parser.add_argument('--loglevel','-l', type=str, help='logging if greater 0')
args = parser.parse_args()

path=args.path
db_log_level="" # -vv for every result

if not path.endswith('/'):
    path=f"{path}/"

if not os.path.exists(f"{path}solution.json"):
    print("no solution folder: missing solution.json")
    sys.exit(-9)

if 'loglevel' in args:
    db_loglevel="-vv"

# restapi root
restapi_root=f"{os.path.dirname(os.getcwd())}/"
# pathes
source_db_script_path=f"{path}database/"
source_plugin_path=f"{path}plugins/"
target_plugin_path=f"{restapi_root}plugins/"
source_wwwroot_path=f"{path}wwwroot/"
target_wwwroot_path=f"{restapi_root}wwwroot/"
# Database config
db_user=CONFIG['default']['mysql']['user']
db_pwd=CONFIG['default']['mysql']['password']
db_host=CONFIG['default']['mysql']['host']
db_database=CONFIG['default']['mysql']['database']
database_update_cmd=f"mysql -u{db_user} -p{db_pwd} -h{db_host} {db_log_level} {db_database} <{source_db_script_path}install.sql"

print("")
print(f"=========================================================================================")
print(f"| RestAPI root path.....: {restapi_root}")
print(f"| Source db script......: {source_db_script_path}")
print(f"| Source plugins........: {source_plugin_path}")
print(f"| Source wwwroot........: {source_wwwroot_path}")
print(f"| Target plugins........: {target_plugin_path}")
print(f"| Target wwwroot........: {target_wwwroot_path}")
print(f"| Database..............: {db_database}")
print(f"| DB host...............: {db_host}")
print(f"| DB user...............: {db_user}")
print(f"| DB password...........: *************")
print(f"=========================================================================================")

def update_database(cdatabase_update_cmd):
    print("================================================================")
    print("| updating the database ...                                    |")
    print("================================================================")
    p = subprocess.Popen(database_update_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        print (line.decode('utf8'))

    retval = p.wait()

    if not retval==0:
        print("*** Error in database update process! ***")
        print("- Check the install.sql script")
        print("- Check if the mysql binary in the path variable")
        print("*** Error in database update process! ***")
        sys.exit()

    print(f"Database updated with return value: {retval}")

    print("================================================================")
    print("| Database updated:OK                                          |")
    print("================================================================")

"""
Copy plugins from source to target
"""
def copy_plugins(source_plugin_path, target_plugin_path):
    print("================================================================")
    print("| installing the plugins ...                                   |")
    print("================================================================")
    if os.path.exists(source_plugin_path):
        for plugin in os.listdir(source_plugin_path):
            source_file=os.path.join(source_plugin_path,plugin)
            target_file=f"{target_plugin_path}{plugin}"

            print(f"{source_file} -> {target_file}")
            shutil.copyfile(source_file, target_file)

        print("================================================================")
        print("| plugins installed:OK                                         |")
        print("================================================================")
        return True
    else:
        print("================================================================")
        print("| plugin directory in source not found                         |")
        print("================================================================")
        return False

"""
Copy wwwroot files from source to target
"""
def copy_wwwroot(source_wwwroot_path, target_wwwroot_path):
    print("================================================================")
    print("| copying wwwroot files ...                                    |")
    print("================================================================")
    if os.path.exists(source_wwwroot_path):
        for root, dirs, files in os.walk(source_wwwroot_path):
            for name in dirs:
                target_path=os.path.join(root,name).replace(source_wwwroot_path, target_wwwroot_path)
                print(f"scanning: {target_path}")
                if not os.path.exists(target_path):
                    print(f"mkdir: {target_path}")
                    os.mkdir(target_path)

            for name in files:
                target_path=os.path.join(root,name).replace(source_wwwroot_path, target_wwwroot_path)
                source_path=os.path.join(root,name)
                print(f"copyfile: {target_path}")
                shutil.copyfile(source_path, target_path)


        print("================================================================")
        print("| copy wwwroot files:OK                                        |")
        print("================================================================")
        return True
    else:
        print("================================================================")
        print("| wwwroot directory in source not found                        |")
        print("================================================================")
        return False

update_database(database_update_cmd)
copy_plugins(source_plugin_path, target_plugin_path)
copy_wwwroot(source_wwwroot_path, target_wwwroot_path)


