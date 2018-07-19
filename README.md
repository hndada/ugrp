##sdvx

#To Do
채보 분석 (Lv.17~)
(v)손처리 좌우 판별
@@홀드는 첫번째 이후 소문자로 표기
벡터 계산
노브는 '각도'로 다루기
(추후)SV

#idea bank
1.짧은 벡터가 많을수록 밀집해있다
1-1.벡터 길이가 일정 이상 되면, 무효화. '손을 떼고 있어도 무방'

2.'규칙도 함수' 구현 시도
OBJECTIVE: (knob)
LLLLLLLL -> regular
RRRRRRRR -> regular
LRLRLRLR -> regular
LRLRRLRR -> irregular   (Max Burning !!)

구현 아이디어:
앞 2개로 다음 노브 방향 예상. 보통 2개의 반복이므로.
LL -> LL
RR -> RR
LR -> LR
RL -> RL
맞으면 1, 틀리면 0
평균 0.8(arbitary number) 이하면 'irregular'으로 판정 

3.노브 돌리는 각도. 대(large)마디당 각도 몇

4.Pattern Library
4-1.겹계단
판단 위해선 과거 노트에 대한 정보가 필요.
알고리즘: 12 23 34 등의 배열이 연속적으로 짧은 간격으로 등장

5.기교 레벨에 따라서 변화하는 손배치
5-1.FX-L,R & BT2,3 can be hit with one hand (#Endroll no.07 no.01~)
5-2.노브가 바쁘면 FX동시타는 한번에 처리 (#Endroll no.11)
5-3.노브가 바쁘면 FX의 손이동을 최소화. (#Endroll last part)
5-4.노트가 한쪽으로 쏠려있으면 두손으로 처리. (EMPIRE of FLAME no.27)
그 외 이미 존재하는 기교 배치는 뻥튀기된 난이도를 조사하면서 추가

##popn
muang: "image segmentation using graph cut algorithms"의 키워드로
채보 이미지 파일로부터 마디 이미지를 자동으로 crop하는 module을 얻을 수 있을 것으로 예상함.