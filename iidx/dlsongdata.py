import urllib3
import js2py
import numpy as np
import time
import random

import convert


CONSOLE_RED = '\033[91m'
CONSOLE_YELLOW = '\033[93m'
CONSOLE_GREEN = '\033[92m'
CONSOLE_NORMAL = '\033[0m'
CONSOLE_BLUE = '\033[94m'
scr_init = """
function ar(){s="";LNDEF=384,cob=["s","w","b","w","b","w","b","w"];
obr=[[0,1,2,3,4,5,6,7],[0,1,2,3,4,5,6,7]];kc=[[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]];
dpalls=[[0,1,2,3,4,5,6,7],[0,7,6,5,4,3,2,1]];imgdir="../";diftype="";twstr="";
ln=[],sp=[],dp=[],tc=[],c1=[],c2=[],cn=[],sides=["",2,2],csd=["","left","right"];
dw=[134,121],dr=[38,4],df=[134,119],ms=["",""," class=m1"," class=m2"];tm=new Date();hsa=8;
genre=title=artist=bpm=opt=lnse=lnhs="",key=ky=back=7,hs=gap=ty=k=1;cncnt=bsscnt=legacy=prt=pty=0;
soflan=level=notes=measure=a=l=m=g=db=p1o=hps=flp=off=lnln=lnst=lned=alls=sran=kuro=sftkey=os=hcn=ttl=0;
sc32=[],sc32base=[],sc32loop=[];
DEFNOTE="01234567";MIRNOTE="07654321";DEFHSA=8;
"""
scr_init_a = scr_init+"""gap=0;k=1;l=0;a=1;"""
scr_init_h = scr_init+"""gap=0;k=1;l=0;a=0;"""
scr_init_n = scr_init+"""
gap=0;k=1;l=1;a=1;"""

def receive_song_data_advanced(url):
    http = urllib3.PoolManager()
    raw = http.request('GET',url)
    try:
        raw = raw.data.decode("shife_jis").split('\n')
    except:
        try:
            raw = raw.data.decode("utf-8").split('\n')
        except:
            return "ERROR"
    scr_enable = False
    scr = ""
    for line in raw:
        if "404 Error" in line:
            return "ERROR"
        if "<script" in line:
            scr_enable = True
            continue
        elif "</script" in line or "hd()" in line:
            scr_enable = False
        if scr_enable is True:
            scr += line + "\n"
    scr_end = """return [sp,tc,ln,c1,bpm,LNDEF,measure];}ar();"""
    res_a = js2py.eval_js(scr_init_a+scr+scr_end)
    res_h = js2py.eval_js(scr_init_h+scr+scr_end)
    res_n = js2py.eval_js(scr_init_n+scr+scr_end)
    return [res_a, res_h, res_n]

# raw = http.request('GET', "http://textage.cc/score/20/_ongaku.html")
# raw = http.request('GET', "http://textage.cc/score/7/spooky.html")
# raw = http.request('GET', "http://textage.cc/score/17/_valse17.html")
# raw = http.request('GET', "http://textage.cc/score/25/anagma.html")
# r = "http://textage.cc/score/21/ancientl.html"
# print(receive_song_data(r,"a"))
# print(receive_song_data(r,"h"))
# print(receive_song_data(r,"n"))


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
    data_diff.append(cur_diff)
    # print(title, cur_diff)
file_diff.close()

data = []
failed = []
warning = []

cnt = 0
cnt_comp = 0
cnt_warn = 0
cnt_errr = 0

def retrieve_data_advanced(url, diff):
    global data, failed, warning
    global cnt_comp, cnt_warn, cnt_errr
    received_data_raw = []
    # try:
    received_data_raw = receive_song_data_advanced(url)
    # except:
        # print(CONSOLE_RED+"Failed to retrieve data:data download fail"+CONSOLE_NORMAL)
    if received_data_raw == "ERROR":
        return False
    ind = 0
    for received_data in received_data_raw:
        try:
            received_data[4].replace("～ ","~")
            if len(received_data[0])>0:
                converted_data, warn = convert.convert_chart(received_data)
                if ind==0:
                    data.append((converted_data,diff[3],url))
                elif ind==1:
                    data.append((converted_data,diff[2],url))
                elif ind==2:
                    data.append((converted_data,diff[1],url))
                ind += 1
                # print("Data Successfully retrieved")
                if len(warn)!=0:
                    warning.append((warn,url,ind))
                    for i in warn:
                        if(i!=None):
                            print(CONSOLE_YELLOW+"WARNING:"+i+CONSOLE_NORMAL)
                    cnt_warn += 1
                else:
                    cnt_comp += 1
            else:
                cnt_comp += 1
        except IndexError as e:
            print(CONSOLE_RED+"Failed to retrieve data:Indexerror at convert.py"+CONSOLE_NORMAL)
            failed.append((url,ind,'convert_index'))
            cnt_errr += 1
        except TypeError as e:
            print(CONSOLE_RED+"Failed to retrieve data:Typeerror at convert.py"+CONSOLE_NORMAL)
            failed.append((url,ind,'convert_type'))
            cnt_errr += 1
        except:
            print(CONSOLE_RED+"Failed to retrieve data:Unknown Error"+CONSOLE_NORMAL)
            failed.append((url,ind,'unknown'))
            cnt_errr += 1
idx = 0
# sheet data link
file_list = open("list.txt", "r")
# http://textage.cc/score/titletbl.js
link_basic = "http://textage.cc/score/"
print(CONSOLE_BLUE+"Crawling "+str(len(data_diff))+" data..." + CONSOLE_NORMAL)
itt=0
for line in file_list.readlines():
    print(CONSOLE_BLUE +"Song Progress: "+str(cnt) + "/"+str(len(data_diff))
            + CONSOLE_GREEN +" Crawled: " + str(len(data))
            + CONSOLE_GREEN + " Perfect: " + str(cnt_comp)
            + CONSOLE_YELLOW +" Warning: " + str(cnt_warn)
            + CONSOLE_RED +" Error: " + str(cnt_errr)
            + CONSOLE_NORMAL)
    cnt += 1
    # itt+=1
    # if itt<132:
        # continue
    title = line.split("'")
    if len(title)<2:
        continue
    title = title[1]
    series = line.split(",")[0].split("[")[1]
     
    url = link_basic + series + "/" + title + ".html"
    if title in data_title:
        diff = data_diff[data_title.index(title)]
        print("Receiving from " + url + "...")
        retrieve_data_advanced(url,diff)
        time.sleep(random.random()/10+0.1)
        print(CONSOLE_GREEN+"saving..."+CONSOLE_NORMAL)
        np.save('rawdata.npy',np.array(data))
        np.save('failed.npy',np.array(failed))
        np.save('warning.npy',np.array(warning))
print(CONSOLE_BLUE +"Song Progress: "+str(cnt) + "/"+str(len(data_diff))
            + CONSOLE_GREEN +" Crawled: " + str(len(data))
            + CONSOLE_GREEN + " Perfect: " + str(cnt_comp)
            + CONSOLE_YELLOW +" Warning: " + str(cnt_warn)
            + CONSOLE_RED +" Error: " + str(cnt_errr)
            + CONSOLE_NORMAL)
print("Finally saving...")
np.save('rawdata.npy',np.array(data))
np.save('failed.npy',np.array(failed))
np.save('warning.npy',np.array(warning))
file_list.close()

