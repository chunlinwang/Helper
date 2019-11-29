#!/usr/bin/env python2

from sshtunnel import SSHTunnelForwarder
import psycopg2
import csv

def createTunnelSSH():
    # Create an SSH tunnel
    tunnel = SSHTunnelForwarder(
        ('hostname', 22),
        ssh_username='cwang',
        ssh_private_key='/Users/chunlin/.ssh/id_rsa',
        remote_bind_address=('remote_host', 5432),
        local_bind_address=('127.0.0.1', 6543), # could be any available port
    )
    # Start the tunnel
    tunnel.start()

    return tunnel

def stopTunnelSSH(tunnel):
    # Stop the tunnel
    tunnel.stop()


def createDBConnect():
    conn = psycopg2.connect(
        database='babylone-users',
        user='babylone_users',
        password='babylone_users',
        host='10.0.0.20',
        port='5432',
    )    

    return conn

def closeDBConnect(conn):
    # Close connections
    conn.close()

def main():
    """
    Entrypoint to the script
    """
    # print('start ssh tunnel')
    # tunnel = createTunnelSSH()

    print('start db connect')
    conn = createDBConnect()

    # Get a database cursor
    cursor = conn.cursor()

    output = csv.writer(open('output.csv', 'w', encoding='utf-8'), delimiter=';')

    with open('order_test.csv', 'r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        for i, orderRaw in enumerate(csvreader):
            # Execute SQL
            userid = orderRaw[1].split('/')
            sql = 'sql'
            cursor.execute(sql)

            # Get the result
            rows = cursor.fetchall()

            for userRow in rows:
                for field in userRow:
                    orderRaw.insert(2, field)

            output.writerow(orderRaw)

    closeDBConnect(conn)
    
    # stopTunnelSSH(tunnel)

if __name__ == "__main__":
    main()
