import numpy as np
from PIL import Image


FILENAME="032"


im=Image.open(FILENAME+".png")

im_cal=np.asarray(im)


'''
세로 나누기 테스트

::sample code::
cropImage = im.crop((100, 100, 150, 150))
cropImage.save('python-crop.jpg')

일단 9칸으로 나눠서 반복문 테스트

len(im_cal)=세로길이
len(im_cal[0])=가로길이

'''
            


'''
알고리즘:

12, 9, 9칸간격으로 줄 테스트해서
시작점(lefttop) 끝점(rightbot) 다수 알아내기

x+21번째줄 (노란색 노트줄)은 흰색이 아예 없음을 이용

그리고 끝점이 제일 작은 (y축값 우선, 그다음이 x축값) 순서대로 crop


'''

               
def find_spot(start): #어차피 121칸 그대로임
    start_tmp=0 #start example. 13번째 '열' (start=12)
    end_tmp=0

    retv=[]

    for loop1 in range(0, len(im_cal)): #세로길이 그대로 볼거임(추후정렬)
        if im_cal[loop1][start+21][0]==255 and im_cal[loop1][start+21][1]==255 and im_cal[loop1][start+21][2]==255: #white
            if start_tmp!=end_tmp: #not same = 마디데이터가 있음
                retv.append([[start, start_tmp], [start+121, end_tmp]])
            start_tmp=loop1
            end_tmp=loop1
        else:
            end_tmp=loop1

    return retv

    #맨 위의 하나의 흰공간, 아래는 딱맞으니 3픽셀 더해서 crop됨
    


save_start=[] #[시작점, 끝점] 저장 후 대충 bubble sort나 할듯


loop=12

while loop+121<len(im_cal[0]):
    #[loop,0] [loop+121,len(im_cal)]
    retv_tmp=find_spot(loop)
    for loop3 in range(len(retv_tmp)):
        save_start.append(retv_tmp[loop3])

    
    loop+=130

##save_start는 정상작동

##bubble_sort는 오른쪽 아래 (y축값 우선, 같다면 x축값) 기준

for loop1 in range(len(save_start)-1):
    for loop2 in range(loop1+1, len(save_start)):
        if save_start[loop1][1][1]-3>save_start[loop2][1][1]+3: #왼쪽게 오른쪽거보다 y가크면
            save_start[loop1],save_start[loop2]=save_start[loop2],save_start[loop1]
        elif save_start[loop1][1][1]+3>=save_start[loop2][1][1] and save_start[loop1][1][1]-3<=save_start[loop2][1][1]: #같다면
            if save_start[loop1][1][0]-3>save_start[loop2][1][0]+3: #x값
                save_start[loop1],save_start[loop2]=save_start[loop2],save_start[loop1]



for loop1 in range(len(save_start)):
    filename_out=FILENAME+"-"+str(loop1)+".png"
    cropim=im.crop((save_start[loop1][0][0],save_start[loop1][0][1]+1,save_start[loop1][1][0],save_start[loop1][1][1]+3))
    cropim.save(filename_out)



    
