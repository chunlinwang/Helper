#!/usr/bin/env bash

# catch variables
if [ -z $1 ]
then
    echo "Please specify the IN directory" 1>&2
    exit 0
fi
inDir=$1

if [ -z $2 ]
then
    echo "Please specify the OUT directory" 1>&2
    exit 0
fi
outDir=$2

if [ -z $3 ]
then
    echo "Please specify the S3 bucket name" 1>&2
    exit 0
fi
bucketName=$3

if [ ! -d ${inDir} ]
then
  echo "${inDir} is not a directory" 1>&2
    exit 0
fi

if [ ! -d ${outDir} ]
then
  echo "${outDir} is not a directory" 1>&2
    exit 0
fi

lockFile="${inDir}/.lock"

if [ -f ${lockFile} ]
then
    echo "An instance is already running" 1>&2
    exit 0
fi

touch ${lockFile}

lines=${4:-8000}
splitDir="${inDir}/split"
rm -rf ${splitDir}
mkdir ${splitDir}

for path in "${inDir}"/*
do
    if [ "${path: -4}" != ".csv" ]
    then
        continue
    fi

   fileFullName=$(basename "$path" ".csv")
   IFS='.'
   read -r -a splitFileFullname <<< "$fileFullName"
   IFS=' '
   filePrefix=${splitFileFullname[0]}
   cd ${splitDir}
   # set header of csv
   head -n 1 $path > header.csv

   # split file csv
   tail -n +2 ${path} | split -l ${lines} -d - "${filePrefix}_"

   # add header and rename csv file
   for file in ${filePrefix}_*
   do
       cat header.csv ${file} > ${file}.csv;
       rm ${file};
   done

   rm header.csv
   mv ${path} ${outDir}
done

aws s3 sync ${splitDir} "s3://${bucketName}/"
rm -rf ${splitDir}

rm ${lockFile}
exit 1
