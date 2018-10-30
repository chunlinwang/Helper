#!/bin/bash

NAME=$1
echo $NAME
DIR=$(pwd)
echo $DIR
LINES=$2

path=$DIR'/'$NAME

echo $path

tail -n +2 $path | split -l $LINES - split_
for file in split_*
do
    head -n 1 $path > tmp_file
    cat $file >> tmp_file
    mv -f tmp_file $file
done

# vervion 2
#!/usr/bin/env bash

# catch variables
if [ -z $1 ]
then
    echo "Please specify the temporary dictionary"
    exit 0
else
    tmpDir=$1
fi

if [ -z $2 ]
then
  echo "Please specify the csv file name"
  exit 0
else
    fileFullName=$2
fi

if [ -z $3 ]
then
    lines=8000
else
    lines=$3
fi

path="${tmpDir}/${fileFullName}"

cd $tmpDir

IFS='.' read -r -a splitFileFullname <<< "$fileFullName"
filePrefix=${splitFileFullname[0]}

rm -rf $filePrefix
mkdir $filePrefix && cd $filePrefix

# set header of csv
head -n 1 $path > header.csv

# split file csv
tail -n +2 $path | split -l $lines -d - "${filePrefix}_"

# add header and rename csv file
for file in ${filePrefix}_*
do
    cat header.csv $file > $file.csv;
    rm $file;
done

rm header.csv
