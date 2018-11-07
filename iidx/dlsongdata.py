import urllib3
import js2py


http = urllib3.PoolManager()
# raw = http.request('GET', "http://textage.cc/score/25/aa_rebld.html")
raw = http.request('GET', "http://textage.cc/score/20/_ongaku.html")
raw = raw.data.decode("shift_jis").split('\n')
scr = """
function ar(){let sp = new Array();let tc= new Array();
gap=0;
ln=0;
k=1;
l=0;
a=1;
"""
# k = 1
# l, m, g, a = 0
# if k=0 > double...?
# N > l = 1
# A > a = 1
# H 
"""
if(char2=="X"){a=1;kuro=1;}
if(char2=="A")a=1;
if(char2=="L")l=1;
if(char2=="N"){l=1;hps=1;}
if(char2=="H")hps=1;
if(char2=="B"){l=1;g=1;}
if(char2=="G" || char2=="R"){l=1;hps=1;g=1;}
if(char2=="P"){l=1;hps=1;pty=1;g=1;}
if(char1=="1")sides[1]=1;
if(char1=="D"){k=0;key=14;}
if(char1=="L"){k=0;key=14;os=1;sides[1]=1;}
if(char1=="R"){k=0;key=14;os=2;}
if(char1=="F"){flp=1;k=0;key=14;}
if(char1=="M"){m=1;k=0;key=14;}
if(char1=="B"){db=1;key=14;}
"""

scr_enable = False
for line in raw:
    if "<body>" in line:
        scr_enable = True
        continue
    elif "</script>" in line or "hd()" in line:
        scr_enable = False
    if scr_enable is True:
        scr+=line+"\n"

# print(scr)
scr_end = """return [sp,tc,bpm];}ar();"""
res = js2py.eval_js(scr+scr_end)
print(res)


# difficulty table
file_diff = open("diff.txt", "r")
# http://textage.cc/score/cstbl.js
data_diff = []
data_title = []
for line in file_diff.readlines():
    title = line.split("'")
    if len(title)<2: continue
    title = title[1]
    data_title.append(title)
    diff = line.split(",")
    if len(diff) < 12: continue
    cur_diff = [0,0,0,0,0]
    cur_diff[0] = diff[3] #SB
    cur_diff[1] = diff[5] #SN
    cur_diff[2] = diff[7] #SH
    cur_diff[3] = diff[9] #SA
    cur_diff[4] = diff[11] #SX
    # print(title, cur_diff)

file_diff.close()



# 0WEWE
# 117127125127125
    # random.shuffle(query)


# sheet data link
file_list = open("list.txt", "r")
# http://textage.cc/score/titletbl.js
link_basic = "http://textage.cc/score/"
for line in file_list.readlines():
    title = line.split("'")
    if len(title)<2:
        continue
    title = title[1]
    series = line.split(",")[0].split("[")[1]
    
    # print(link_basic + series + "/" + title)
    # http = urllib3.PoolManager()
    # data_raw = http.request('GET', "http://textage.cc/score/15/rokmenow")
    # print(data_raw.status,data_raw.data)    
file_list.close()
