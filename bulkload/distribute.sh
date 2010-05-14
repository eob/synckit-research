#!/bin/bash

gzip -9 -c $1 > $1.gz
cp $1 static
cp $1 gzip
cp $1 gzip-static
cp $1 gzip-proxy-cache
cp $1 gzip-static-proxy-cache
cp $1.gz gzip-static
cp $1.gz gzip-static-proxy-cache
rm $1.gz
