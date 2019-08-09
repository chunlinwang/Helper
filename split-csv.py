#!/usr/bin/env python3

import argparse
import csv
import os
import shutil
import sys

from datetime import datetime

SPLIT_TMP_STORAGE = 'SPLIT-FILES'
LOCK_FILENAME = 'lock'

def split(input, split_absolut_path, delimiter=';', row_limit=1000,
          output_name_template='%s_%s.csv', keep_headers=True):
    """
    Split csv file, encoding of the file must be uft-8.
    """

    if not os.path.exists(input):
        return

    if 0 == os.path.getsize(input):
        return

    filename = os.path.splitext(input)[0]
    with open(input, 'r', newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=delimiter)
        current_piece = 1

        current_out_path = os.path.join(
            split_absolut_path,
            output_name_template % (filename, current_piece)
        )

        current_out_writer = csv.writer(open(current_out_path, 'w', encoding='utf-8'), delimiter=delimiter)
        current_limit = row_limit

        # set headers
        if keep_headers:
            headers = csvreader.__next__()
            current_out_writer.writerow(headers)

        for i, row in enumerate(csvreader):
            # create new file
            if len(headers) == len(row):
                if i + 1 > current_limit:
                    current_piece += 1
                    current_limit = row_limit * current_piece
                    current_out_path = os.path.join(
                        SPLIT_TMP_STORAGE,
                        output_name_template % (filename, current_piece)
                    )
                    current_out_writer = csv.writer(open(current_out_path, 'w', encoding='utf-8'), delimiter=delimiter)
                    if keep_headers:
                        current_out_writer.writerow(headers)
                current_out_writer.writerow(row)
            else:
                log = 'line skipped: ' +  ' '.join(row)
                print(log.encode())

def sync_s3(inDir, outDir):
    sync_command = "aws s3 sync " + inDir +" s3://" + outDir + "/"
    os.system(sync_command)

def main():
    """
    Entrypoint to the script
    """

    # parse args
    parser = argparse.ArgumentParser(description="Simple DynamoDB backup/restore/empty.")
    parser.add_argument("-i", "--input", help="Please specify the IN directory")
    parser.add_argument("-o", "--output", help="Please specify the OUT directory")
    parser.add_argument("-s3", "--s3bucket", help="Please specify the S3 bucket name")
    parser.add_argument("-l", "--limit", help="row limit of split file")
    args = parser.parse_args()

    split_absolut_path = os.path.join(
        args.input,
        SPLIT_TMP_STORAGE
    )

    if not os.path.exists(split_absolut_path):
        os.mkdir(split_absolut_path)

    lock_path = os.path.join(
        args.input,
        LOCK_FILENAME
    )

    # check lock file
    if os.path.exists(lock_path):
        print('Process has been launched.')
        sys.exit(0)
    else:
	    open(lock_path, "w+")

    os.chdir(args.input)
    for path in os.listdir():
        if path.endswith('.csv'):
            print(datetime.now().isoformat(timespec='minutes'))
            print(path)
            split(path, split_absolut_path, row_limit=int(args.limit))
            output_path = os.path.join(
                args.output,
                path
            )
            os.rename(os.path.abspath(path), output_path)

    # aws s3 sync
    sync_s3(split_absolut_path, args.s3bucket)

    # remove split files
    if os.path.exists(split_absolut_path):
        shutil.rmtree(split_absolut_path)

    # remove lock
    os.unlink(lock_path)

if __name__ == "__main__":
    main()
