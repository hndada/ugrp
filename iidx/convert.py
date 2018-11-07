import numpy as np
table="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
DV = 192

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
    while it < DV:
        res[it,loc-48] = 1
        it += loc_var
    return res

def add_note_complex(loc_init, data, res):
    div = len(data)
    it = loc_init
    loc = 0
    # print(data)
    while it<DV:
        notedata = get_table(data[loc])
        loc += 1
        if notedata//8!=0:
            res[it,notedata//8] = 1
        if notedata%8!=0:
            res[it+DV//div//2,notedata%8] = 1
        it+=DV//div
    return res

def scratch_convert(data,div):
    ret = [0]*len(data)*6
    ptr = 0
    for i in data:
        for j in reversed(range(6)):
            if (get_table(i)>>j)&1 == 1:
                ret[ptr] = 1
            ptr += 1
    return ret[:div]

def add_scratch_basic(loc_init, div, res):
    pos = loc_init
    while (pos < DV):
        res[pos, 0] = 1
        pos += DV//div
    return res

def add_scratch_complex(data, res):
    for i in range(len(data)):
        if data[i] == 1:
            res[DV*i//len(data), 0] = 1
    return res

def get_loc_precise(f, s):
    return DV*get_table(f)//8+DV//8*get_table(s)//64

def convert_node_ex(node):
    pos = 0
    res = np.zeros((DV,8))
    is_scr = False
    while(pos<len(node)):
        mode = 0
        init = 0
        data = [0]*8
        ptr = 1
        # add sequencial note for one lane
        # [A][B] - [A]:note div(CcRrPp), [B]:note lane
        if (node[pos]=="C"): # 1/2
            mode = 1; init =      0; div =  2; ptr = 1 if is_scr else 2;
        elif (node[pos]=="c"): # 1/2H
            mode = 1; init = DV// 4; div =  2; ptr = 1 if is_scr else 2;
        elif (node[pos]=="R"): # 1/4
            mode = 1; init =      0; div =  4; ptr = 1 if is_scr else 2;
        elif (node[pos]=="r"): # 1/4H
            mode = 1; init = DV// 8; div =  4; ptr = 1 if is_scr else 2;
        elif (node[pos]=="P"): # 1/8
            mode = 1; init =      0; div =  8; ptr = 1 if is_scr else 2;
        elif (node[pos]=="p"): # 1/8H
            mode = 1; init = DV//16; div =  8; ptr = 1 if is_scr else 2;
        
        # complex style, each letter divided with two part
        # [A][BC~] - [A]:note div(BbQqOoXxZ), [BC~]:note data
        elif (node[pos]=="B"): # 1 Comp
            mode = 2; init =      0; div =  1; ptr = 2;
        elif (node[pos]=="b"): # 1H Comp
            mode = 2; init = DV// 4; div =  1; ptr = 2;
        elif (node[pos]=="Q"): # 1/2 Comp
            mode = 2; init =      0; div =  2; ptr = 2 if is_scr else 3;
        elif (node[pos]=="q"): # 1/2H Comp
            mode = 2; init = DV// 8; div =  2; ptr = 2 if is_scr else 3;
        elif (node[pos]=="O"): # 1/4 Comp
            mode = 2; init =      0; div =  4; ptr = 3 if is_scr else 5;
        elif (node[pos]=="o"): # 1/4H Comp
            mode = 2; init = DV//16; div =  4; ptr = 3 if is_scr else 5;
        elif (node[pos]=="X"): # 1/8 Comp
            mode = 2; init =      0; div =  8; ptr = 4 if is_scr else 9;
        elif (node[pos]=="x"): # 1/8H Comp
            mode = 2; init = DV//24; div =  8; ptr = 4 if is_scr else 9;
        elif (node[pos]=="Z"): # 1/16 Comp
            mode = 2; init =      0; div = 16; ptr = 5 if is_scr else 17;
        
        elif (node[pos]=="S"): # 1/3 Comp...?
            mode = 2; init =      0; div =  3; ptr = 3 if is_scr else 4;
        elif (node[pos]=="s"): # 1/3H Comp
            mode = 2; init = DV//12; div =  3; ptr = 3 if is_scr else 4;
        elif (node[pos]=="T"): # 1/6 Comp
            mode = 2; init =      0; div =  6; ptr = 4 if is_scr else 7;
        elif (node[pos]=="t"): # 1/6H Comp
            mode = 2; init = DV//24; div =  6; ptr = 4 if is_scr else 7;
        elif (node[pos]=="U"): # 1/12 Comp
            mode = 2; init =      0; div = 12; ptr = 5 if is_scr else 13;

        # 1~7 : add one note for lane i
        # [A][BC] - [A]:note type(1~7) [BC]:timing
        elif (node[pos]=="1" or node[pos]=="2" or node[pos]=="3" or node[pos]=="4" or node[pos]=="5" or node[pos]=="6" or node[pos]=="7"):
            mode = 3; ptr =  3;
            div = 1; data[ord(node[pos])-48] = 1
        # 8 : add BigJang
        # 8[A][BC] - [A]:note type(2~7 layne, binary), [BC]:timing
        elif (node[pos]=="8"):
            for i in range(6):
                if((get_table(node[pos+1])>>i)&1==1):
                    data[i+2] = 1
            mode = 3; ptr =  4;
        # 9 : BigJang + note 1
        # [9][A][ABC] add note 1
        elif (node[pos]=="9"):
            mode = 3; ptr =  4;
            for i in range(6):
                if((get_table(node[pos+1])>>i)&1==1):
                    data[i+2] = 1
            data[1] = 1
            pos += 4
        # _ - add scratch at AA
        # _[AA][BB] - add scratch at AA, BB, CC...
        elif (node[pos]=="_"):
            is_scr = True; mode = 4;
        # change to scratch mode
        elif (node[pos]=="-"):
            is_scr = True; ptr = 1;
        # else = ERROR
        else:
            ptr += 1
            return "ERROR"
        if is_scr:
            if   mode == 1:
                res = add_scratch_basic(init,div,res)
            elif mode == 2: # ??AA not included
                res = add_scratch_complex(scratch_convert(node[pos+1:pos+ptr],div*2),res)
            elif mode == 3:
                res[0,0] = 1
            elif mode == 4:
                pos += 1
                while(pos<len(node)):
                    res[get_loc_precise(node[pos],node[pos+1]),0] = 1
                    pos += 2
        else:
            if   mode == 1:
                res = add_note_basic(init,DV//div,node[pos+1],res)
            elif mode == 2:
                res = add_note_complex(init,node[pos+1:pos+ptr],res)
            elif mode == 3:
                for i in range(8):
                    if data[i]==1:
                        res[get_loc_precise(node[pos+1],node[pos+2]),i] = 1
            elif mode == 4:
                # need more work - single notes and etc
                res[0,0] = 1
        pos += ptr
                
    return res

def get_ord_nm(val):
    if ord(val)>=48 and ord(val)<=57:
        return ord(val)-48
    elif ord(val)>=65 and ord(val)<=70:
        return ord(val)-55
    elif ord(val)>=97 and ord(val)<=102:
        return ord(val)-87

def add_note_nm(f, s):
    r = [0]*8
    first = get_ord_nm(f)
    second = get_ord_nm(s)
    if first>=8:
        first-=8; r[7] = 1
    if first>=4:
        first-=4; r[6] = 1
    if first>=2:
        first-=2; r[5] = 1
    if first>=1:
        first-=1; r[4] = 1
    if second>=8:
        second-=8; r[3] = 1
    if second>=4:
        second-=4; r[2] = 1
    if second>=2:
        second-=2; r[1] = 1
    if second>=1:
        second-=1; r[0] = 1
    return r

def convert_node_nm(node):
    # [x][ABC] = length of text(div) * 2 in hex
    # [@][AB] = gap AB:(beat)
    res = np.zeros((DV,8))
    note_div = len(node)//2
    pos = 0
    if(node[0] == "x"): # extended format
        note_div = int("0"+node[1:4],16)//2
        pos = 4
    it = 0
    while it < note_div:
        if(node[pos]=="@"):
            sft = int("0x"+node[pos+1:pos+3],16)
            pos += 3
            it += sft
        else:
            for i in range(8):
                if res[(DV*it)//note_div,i] == 0:
                    res[(DV*it)//note_div,i] = add_note_nm(node[pos],node[pos+1])[i]
            pos += 2
            it += 1
    return res

def convert_node(node):
    res = np.zeros((DV,8))
    if node == None or node=="":
        return res
    if(node[0] == "#"):
        return convert_node_ex(node[1:])
    else:
        return convert_node_nm(node)

notedata = ["","","#Od4Eu","#XoEAQAQ4r","#QIG2EI","#Q4r","#OiwBd","#X4EAQAg4I","#Q4G2EI","#OoB4g","88","44","22","#OXrjR6AA","#Of/bb7AA","#OW2kk6AA","#ONtJJ5AA","#OXrsa4AA","#OI4Z4","#XIA4AoI4G4AA","#XII4AALoAQgH","#X0ErDiCZB","#O4oPo","#XQ4oAY4oC7AA","#OnoHYQ4F","#XQHA4NFYQB/","#XPGApgDAh","#XfGBpUDBp","#XfGBogDBY","#XPGBpUDFB","#XfGApgDAh","#XfGBpmDBp","#XfGBogDBg","#Or+jq","#OIYhY_","#OIYxY5AA","#OJYBf7AA","#OJYJYQ1l","#XwBAQDAgy_","#O56jl","#OJYJYQwF","#XIBAIOGgQ7AA","#XIBAQCArrXoFAwGAAA","#XIBAIBGYY7AA","#XQCAQHQgg","#XoFAoFCoo","#Oxd60","#XIB4YD4II_","#XrD4NFFQQ","#odoUgB+","#Opd9Z","#OgAD8_","#X4FAIAQA0","#OwNHG","#qsa4Fo","#OwLqn","#qbG","#O9Z0V","#OKccu","#OIYBY7AA_","#XOAYAvIYA4AA","#OJYpY6AA","#XIIYDIIYABn","#XIAoBY4oA7AA","#XU4oBY4oT7AA","#OnoHIQ4F","#X0ErDiCZB","#XvGApgDAh","#XfGBpmDBp","#XfGBogDBo","#XPGBpUDFB","#XfGApgDAh","#XfGBpmDBp","#XfGBogDBQ","#XgI4wogei","#OL8Ur5AA","#OM0fi5DA","#OMaviQwG","#OL5VjB2","#XQI4YQg1j6AA","#XQgwYI4sa","#XIoYQg41j","#XIBAINFgQX4HA44AAA","01"]


def print_node_data(arr, d):
    for i in reversed(range(len(arr))):
        if i % (DV//d) != 0:
            continue
        print("%4d:%s"%(i%DV,str(arr[i])))
        if i % DV == 0:
            print("     node " + str(i//DV))


arr = np.zeros((DV*len(notedata),8))
k = 0
for i in range(len(notedata)):
    tmp = convert_node(notedata[i])
    if(str(tmp)=="ERROR"):
        print("ERROR @ " +str(i) + ":" + notedata[i])
        continue
    for i in tmp:
        arr[k] = i
        k += 1
print_node_data(arr, 16)
