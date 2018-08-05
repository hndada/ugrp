"""
2.DetermineKnobType (detk.py) (revised ver of ‘vol_change’)
1.ExtendKSH (extksh.py)

3.CalculateKnobSpinQuantity (cckq.py)
4.DetermineLR (lr.py) (detLR.py)
5.AddTiming (time.py)
6.CalculateHandCoordinates (cchc.py)
7.CalculateHandDistance (cchd.py)
8.DivideToInterval (div.py)
9.CalculateDensity (ccden.py)
10.CalculateHandMoveSpeed (cchms.py)
11.(CalculateLegibility)
"""
import sys
import re

fileobj=open(sys.argv[1],'rt', encoding='UTF8')
file_content=fileobj.read() #file_content is 'str'
fileobj.close()

#split files
#print(file_content)
#print()
c_info=[]
c_cont_all=[]
lsplit=re.split('\n+',file_content)
for i in range(len(lsplit)):
    if (lsplit[i]=='--'):
        c_info=lsplit[:i] #0~i-1
        c_cont_all=lsplit[i:] # i ~ end
        break
#print("chart info:")
#print(c_info)
#print("chart content:")
#print(c_cont_all[:20])





"""
c_cont.append([])
tune=0
for i in range(len(c_cont_all)):
    if(c_cont_all[i]!='--'):
        c_cont[tune].append(c_cont_all[i])
    else: #new tune
        c_cont.append([])
        tune+=1
"""



c_cont=[] #tune would be increment 1 when displayed
tune=-1 #all charts start with '--'
for i in range(len(c_cont_all)): #range(1:len(c_cont_all))
    if(c_cont_all[i]=='--'): #new tune
        tune+=1
        c_cont.append([])
    c_cont[tune].append(c_cont_all[i])

if (c_cont[-1]==['--', '']): #delete null tune
    del c_cont[-1]
    tune-=1
#planned to delete empty tunes in no use at the end of charts  
#But there's some case that has true empty tune: 02-02053e

#print(c_cont[1])
#print(c_cont[-1])
#print("tune:", tune)

#print(c_cont[2])
#print(c_cont[2][0])
#format: c_cont[#no. tune] 
#len(c_cont[tune])= 1+1 or 4 or 8+1, ...
notelist=[]
infolist=[]
for i in range(tune):
    infolist.append([])
    noteline=len(c_cont[i])
    #print("noteline:", noteline)
    for j in range(len(c_cont[i])):
        if(c_cont[i][j][0] not in ['0','1','2']):
            infolist[i].append(j)
            noteline-=1 
    #print("i:",i, "noteline:", noteline)
    notelist.append(noteline)
#print(notelist)
#print(infolist)

#2. DetermineKnobType
c_cont_all_k=[]
newknoblist=[]
for LorR in range(8,10):
    prev='-'
    newknob=''
    numtune=-1
    coloncount=0
    for line in c_cont_all:
        if '|' not in line: #not a noteline
            if line=='--':
                numtune+=1
            continue
        if line[LorR]==':':
            coloncount+=1
        else:
            if prev!='-': #Determine
                if line[LorR]==prev: #stay knob
                    newknob+='"'*coloncount
                elif (notelist[numtune]/(coloncount+1))==32: #rect knob
                    newknob+='#'*coloncount 
                else: #active line knob
                    newknob+=':'*coloncount 
            newknob+=line[LorR]
            prev=line[LorR]
            """
            if prev!='-' and prev not in knobcode:
                print('exception occurred! knob:', prev)
            """
            coloncount=0
    newknoblist.append(newknob)
    #print(newknob[:100])

line_idx=0
for line in c_cont_all:
    listline=list(line)
    if '|' in line: #noteline
        for LorR in range(8,10):
            listline[LorR]=newknoblist[LorR-8][line_idx]
        line_idx+=1
    c_cont_all_k.append(''.join(listline))

#print(c_cont_all[:30])
#print(c_cont_all_k[:30])
f1=open("./ksh/k_"+sys.argv[1].replace('./ksh/',''),"w",encoding="UTF8")
f1.write('\n'.join(c_info)+'\n')
for line in c_cont_all_k:
    f1.write(line+'\n')
f1.close()

f2=open("./ksh/all_"+sys.argv[1].replace('./ksh/',''),"w",encoding="UTF8")
f2.write('\n'.join(c_info)+'\n')


#1. ExtendKSH
for i in range(3,4): #i: number of tunes
    f2.write("#"+str(i+1)+'-------\n')
    for j in range(notelist[i]+len(infolist[i])): #j: the number of lines in a tune
        if(j not in infolist[i]): #c_cont[i][j]: 1111|00|--
            listline=list(c_cont[i][j])
            #print(listline)
            #listline
            #c_cont[i][j]+='|--|[0.0, 0.0]|0.0|[0.0, 0.0, 0.0, 0.0]|[0.0, 0.0]'


#3. CalculateKnobSpinQuantity
knobcode='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmno'

