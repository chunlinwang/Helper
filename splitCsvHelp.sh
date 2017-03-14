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
