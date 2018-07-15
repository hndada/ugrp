
#I. Check L or R
"""
1. basically, Left side including knob-L and BT 1,2 and FX-L are 'L'
and totally same at the other side but 'R'
2. all is L when knob-R is activated except "stay knob", vice versa.
3-1. a.k.a. particular hand position: "hand-crossing(손교차)'
->only when one of knob is "stay"
3-2.'more easy hand position if one use his or her "technical skill"
(기교를 써서 더 쉬운 손배치가 가능한 경우 -> HEAVENLY SMILE MXM)' 
"""

#duplicated code start
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

#duplicated code end

count_cross=0
for i in range(tune): #i: number of tunes
    for j in range(notelist[i]+len(infolist[i])): #j: number of lines in a tune
        if(j not in infolist[i]):
            #c_cont[i][j]: 1111|00|--
            listline=list(c_cont[i][j])
            hand=0
            cross=0 #indicate whether hand-crossing is occurred
            while(hand!=10):
                if(hand in [0, 1, 5]): #Left side
                    if (listline[hand]!='0'): #left side is activated
                        if (listline[8] not in ['-',':']): #knob-L is also activated
                            if(listline[9] in ['-',':']): #when knob-R's state is 'stay'
                                cross=1 #run 결과 손교차 횟수가 거의 손 이동 횟수 수준으로 나옴 
                                listline[hand]='L' #then we can hit normally
                            else:
                                listline[hand]='R'
                        else:
                            listline[hand]='L'
                if(hand in [2, 3, 6]): #right side
                    if (listline[hand]!='0'): #right side is activated
                        if (listline[9] not in ['-',':']): #knob-R is also activated
                            if(listline[8] in ['-',':']): #when knob-L's state is 'stay'
                                cross=1
                                listline[hand]='R' #then we can hit normally
                            else:
                                listline[hand]='L'
                        else:
                            listline[hand]='R'
                if(hand==8): #knob-L
                    if (listline[hand]!='-'):
                        listline[hand]='R' if cross else 'L'
                if(hand==9): #knob-R
                    if (listline[hand]!='-'):
                        listline[hand]='L' if cross else 'R'
                hand+=1
            count_cross+=cross

print("count_cross:",count_cross)
