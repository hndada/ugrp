"""
0.Calculate notelist and a sum of tunes shortly
1.DetermineKnobType (revised ver of ‘vol_change’)
2.ExtendKSH (nah just put a comma between two objects) --> would be joined to 0. and be "1."
3.CalculateKnobSpinQuantity (wow such haard)
4.DetermineLR (advanced version of detLR.py)

5.AddTiming (time.py) (BPM and tune size(except info) matters)
6.CalculateHoldDecayed (with lowercase of LR and timing)

7.CalculateHandCoordinates 
8.CalculateHandDistance 
9.(CalculateBPMratio)

10.DivideToInterval 
11.CalculateDensity 
12.CalculateHandMoveSpeed 
13.(CalculateLegibility)
"""

#inaccurate rounding float number issue
"""
#1.makes float number to integer temporarily and divide
#2.also, seems that we need 3 or more DECIMAL_KNOB
""" 

#naming issue
"""
notelist --> noteline_sum
infolist --> infoline
TRANSVERSE_FACTOR --> KNOB_TRANS
"""

#tune+1-1 #way to treat empty first tune
"""
#planned to delete empty tunes in no use at the first and last of charts  
#meanwhile, there's a few cases that has true empty tune: 1st tune at 02-02053e
#also, not simple. Need to move tune info to next or other tune.
"""

#try to implement another style of line increment
"""
instead of 'cc[i]', cc[dashindex[tune]+i] with deleting initialization and maually increment 
instead of 'while tune!=tune_total', for tune in range(tune_total) with deleting initialization and maually increment 
instead of dashindex, tuneindex
need to fix header printing
"""

## Advanced 
"""
1. Need to update DetermineLR gradually
"""

import sys
import re
from decimal import Decimal, ROUND_HALF_UP

fileobj=open(sys.argv[1],'rt', encoding='UTF-8-sig')
file_content=fileobj.read() #file_content is 'str'
fileobj.close()

#split files
header={}
cc=[]
lsplit=re.split('\n+',file_content)
for i in range(len(lsplit)):
    if (lsplit[i]=='--'):
        for j in range(i):
            line_split=lsplit[j].split('=')
            header[line_split[0]]=line_split[1] #0 ~ i-1
        cc=lsplit[i:] # i ~ end
        break
#print(header)
#print("chart content:", cc[:20])

#Generate a file proceeded to current stage
def interim(stage):
    filename='f'+str(stage)
    filename=open("./ksh/"+str(stage)+"_"+sys.argv[1].replace('./ksh/',''),"w",encoding="UTF-8-sig")
    #filename.write('\n'.join(str(header))+'\n')
    filename.write('\n'.join(header)+'\n')
    tune=0
    for i in range(len(cc)):
        if cc[i]=='--':
            filename.write("#"+str(tune+1-1)+'-------\n')
            tune+=1
        else:
            filename.write(cc[i]+'\n')
    filename.close()

#0. Calculate notelist and a sum of tunes shortly
while(len(cc[-1])==0): #some empty newlines
    del cc[-1]
tune_total=cc.count('--')
if cc[-1]=='--': #some empty tunes
    #not to delete cc[-1], it used to calculate
    tune_total-=1

dashindex=[i for i, line in enumerate(cc) if line=='--'] #ith: first line number at ith tune
tunesize=[dashindex[i+1]-dashindex[i] for i in range(len(dashindex)-1)]
#print("dashindex:", dashindex)
#print("tunesize:", tunesize)
#print(len(dashindex), len(tunesize), tune_total)
infolist=[]
linecount=0
for i in range(tune_total):
    infolist.append([])
    for j in range(tunesize[i]):
        if '|' not in cc[linecount+j]:
            infolist[i].append(j)
    linecount+=tunesize[i]
notelist=[tunesize[i]-len(infolist[i]) for i in range(len(tunesize))]
#print("tunesize:", tunesize)
#print("notelist:", notelist)
#print("infolist:", infolist)


