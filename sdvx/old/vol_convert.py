#original Author: YS
#slightly modified by Muang

##ksh파일 read
import os
import sys
import re

f=open(sys.argv[1],'rt', encoding='UTF8')
data=f.readlines()
data_original=data

###마디 나누기(이펙트 고려 X)
bar=[]
bartmp=[]
notstart=False

for i in range(len(data)):
    if len(data[i])>=11:
        if data[i][4]=='|' and data[i][7]=='|':
            notstart=True
            bartmp.append(data[i])
    if data[i]=="--\n" and notstart:
        bar.append(bartmp)
        bartmp=[]

###마디 개수 세기 (비트 판단, 직각노브: (64비트 2칸)*배수)
barsize=[]
for i in range(len(bar)):
    barsize.append(len(bar[i]))



### 노브 값 왼쪽부터 오른쪽으로

vol="0257ACFHKMPSUXZbehjmo" #.find()이용

###노브 이동 구분하기###
### ">" 는 오른쪽으로 "<"는 왼쪽으로 "*"는 왼쪽직각 "#"는 오른쪽직각 ":"는 주차 "-"는 없음###


sttl=0
bar_now=-1

#왼쪽 첫노브
for i in range(len(data)):
    if data[i]=="--\n":
        bar_now+=1
    if len(data[i])>=11:
        if data[i][4]=='|' and data[i][7]=='|':
            if data[i][8] in vol:
                sttl=i+1
                break

#왼쪽 노브 데이터 사이 방향 읽기

voll_dir=[] #':'묶음들마다 방향 저장
voll_pre=data[sttl-1][8]
voll_pre_dist=1 #거리, 직각체크
for i in range(sttl,len(data)):
    if data[i]=="--\n":
        bar_now+=1
    if len(data[i])>=11:
        if data[i][4]=='|' and data[i][7]=='|': #줄
            if data[i][8] in vol: #노브 위치 파악시 pre랑 비교해서 방향 체크
                if vol.find(data[i][8])==vol.find(voll_pre): #지속
                    voll_dir.append(':')
                elif vol.find(data[i][8])>vol.find(voll_pre): #큰 값=오른쪽
                    if int(barsize[bar_now]/voll_pre_dist)==32:
                        voll_dir.append('#')
                    else:
                        voll_dir.append('>')
                else: #작은 값=왼쪽
                    if int(barsize[bar_now]/voll_pre_dist)==32:
                        voll_dir.append('*')
                    else:
                        voll_dir.append('<')
                voll_pre=data[i][8]
                voll_pre_dist=0
            voll_pre_dist+=1
    
#오른쪽도 왼쪽과 마찬가지로 진행    

sttr=0
bar_now=-1
            
#오른쪽 첫노브
for i in range(len(data)):
    if data[i]=="--\n":
        bar_now+=1
    if len(data[i])>=11:
        if data[i][4]=='|' and data[i][7]=='|':
            if data[i][9] in vol:
                sttr=i+1
                break


volr_dir=[] #':'묶음들마다 방향 저장
volr_pre=data[sttr-1][9]
volr_pre_dist=1 #거리, 직각체크
for i in range(sttr,len(data)):
    if data[i]=="--\n":
        bar_now+=1
    if len(data[i])>=11:
        if data[i][4]=='|' and data[i][7]=='|': #줄
            if data[i][9] in vol: #노브 위치 파악시 pre랑 비교해서 방향 체크
                if vol.find(data[i][9])==vol.find(volr_pre): #지속
                    volr_dir.append(':')
                elif vol.find(data[i][9])>vol.find(volr_pre): #큰 값=오른쪽
                    if int(barsize[bar_now]/volr_pre_dist)==32:
                        volr_dir.append('#')
                    else:
                        volr_dir.append('>')
                else: #작은 값=왼쪽
                    if int(barsize[bar_now]/volr_pre_dist)==32:
                        volr_dir.append('*')
                    else:
                        volr_dir.append('<')
                volr_pre=data[i][9]
                volr_pre_dist=0
            volr_pre_dist+=1


#데이터 수정
def volchange(txt,voll,volr):
    return txt[0:8]+voll+volr+"\n"

getvoll=-1
getvolr=-1

for i in range(len(data)):
    if len(data[i])>=11:
        if data[i][4]=='|' and data[i][7]=='|':
            txt=data[i]
            voll_tmp=data[i][8]
            volr_tmp=data[i][9]
            if data[i][8] in vol:
                getvoll+=1
            if data[i][9] in vol:
                getvolr+=1
            if data[i][8] == ':':
                voll_tmp=voll_dir[getvoll]
            if data[i][9] == ':':
                volr_tmp=volr_dir[getvolr]
            data[i]=volchange(txt,voll_tmp,volr_tmp)


#결과값 출력

f2=open("./ksh/vol_converted_"+sys.argv[1].replace('./ksh/',''),"w",encoding="UTF8")
f2.writelines(data)
f.close()
f2.close()
