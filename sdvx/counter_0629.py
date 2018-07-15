"""objective:
chip note:
count number of 1s
count number of 2s

hold note: with 'tick'
count number of 2s
count number of 1s

knob:
count number of right angles
else: count with 'tick'

parsing with --
[0000,22,--,1111,00,--,0011,20,--,1100,02,--],[1111,00,--,0101,22,--,1111,00,--,1010,22,--]
double array
then operate uniquely among 3*i, 3*i+1, 3*i+2
"""

import sys
import re

fileobj=open(sys.argv[1],'rt', encoding='UTF8')
file_content=fileobj.read()
fileobj.close()

#split files
#print(file_content)
#print()
c_info=[]
c_cont_all=[]
c_cont=[]
lsplit=re.split('\n+',file_content)
for i in range(len(lsplit)):
    if (lsplit[i]=='--'):
        c_info=lsplit[:i] #0~i-1
        c_cont_all=lsplit[(i+1):] # i+1 ~ end
        break
#print("chart info:")
#print(c_info)
#print("chart content:")
#print(c_cont_all[:10])

c_cont.append([])
tune=0
for i in range(len(c_cont_all)):
    if(c_cont_all[i]!='--'):
        c_cont[tune].append(c_cont_all[i])
    else: #new tune
        c_cont.append([])
        tune+=1
#print(c_cont[2])
#print("tune:", tune)


#print(c_cont[2])
#print(c_cont[2][0])
#print(c_cont[2][0][0])
#format: c_cont[#no. tune] #len(c_cont[tune])= 1+1 or 4 or 8+1, ...
notelist=[]
infolist=[]
for i in range(tune):
    infolist.append([])
    noteline=len(c_cont[i])
    #print(c_cont[i])
    #print("noteline:", noteline)
    for j in range(len(c_cont[i])):
        if(c_cont[i][j][0] not in ['0','1','2']):
            infolist[i].append(j)
            noteline-=1 
    #print("i:",i,"noteline:", noteline)
    notelist.append(noteline)
#print(infolist)

numBTchip=[]
numBThold=[]
numFXchip=[]
numFXhold=[]
numVLrect=[]
numVLhold=[]
for i in range(tune): #i: number of tunes
    BTchip=0
    BThold=[0,0,0,0] #BT A,B,C,D
    BTholdon=[0,0,0,0] #hold-on:check whether the last line was hold
    trueBThold=0

    FXchip=0
    FXhold=[0,0] #FX L,R
    FXholdon=[0,0]
    trueFXhold=0

    VLrect=0
    VLholdL=0
    VLholdR=0
    for j in range(notelist[i]+len(infolist[i])): #j: number of lines in a tune
        if(j not in infolist[i]):
            #c_cont[i][j]: 1111|00|--
            hand=0
            while(hand!=10):
                if(hand<4): #BT
                    if (c_cont[i][j][hand]=='2'): #hold
                        BTholdon[hand]=1
                        BThold[hand]+=1
                    else:
                        BTholdon[hand]=0
                        trueBThold+=int(BThold[hand]*12/notelist[i])
                        if (c_cont[i][j][hand]=='1'): #chip
                            BTchip+=1
                        #else: pass
                elif(hand>4 and hand<7): #FX
                    if (c_cont[i][j][hand]=='1'): #hold
                        FXholdon[hand-5]=1
                        FXhold[hand-5]+=1
                    else:
                        FXholdon[hand-5]=0
                        trueFXhold+=int(FXhold[hand-5]*12/notelist[i])
                        if (c_cont[i][j][hand]=='2'): #chip
                            FXchip+=1
                        #else: none
                """ #past
                    if (c_cont[i][j][hand]=='2'): #chip
                        FXchip+=1
                    elif (c_cont[i][j][hand]=='1'): #hold
                        FXhold+=1
                    #else: none
                """
                """
                elif(hand>7 and hand<10): #VOL
                    if (c_cont[i][j][hand]=='1'): #chip
                        BTchip+=1
                    elif (c_cont[i][j][hand]=='2'): #hold
                        BThold+=1
                    #else: none
                """
                hand+=1
    numBTchip.append(BTchip)
    numBThold.append(trueBThold)
    numFXchip.append(FXchip)
    numFXhold.append(trueBThold)
    print("i:",i,"BT:",trueBThold, "FX:",trueFXhold)
    #numFXhold.append(FXhold*12/notelist[i])
    #print("i:", i, "FX:", FXhold*12/notelist[i], int(FXhold*12/notelist[i]), 
    #"    BT:", BThold*12/notelist[i], int(BThold*12/notelist[i]))
#tick count: 12 per one full tune
numALLchip=sum(numBTchip)+sum(numFXchip)
numALLhold=sum(numBThold)+sum(numFXhold)
print(numALLchip, numALLhold)