#!/bin/sh
cd ..
COUNTER=0
while [ true ]; do
  echo $COUNTER
  COUNTER=$((COUNTER+1))
  python -m neubot_cdn_test $@
  sleep 300
done
