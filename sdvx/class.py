import f_lib as lib
from sys import argv
from decimal import Decimal, ROUND_HALF_UP
import csv

MARGIN=0.30
FOR_MATLAB=1 #better format for running MATLAB, but inferior to see directly
NO_NOV=0

kshfiles=lib.gen_kshfiles(argv[1])

if FOR_MATLAB:
    csvname=open('lvl_class.csv','w', newline='')
    wr=csv.writer(csvname)

level_all=[]
for ksh in kshfiles:
    header, _ = lib.readksh(ksh)
    if NO_NOV and int(header['level'])<=6: continue
    level_all.append(int(header['level']))


dec=lambda value: Decimal(value).quantize(Decimal('0.0001'), ROUND_HALF_UP)
print("Printing level distribution")
#from 20 to 1 // 1 to 20 if FOR_MATLAB

#level_freq: frequency of charts which have specific level; value range: 0 to 1 
level_freq=[level_all.count((i,i+1)[FOR_MATLAB])/len(level_all) for i in (range(20, 0, -1), range(20))[FOR_MATLAB]]
for i in range(20):
    dec_f=dec(level_freq[i])
    print('{:2d}: {:3d} ({:5.2f}%)'.format((20-i,i+1)[FOR_MATLAB], level_all.count((20-i,i+1)[FOR_MATLAB]), 100*dec_f))
print("Total:", len(level_all))

level_accumulate=[sum(level_freq[:(i+1)]) for i in range(20)]

level_section=[]
print('\nPrinting each section boundary including margin')
for i in range(20):
    startpoint=0 if i==0 else max([level_accumulate[i-1]-level_freq[i-1]*MARGIN,0])
    endpoint=1 if i==19 else min([level_accumulate[i]+level_freq[i]*MARGIN,1])
    level_section.append([startpoint, endpoint])
    dec_s=dec(startpoint)
    dec_e=dec(endpoint)
    print('{:2d}:[{:5.2f}%, {:6.2f}%]'.format((20-i,i+1)[FOR_MATLAB], 100*dec_s, 100*dec_e))
    if FOR_MATLAB: wr.writerow([i+1, 100*dec_s, 100*dec_e])