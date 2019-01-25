#!/bin/gawk -f
#
# ./comp.awk < pola-b  > d
#
BEGIN{
  FS=" ";
}

{ 
  s=($3+$8)/2;
  d=0;
  if(s>0){ d=($3-$8)/s; }
  print d;
}
