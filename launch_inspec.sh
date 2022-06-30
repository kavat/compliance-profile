#!/bin/bash

git clone https://github.com/dev-sec/linux-baseline.git
git clone https://github.com/dev-sec/cis-dil-benchmark.git
cd linux-baseline
inspec exec . -t ssh://$2@$1 --user $2 --password $3 --chef-license=accept-silent --reporter json:- | jq . > ../linux-baseline.json
cd ..
cd cis-dil-benchmark
inspec exec . -t ssh://$2@$1 --user $2 --password $3 --chef-license=accept-silent --reporter json:- | jq . > ../cis-dil-benchmark.json
cd ..
