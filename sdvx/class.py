import f_lib as lib
from sys import argv
from decimal import Decimal, ROUND_HALF_UP

MARGIN=0.10

kshfiles=lib.gen_kshfiles(argv[1])
level_all=[]
#level_list.count(i)/len(level_list) for i in range(20)
for ksh in kshfiles:
    header, _ = lib.readksh(ksh)
    #print(header['title'], header['difficulty'], int(header['level']))
    level_all.append(int(header['level']))

dec=lambda value: Decimal(value).quantize(Decimal('0.0001'), ROUND_HALF_UP)
print("Printing level distribution")
#from 20 to 1
level_freq=[level_all.count(i)/len(level_all) for i in range(20, 0, -1)]
for i in range(20):
    dec_f=dec(level_freq[i])
    print('{:2d}: {:3d} ({:5.2f}%)'.format(20-i, level_all.count(20-i), 100*dec_f))
#print(level_freq)
print("Total:", len(level_all))

level_accumulate=[sum(level_freq[:(i+1)]) for i in range(20)]
#print(level_accumulate)

level_section=[]
print()
print('Printing each section boundary including margin')
for i in range(20):
    startpoint=0 if i==0 else level_accumulate[i-1]-level_freq[i-1]*MARGIN
    endpoint=1 if i==19 else level_accumulate[i]+level_freq[i]*MARGIN
    level_section.append([startpoint, endpoint])
    dec_s=dec(startpoint)
    dec_e=dec(endpoint)
    print('{:2d}:[{:5.2f}%, {:6.2f}%]'.format(20-i, 100*dec_s, 100*dec_e))
    #print(20-i, ":[", 100*dec_s, "%,", 100*dec_e, "%]")