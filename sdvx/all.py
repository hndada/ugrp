#노브에서 매번 손이동 한것으로 계산됨
#변박곡 에러

#구분선 재정의 ('|') #hold_decayed, knob_quantity 0은 zero로.

#Nullity 나왔을 때 대처 (3-1에서 앞서 감지)
#1.홀드면 --> 홀드를 한손으로.
#2.노트면 --> 노브 보정 등을 기대하여 노브 조작 X

#weight, factor 모아보기

#노브방향 바뀔때 strain 추가 with gradient
"""
앞 노브 전체 회전량의 절반
(직각이면 상수의 0.75배)
직각 duration만큼에 대하여 선형분배 (duration보다 짧으면 첫 라인에 몰아넣기)
빈칸 존재하면 리셋
주차가 1박자 이상 존재하면 리셋 (튠넘어가는 경우 총합 박자)
"""

"""
1.Calculate main datas
2.DetermineKnobType (revised ver of ‘vol_change’)
3.CalculateKnobSpinQuantity (wow such hard)
(3-1.CheckSpecialPattern (sewing, duplex))
4.DetermineLR (advanced version of detLR.py)
5.CalculateHoldDecayed (with lowercase of LR and beats)
6.CalculateHandCoordinates (center of the active buttons and knobs)
6-1.CalculateMovement (calculation result locates at latter point)
7.(CalculateBPMratio)
8.AddTiming (BPM and tune size(except info) matters)
9.DivideToInterval (cut the chart every 400ms except chart info; no use since this stage)
(10.CalculateDifficultyFactor)
10-1.CalculateDensity (thanks to same interval size, just sum up chip and hold_decayed plus knob_quantity) (but for precise decision, divide by its unique duration time)
10-2.CalculateHandMoveSpeed (thanks to same interval size, just sum amount hand distance)
10-3.(CalculateLegibility)
11.run for all charts and output automatically
"""

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

from sys import argv
from re import split
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction
import math
import numpy as np
import csv
"""
from os import listdir
from os.path import isfile, join
"""
import os

kshfiles=[]
for (path, dir, files) in os.walk(argv[1]):
    for filename in files:
        ext = os.path.splitext(filename)[-1]
        if ext == '.ksh':
            kshfiles.append(path+'/'+filename)

#onlyfiles = [f for f in listdir(argv[1]) if isfile(join(argv[1], f))]
#go to very front
w=[0.8, 0.1, .05, .5] #weight list
difficulty_order=open(argv[1]+'/difficulty_order.csv',"w",encoding="UTF-8-sig", newline='')
wr2=csv.writer(difficulty_order)

wr2.writerow(["weight:", w])
wr2.writerow(["song name.", "difficulty name", "level", "calculated level"])

