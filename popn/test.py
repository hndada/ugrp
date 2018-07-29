#SETUP

from PIL import Image
import numpy as np

BLOCK=48

FILENAME="016"

im=Image.open(FILENAME+'.png') # loop사용 데이터 read 가능
pix=np.array(im)
f=open(FILENAME+".txt","w+")


table_file=open("table.txt","r")


###흰,노,초,파,빨
###파,빨:흰선, 흰,노,초:검은선
'''
모든 흰색: 255 255 255
회색: 195 195 195
모든 검은색: 0 0 0
노란색: 255 255 0
초록: 128 255 128
파란색: 0 0 255
빨간색: 255 128 128

회색선(점선포함) n개 : 총 2(n+1)칸 // 편의성을 위해 간략화.
ㄴ스크린같은 예외사례도 대체적으로 이렇게 볼 수 있음. 선, 칸, 선, 칸 이렇게 보기 쉽게

'''

#table 정리
table=[]
table=table_file.readlines()




#RGB
def chkrgb(a,b,c,d):
    if (a[0]==b) and (a[1]==c) and (a[2]==d):
        return True
    return False


#

lines=9
blocks=len(pix)-3 #상하는 img랑 일치.


data=[] #blank data

for i in range(blocks):
    data.append([0,0,0,0,0,0,0,0,0])



#init

def cmplst(a,b):#compare list
    for i in range(len(a)):
        if a[i]!=b[i]:
            return False
    return True

def chkbt(a,b):
    cn=pix[a][b] #center
    up=pix[a+1][b]
    dn=pix[a-1][b]

    if (not cmplst(cn,up)) and (not cmplst(cn,dn)):
        return True
    return False



i1=8
i2=blocks-1
datai1=0
datai2=0

while i1<113: #loop 9회
    i2=blocks-1
    datai2=0
    while i2>0:
        if chkbt(i2,i1):
            data[datai2][datai1]=1
        i2-=1
        datai2+=1
    i1+=13
    datai1+=1



#hold note처리중..


#print

for i in range(len(data)):
    val_tmp=data[i][0]*256 + data[i][1]*128 + data[i][2]*64 + data[i][3]*32 + data[i][4]*16 + data[i][5]*8 + data[i][6]*4 + data[i][7]*2 + data[i][8]
    datatmp=table[val_tmp]
    f.write(datatmp)
    



#FILE OUTPUT

f.close()
