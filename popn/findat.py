import numpy as np

FILENAME="004-1"
BPM=165

f=open(FILENAME+".txt","r")
f2=open(FILENAME+"-at.txt","w+")



data=f.readlines()
datatime=[]


##시간 읽기

def findtime(a):
    retv=0
    for i in range(10,len(a)-1):
        retv*=10
        retv+=int(a[i])
    return retv

for i in range(len(data)):
    datatime.append(findtime(data[i])) ##datatime 각 줄 시간 저장



##처리용

def txt2lst(a):
    retv=[]
    for i in range(9):
        if data[a][i]!='0':
            retv.append(1)
        else:
            retv.append(0)
    return retv

def lstand(p,q): ##둘다존재
    retv=[]
    for i in range(9):
        retv.append(p[i]&q[i])
    return retv


##트릴##

'''
1)정박트릴
2)변박트릴
전부 고려해야됨. (난이도요소)


알고리즘:
예시: 004.png

1. (1,2) (1,3) .... (7,9) (8,9) 의 라인만 체크한다
2. 두 개가 반복될시 일단 트릴 속성 간주

2-1. 123/456과 135/246의 트릴같은 경우 다른 속성으로 간주


'''

trilltable=[[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]]
#ㄴ 트릴체크후 시간저장용. 사실상 0간격의 트릴은 존재X

trill1=0 #트릴체크1
trill2=1 #트릴체크2


for trill1 in range(9):
    for trill2 in range(9):
        if trill1==trill2: #같은건 배제
            continue
        timeval=0 #시간간격 체크용 (트릴 중간에 다른노트 데이터가 있어도 트릴 간주)
        notecnt=0 # 4 이상시 트릴
        for loop in range(len(data)):
            timeval+=datatime[loop] #다음노트까지 걸린시간 (노트발견시 초기화)
            if timeval > 10: #10 내에 없으면 (임의의 값)
                if notecnt>=4: #4번 이상(트릴)이후 없는거면
                    tmpval=trilltable[trill1][trill2]
                    if tmpval>=4: #기존에 그트릴이 있다면
                        trilltable[trill1][trill2]+=notecnt #더함 (1212 트릴치다 쉬다 1212트릴나오면 일단은 연속 간주. ###추후 의견나눌예정)
                    else: #없다면 (노트 하나, 두개같이 작은거)
                        trilltable[trill1][trill2]=notecnt #트릴사이즈
                notecnt=0 #지금까지 센거 초기화
                timeval=0
            if notecnt%2==0: #트릴1
                if data[loop][trill1]!='0' and timeval < 10: #10 내에 치면 (임의의 값, 수정예정)
                    timeval=0 #시간간격초기화 (다음노트찾기 시작)
                    notecnt+=1 #노트수 추가
                else:
                    continue #loop 계속돔
            else: #트릴2
                if data[loop][trill2]!='0' and timeval < 10:
                    timeval=0
                    notecnt+=1
                else:
                    continue
        #loop이 끝남
        tmpval2=trilltable[trill1][trill2]
        if tmpval2>=4: #기존에 그트릴이 있다면
            trilltable[trill1][trill2]+=notecnt #더함 (1212 트릴치다 쉬다 1212트릴나오면 일단은 연속 간주. ###추후 의견나눌예정)
        else: #없다면 (노트 하나, 두개같이 작은거)
            trilltable[trill1][trill2]=notecnt #트릴사이즈
                
#트릴table에 저장이 끝난 후엔
for loop1 in range(9):
    for loop2 in range(9):
        if trilltable[loop1][loop2]>=4: #트릴사이즈
            whichbig=trilltable[loop1][loop2] #뭐가 더 크냐 (535353트릴의 경우 5 기준이며 6개짜리 3 기준이면 5개짜리 판별)
            if whichbig<trilltable[loop2][loop1]:
                whichbig=trilltable[loop2][loop1]
            f2.write("트릴\n"+str(loop1)+','+str(loop2)+'번 트릴이 '+str(whichbig)+'번만큼 반복\n')
            trilltable[loop1][loop2]=trilltable[loop2][loop1]=0





##계단##


## 만약 13-2-13-2같은 트릴이 아니라면 -> 트릴 데이터만 따로 리스트에서 삭제 후 처리 필요 (트릴 짠 후)


