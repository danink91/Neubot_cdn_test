#!/bin/sh
cd ..
COUNTER=0
while [ true ]; do
  COUNTER=$((COUNTER+1))
  date
  echo "start test: $COUNTER"
#chiedere a simo se metto 2>/dev/null poi il -v non mi va
  python -m neubot_cdn_test $@ 
  echo "end test: $COUNTER"
  sleep 1800
done
