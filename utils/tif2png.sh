#!/bin/bash
# convert all tif to png to save space
for file in $(find . -name '*.tif')
do
  echo $file
  if [ ! -f ${file/%.tif/.png} ];
  then
    convert $file ${file/%.tif/.png};
    rm $file
  else
    echo "Warning: file ${file/%.tif/.png} exists!";
  fi
done
