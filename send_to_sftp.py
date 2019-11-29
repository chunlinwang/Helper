#!/usr/bin/env python3

import argparse
import os
import pysftp
import requests

AWS_PUBLIC_IP_INFO_URL = 'http://169.254.169.254/latest/meta-data/public-ipv4'
IP = "*.*.*.*" // should be changed
PREPROD_SFTP_HOST = "sftp_host" // should be changed
LBM_SFTP_USERNAME = "sftp_username" // should be changed
LBM_SFTP_PASSWORD = "sftp_password" // should be changed
LBM_SFTP_PORT = "sftp_port" // should be changed

# connection closed automatically at the end of the with-block
def copy(input, output, host, port, username, password):
    """
    Send file to sftp.
    """
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    with pysftp.Connection(host, username, password=password, port=port, cnopts=cnopts) as sftp:
        os.chdir(input)
        for subPath in os.listdir(input):
            if os.path.isdir(input+subPath+'/'):
                os.chdir(input+subPath+'/')
                with sftp.cd('in'):
                    for file in os.listdir(input+subPath+'/'):
                        fileToSend = os.path.join(input, subPath, file)
                        fileToArchive = os.path.join(output, subPath, file)
                        sftp.put(fileToSend, subPath+'/new_'+file)
                        os.rename(fileToSend, fileToArchive)

def checkIp():
      res = requests.get(AWS_PUBLIC_IP_INFO_URL)
      return res.text

def main():
    """
    Entrypoint to the script
    """

    # parse args
    parser = argparse.ArgumentParser(description="Copy files with sftp")
    parser.add_argument("-i", "--input", help="Please specify the IN directory")
    parser.add_argument("-o", "--output", help="Please specify the OUT directory")
    parser.add_argument("-u", "--sftpUsername", help="Please specify the sftp username", default=LBM_SFTP_USERNAME)
    parser.add_argument("-p", "--sftpPassword", help="Please specify the sftp password", default=LBM_SFTP_PASSWORD)
    parser.add_argument("-H", "--sftpHost", help="Please specify the sftp host", default=PREPROD_SFTP_HOST)
    parser.add_argument("-P", "--sftpPort", help="Please specify the sftp port", default=LBM_SFTP_PORT, type=int)
    args = parser.parse_args()

    if checkIp() == ZOLAPROD_SFTP_PUBLIC_IP :
        if not os.path.exists(args.output):
            os.mkdir(args.output)

        copy(args.input, args.output, args.sftpHost, args.sftpPort, args.sftpUsername, args.sftpPassword)

if __name__ == "__main__":
    main()
