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

data = [[None, None, None, None, '822040', '821040', '820820', '421080', '280014408208', '50002410a040', '88003004c002', '1400a0085002', '080412204480', '0204100220102040', '802040102008100a', 'x030a0@0248001080@0224@02900040082000900008400400', 'x03032@0248@0290@0224@0292@0248@02820008041000', 'a200104420001800200440002a005000840028005000a000', '00a8', None, None, None, '4810a000', '42048800', '24085000', '02845020', '84085000', '82240840', '44289020', '42289040', '8410a040', '02845020', '82042800', '04904010', '22045020', '84108440', 'c400640018005444', '5400a404c4005400', 'c200a8004800a222', 'a2005202a2006200', '62102804c0106218', 'c410621462105408', 'c2102804c010620c', '8200540ca2106410', 'x020c2@032200020002@0314402040', 'x0208c@02022800020008@030a201040', 'x020a4@032400040004@030c201040', 'a200120202000200', 'x060c4@0b6c@1712@0220020040000280@02', '0200140428085212', '240080001000220010022000420080001000220010022000', 'x06042@0380@0320@0342@032000020040@0312@0320@0340@0316@0220@0244@0280@02', '2c00202020002020', '2000202040008000', '1000101010001010', '1000101080004000', '8200424242008200', '4200222222008800', '8400282828008200', '4200222222002000', '4800880808004800', '2400840404000400', '2200820202000200', '44140404', '28880808', 'a0508844', '2200101010008000', '542a542a', 'x03027@0524@0224@022004@0424@0224@02', '2400242444008400', '4200424242004242', '4200424222001200', '80042010', '2002', '80002010', 'x08022@0f02@0702@0754@0f2c@0e01', 'd0002844', 'x0108800400442@03', '90004814', 'x01088@028090@03', '48008422', '44801240', '24004408', '82004422', '18004824', 'x01812@0204040420@02222222', 'x01848@0244444490@02545454', '8b00944a', 'x01094@02208a002080', 'x01054@0386004a02', '64824850', '82102040', '82041020', '42040884', '22084010', '82040850', 'a0004824', 'x18012@2f24@0f48@0f90@0f22@0f44@0f88@0f50@1728@1401@02', 'x060d2@0520@0510@0220@0240000680@0210@0220060040@0280@0252@0b', 'x180cb@1710@1702@0b20@0b40@0706@0380@0b10@0b20@0306@0740@0b80@0b52@2c01@02', 'aaa8', 'x010c6@03a6000820', '5528a050a850a450', '2a14a2502a145228', '542298441a24c0a8', '3418a054a854a854', 'x180ab@1740@1702@0b10@0b20@0706@0340@0b10@0b20@0306@0740@0b80@0b52@2c01@02', 'x180ca@1720@1702@0b20@0b40@0702@0380@0b08@0b10@0302@0720@0b40@0b92@2c01@02', '2ea8', 'x08057@1e01c6@0f10@0740@07', '8a289050', '88288442', '82204214', '8200200042001404', '4200200082004404', '8200200082004404', 'x18002@0220@1080@0b08@0f02@0220@12080002@0b20@0b02@0240@1480@0710@0c40@0202@0f10@0702@0740@0f', 'x18002@0220@1080@0f20@0b02@0240@12200002@0b40@0b84@1f28@0f80@0f50@1f', 'a20a', 'x018@0304@02080010002000', '8240', '8220', '5a0020041000880040102000980040020800140020084000', 'b20040042000180080102000c40020021000480010084000', 'a600400820004400201040009a0040042000480020044000', '0a0010044000a80040041000480020020800240010082000', '540020084000900040041000a20040041000280080044000', '820040081000a40040102000880040042000420020041000', '4a0020041000280040041000a20040041000480020044000', 'aa0408122450aa4490284482', '24104080', '42142010', '82040840', '24882010', '2680204c00', '5880204a00', '548020', '8a1020', '8a', '8a', '8a', '8a', 'aa48a8', '4a8a4a', 'aaaaaa', 'b2b2b2', '940094949400', '949494', 'd2d2d2', 'e2e2e2', 'a400b4b4b400', 'e4e2c2', 'c200c2c2c200', 'b2b2ca', '96', 'x00c0080@04', 'x018@0502@06'], [None, ['2450'], None, None, None, None, None, None, None, None, None, None, None, None, ['2800'], None, None, None, ['2450'], None, ['2300'], None, None, None, None, None, None, None, ['2400'], None, None, None, None, None, None, ['2500'], ['2600'], None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, ['2800'], None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, ['2700'], None, None, None, ['2800'], None, None, None, None, None, None, None, None, None, None, None, None, None, ['2700'], None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, ['2400'], None, ['2100'], None, ['2600'], None, None, None, None, None, None, None, None, None, None, None, ['2800'], None, None, None, ['2900'], None, ['31064'], None, None, None, None, None, ['3300'], None, ['3400'], None, ['3500'], ['3600'], None, None, None, None, None, ['2400']], [None, None, None, None, None, None, None, None, None, None, None, None, None, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 384, 480, 480], [], '210~360', 288, 157]

notedata = data[0]
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
print_node_data(arr, 8)
