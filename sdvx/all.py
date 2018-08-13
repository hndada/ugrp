#5번에서 effective beat check
#주석 정리
#메모 정리 /폰,컴퓨터
#중복코드 개선 (remain/)
#6번 구현

#new try
#투덱사이트에서 자체적으로 계산한 난이도요소들을 input으로
#pms에 그대로 적용, 어떻게 되나 관찰

#output
#1 구간 내 밀도(노트+노브), 손의 이동속도 
#2 구간 내 노트(원핸드 included/excluded), 노브, 원핸드(노트 on일때 knob도 on이면 원핸드 카운트++) 밀도 각각, 손의 이동속도 

"""
1.Calculate main datas
2.DetermineKnobType (revised ver of ‘vol_change’)
3.CalculateKnobSpinQuantity (wow such haard)
4.DetermineLR (advanced version of detLR.py)

5.CalculateHoldDecayed (with lowercase of LR and beats)
6.CalculateHandCoordinates (center of the active buttons and knobs)
6-1.CalculateHandDistance (calculation result locates at latter point)
7.AddTiming (BPM and tune size(except info) matters)
8.(CalculateBPMratio)

9.DivideToInterval (cut the chart every 400ms except chart info; no use since this stage)
10.CalculateDifficultyFactor
10-1.CalculateDensity (thanks to same interval size, just sum up chip and hold_decayed plus knob_quantity) (but for precise decision, divide by its unique duration time)
10-2.CalculateHandMoveSpeed (thanks to same interval size, just sum amount hand distance)
10-3.(CalculateLegibility)
11.run for all charts and output automatically
"""

###Fatal error
#need to consider the info 'beat'
#beat numerator -> the number of beats in the tune
#beat denominator -> the number that the tune divided by. default:4 
#example: 8/4   duration:2 tune     content:2 tune      formation:1 tune
#       : 5/4   duration:1.25 tune  content:1.25 tune   formation:1 tune
#       : 1/4   duration:0.25 tune  content:0.25 tune   formation:1 tune
#       : 4/8   duration:0.50 tune  content:0.50 tune   formation:1 tune (<==> 2/4)
#1튠이 차지하는 길이
#다행히 튠 하나 내에선 beat가 바뀌지 않는다 (튠 내에서 바꾸면 ksh에 저장되지 않는다)
#tune은 beat를 담는 단위.

#basically, the beat fraction is irreducible if denominator is bigger than 4
#example of charts which have various beats: soflan, -resolve-, doppelganger 
#Aragami(guess: #15 and #16 is actually 12 tunes each with beat=1/16 and most tune has beat=3/4(=12/16))
#변하지 않는 값은 editor에서 1박자(보통 생각하는 4분의 1튠)의 길이.

#important info: t, beat, stop, @)96(not in infoline)
#soso important info: tilt(ex. keep biggest), zoom_top/bottom --> #판정에 약간 영향 
#                     laserrange_r/l -> 가독성에 다소 영향
#not important info: fx-l, fx-r #only sound changes

#ksh 전문가 되는중
#sdvx.in보다 mega가 더 정확한 것도 있다 (ongaku resolve)
#mega: 9/16
#sdvx.in: 2.25/4 

#tune_den 붙은건 죄다 재검토할 필요가 있음

#Decimal 잘먹히는지 간단히 확인
#노브방향 바뀔때 strain 추가 with gradient
#동시타는 하향
#난이도는 모두를 위한 것.-ppy #노비스 노브 돌리는양은 있는 그대로. #여차하면 3차 난이도에 적용
#노비스에서는 직각 하향 없게


#naming issue
"""
unite two word naming format: use '_' or not? //overall variable or each-tune variable
rectknob or slamknob(ksh readme ver)
order of two-word: DECIMAL_KNOB(v) or KNOB_DECIMAL etc.
"""

#초기화 함수 추가 (beat_per_tune, BPM 등)

