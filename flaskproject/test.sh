#!/bin/bash

inputFile="./privatekey.json"

iconv -f UTF-8 "$inputFile" -o /dev/null

if [[ $? -eq 0 ]]
then
    echo "Valid UTF-8 file.";
else
    echo "Invalid UTF-8 file!";
fi
