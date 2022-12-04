#!/bin/bash

cat file.txt | grep sender | awk '{print "sender " $7}' > mean.txt
cat file.txt | grep receiver | awk '{print "receiver " $7}' >> mean.txt

echo "interval,bitrate" >  parsed.txt
cat file.txt | grep sec | awk '{print $3 "," $7}' >> parsed.txt