#!/bin/bash

FILE=fulltopoDummy.txt

cat $FILE | grep sender | awk '{print "sender " $7}' > mean.txt
cat $FILE | grep receiver | awk '{print "receiver " $7}' >> mean.txt

echo "interval,bitrate" >  parsed.txt
cat $FILE | grep sec | awk '{print $3 "," $7}' >> parsed.txt