datacpy=[] #복사해서 겹치는건 지우는식으로 계단 배제 예정. (예: X자에서 한 팔만 빠진 계단)
for i in range(len(data)):
    datacpy.append(txt2lst(i))




'''알고리즘:
O(n^2)
시작위치 계속 바꿔가며 for문돌림

1) 첫 번째 나온 노트들부터 수직으로 돌림
1-1) (1,3,9동타일경우 1로 계단 삭제하고 3 계단 삭제 후 9 계단도 삭제)
2) 삭제가 더 안될때 수평길이 3 이상일경우 계단 저장

'''

stairlen=datacpy[0]
stairheight=0

def findnext(a,b):
    pass


#예시: 1 4 5 6 7 6 5 4의 경우 1이 계속 저장되어있다 어느 순간 삭제됨


loop=0
while loop<len(data): #모든 노트가 삭제될때까지 반복
    stairwidth=[0,0,0,0,0,0,0,0,0] #트릴배제용
    stairheight=1 #이중 while 계산용
    stairstart=-1 # 시작위치 찾기 (아래for)
    for looptmp in range(9):
        if datacpy[loop][looptmp]==1:
            stairstart=looptmp
            stairwidth[looptmp]=1
            datacpy[loop][looptmp]=0
            break
    if stairstart==-1: #전부 지워졌으면 or 없으면
        loop+=1
        continue

    timecnt=datatime[loop] #다음노트까지시간
    if timecnt>20: #너무 길면
        continue #그냥 반복문 계속반복함
    stairtime=datatime[loop] #계단 시간 합산

    #두 번째 loop는 다음 노트 계속 찾다가 시간 이상 안나오면 끝냄
    for loop2 in range(loop+1,len(data)):
        if stairstart==0: #1노트
            if datacpy[loop2][1]==1:
                stairstart=1 #손은 2번에 왔고
                timecnt=datatime[loop2] #시간은 초기화고
                stairtime+=datatime[loop2] #계단패턴시간
                stairwidth[1]=1 #계단가로
                stairheight+=1 #계단세로
                datacpy[loop2][1]=0 #중복방지
            else: #아니라면
                timecnt+=datatime[loop2] #시간추가
                stairtime+=datatime[loop2]
                if timecnt>20: #특정 값 (추후 계산필요) 넘으면
                    break #뒤도보지않고 break

                
        elif stairstart==8: #9노트
            if datacpy[loop2][7]==1:
                stairstart=7 #손은 8번에 왔고
                timecnt=datatime[loop2] #시간은 초기화고
                stairtime+=datatime[loop2] #계단패턴시간
                stairwidth[7]=1 #계단가로
                stairheight+=1 #계단세로
                datacpy[loop2][7]=0 #중복방지
            else: #아니라면
                timecnt+=datatime[loop2] #시간추가
                stairtime+=datatime[loop2]
                if timecnt>20: #특정 값 (추후 계산필요) 넘으면
                    break #뒤도보지않고 break

                
        else: #2~8노트 (좌우 비교 fault 방지)
            if datacpy[loop2][stairstart-1]==1: #왼쪽
                stairstart-=1 #손은 왼쪽에 갔고
                timecnt=datatime[loop2] #시간은 초기화고
                stairtime+=datatime[loop2] #계단패턴시간
                stairwidth[stairstart]=1 #계단가로
                stairheight+=1 #계단세로
                datacpy[loop2][stairstart]=0 #중복방지
            elif datacpy[loop2][stairstart+1]==1: #오른쪽
                stairstart+=1 #손은 오른쪽에 갔고
                timecnt=datatime[loop2] #시간은 초기화고
                stairtime+=datatime[loop2] #계단패턴시간
                stairwidth[stairstart]=1 #계단가로
                stairheight+=1 #계단세로
                datacpy[loop2][stairstart]=0 #중복방지
            else: #아니라면
                timecnt+=datatime[loop2] #시간추가
                stairtime+=datatime[loop2]
                if timecnt>20: #특정 값 (추후 계산필요) 넘으면
                    break #뒤도보지않고 break

    if sum(stairwidth)>=3:
        f2.write("계단\n시간: "+str(stairtime)+"\n좌우길이: "+str(sum(stairwidth))+"\n개수: "+str(stairheight))
    





f.close()
f2.close()