#1. DetermineKnobType
newknoblist=[]
for LorR in range(8,10):
    prev='-'
    newknob=''
    tune=-1
    coloncount=0
    for line in cc:
        if '|' not in line: #not a noteline
            if line=='--':
                tune+=1
            continue
        if line[LorR]==':':
            coloncount+=1
        else:
            if prev!='-': #Determine
                if line[LorR]==prev: #stay knob
                    newknob+='"'*coloncount
                elif (notelist[tune]/(coloncount+1))==32: #rect knob
                    newknob+='#'*coloncount 
                else: #active line knob
                    newknob+=':'*coloncount 
            newknob+=line[LorR]
            prev=line[LorR]
            coloncount=0
    newknoblist.append(newknob)
    #print(newknob[:100])

#replace
i_noteline=0
for i in range(len(cc)):
    listline=list(cc[i])
    if '|' in cc[i]: #noteline
        for LorR in range(8,10):
            listline[LorR]=newknoblist[LorR-8][i_noteline]
        i_noteline+=1
    cc[i]=''.join(listline)

#interim(1)

#2. ExtendKSH
i=0 #line count
tune=0
while(tune!=tune_total):
    for _ in range(tunesize[tune]):
        if _ not in infolist[tune]:
            cc[i]+=(','+cc[i][8:10])
        i+=1
    tune+=1

#interim(2)

#3. CalculateKnobSpinQuantity
knobcode='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmno'

#only for scaling
#(knob_diff / tune_total)*TRANSVERSE_FACTOR = spin per tune 
#default:1  
TRANSVERSE_FACTOR=1 

#Suppose that need to spin 1/8 of field width to hit rect knob
#between 1/5 to 1/10 with the simulation
CHOKKAKU=(len(knobcode)-1)/6

#float number format settings
#default: DECIMAL_KNOB = 2
DECIMAL_KNOB=2
DIGIT=len(str( (len(knobcode)-1)*TRANSVERSE_FACTOR) )+2+DECIMAL_KNOB

newknoblist=[]
for LorR in range(8,10):
    # possible sign list: knobcode, - :" # 
    i=0 #line count
    tune=0 #initialization is so much critical
    newknob=[] #list of float numbers
    prev='-'
    colon_count=[0] #not to delete last element of the list
    rect_switch=0
    tune_fraction=[]  
    while(tune!=tune_total):
        for _ in range(tunesize[tune]):
            line=cc[i]
            if _ not in infolist[tune]:
                if line[LorR]=='-': #both 'righ before a knob starts' and 'right after a knob ends'
                    prev='-'
                    newknob.append(' '*DIGIT)
                elif line[LorR] in ':"#':
                    colon_count[-1]+=1
                    if line[LorR]=='#':
                        rect_switch=1 
                else: #The letter
                    if prev!='-': #End of the knob
                        #add for last unit
                        colon_count[-1]+=1 

                        #make exact number of space to each tune
                        for j in range(len(colon_count)):
                            fraction=colon_count[j]/notelist[tune-(len(colon_count)-1)+j]
                            tune_fraction.append(fraction)

                        #calculate knob_diff
                        knob_diff=knobcode.index(line[LorR])-knobcode.index(prev)
                        if rect_switch:  
                            #MG277: rect knob is treated as line knob in specific condition
                            sign=lambda x: (1,-1)[x<0]
                            knob_diff=sign(knob_diff)*CHOKKAKU
                            rect_switch=0

                        #calculate the amount of spin in each line
                        knob_diff*=TRANSVERSE_FACTOR
                        for j in range(len(colon_count)):
                            knob_ratio=tune_fraction[j]/sum(tune_fraction)
                            spin_line='{: {width}.{point}f}'.format(
                                round(knob_diff*knob_ratio/colon_count[j], DECIMAL_KNOB), width=DIGIT, point=DECIMAL_KNOB)
                            
                            if float(spin_line)==0:
                                spin_line=' '*DIGIT
                            newknob+=[spin_line]*colon_count[j]
                        
                        #clean up
                        colon_count=[0]
                        tune_fraction=[]
                    else: #Start of the knob
                        newknob.append(' '*DIGIT)
                    prev=line[LorR]
            i+=1
        if colon_count!=[0]: #toss
            colon_count.append(0)
        tune+=1
    newknoblist.append(newknob.copy())

#length test
#print(len(newknoblist[0]))
#print(len(cc),len(newknoblist[0])+sum([len(infolist[i]) for i in range(len(infolist))]))

