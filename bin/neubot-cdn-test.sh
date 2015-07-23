#!/bin/sh
cd ..
COUNTER=0
while [ true ]; do
  COUNTER=$((COUNTER+1))
  echo "start test: $COUNTER at"
  date
  python -m neubot_cdn_test $@
  echo "end test: $COUNTER at"
  date
  sleep 1500
done
