import numpy as np

FILENAME="007-1"
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

f2.print("트릴: ")

trlchk1=[0,0,0,0,0,0,0,0,0] #트릴 첫번째 모양
trlchk2=[0,0,0,0,0,0,0,0,0] #트릴 두번째 모양

def lstand(p,q): ##둘다존재
    retv=[]
    for i in range(9):
        retv.append(p[i]&q[i])
    return retv


def printtrill(l1, l2, v):
    
    f2.print("".join(l1) + " 하고 " + "".join(l2) " 트릴이 " + str(v) "회 반복된다\n") 


loopcnt=0

for loop1 in range(len(data)):
    tmp=txt2lst(loop1)
    whichone=loop1%2 ##두개로 나누기 위함
    if whichone==0:
        trltmp=lstand(trlchk1,tmp) # 전전 데이터와 비교
        ##0이 아닐 경우는 개수 계속 체크
        ##0일 경우는 트릴체크 끝내고 다시 시작
        if sum(trltmp)==0:
            if loopcnt>=4:
                printtrill(trlchk1, trlchk2, loopcnt)    
            loopcnt=0
            trlchk1=tmp
        else:
            loopcnt+=1
            
    else:
        trltmp=lstand(trlchk2,tmp)
        if sum(trltmp)==0:
            print(loopcnt)
            loopcnt=0
            trlchk2=tmp
        else:

''' #오류발견으로 작업 스탑
    




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