#4. DetermineLR (formerly known as detLR.py)
"""
Determine which hand to hit with, as every valid sign
##Rule
1. Basically, determine 'L' if an object locates left side: knob-L, BT-A, BT-B, FX-L, vice versa.
2. if an active 'knob' object and 'chip' objects are appeared at the same time, 
the knob object gets its normal direction and chip objects gets the other side.
3. if an active 'knob' object and 'hold' objects are appeared at the same time, there's two case possible.
3-1. when the object is 'first tick' (which means knob and hold start at the same time), 
the knob object gets its normal direction and hold objects gets the other side, like Rule #2.
3-2. when the object is not 'first tick' (which means the hold objects already last before knob start),
hold objects gets its determined direction at first tick, and knob objects gets the other side.
4. Players could use their 'technical skills' to use hand placement easier than the one determined by simple hand placement rules 
-> 4번을 바로 적용.

cf) An 'active knob' means all knobs, except static knobs aka 'parking knobs'
"""
#Korean
"""
#현재 라인에 노브가 있는지 확인.
#칩노트: 결과적으로 노브가 무조건 우선시.
#노브없으면 기본값으로 배정 (현재 '기교' 적용 없음)
#->손배치 바로 적용
#노브있으면, 노브의 반댓손으로 처리.

#홀드노트: 기존에 있는 걸 우선시함.
#동시에 있는 경우 노브 > 홀드 > 칩. 노브와 홀드가 동시에 같은 손으로 처리되지 않는것을 원칙으로 한다.
#노브있으나 홀드on이면 홀드 손 유지. 노브를 반대손으로 처리
#노브있으나 홀드off이면(즉, 동시에 시작함) 노브 손 기본값, 홀드를 반대손으로 처리
#한번 홀드on하면 끝날때까지 손을 바꾸지 않음.
"""

holdon=[0]*6 #check if the hold is already on(active)
holdside=['N']*6 #L/R: Left/Right   B:Both; also granted when other hand is free N:Nullity; something went wrong
knobon=0 #check if the knob is already on(active)
knobside='N'
BTFX=[0,1,2,3,5,6]
KNOB=[8,9]
#BTFX, KNOB: hand-wise
#holdon, holdside: numeric-wise

def otherside(hand, side):
    if side=='L':
        return 'R'
    if side=='R':
        return 'L'
    if side=='B':
        if hand in [0,1,5,8]:
            return 'R'
        if hand in [2,3,6,9]:
            return 'L' 
    if side=='N':
        return 'N'

def side(hand):
    if hand in [0,1,5,8]:
        return 'L'
    if hand in [2,3,6,9]:
        return 'R'

def check_code(mode, hand):
    if (mode=='chip'):
        if hand in [0,1,2,3]:
            return '1'
        if hand in [5,6]:
            return '2'
    if (mode=='hold'):
        if hand in [0,1,2,3]:
            return '2'
        if hand in [5,6]:
            return '1'

for i in range(tune): #i: number of tunes
    f2.write("#"+str(i)+'-------\n')
    for j in range(notelist[i]+len(infolist[i])): #j: the number of lines in a tune
        if(j not in infolist[i]): #c_cont[i][j]: 1111|00|--
            listline=list(c_cont[i][j])
            #check the switches
            if(any([holdon[x] for x in range(6)])):
                for k in range(len(BTFX)):
                    if listline[BTFX[k]]!=check_code('hold',BTFX[k]):
                        holdon[k]=0
                        holdside[k]='N'
            if(knobon):
                if(all([listline[x] in ['-',':'] for x in KNOB])):
                    knobon=0
                    knobside='N'
            #scan one line: 1111|00|--
            hand=8
            while(hand!=7):
                if(hand in KNOB):
                    if (listline[hand] not in ['-',':']):
                        for k in range(6):
                            if holdon[k]:
                                listline[hand]=otherside(BTFX[k], holdside[k])
                                break
                        else:
                            listline[hand]=side(hand)
                        knobon=1
                        knobside=listline[hand]
                    else:
                        listline[hand]=' '
                if(hand in BTFX):
                    if (listline[hand]!='0'):
                        if(listline[hand]==check_code('chip', hand)):
                            if(knobon):
                                listline[hand]=otherside(hand, knobside)
                            else:
                                listline[hand]=side(hand)
                        elif(listline[hand]==check_code('hold', hand)):
                            if(knobon):
                                listline[hand]=otherside(hand, knobside)
                            else:
                                for x in KNOB:
                                    if(listline[x] not in ['-',':',' ']): #if(listline[8]!=' '):
                                        listline[hand]=otherside(x,side(x))
                                else:
                                    if(holdon[BTFX.index(hand)]):
                                        listline[hand]=holdside[BTFX.index(hand)]
                                    else:
                                        listline[hand]=side(hand)
                            holdon[BTFX.index(hand)]=1
                            holdside[BTFX.index(hand)]=listline[hand]
                    else:
                        listline[hand]=' '
                hand+=1
                if hand==10:
                    hand=0
            f2.writelines(''.join(listline)+'\n')
        else:
            f2.write(c_cont[i][j]+'\n')

f2.close()