## Advanced
#1. Need to update DetermineLR gradually
#2. tune+1-1    #way to treat empty first tune
"""#2
planned to delete empty tunes in no use at the first and last of charts  
meanwhile, there's a few cases that has true empty tune: 1st tune at 02-02053e
also, not simple. Need to move tune info to next or other tune.
"""
#3. slam knob
"""#3
MG277: rect knob is treated as line knob in specific condition
"""

from sys import argv
from re import split
from decimal import Decimal, ROUND_HALF_UP

fileobj=open(argv[1],'rt', encoding='UTF-8-sig')
file_content=fileobj.read() #file_content is 'str'
fileobj.close()

#1.Calculate main datas

#split files
header={}
cc=[]
lsplit=split('\n+',file_content)
for i in range(len(lsplit)):
    if (lsplit[i]=='--'):
        for j in range(i):
            line_split=lsplit[j].split('=')
            header[line_split[0]]=line_split[1] #0 ~ i-1
        cc=lsplit[i:] # i ~ end
        break

#Suppose that all ksh files ends with '--\n\n' (2 lines with sign of the tune empty)
tuneindex=[i for i, line in enumerate(cc) if line=='--'] #ith: first line number at ith tune
tunesize=[tuneindex[i+1]-tuneindex[i] for i in range(len(tuneindex)-1)]
tune_total=len(tunesize)
infoline=[]
BPMidx=[]
beatidx=[]
for tune in range(tune_total):
    infoline.append([])
    BPMidx.append([])
    beatidx.append([])
    for i in range(tunesize[tune]):
        if '|' not in cc[tuneindex[tune]+i]:
            infoline[tune].append(i)
            if cc[tuneindex[tune]+i].split('=')[0]=='t':
                BPMidx[tune].append(i)
            if cc[tuneindex[tune]+i].split('=')[0]=='beat':
                beatidx[tune].append(i)
tune_den=[tunesize[tune]-len(infoline[tune]) for tune in range(tune_total)]

#Generate a file proceeded to current stage
def interim(stage):
    filename='f'+str(stage)
    filename=open("./ksh/"+str(stage)+"_"+
        argv[1].replace('./ksh/',''),"w",encoding="UTF-8-sig")
    for k, v in header.items():
        filename.write('{:s}={:s}'.format(k, v)+'\n')
    for tune in range(tune_total):
        for i in range(tunesize[tune]):
            if i==0:
                filename.write("#"+str(tune+1-1)+'-------\n')
            else:
                filename.write(cc[tuneindex[tune]+i]+'\n')
            #if tune!=tune_total-1 or i!=tunesize[tune]-1:
            #    filename.write('\n')
    filename.write("-------")
    filename.close()

#add the division mark at the end of every noteline 
def mark(chara):
    for tune in range(tune_total):
        for i in range(tunesize[tune]):
            if i not in infoline[tune]:
                cc[tuneindex[tune]+i]+=chara

#interim(1)

#2. DetermineKnobType
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
                elif 1/((coloncount+1)/tune_den[tune])==32: #slam knob
                    newknob+='#'*coloncount 
                else: #active line knob
                    newknob+=':'*coloncount 
            newknob+=line[LorR]
            prev=line[LorR]
            coloncount=0
    newknoblist.append(newknob)

#replace
i_note=0
for i in range(len(cc)):
    listline=list(cc[i])
    if '|' in cc[i]: #noteline
        for LorR in range(8,10):
            listline[LorR]=newknoblist[LorR-8][i_note]
        i_note+=1
    cc[i]=''.join(listline)

mark(',')
#duplicate
for tune in range(tune_total):
    for i in range(tunesize[tune]):
        if i not in infoline[tune]:
            cc[tuneindex[tune]+i]+=cc[tuneindex[tune]+i][8:10]


#interim(2)

#3. CalculateKnobSpinQuantity
knobcode='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmno'

#only for scaling
#(knob_diff / tune_total)*KNOB_SCALING = spin per tune 
#default:1  
KNOB_SCALING=1*4

