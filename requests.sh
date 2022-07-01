#/bin/bash

username=$1
password=$2
host=$3
profile=$4
os=$5

curl -X POST http://127.0.0.1:5000/run_profile \
   -H 'Content-Type: application/json' \
   -d "{\"username\":\"$username\",\"password\":\"$password\",\"host\":\"$host\",\"profile\":\"$profile\",\"os\":\"$os\"}"
