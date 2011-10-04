#! /bin/bash

for i in *.svg
do
    convert $i ${i%.svg}.png
done
