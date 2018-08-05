f=open("./KnobDict.txt",'w')
f.write("{")
for i in range(10):
    f.write("'"+str(i)+"'")
    f.write(":")
    f.write(str(i))
    f.write(", ")
for i in range(ord('A'),ord('Z')+1): #ord('A')==65
    f.write("'"+str(chr(i))+"'")
    f.write(":")
    f.write(str(i-55))
    f.write(", ")
    if ((i-55)%10==0):
        f.write("\n")
for i in range(ord('a'),ord('o')+1): #ord('a')==97
    f.write("'"+str(chr(i))+"'")
    f.write(":")
    f.write(str(i-61))
    if(i!=ord('o')):
        f.write(", ")
    if ((i-61)%10==0):
        f.write("\n")
f.write('}')
f.close()