#!/bin/bash
# script that takes merged input of lithops map functions and calls SNPs on properly merged mpileup

# example command line bash mpileup_merge_reduce.sh test.txt /home/lumar/bioss/cloudbutton/scripts/02_mpileup_merge/
file=$1
dir=$2
cat "$file" |
sort --parallel 3 -T . -k1,1 -k2,2n | 
awk -F '\t' 'function print_current(){if (old!="") print old"\t"len"\t"syms"\t"quals} {curr=$1"\t"$2"\t"$3; if (curr!=old) {if (old!="") print_current(); len=0; syms=""; quals=""; old=curr} len+=$4; syms=syms $5; quals=quals $6} END{print_current()}' |\
${dir}./SiNPle-0.5 