#Suppose that need to spin 1/8 of field width to hit rect knob
#between 1/5 to 1/10 with the simulation
CHOKKAKU=(len(knobcode)-1)/6

#float number format settings
#this is only for good-looking, no effect on difficulty element values 
#default: DECIMAL_KNOB = 2
DECIMAL_KNOB='.0001'
INTEGER_KNOB=str((len(knobcode)-1)*KNOB_SCALING)
DIGIT_KNOB=len('-') + len(INTEGER_KNOB) + len(DECIMAL_KNOB)

#튠 및 BPM은 상관없다. 노브가 차지하고 있는 beat의 값이 중요할 뿐
newknoblist=[]
for LorR in range(8,10):
    # possible sign list: knobcode, - :" #
    beats_per_tune=4.0
    newknob=[] #list of float numbers
    prev='-'
    colon_count=[0] #not to delete last one element of the list
    rect_switch=0
    beat_fraction=[]  
    for tune in range(tune_total): #initialization is so much critical      #automatically initialized yay
        if len(beatidx[tune]):
            beats_fraction=[int(cc[tuneindex[tune]+
            beatidx[tune][0]].split('=')[1].split('/')[i]) for i in range(2)]
            beats_per_tune=float(beats_fraction[0]/beats_fraction[1])*4
        for i in range(tunesize[tune]):
            line=cc[tuneindex[tune]+i]
            if i not in infoline[tune]:
                if line[LorR]=='-': #'right before a knob starts' or 'right after a knob ends'
                    prev='-'
                    newknob.append(' '*DIGIT_KNOB)
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
                            fraction=beats_per_tune*(colon_count[j]/tune_den[tune-(len(colon_count)-1)+j])
                            beat_fraction.append(fraction)
                        #calculate knob_diff
                        knob_diff=knobcode.index(line[LorR])-knobcode.index(prev)
                        if rect_switch:
                            sign=lambda x: (1,-1)[x<0]
                            knob_diff=sign(knob_diff)*CHOKKAKU
                            rect_switch=0
                        #calculate the amount of spin in each line
                        knob_diff*=KNOB_SCALING
                        for j in range(len(colon_count)):
                            knob_ratio=beat_fraction[j]/sum(beat_fraction)
                            remain=knob_ratio*knob_diff
                            for k in range(colon_count[j]): #special method to calculate float value to reduce decimal value loss
                                if knob_diff:
                                    spin_delta='{:{width}.{point}f}'.format(float(Decimal(
                                    str(remain/(colon_count[j]-k))).quantize(Decimal(DECIMAL_KNOB), 
                                    ROUND_HALF_UP)), width=DIGIT_KNOB, point=len(DECIMAL_KNOB)-1)
                                    remain-=remain/(colon_count[j]-k)
                                else: #stayknob
                                    spin_delta=' '*DIGIT_KNOB
                                newknob.append(spin_delta) 
                        #clean up
                        colon_count=[0]
                        beat_fraction=[]
                    else: #Start of the knob
                        newknob.append(' '*DIGIT_KNOB)
                    prev=line[LorR]
        if colon_count!=[0]: #toss
            colon_count.append(0)
    newknoblist.append(newknob.copy())

#add newknob to chart
i_note=0
for i in range(len(cc)):
    if '|' in cc[i]: #noteline
        for LorR in range(8,10):
            if LorR==8:
                cc[i]+=','+newknoblist[LorR-8][i_note]
            else:
                cc[i]+=' '+newknoblist[LorR-8][i_note]
        i_note+=1

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