for ksh in range(len(kshfiles)):

    fileobj=open(kshfiles[ksh],'rt', encoding='UTF-8-sig')
    file_content=fileobj.read()#file_content is 'str'
    fileobj.close()

    #1.Calculate main datas
    #split files
    ZERO_TO_BLANK=0 #make sure run the code before 'CalculateDifficultyFactor' only if this switch is activated
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

    print("Processing", header['title'], header['difficulty'], "...")

    #Suppose that all ksh files ends with '--\n\n' (2 lines with sign of the tune empty)
    tuneindex=[i for i, line in enumerate(cc) if line=='--'] #ith: first line number at ith tune
    tunesize=[tuneindex[i+1]-tuneindex[i] for i in range(len(tuneindex)-1)]
    tune_total=len(tunesize)
    infoline=[]
    BPMidx=[]
    tunebeat=[]
    up_to_date_beat=4.0
    for tune in range(tune_total):
        infoline.append([])
        BPMidx.append([])
        for i in range(tunesize[tune]):
            if '|' not in cc[tuneindex[tune]+i]:
                infoline[tune].append(i)
                if cc[tuneindex[tune]+i].split('=')[0]=='t':
                    BPMidx[tune].append(i)
                if cc[tuneindex[tune]+i].split('=')[0]=='beat':
                    beats_fraction=[int(cc[tuneindex[tune]+i    
                    ].split('=')[1].split('/')[j]) for j in range(2)]
                    up_to_date_beat=float(beats_fraction[0]/beats_fraction[1])*4
        tunebeat.append(up_to_date_beat)
    tune_den=[tunesize[tune]-len(infoline[tune]) for tune in range(tune_total)]
    
    #temporary continue
    if any([len(BPMidx[i]) for i in range(len(BPMidx))]):
        continue


    #Generate a file proceeded to current stage
    """
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
    """

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
                    elif (coloncount+1)/(tune_den[tune]/tunebeat[tune])==1/8: #slam knob
                        #this condition could not cover the case:
                        #slam knob spread over 2 tunes which tune_den is not same
                        #but the case is too rare to affect difficulty
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
    #( knob_diff / beats_amount ) * KNOB_SCALING = spin per beats
    knobcode='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmno'
    KNOB_SCALING=1

    #slam knob has critical spin amount to be hit
    #between 1/5 to 1/10 of field width by simulation
    #practically, beginners aren't aware it
    CHOKKAKU_CRITICAL=0.15
    if header['difficulty']=='light': 
        CHOKKAKU_CRITICAL=0.75
    elif header['difficulty']=='challenge':
        CHOKKAKU_CRITICAL=0.5
    CHOKKAKU=(len(knobcode)-1)*CHOKKAKU_CRITICAL

    def floatinfo(obj_type):
        #no effect on calculating difficulty values
        if obj_type=='KNOB':
            point='.0001'
            width=len('-')+len(str((len(knobcode)-1)*KNOB_SCALING))+len(point)
            #sign, integer, decimal
        elif obj_type=='HOLD':
            point='.001'
            width=len('1')+len(point)
        elif obj_type=='TIME':
            point='.001'
            width=len('120000')+len(point)
        elif obj_type=='HAND':
            point='.001'
            width=len('10')+len(point)
        return point, width

    def floatformat(value, obj_type):
        point, width = floatinfo(obj_type)
        if value or not ZERO_TO_BLANK:
            dec=Decimal(value).quantize(Decimal(point), ROUND_HALF_UP)
            return '{:{w}.{p}f}'.format(float(dec), w=width, p=len(point)-1)
        else:
            return '{:{w}}'.format(' ', w=width)
    newknoblist=[]
    for LorR in range(8,10):
        # possible sign list: knobcode, - :" #
        newknob=[] #list of float numbers
        prev='-'
        colon_count=[0] #not to delete last one element of the list
        slam_switch=0
        beat_fraction=[]  
        for tune in range(tune_total):
            beats_per_tune=tunebeat[tune]
            for i in range(tunesize[tune]):
                line=cc[tuneindex[tune]+i]
                if i not in infoline[tune]:
                    if line[LorR]=='-': #including 'right before a knob starts' or 'right after a knob ends'
                        prev='-'
                        newknob.append(0.0)
                    elif line[LorR] in ':"#':
                        colon_count[-1]+=1
                        if line[LorR]=='#':
                            slam_switch=1 

                    else: #The letter
                        if prev!='-': #End of the knob
                            #"no" add for last unit
                            #colon_count[-1]+=1 

                            #make exact number of space to each tune
                            for j in range(len(colon_count)):
                                fraction=beats_per_tune*(colon_count[j]/tune_den[tune-(len(colon_count)-1)+j])
                                beat_fraction.append(fraction)
                            #calculate knob_diff
                            knob_diff=knobcode.index(line[LorR])-knobcode.index(prev)
                            if slam_switch:
                                sign=lambda x: (1,-1)[x<0]
                                knob_diff=sign(knob_diff)*CHOKKAKU
                                slam_switch=0
                            #calculate the amount of spin in each line
                            knob_diff*=KNOB_SCALING
                            for j in range(len(colon_count)):
                                knob_ratio=beat_fraction[j]/sum(beat_fraction)
                                remain=knob_ratio*knob_diff
                                for k in range(colon_count[j]): #special calculate method to reduce value loss
                                    spin_per_line=remain/(colon_count[j]-k)
                                    remain-=spin_per_line
                                    newknob.append(spin_per_line)
                            #get next knob (duplicated)
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
                            #clean up (re-initializing)
                            if cc[idx+line_offset][LorR] in '-"': #true end of knob
                                colon_count=[0]
                                newknob.append(0.0)
                            else:
                                colon_count=[1]
                            beat_fraction=[]
                        else: #Start of the knob
                            colon_count[-1]+=1
                            #newknob.append(' '*floatinfo('KNOB')[1])
                        prev=line[LorR]
            if colon_count!=[0]: #toss
                colon_count.append(0)
        newknoblist.append(newknob.copy())

    #add newknob to chart
    i_note=0
    for i in range(len(cc)):
        if '|' in cc[i]: #noteline
            for LorR in range(8,10):
                cc[i]+=',' if LorR==8 else ' ' #'/'
                cc[i]+=floatformat(newknoblist[LorR-8][i_note],'KNOB')
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
    knobon=[0]*2 #check if the knob is already on(active)
    knobside=['N']*2
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

    hold_begin=[] #for one of progress in No.5 stage: determine actual BPM
    prev_next=['-']*2
    Nullity_BTFX_while_all_KNOB_on=0
    for tune in range(tune_total):
        hold_begin.append([])
        for i in range(tunesize[tune]):
            hold_begin_line=[0]*6 #only this list has element of infoline; for compatibility to hold_decayed
            if i not in infoline[tune]:
                listline=list(cc[tuneindex[tune]+i][:10]) #1111|00|--
                #check the switches
                if any([holdon[x] for x in range(len(holdon))]):
                    for j in range(len(BTFX)):
                        if listline[BTFX[j]]!=check_code('hold',BTFX[j]):
                            holdon[j]=0
                            holdside[j]='N'
                if any([knobon[x] for x in range(len(knobon))]):
                    for x in KNOB:
                        if listline[x] in '-"':
                            knobon[x-8]=0
                            knobside[x-8]='N'
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
                        #determine letter is whether a tip of stayknob or slamknob
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
                            knobon[hand-8]=1
                            knobside[hand-8]=listline[hand]
                        else:  #knob free
                            listline[hand]=' '
                            knobon[hand-8]=0
                            knobside[hand-8]='N'

                    if hand in BTFX:
                        capital=True
                        if listline[hand]!='0':                                
                            if listline[hand]==check_code('chip', hand):
                                if any(knobon):
                                    for j in range(len(knobon)):
                                        if knobon[j]: #if knob already exist
                                            listline[hand]=otherside(hand, knobside[j], capital)
                                            break
                                else:
                                    listline[hand]=side(hand, capital)
                                if ' ' not in listline[8:10]: #Nullity
                                    listline[hand]='N'
                                    Nullity_BTFX_while_all_KNOB_on+=1
                            elif listline[hand]==check_code('hold', hand):
                                capital=False
                                if any(knobon):
                                    for j in range(len(knobon)):
                                        if knobon[j]: #if knob already exist
                                            listline[hand]=otherside(hand, knobside[j], capital)
                                            break
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
                                    Nullity_BTFX_while_all_KNOB_on+=1
                                hold_begin_line[BTFX.index(hand)]=1 if holdon[BTFX.index(hand)]==0 else 0
                                holdon[BTFX.index(hand)]=1
                                holdside[BTFX.index(hand)]=listline[hand]
                        else:
                            listline[hand]=' '
                    hand=(hand+1)%10
                cc[tuneindex[tune]+i]=''.join(listline+list(cc[tuneindex[tune]+i][10:]))
            hold_begin[tune].append(hold_begin_line)

    if Nullity_BTFX_while_all_KNOB_on:
        continue
        #print("Nullity detected! Nullity_BTFX_while_all_KNOB_on: ", Nullity_BTFX_while_all_KNOB_on)

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

    def holdbeat(lower, upper):
        holdbeat_integral=lambda ith_beat: HOLD_TICK_PER_ONE_BEAT*ith_beat**(1/HOLD_DECAY_EXP)
        return holdbeat_integral(upper)-holdbeat_integral(lower)

    #scaling
        #knob doesn't count in this stage; only non-knob matters
        #default beats is '16beats per 4 beat-time(per 1 tune)'
        #possible to consider 'knob beat' with counting knob turnabout(knob direction switch)

    BPMscale=[]
    for tune in range(tune_total):
        BPMscale.append([])
        beats_per_tune=tunebeat[tune]
        divisor=[1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48]
        tune_fragment=lambda x: (1, math.modf(x)[0])[not math.modf(x)[1] and math.modf(x)[0]!=0] #has only decimal value
        if tune_den[tune]>=beats_per_tune:
            lines_stack=[]
            i_note=0
            i_info=0
            for i in range(tunesize[tune]):
                if i not in infoline[tune]:
                    i_note+=1
                    if i_note % (tune_den[tune]/beats_per_tune) == 1:
                        lines_stack.append(i)
            #calculate scaling for every beat time in a tune
            for ith_beat in range(math.ceil(beats_per_tune)): #2.25 -> 3 scans in total            
                lines_per_beat_full=tune_fragment(beats_per_tune-ith_beat)*tune_den[tune]/beats_per_tune
                skipped=0
                div=1
                #loop as much as possible
                for i in range(1, len(divisor)):
                    div=divisor[i]
                    lines_per_beat=lines_per_beat_full/div #start at "1 beat exists in one beat time"
                    if lines_per_beat<1:
                        div=divisor[i-1-skipped]
                        break
                    elif lines_per_beat!=int(lines_per_beat): #if lines_per_beat is float value - possible when messed with 6 and 8 beats
                        skipped=1
                        continue
                    beat_valid=[]
                    #if lines_per_beat_full/lines_per_beat!=int(lines_per_beat_full/lines_per_beat):
                    #    print("float decimal error occurred!")
                    for j in range(int(lines_per_beat_full/lines_per_beat)):
                        i_note=0
                        i_info=0
                        beat_invalid_switch=1
                        #if lines_per_beat!=int(lines_per_beat):
                        #    print("float decimal error occurred!")
                        while i_note!=lines_per_beat:
                            line_offset=lines_stack[ith_beat]+int(j*lines_per_beat)+i_note+i_info
                            #if j*lines_per_beat+i_note+i_info!=int(j*lines_per_beat+i_note+i_info):
                            #    print("float decimal error occurred!")
                            if line_offset not in infoline[tune]:
                                i_note+=1
                                line_part=cc[tuneindex[tune]+line_offset][:8] #'    |  |'
                                if ('L' in line_part) or ('R' in line_part) or any(
                                    hold_begin[tune][line_offset][k] for k in range(6)):
                                    beat_valid.append(1)
                                    beat_invalid_switch=0
                                    break
                            else:
                                i_info+=1
                        if beat_invalid_switch:
                            beat_valid.append(0)
                    if beat_valid.count(1)<=len(beat_valid)/2:
                        div=divisor[i-1-skipped]
                        break
                    else: #passed current divisor
                        skipped=0
                BPMscale[tune].append((1/4)*div) #currently scaling==1 when 4 beats exist in one beat time
        else: #tune_den[tune] < 4
            for ith_beat in range(math.ceil(beats_per_tune)):
                BPMscale[tune].append((1/4)*1)

    """
    for i in range(len(BPMscale)):
        print("tune:", i+1, end='  ')
        for j in range(len(BPMscale[i])):
            print(int(16*BPMscale[i][j]), end=' ')
        print()
    """
    mark(',')
    beats_per_tune=4.0
    for hand in BTFX:
        holdcount=0.0
        for tune in range(tune_total):
            beats_per_tune=tunebeat[tune]
            i_note=0
            i_info=0
            for i in range(tunesize[tune]):
                if i not in infoline[tune]:
                    if cc[tuneindex[tune]+i][hand] in 'lr': # hold
                        lower=holdcount
                        if tune_den[tune]>=beats_per_tune:
                            BPMscale_idx=math.floor(i_note/(tune_den[tune]/beats_per_tune))
                            upper=lower+(beats_per_tune*BPMscale[tune][BPMscale_idx])/tune_den[tune]
                        else:
                            upper=lower+beats_per_tune*(1/4)/tune_den[tune]
                        cc[tuneindex[tune]+i]+=floatformat(holdbeat(lower, upper), 'HOLD')
                        holdcount=upper
                    else:
                        holdcount=0.0
                        cc[tuneindex[tune]+i]+=floatformat(0.0, 'HOLD')
                    i_note+=1
                else: #infoline
                    i_info+=1
        if BTFX.index(hand)!=len(BTFX)-1:
            mark(' ')

    #interim(5)
    #6.CalculateHandCoordinates (center of the active buttons and knobs)
    #6-1.CalculateMovement (calculation result locates at latter point)
    #same format from knob quantity calculation

    #4 BTs, 2 FXes, 2 knobs, start
    xy=((-9,2),(-3,2),(3,2),(9,2),(-6,-4),(6,-4),(-14,7.5),(14,7.5),(0,8))
    def center(hand_queue):
        choice=list(set(hand_queue)) #remove duplicated element in center calculation (that is, no weight in multiple appearence)
        return np.average([xy[(BTFX+KNOB).index(choice[i])] for i in range(len(choice))], axis=0)

    def nearby(hand):
        if hand==0:
            return (0,1,2,5)
        if hand==3:
            return (1,2,3,6)
        if hand==1 or hand==2:
            return tuple(BTFX)
        if hand==5:
            BTFXcopy=BTFX.copy()
            BTFXcopy.remove(3)
            return tuple(BTFXcopy)
        if hand==6:
            BTFXcopy=BTFX.copy()
            BTFXcopy.remove(0)
            return tuple(BTFXcopy)
        if hand in [8,9]: #knob
            return (hand,) #only itself is nearby

    major_hand={'Ll':(0,1,5), 'Rr':(2,3,6)}
    major_center={LorR:center(major_hand[LorR]) for LorR in ['Ll', 'Rr']}

    HAND_SCALING=1
    Nullity_cannot_cover_with_one_hand=0 #can only be checked after LR determined
    distance_list=[]
    for LorR in ['Ll', 'Rr']:
        distance=[]
        hand_queue=[]
        center_point_prev=np.array([])
        center_point=major_center[LorR] #topologically same to 'knobcode'
        colon_count=[0] #not to delete last one element of the list
        beat_fraction=[]
        for tune in range(tune_total):
            beats_per_tune=tunebeat[tune]
            i_note=0
            i_info=0
            for i in range(tunesize[tune]):
                if i not in infoline[tune]: #calculate hand coordinates(location)
                    if any(LorR[x] in cc[tuneindex[tune]+i][:10] for x in range(2)): #using left or right hand in this line
                        Nullity_check=[]
                        handstill=[]
                        #update queue for every active line
                        for hand in [8,0,5,1,2,6,3,9]: #start with and end to obj which has lowest locality
                            if cc[tuneindex[tune]+i][hand] in LorR:
                                #not-a-beginning hold object: no put if already exist in queue, no colon_count reset
                                if hand in BTFX:
                                    if cc[tuneindex[tune]+i][hand] in 'lr' and not hold_begin[tune][i_note+i_info][BTFX.index(hand)]:
                                        handstill.append(True)
                                        if hand in hand_queue:
                                            continue
                                else: #no put same knob object in queue more than twice
                                    handstill.append(True)
                                    if hand in hand_queue: #there's no case that any BTFX appears when spinning knob 
                                        continue
                                if len(hand_queue)==4: #suppose each hand can press buttons up to 4
                                    del hand_queue[0]
                                if len(hand_queue) and hand not in nearby(hand_queue[-1]): #reset queue if new item is not nearby to before one
                                    hand_queue=[]
                                hand_queue.append(hand)
                                if not any(handstill):
                                    Nullity_check.append(hand)
                                    handstill.append(False)
                        
                        if all(handstill):
                            colon_count[-1]+=1
                            continue
                        #Nullity check
                        find=False
                        for j in range(len(Nullity_check)):
                            for k in range(len(Nullity_check)):
                                if any([Nullity_check[k] not in nearby(Nullity_check[j])]):
                                    find=True
                                    Nullity_cannot_cover_with_one_hand+=1
                                    break
                            if find: break #break double loop at once 

                        #calculate center_point
                        if all([hand_queue[j] in major_hand[LorR] for j in range(len(hand_queue))]):
                            center_point=major_center[LorR]
                        else:
                            center_point=center(hand_queue)

                        #whether hand location has changed or not, calculate distance in each line
                        if center_point_prev.size:
                            hand_dist=np.linalg.norm(center_point-center_point_prev)*HAND_SCALING
                        #before first noteline appeared
                        else: hand_dist=0.0
                        
                        #make exact number of space to each tune
                        for j in range(len(colon_count)):
                            fraction=beats_per_tune*(colon_count[j]/tune_den[tune-(len(colon_count)-1)+j])
                            beat_fraction.append(fraction)
                        
                        #calculate the amount of distance in each line
                        for j in range(len(colon_count)):
                            #temporary fixfix
                            if sum(beat_fraction)==0:
                                beat_fraction.append(0.25)
                            dist_ratio=beat_fraction[j]/sum(beat_fraction)
                            remain=dist_ratio*hand_dist
                            for k in range(colon_count[j]): #special calculate method to reduce value loss
                                dist_per_line=remain/(colon_count[j]-k)
                                #dist_delta=floatformat(dist_per_line, 'HAND')
                                remain-=dist_per_line
                                distance.append(dist_per_line)

                        # reset colon_count and update center_point_prev
                        colon_count=[1]
                        beat_fraction=[]
                        center_point_prev=center_point
                    else: #noteline but don't need current LorR
                        colon_count[-1]+=1
                    i_note+=1
                else: i_info+=1
            if tune==tune_total-1: #last noteline and after of it
                for j in range(len(colon_count)):
                    for k in range(colon_count[j]):
                        distance.append(0.0)
            elif colon_count!=[0]: #toss
                colon_count.append(0)
        distance_list.append(distance)

    #print(len(distance_list[1]),sum([tune_den[tune] for tune in range(tune_total)]))
    #add hand distance amount to chart
    i_note=0
    for i in range(len(cc)):
        if '|' in cc[i]: #noteline
            for LorR in range(2):
                cc[i]+=',' if LorR==0 else ' '
                cc[i]+=floatformat(distance_list[LorR][i_note], 'HAND')
            i_note+=1

    if Nullity_cannot_cover_with_one_hand:
        print("Nullity detected! Nullity_cannot_cover_with_one_hand: ", Nullity_cannot_cover_with_one_hand)

    #interim(6)
    #7.AddTiming (BPM and tune size(except info) matters)
    #9.DivideToInterval (cut the chart every 400ms except chart info; no use since this stage)
    #timing in each line indicates 'the time right after the line has passed'
    #새로운 interval마다 n번째, 시간 표시

    beats_per_tune=4.0
    BPM=1 #Beats Per Minute
    if '-' not in header['t']:
        BPM=float(header['t'])
    duration=lambda BPM: 60*1000/BPM
    time=0.0
    INTERVAL=400
    checkpoint=0.0
    section_index=[] #indice of first line of each section
    section_duration=[]
    def markup(idx):
        section_index.append(idx+1)
        offset=1
        while True:
            if '|' in cc[idx+offset]:
                offset+=1
            else: break
        cc[idx+offset]+=floatformat(time, 'TIME')
        cc[idx+offset]+='\tNo.'+str(len(section_index)-1) #+'('+str(int(time-checkpoint))+')'
        if idx!=-1: #except for very first idx
            section_duration.append(time-checkpoint)

    mark(',')
    #for markup first section
    markup(-1)
    for tune in range(tune_total):
        beats_per_tune=tunebeat[tune]
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
                        #if (time-checkpoint)>=INTERVAL: #possible to enhance the condition to allow less than INTERVAL
                        if time-len(section_index)*INTERVAL>=0:
                            markup(tuneindex[tune]+i_note+i_info)
                            checkpoint=time
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
                while i_note!=tune_num:
                    if BPMidx[tune][i]+i_note+i_info in infoline[tune]:
                        i_info+=1
                    else:
                        time+=time_unit
                        if time-len(section_index)*INTERVAL>=0: #possible to enhance the condition to allow less than INTERVAL
                            markup(tuneindex[tune]+BPMidx[tune][i]+i_note+i_info)
                            checkpoint=time
                        i_note+=1
        else:
            time_unit=duration(BPM)*beats_per_tune/tune_den[tune]
            i_note=0
            i_info=0
            while i_note!=tune_den[tune]:
                if i_note+i_info in infoline[tune]:
                    i_info+=1
                else:
                    time+=time_unit
                    if time-len(section_index)*INTERVAL>=0: #possible to enhance the condition to allow less than INTERVAL
                        markup(tuneindex[tune]+i_note+i_info)
                        checkpoint=time
                    i_note+=1

    section_size=[section_index[i+1]-section_index[i] for i in range(len(section_index)-1)]
    section_size.append(len(cc)-section_index[-1])

    #to wrap up last section
    section_duration.append(time-checkpoint)
    """
    offset=0
    while True:
        if '|' not in cc[len(cc)-1-offset]:
            offset+=1
        else:
            if section_index[-1]<len(cc)-1-offset:      
                break
    """
    #interim(7)
    #10.CalculateDifficultyFactor
    #CalculateDensity #CalculateHandMoveSpeed
    
    difficulty_score=[]
    for ith_sect in range(len(section_index)):
        #difficulty_score.append([])
        holdchip=[0,0] #for giving advantage of density bias in hands
        movement=0
        knobspin=0
        for i in range(section_size[ith_sect]):
            if '|' not in cc[section_index[ith_sect]+i]: #infoline
                continue
            line_split=cc[section_index[ith_sect]+i].split(',')
            #0:main  1:knob status  2:knob quantity  
            #3:hold_decayed  4:hand distance  5:time info
            for LorR in range(2):
                essence=line_split[0][:7]
                holdchip[LorR]+=essence.count('LR'[LorR]) #chip
                for hand in BTFX:
                    if essence[hand]=='lr'[LorR]: #hold
                        holdchip[LorR]+=float((line_split[3].split())[BTFX.index(hand)])
            movement+=sum(float(line_split[4].split()[j]) for j in range(len(line_split[4].split())))
            knobspin+=sum(abs(float(line_split[2].split()[j])) for j in range(len(line_split[2].split())))
        holdchip_sum=sum(holdchip)
        holdchip_sub=abs(holdchip[0]-holdchip[1])
        """
        for LorR in range(2):
            difficulty_score.append(holdchip[LorR]/section_duration[ith_sect])
        difficulty_score.append(movement/section_duration[ith_sect])
        difficulty_score.append(knobspin/section_duration[ith_sect])
        """
        difficulty_score.append(sum([holdchip_sum*w[0],holdchip_sub*w[1],movement*w[2],knobspin*w[3]]))
    difficulty_score_sorted=difficulty_score.copy()
    difficulty_score_sorted.sort(reverse=True)
    DECAY_FACTOR=0.9
    DIFFICULTY_SCALING=0.8
    difficulty_result=sum([difficulty_score[i]*DECAY_FACTOR**i for i in range(len(difficulty_score))])*DIFFICULTY_SCALING
    #print(header['title'], header['difficulty'], ": ", difficulty_result)

    """
    section_score=open("./ksh/"+"section_score_"+
        argv[1].replace('./ksh/','')+'.csv',"w",encoding="UTF-8-sig", newline='')
    wr1=csv.writer(section_score)
    wr1.writerow(["section No.", "section difficulty score", "decay weight", "weighted score"])
    for i in range(len(difficulty_score_sorted)):
        wr1.writerow([difficulty_score.index(difficulty_score_sorted[i]), 
        difficulty_score_sorted[i], DECAY_FACTOR**i, difficulty_score_sorted[i]*DECAY_FACTOR**i])
    """

    wr2.writerow([header['title'], header['difficulty'], header['level'], difficulty_result])
    #후에 learning 돌릴때
    #모델 구조, '3차'
    # 1. 모델 식 그자체. 어떤 식을 쓸건지
    # 2. 값 도출하는데 있어 사용된 상수들 (hold decay log coefficient, interval length, etc.)
    # 3. 본격적 식 내 weight