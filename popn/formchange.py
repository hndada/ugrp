import numpy as np

FILENAME="007"
BPM=165

f=open(FILENAME+".txt","r")
f2=open(FILENAME+"-1.txt","w+")


data=f.readlines()
loop=1
while loop<len(data):
    tmp=0
    pre=loop-1
    while data[loop]=="000000000\n":
        tmp+=1
        loop+=1
        if loop>=len(data):
            break
    writetxt=data[pre][0:9]+"#"+str(tmp)+"\n"
    f2.write(writetxt)
    loop+=1



f.close()
f2.close()
