import function_lib as lib
from sys import argv
import os
import csv
from time import sleep

par=lib.pardir(argv[1])

""" #cannot replace crashed header due to its 'crashed header': cannot get the header 
header_replace={}
with open(par+'/header_fix/fixlist.csv', 'r') as fixlist_file:
    fixlist=csv.reader(fixlist_file)
    for line in fixlist:
        fix_content_dict={line[i].split(':')[0]:line[i].split(':')[1] for i in range(2,len(line))}
        header_replace[(line[0], line[1])]=fix_content_dict
"""
print("☆★☆ -= KSH Level Updater =- ★☆★")
sleep(1)
#just for check integrity, because new leveling system has already applied to IV charts
while True:
    iv_switch=input("Check & Update 'SDVX IV' version charts as well? (Y/N) ")
    if any(iv_switch==('Y','N')[i] for i in range(2)):
        break
while True:
    backup_switch=input("Save old .ksh files? (Y/N) ")
    if any(backup_switch==('Y','N')[i] for i in range(2)):
        break
#decode_switch=input("Fix the crashed header to normal with prepared replacement? "+
#    "current:"+str(len(header_replace))+" (Y/N)")


print("Start to make backup to", par+'/'+argv[1].split('/')[-1]+'_old', "  ...")
if backup_switch=='Y':
    lib.copytree(argv[1], par+'/'+argv[1].split('/')[-1]+'_old')

DIFF_TYPE=['light','challenge','extended','infinite']
DIFF_TYPE_AC=['NOV', 'ADV', 'EXH', 'INF/GRV']

level_table={}
def csv_addline(filepath):
    with open(filepath,"r",encoding="UTF-8-sig",newline="") as f:
        reader_obj=csv.reader(f)
        for line in reader_obj:
            for i in range(4):
                if line[i]: line[i]=int(line[i])
            title=''.join(e for e in line[4] if e.isalnum())
            level_table[title]=tuple(line[:4])

csv_addline(par+"/lvl/before_iv.csv")
if iv_switch: csv_addline(par+"/lvl/iv_only.csv")

#delete old file and make new file
def kshout(filepath):
    os.remove(filepath)
    filename=open(filepath,"w",encoding="UTF-8-sig")
    for k, v in header.items():
        filename.write('{:s}={:s}'.format(str(k), str(v))+'\n')
    for line in cc:
        filename.write(line+'\n')

print("Start to update...")
#update level automatically if identical title is found in level table
ksh_files=lib.gen_kshfiles(argv[1])
manually=[]
for i in range(len(ksh_files)):
    header, cc=lib.readksh(ksh_files[i])
    title=''.join(e for e in header['title'] if e.isalnum())
    diff_type=header['difficulty']
    level=header['level']
    found=False
    """
    if (title, diff_type) in header_replace:
        header_update_info=header_replace[(title, diff_type)]
        for k, v in header_update_info.items():
            header[k]=v
        kshout(ksh_files[i])
        found=True
    """
    if title in level_table:
        header['level']=level_table[title][DIFF_TYPE.index(diff_type)]
        kshout(ksh_files[i])
        found=True
    if not found:
        if int(level)<=12:
            continue
        manually.append(i)
    if i and i%(len(ksh_files)/4)==0:
        print(int(25*i/(len(ksh_files)/4)),"%"," has completed...", sep='')
print("Complete automatic level update!")

print()
if len(manually):
    print(len(manually), "ksh files need to update manually in", len(ksh_files), "in total.")
    print("Input -1 if want to keep the chart level as it is.")
else: print("All Clear!", end=' ')

print()
for i in manually:
    header, cc=lib.readksh(ksh_files[i])
    title=header['title']
    diff_type=header['difficulty']
    level=header['level']
    newlvl=input(title+' '+DIFF_TYPE_AC[DIFF_TYPE.index(diff_type)]+
    "(current level: "+str(level)+")"+": ")
    if int(newlvl)!=-1:
        header['level']=newlvl
        kshout(ksh_files[i])

print("Update has completed!")