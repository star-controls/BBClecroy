#!/bin/gawk -f
BEGIN{
  FS=" ";
}

{ 
  v=$3;
  if (v>0) {print v;}
}
