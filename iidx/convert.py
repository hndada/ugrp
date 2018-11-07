import numpy as np
table="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

def get_table(data):
    data = ord(data[0])
    if data==43:
        return 62
    elif data==47:
        return 63
    elif data<=46:
        return -1
    elif data<=57:
        return data+4
    elif data<=64:
        return -1
    elif data<=90:
        return data-65
    elif data<=96:
        return -1
    elif data<=122:
        return data-97+26
    else:
        return -1

def get_note_naive(data):
    ret = 0
    if data[0]=="1" or data[0]=="2" or data[0]=="4" or data[0]=="8":
        ret += 16*int(data[0])
    if data[1]=="1" or data[1]=="2" or data[1]=="4" or data[1]=="8":
        ret += int(data[1])
    return ret

def add_note_basic(loc_init, loc_var, loc, res):
    it = loc_init
    while it < 192:
        res[it,loc-48] = 1
        it += loc_var
    return res

def add_note_complex(loc_init, data, res):
    div = len(data)
    it = loc_init
    loc = 0
    # print(data)
    while it<192:
        notedata = get_table(data[loc])
        loc += 1
        if notedata//8!=0:
            res[it,notedata//8] = 1
        if notedata%8!=0:
            res[it+192//div//2,notedata%8] = 1
        it+=192//div
    return res

def convert_node_ex(node):
    pos = 0
    res = np.zeros((192,8))
    mode = 0
    loc_init = 0
    loc_var = 0
    loc = 0
    while(pos<len(node)):
        # add sequencial note for one lane
        # [A][B] - [A]:note div(CcRrPp), [B]:note lane
        if (node[pos]=="C"): # 1/2
            res = add_note_basic( 0,96,node[pos+1],res)
            pos += 2
        elif (node[pos]=="c"): # 1/2H
            res = add_note_basic(48,96,node[pos+1],res)
            pos += 2
        elif (node[pos]=="R"): # 1/4
            res = add_note_basic( 0,48,node[pos+1],res)
            pos += 2
        elif (node[pos]=="r"): # 1/4H
            res = add_note_basic(24,48,node[pos+1],res)
            pos += 2
        elif (node[pos]=="P"): # 1/8
            res = add_note_basic( 0,24,node[pos+1],res)
            pos += 2
        elif (node[pos]=="p"): # 1/8H
            res = add_note_basic(12,24,node[pos+1],res)
            pos += 2
        
        # complex style, each letter divided with two part
        # [A][BC~] - [A]:note div(BbQqOoXxZ), [BC~]:note data
        elif (node[pos]=="B"): # 1 Comp
            res = add_note_complex( 0,node[pos+1],res)
            pos += 2
        elif (node[pos]=="b"): # 1H Comp
            res = add_note_complex(48,node[pos+1],res)
            pos += 2
        elif (node[pos]=="Q"): # 1/2 Comp
            res = add_note_complex( 0,node[pos+1:pos+3],res)
            pos += 3
        elif (node[pos]=="q"): # 1/2H Comp
            res = add_note_complex(24,node[pos+1:pos+3],res)
            pos += 3
        elif (node[pos]=="O"): # 1/4 Comp
            res = add_note_complex( 0,node[pos+1:pos+5],res)
            pos += 5
        elif (node[pos]=="o"): # 1/4H Comp
            res = add_note_complex(12,node[pos+1:pos+5],res)
            pos += 5
        elif (node[pos]=="X"): # 1/8 Comp
            res = add_note_complex( 0,node[pos+1:pos+9],res)
            pos += 9
        elif (node[pos]=="x"): # 1/8H Comp
            res = add_note_complex( 6,node[pos+1:pos+9],res)
            pos += 9
        elif (node[pos]=="Z"): # 1/16 Comp
            res = add_note_complex( 0,node[pos+1:pos+17],res)
            pos += 17
        
        elif (node[pos]=="S"): # 1/3 Comp...?
            res = add_note_complex( 0,node[pos+1:pos+4],res)
            pos += 4
        elif (node[pos]=="s"): # 1/3H Comp
            res = add_note_complex(16,node[pos+1:pos+4],res)
            pos += 4
        elif (node[pos]=="T"): # 1/6 Comp
            res = add_note_complex( 0,node[pos+1:pos+7],res)
            pos += 7
        elif (node[pos]=="t"): # 1/6H Comp
            res = add_note_complex( 8,node[pos+1:pos+7],res)
            pos += 7
        elif (node[pos]=="U"): # 1/12 Comp
            res = add_note_complex( 0,node[pos+1:pos+13],res)
            pos += 13

        # 1~7 : add one note for lane i
        # [A][BC] - [A]:note type(1~7) [BC]:timing
        elif (node[pos]=="1" or node[pos]=="2" or node[pos]=="3" or node[pos]=="4" or node[pos]=="5" or node[pos]=="6" or node[pos]=="7"):
            res[192*get_table(node[pos+1])//8+24*get_table(node[pos+2])//64, ord(node[pos])-48] = 1
            pos += 3
        
        # 8 : add BigJang
        # 8[A][BC] - [A]:note type(2~7 layne, binary), [BC]:timing
        elif (node[pos]=="8"):
            for i in range(6):
                if((get_table(node[pos+1])>>i)&1==1):
                    res[192*get_table(node[pos+2])//8+24*get_table(node[pos+3])//64, i+2] = 1
            pos += 4

        # 9 : ?
        # [9][1][?][AB] => make format as 1XX note, but not shift back

        # _ : add scratch for first
        # _ - add scratch at AA
        # _[AA][BB] - add scratch at AA, BB, CC...
        elif (node[pos]=="_"):
            res[0,0] = 1
            pos += 1
        # - : add scratchs A6A5A4A3A2A1B6B5B4B3B2B1C6C5C4C3
        # [-][C] - put note on every 2 beat
        # [-][R] - put note on every beat (4)
        # [-][P] - put note on every 1/2 beat (8)
        ## T, U, X = doesn't need to have every digit - leftover = A
        # [-][B] - div by 2
        # [-][Q] - div by 4
        # [-][O] - div by 8
        # [-][X][ABC] - div by 16 a6a5a4a3a2a1b6b5b4b3b2b1c6c54c3c2
        # [-][Z][ABCDEF] - div by 32
        # [-][S][A] - div by 6
        # [-][T][AB] - div by 12 A:6 B:6
        # [-][U][ABCD] - div by 24 A:6 B:6
        # else = ERROR
        else:
            pos += 1
            return "ERROR"
    return res

def get_ord_nm(val):
    if ord(val)>=48 and ord(val)<=57:
        return ord(val)-48
    elif ord(val)>=65 and ord(val)<=70:
        return ord(val)-55
    elif ord(val)>=97 and ord(val)<=102:
        return ord(val)-87

def convert_node_nm(node):
    res = np.zeros((192,8))
    note_div = len(node)//2
    loc = 0 
    for i in range(note_div):
        first = get_ord_nm(node[2*i])
        second = get_ord_nm(node[2*i+1])
        if first>=8:
            first-=8
            res[loc,7] = 1
        if first>=4:
            first-=4
            res[loc,6] = 1
        if first>=2:
            first-=2
            res[loc,5] = 1
        if first>=1:
            first-=1
            res[loc,4] = 1
        if second>=8:
            second-=8
            res[loc,3] = 1
        if second>=4:
            second-=4
            res[loc,2] = 1
        if second>=2:
            second-=2
            res[loc,1] = 1
        if second>=1:
            second-=1
            res[loc,0] = 1
        loc += 192//note_div
    return res

def convert_node(node):
    res = np.zeros((192,8))
    if node == None or node=="":
        return res
    if(node[0] == "#"):
        return convert_node_ex(node[1:])
    else:
        return convert_node_nm(node)

notedata = ["","","#Od4Eu","#XoEAQAQ4r","#QIG2EI","#Q4r","#OiwBd","#X4EAQAg4I","#Q4G2EI","#OoB4g","88","44","22","#OXrjR6AA","#Of/bb7AA","#OW2kk6AA","#ONtJJ5AA","#OXrsa4AA","#OI4Z4","#XIA4AoI4G4AA","#XII4AALoAQgH","#X0ErDiCZB","#O4oPo","#XQ4oAY4oC7AA","#OnoHYQ4F","#XQHA4NFYQB/","#XPGApgDAh","#XfGBpUDBp","#XfGBogDBY","#XPGBpUDFB","#XfGApgDAh","#XfGBpmDBp","#XfGBogDBg","#Or+jq","#OIYhY_","#OIYxY5AA","#OJYBf7AA","#OJYJYQ1l","#XwBAQDAgy_","#O56jl","#OJYJYQwF","#XIBAIOGgQ7AA","#XIBAQCArrXoFAwGAAA","#XIBAIBGYY7AA","#XQCAQHQgg","#XoFAoFCoo","#Oxd60","#XIB4YD4II_","#XrD4NFFQQ","#odoUgB+","#Opd9Z","#OgAD8_","#X4FAIAQA0","#OwNHG","#qsa4Fo","#OwLqn","#qbG","#O9Z0V","#OKccu","#OIYBY7AA_","#XOAYAvIYA4AA","#OJYpY6AA","#XIIYDIIYABn","#XIAoBY4oA7AA","#XU4oBY4oT7AA","#OnoHIQ4F","#X0ErDiCZB","#XvGApgDAh","#XfGBpmDBp","#XfGBogDBo","#XPGBpUDFB","#XfGApgDAh","#XfGBpmDBp","#XfGBogDBQ","#XgI4wogei","#OL8Ur5AA","#OM0fi5DA","#OMaviQwG","#OL5VjB2","#XQI4YQg1j6AA","#XQgwYI4sa","#XIoYQg41j","#XIBAINFgQX4HA44AAA","01"]


notedata = ["#SBBB"]
def print_node_data(arr, d):
    for i in reversed(range(len(arr))):
        if i % (192/d) != 0:
            continue
        print("%4d:%s"%(i%192,str(arr[i])))
        if i % 192 == 0:
            print("     node " + str(i//192))


arr = np.zeros((192*len(notedata),8))
k = 0
for i in range(len(notedata)):
    tmp = convert_node(notedata[i])
    if(str(tmp)=="ERROR"):
        print("ERROR @ " +str(i) + ":" + notedata[i])
        continue
    for i in tmp:
        arr[k] = i
        k += 1
print_node_data(arr, 6)
