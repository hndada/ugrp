"""
0.Calculate notelist and a sum of tunes shortly
1.DetermineKnobType (revised ver of ‘vol_change’)
2.ExtendKSH (nah just put a comma between two objects)
3.CalculateKnobSpinQuantity (wow such haard)

4.DetermineLR (detLR.py)
5.AddTiming (time.py) (BPM and tune size(except info) matters)

5_5.CalculateHoldDecayed (with lowercase of LR and timing)
6.CalculateHandCoordinates 
7.CalculateHandDistance 
7_5.(CalculateBPMratio)

8.DivideToInterval 
9.CalculateDensity 
10.CalculateHandMoveSpeed 
11.(CalculateLegibility)
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

## Advanced 
"""
1. Need to update DetermineLR gradually
"""

import sys
import re

fileobj=open(sys.argv[1],'rt', encoding='UTF8')
file_content=fileobj.read() #file_content is 'str'
fileobj.close()

#split files
c_info=[]
cc=[]
lsplit=re.split('\n+',file_content)
for i in range(len(lsplit)):
    if (lsplit[i]=='--'):
        c_info=lsplit[:i] #0 ~ i-1
        cc=lsplit[i:] # i ~ end
        break
#print("chart content:", cc[:20])

#Generate a file proceeded to current stage
def interim(stage):
    filename='f'+str(stage)
    filename=open("./ksh/"+str(stage)+"_"+sys.argv[1].replace('./ksh/',''),"w",encoding="UTF8")
    filename.write('\n'.join(c_info)+'\n')
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

dashindex=[i for i, line in enumerate(cc) if line=='--']
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
#default: DECIMAL = 2
DECIMAL=2
DIGIT=len(str( (len(knobcode)-1)*TRANSVERSE_FACTOR) )+2+DECIMAL

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
                                round(knob_diff*knob_ratio/colon_count[j], DECIMAL), width=DIGIT, point=DECIMAL)
                            
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
#주차 노브 끝날때 마지막
#직각노브 대문자
#Nullity로 그 외의 손배치 확인

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
holdside=['N']*6 #L/R: Left/Right   B:Both; also granted when other hand is free N:Nullity; something went wrong
knobon=0 #check if the knob is already on(active)
knobside='N'
BTFX=[0,1,2,3,5,6]
KNOB=[8,9]
#BTFX, KNOB: hand-wise
#holdon, holdside: numeric-wise

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
rect_switch=0
while tune!=tune_total:
    for _ in range(tunesize[tune]):
        if _ not in infolist[tune]:
            listline=list(cc[i][:10]) #1111|00|--

            #check the switches
            if any([holdon[x] for x in range(6)]):
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
                    # 0##a: 'LR' (1st prior)
                    # 0::a: 'lr' (2nd prior)
                    # 0""a: '  '   
                    # ----: '  '                   
                    capital=False
                    prev_next=''
                    knob_backup=listline[hand]
                    if listline[hand] not in '-"':
                        for j in range(6):
                            if holdon[j]: #hold already existed
                                listline[hand]=otherside(BTFX[j], holdside[j], capital)
                                break
                            else:
                                listline[hand]=side(hand, capital)
                        if knob_backup=='#':
                            listline[hand]=str(listline[hand]).upper()                    
                        knobon=1
                        knobside=listline[hand]

                        #determine letter is whether a tip of stayknob or rectknob
                        if knob_backup in knobcode:       
                            for sign in [-1, 1]:
                                line_offset=1
                                tune_offset=0
                                while True:
                                    #dashindex[i]: first line number at ith tune
                                    if sign==-1: #prev
                                        if i+line_offset < dashindex[tune-tune_offset]: 
                                            tune_offset+=1
                                    else: #soon
                                        if i+line_offset >= dashindex[(tune+1)+tune_offset]:
                                            tune_offset+=1
                                    if i+line_offset*sign-dashindex[
                                        tune+tune_offset*sign] in infolist[tune+tune_offset*sign]:
                                        line_offset+=1
                                    else: break
                                """
                                print(cc[i+line_offset*sign])
                                print("No.",i+line_offset*sign-dashindex[tune+tune_offset*sign])
                                print("tune: ", tune, "tune_offset: ", tune_offset)
                                print("i: ", i, "line_offset: ", line_offset*sign)
                                print("infolist[tune+tune_offset*sign]", infolist[tune+tune_offset*sign])
                                print("notelist:", notelist[tune+tune_offset*sign])
                                """
                                #if tune==1 and i>=4 and i<=6:
                                #    print("i:",i,"cc:",cc[i+line_offset*sign][hand])
                                prev_next+=cc[i+line_offset*sign][hand]
                                if tune==1 and i>=4 and i<=6:
                                    print("pn:",prev_next)
                            if '#' in prev_next: #a tip of rectknob 
                                listline[hand]=str(listline[hand]).upper()
                    if listline[hand] in '-"' or prev_next in ['-"','"-','""']: #none and stayknob including its tip
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
                            holdon[BTFX.index(hand)]=1
                            holdside[BTFX.index(hand)]=listline[hand]
                    else:
                        listline[hand]=' '
                hand=(hand+1)%10
            cc[i]=''.join(listline+list(cc[i][10:]))
        i+=1
    tune+=1

interim(4)

#9.CalculateDensity 
#노브와 노트 동시에 처리하는거에 가중치 or 손이동 쪽에서 가중치를 줘야하려나