prev_next=['-']*2
Nullity=0
for tune in range(tune_total):
    for i in range(tunesize[tune]):
        if i not in infoline[tune]:
            listline=list(cc[tuneindex[tune]+i][:10]) #1111|00|--
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
                    # 0##a: 'LR' (1st prior)
                    # 0::a: 'lr' (2nd prior)
                    # 0""a: '  '   
                    # ----: '  '
                    free=0
                    capital=False
                    if listline[hand]=='#':
                        capital=True
                    #determine letter is whether a tip of stayknob or rectknob
                    if listline[hand] in knobcode:
                        line_offset=1
                        tune_offset=0
                        idx=tuneindex[tune]+i
                        while True: #next knob 
                            if idx+line_offset >= tuneindex[(tune+1)+tune_offset]:
                                tune_offset+=1
                            else: pass
                            if idx+line_offset-tuneindex[tune+tune_offset] in infoline[tune+tune_offset]:
                                line_offset+=1
                            else: break
                        prev_next[hand-8]+=cc[idx+line_offset][hand]
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
                                Nullity+=1
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
                                Nullity+=1
                            holdon[BTFX.index(hand)]=1
                            holdside[BTFX.index(hand)]=listline[hand]
                    else:
                        listline[hand]=' '
                hand=(hand+1)%10
            cc[tuneindex[tune]+i]=''.join(listline+list(cc[tuneindex[tune]+i][10:]))

if Nullity:
    print("Null detected! Nullity: ", Nullity)

#interim(4)

#5.CalculateHoldDecayed (with lowercase of LR and timing)
# total holding(holdcount) function: y=a*x^b (x: time), (a>0, 0<b<=1)    #put it at front 
#홀드 중간에 BPM이 바뀌면. ->상관없음

#The bigger HOLD_DECAY_EXP, the faster holding decays.
#default:2, range: HOLD_DECAY_EXP>=1    #argv[x] soon
HOLD_DECAY_EXP=2

#Set hold tick value per one beat
#1.5 or 1, or else
#Currently 1.5 holdtick per one (tune)beat
HOLD_TICK_PER_ONE_BEAT=3/2

#scaling: 홀드 비트 수 뻥튀기 방지
#scaling: Make sure the number of beats is limited in 9 ~ 16 in each tune except empty tune
#if beats are too much to its original BPM (ex. 32beats), scales BPM up to double (ex. EMPIRE OF FLAME)
#similarly, if beats are too less to its origianl BPM (ex. 4beats), scales BPM down to half (ex. CHOU CHOU KOU SOKU)
#example: BPM 999 with 4 beats per tune --> BPM 249.75 with 16 beats per tune 
#         BPM 114 with 32 beats per tune --> BPM 228 with 16 beats per tune
#         BPM 161 with 32 beats per tune --> BPM 322 with 16 beats per tune
#knobs don't affect at counting beats, because this is only for holdtick
#if BPM is scaled down, duration per one beat increased, which means the amount of hold beats(holding) is decreased. v.v.
#this scaling is only for calculating holdtick, but possible to expand this idea to other stage

"""
def holdbeat(lower, upper, scaling=1):
    holdtick_integral=lambda time: HOLD_TICK_PER_ONE_BEAT*(
        BPM*scaling/60)**(1/HOLD_DECAY_EXP)*time**(1/HOLD_DECAY_EXP)
    return holdtick_integral(upper)-holdtick_integral(lower)
"""
def holdbeat(lower, upper, scaling=1):
    holdbeat_integral=lambda ith_beat: HOLD_TICK_PER_ONE_BEAT*(ith_beat*scaling)**(1/HOLD_DECAY_EXP)
    return holdbeat_integral(upper)-holdbeat_integral(lower)

#beat_scaling=[1]*tune_total
beat_scaling=[]
#scaling
        #scaling
        #정직하게 4비트면 16비트로 뻥튀기
        #노브덕에 16비트 먹었는지 등을 확인
        #노트쪽 영역 스캔.
        # all(), cc[tuneindex[tune]+i][:10] == '0000|00|00'
        #노브도 반영할지 말지는 후에 결정 
        # --> 만약 한다면 돌리는 방향 전환을 하나의 beat로 삼는건데 잘 안드러날듯
for tune in range(tune_total):
    beats_list=[]
    for i in range(tunesize[tune]):
        if i not in infoline[tune]:
            if cc[tuneindex[tune]+i][:8]=='    |  |':
                beats_list.append(0)
            else:
                beats_list.append(1)


