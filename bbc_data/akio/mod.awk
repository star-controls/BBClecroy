#!/bin/gawk -f
#
# ./mod.awk -v diff=50 < demand.20110124.bbc > demand.20110124a.bbc
#
BEGIN{
  FS=" ";
}

{ 
  v=$3;
  if (v>0) {v+=diff;}
  printf("%s %s %s %s %s \n",$1,$2,v,$4,$5);
}