#add to chart
tune=0
i_noteline=0
for i in range(len(cc)):
    if '|' in cc[i]: #noteline
        for LorR in range(8,10):
            cc[i]+=','+newknoblist[LorR-8][i_noteline]
        i_noteline+=1

#interim(3)

#4. DetermineLR
#English
"""
#Determine which hand to hit with, as every valid sign
##Rule
#1. Basically, determine 'L' if an object locates left side: knob-L, BT-A, BT-B, FX-L, vice versa.
#2. if an active 'knob' object and 'chip' objects are appeared at the same time, 
#the knob object gets its normal direction and chip objects gets the other side.
#3. if an active 'knob' object and 'hold' objects are appeared at the same time, there's two case possible.
#3-1. when the object is 'first tick' (which means knob and hold start at the same time), 
#the knob object gets its normal direction and hold objects gets the other side, like Rule #2.
#3-2. when the object is not 'first tick' (which means the hold objects already last before knob start),
#hold objects gets its determined direction at first tick, and knob objects gets the other side.
#4. Players could use their 'technical skills' to use hand placement easier than the one determined by simple hand placement rules 
#-> 4번을 바로 적용.
#cf) An 'active knob' means all knobs, except static knobs aka 'parking knobs'
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
holdside=['N']*6 #L/R: Left/Right   B:Both; also granted when other hand is free    N:Nullity; something went wrong
knobon=0 #check if the knob is already on(active)
knobside='N'
BTFX=[0,1,2,3,5,6]
KNOB=[8,9]

def otherside(hand, side, capital):
    if side in 'Ll':
        return 'R' if capital else 'r'
    if side in 'Rr':
        return 'L' if capital else 'l'
    if side in 'Bb':
        if hand in [0,1,5,8]:
            return 'R' if capital else 'r'
        if hand in [2,3,6,9]:
            return 'L' if capital else 'l'
    if side in 'Nn':
        return 'N' if capital else 'n'

def side(hand, capital):
    if hand in [0,1,5,8]:
        return 'L' if capital else 'l'
    if hand in [2,3,6,9]:
        return 'R' if capital else 'r'

def check_code(mode, hand):
    if mode=='chip':
        if hand in [0,1,2,3]:
            return '1'
        if hand in [5,6]:
            return '2'
    if mode=='hold':
        if hand in [0,1,2,3]:
            return '2'
        if hand in [5,6]:
            return '1'

i=0 #line count
tune=0
prev_next=['-']*2
Nullity_count=0
while tune!=tune_total:
    for _ in range(tunesize[tune]):
        if _ not in infolist[tune]:
            listline=list(cc[i][:10]) #1111|00|--

            #check the switches
            if any([holdon[x] for x in range(len(holdon))]):
                for j in range(len(BTFX)):
                    if listline[BTFX[j]]!=check_code('hold',BTFX[j]):
                        holdon[j]=0
                        holdside[j]='N'
            if knobon:
                if all([listline[x] in '-"' for x in KNOB]):
                    knobon=0
                    knobside='N'

            #scan the line
            hand=8
            while hand!=7:
                if hand in KNOB:
                    free=0
                    # 0##a: 'LR' (1st prior)
                    # 0::a: 'lr' (2nd prior)
                    # 0""a: '  '   
                    # ----: '  '                   
                    capital=False
                    if listline[hand]=='#':
                        capital=True

                    #determine letter is whether a tip of stayknob or rectknob
                    if listline[hand] in knobcode:
                        line_offset=1
                        tune_offset=0
                        while True: #next knob
                            
                            if i+line_offset >= dashindex[(tune+1)+tune_offset]:
                                tune_offset+=1
                            else: pass
                            if i+line_offset-dashindex[tune+tune_offset] in infolist[tune+tune_offset]:
                                line_offset+=1
                            else: break
                        prev_next[hand-8]+=cc[i+line_offset][hand]
                        if '#' in prev_next[hand-8]:
                            capital=True
                        elif prev_next[hand-8] in ['-"','"-','""']:
                            free=1
                        
                    prev_next[hand-8]=listline[hand]
                    if listline[hand] not in '-"' and not free:
                        for j in range(len(holdon)):
                            if holdon[j]: #if hold already exist
                                listline[hand]=otherside(BTFX[j], holdside[j], capital)
                                break
                            else:
                                listline[hand]=side(hand, capital)           
                        knobon=1
                        knobside=listline[hand]
                    else:  #knob free
                        listline[hand]=' '
                        knobon=0
                        knobside='N'

                if hand in BTFX:
                    capital=True
                    if listline[hand]!='0':                                
                        if listline[hand]==check_code('chip', hand):
                            if knobon:
                                listline[hand]=otherside(hand, knobside, capital)
                            else:
                                listline[hand]=side(hand, capital)
                            if ' ' not in listline[8:10]: #Nullity
                                listline[hand]='N'
                                Nullity_count+=1
                        elif listline[hand]==check_code('hold', hand):
                            capital=False
                            if knobon:
                                listline[hand]=otherside(hand, knobside, capital)
                            else:
                                for x in KNOB:
                                    if listline[x]!=' ':
                                        listline[hand]=otherside(x, side(x, capital), capital)
                                else:
                                    if holdon[BTFX.index(hand)]:
                                        listline[hand]=holdside[BTFX.index(hand)]
                                    else:
                                        listline[hand]=side(hand, capital)
                            if ' ' not in listline[8:10]: #Nullity
                                listline[hand]='n'
                                Nullity_count+=1
                            holdon[BTFX.index(hand)]=1
                            holdside[BTFX.index(hand)]=listline[hand]
                    else:
                        listline[hand]=' '
                hand=(hand+1)%10
            cc[i]=''.join(listline+list(cc[i][10:]))
        i+=1
    tune+=1

if Nullity_count!=0:
    print("Null detected! Nullity_count: ", Nullity_count)

#interim(4)

#5.AddTiming (BPM and tune size(except info) matters)
#BPM 변화 생기는 i 찾기 (t=XX) that is in infolist
#BPM 변화 없는 하나의 튠은 모두 같은 timing 간격을 갖는다. only tune size matters
#변속 발견하면 stack해둔 라인들 계산 시작. 변속 없는 튠은 쭈루룩 간단 계산, 있는건 조금 신경써줘서 계산

#if BPM:280 -> 280/4= 65 tunes per 60 sec = 60,000 ms 
#923.077ms per one tune
#57.702ms per one line if notelist[tune]==16
def duration(BPM):
    #return round(60*1000/(BPM/4)*10**DECIMAL)/10**DECIMAL
    return 60*1000/(BPM/4)

BPM=1 #Beats Per Minute
if '-' not in header['t']:
    BPM=int(header['t'])

tune=0
time=0.0
while tune!=tune_total:
    tune_info={}
    BPMidx=[]
    #make tune_info
    for i in range(tunesize[tune]):
        if i in infolist:
            line_split=cc[dashindex[tune]+i].split('=')
            tune_info[line_split[0]]=line_split[1]
            BPMidx.append(i)
    
    for i in range(tunesize[tune]):
        #find BPM change with tune_info
        if i in infolist[tune]:
            if i in BPMidx:
                BPM=cc[dashindex[tune]+i]
        else:
            time+=duration(BPM)/notelist[tune]
            cc[dashindex[tune]+i]+=','+str(Decimal(str(time)).quantize(Decimal('000000.001'), ROUND_HALF_UP))
            #'{: {width}.{point}f}'.format(
            #    str(round(time*10**DECIMAL)/10**DECIMAL), width=DIGIT, point=DECIMAL)
    tune+=1
interim(5)

#6.CalculateHoldDecayed (with lowercase of LR and timing)
#calculate integral for every interval
# 맨처음에 1을 넣을까 말까 --> 넣지말자, 처음거에 대한 보정은 이미 함수에서 반영됨
# y=alog(x-b), with (15, 1) (100, 4) <-(ms, objcount)


"""
#7.CalculateHandCoordinates 
xy_list=[[-729,162],[-243,162],[243,162],[729,162],
[-481,-326],[481,-326],
[-1133,598],[1133,598],[0,650]]
#4 BTs, 2 FXes, 2 knobs, start
"""

#11.CalculateDensity 
#노브와 노트 동시에 처리하는거에 가중치 or 손이동 쪽에서 가중치를 줘야하려나