#Since each chart column are independent to each other, loop it each other
mark(',')
DECIMAL_HOLD='.001'
beats_per_tune=4.0
for hand in BTFX:
    holdcount=0.0
    for tune in range(tune_total):
        if len(beatidx[tune]):
            beats_fraction=[int(cc[tuneindex[tune]+
            beatidx[tune][0]].split('=')[1].split('/')[i]) for i in range(2)]
            beats_per_tune=float(beats_fraction[0]/beats_fraction[1])*4
        for i in range(tunesize[tune]):
            if i not in infoline[tune]:
                if cc[tuneindex[tune]+i][hand] in 'lr': # hold
                    lower=holdcount
                    upper=lower+beats_per_tune/tune_den[tune]
                    cc[tuneindex[tune]+i]+='{:{width}.{point}f}'.format(
                        float(Decimal(str(holdbeat(
                        lower, upper, beat_scaling[tune]))).quantize(Decimal(DECIMAL_HOLD), ROUND_HALF_UP)), 
                        width=len('1')+len(DECIMAL_HOLD), point=len(DECIMAL_HOLD)-1)
                    holdcount=upper
                else:
                    holdcount=0.0
                    cc[tuneindex[tune]+i]+=' '*(len('1')+len(DECIMAL_HOLD))
    mark(' ') if BTFX.index(hand)!=len(BTFX)-1 else mark(',')


"""
#Since each chart column are independent to each other, loop it each other
DECIMAL_HOLD='.001'
holdtime=0.0 #holdtime must be able to remain after tunes end
prev_timing=0.0
for hand in BTFX:
    for tune in range(tune_total):
        for i in range(tunesize[tune]):
            #infoline - find BPM change
            if i in infoline[tune]:
                if i in BPMidx:
                    
            else: #noteline
                timing=float(cc[tuneindex[tune]+i].split(',')[4])
                #check and update holdon switch for every noteline
                if holdtime:
                    if cc[tuneindex[tune]+i][hand] not in 'lr': #not hold
                        holdtime=0.0

                if cc[tuneindex[tune]+i][hand] in 'lr': #hold
                    lower=holdtime
                    upper=lower+(timing-prev_timing)
                    

                    cc[tuneindex[tune]+i]+=','+'{: {width}.{point}f}'.format(
                    float(Decimal(str(holdtick(lower, upper, scaling))).quantize(
                        Decimal(DECIMAL_HOLD), ROUND_HALF_UP)),
                        width=len('30')+len(DECIMAL_HOLD), point=len(DECIMAL_HOLD)-1) #guess max holdtick~=30 or 2 digits
                    holdtime+=upper-lower
                    prev_timing=timing
"""

#interim(5)

#6.CalculateHandCoordinates 
#xy_list=[
#[-729,162],[-243,162],[243,162],[729,162],
#[-481,-326],[481,-326],
#[-1133,598],[1133,598],[0,650]]
#4 BTs, 2 FXes, 2 knobs, start

#6.CalculateHandCoordinates (center of the active buttons and knobs)
#6-1.CalculateHandDistance (calculation result locates at latter point)
#노브 돌리는양 계산하듯이.
#왼손, 오른손에 대하여 for문 2번돌림 for each_hand in ['Ll','Rr']


#7.AddTiming (BPM and tune size(except info) matters)
#timing은 현재라인을 처리한 후의 시각
beats_per_tune=4.0
BPM=1 #Beats Per Minute
if '-' not in header['t']:
    BPM=int(header['t'])
duration=lambda BPM: 60*1000/BPM

DECIMAL_TIME='.001'
time=0.0
#tunetime=[] #list of lists of time portion(s) in each tune.
            #add new time portion for every BPM change happens
            #soon be deleted
