#!/bin/bash
#$pubip = `aws ec2 describe-addresses | grep "PublicIp" | cut -d ':' -f 2 | cut -d '"' -f 2 | grep -v amazon | tail -n 1`
while true ;
do
        echo $1 is havng `curl -Is -k https://$1/ | head -n 1 && sleep 1`
done
