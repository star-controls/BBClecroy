#!/bin/gawk -f
#
# ./polbtoa.awk < demand_28gev_normalpolA_20110614.bbc > demand_28gev_normalpolA_20110614a.bbc
#
BEGIN{
  FS=" ";
}

{ 
  d=$6;
  v=$3;
  if(d!=0){ v=$3 + int($3*d) }; 
  if(NF>4){
    print $1,$2,v,$4,$5;
  }else{
    print $0;
  }
}