for tune in range(tune_total):
    if len(beatidx[tune]):
        beats_fraction=[int(cc[tuneindex[tune]+
        beatidx[tune][0]].split('=')[1].split('/')[i]) for i in range(2)]
        beats_per_tune=float(beats_fraction[0]/beats_fraction[1])*4
    if len(BPMidx[tune]):
        no_BPM_change_at_start=any(i not in infoline[tune] for i in range(BPMidx[tune][0]))
        #if BPM no change from previous tune
        if no_BPM_change_at_start: 
            tune_num=0
            for j in range(BPMidx[tune][0]):
                if j not in infoline[tune]:
                    tune_num+=1
            time_unit=duration(BPM)*beats_per_tune*(1/tune_den[tune])
            i_note=0
            i_info=0
            while i_note!=tune_num:
                if i_note+i_info in infoline[tune]:
                    i_info+=1
                else:
                    time+=time_unit
                    cc[tuneindex[tune]+i_note+i_info]+='{:{width}.{point}f}'.format(float(Decimal(
                    str(time)).quantize(Decimal(DECIMAL_TIME), 
                    ROUND_HALF_UP)), width=len('120000')+len(DECIMAL_TIME), point=len(DECIMAL_TIME)-1)
                    i_note+=1

        for i in range(len(BPMidx[tune])):
            BPM=float(cc[tuneindex[tune]+BPMidx[tune][i]].split('=')[1])          
            if i<len(BPMidx[tune])-1:
                endpoint=BPMidx[tune][i+1]
            else:
                endpoint=tunesize[tune]
            tune_num=0
            for j in range(BPMidx[tune][i], endpoint):
                if j not in infoline[tune]:
                    tune_num+=1
            time_unit=duration(BPM)*beats_per_tune*(1/tune_den[tune])
            i_note=0
            i_info=0
            while i_note!=tune_num: #to reduce decimal value loss
                if BPMidx[tune][i]+i_note+i_info in infoline[tune]:
                    i_info+=1
                else:
                    time+=time_unit
                    cc[tuneindex[tune]+BPMidx[tune][i]+i_note+i_info]+='{:{width}.{point}f}'.format(
                    float(Decimal(str(time)).quantize(Decimal(DECIMAL_TIME), 
                    ROUND_HALF_UP)), width=len('120000')+len(DECIMAL_TIME), point=len(DECIMAL_TIME)-1)
                    i_note+=1
            #tunetime[tune].append(duration(BPM)*beats_per_tune*(tune_num/tune_den[tune]))
    else:
        time_unit=duration(BPM)*beats_per_tune/tune_den[tune]
        i_note=0
        i_info=0
        while i_note!=tune_den[tune]: #to reduce decimal value loss
            if i_note+i_info in infoline[tune]:
                i_info+=1
            else:
                time+=time_unit
                cc[tuneindex[tune]+i_note+i_info]+='{:{width}.{point}f}'.format(
                float(Decimal(str(time)).quantize(Decimal(DECIMAL_TIME), 
                ROUND_HALF_UP)), width=len('120000')+len(DECIMAL_TIME), point=len(DECIMAL_TIME)-1)
                i_note+=1
        #tunetime[tune].append(duration(BPM)*beats_per_tune)

"""
for tune in range(tune_total):
    for i in range(tunesize[tune]):
        #find BPM change
        if i in infoline[tune]:
            if i in BPMidx:
                BPM=float(cc[tuneindex[tune]+i].split('=')[1])
        else:
            time+=duration(BPM)/tune_den[tune]
            cc[tuneindex[tune]+i]+=','+'{: {width}.{point}f}'.format(
            float(Decimal(str(time)).quantize(Decimal(DECIMAL_TIME), ROUND_HALF_UP)),
            width=len('120000')+len(DECIMAL_TIME), point=len(DECIMAL_TIME)-1) #120000ms==120sec
"""

interim(7)

#11.CalculateDensity 
#노브와 노트 동시에 처리하는거에 가중치 or 손이동 쪽에서 가중치를 줘야하려나

#후에 learning 돌릴때
#모델 구조, '3차'
# 1. 모델 식 그자체. 어떤 식을 쓸건지
# 2. 값 도출하는데 있어 사용된 상수들 (hold decay log coefficient, interval length, etc.)
# 3. 본격적 식 내 weight