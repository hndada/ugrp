##sdvx

#To Do
손처리 좌우 판별 (done)
벡터 도입


#손교차곡 list (add more please)
Lv18 Juggler's Madness

Lv18 #Endroll (needs lots of trial and error)
(no.65~72) (약간 어색할 것으로 예상.)
(no.73~76)
(no.77~80: 손교차가 아니나 현 알고리즘으로는 복잡한 손배치가 구현됨)

Lv20 I (no.65~71) 
:difficult to determine L/R automatically. will just try manually

Lv19 Staring at Star (no.34) 
Success! by Pure Luck


#idea bank
짧은 벡터가 많을수록 밀집해있다
벡터 길이가 일정 이상 되면, 무효화. '손을 떼고 있어도 무방'

'규칙도 함수' 구현 시도
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

##popn
