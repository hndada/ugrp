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

scr_init_a = """
function ar(){let sp = new Array();let tc= new Array();let ln= new Array();let c1 = new Array();LNDEF=384;
gap=0;k=1;l=0;a=1;"""
scr_init_h = """
function ar(){let sp = new Array();let tc= new Array();let ln= new Array();let c1 = new Array();LNDEF=384;
gap=0;k=1;l=0;a=0;"""
scr_init_n = """
function ar(){let sp = new Array();let tc= new Array();let ln= new Array();let c1 = new Array();LNDEF=384;
gap=0;k=1;l=1;a=1;"""
def receive_song_data(url, diff="a"):
    http = urllib3.PoolManager()
    raw = http.request('GET', url)
    try:
        raw = raw.data.decode("shift_jis").split('\n')
    except:
        raw = raw.data.decode("utf-8").split('\n')
    if diff=="a":
        scr = scr_init_a
    elif diff=="h":
        scr = scr_init_h
    elif diff=="n":
        scr = scr_init_n
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
    scr_end = """return [sp,tc,ln,c1,bpm,LNDEF,measure];}ar();"""
    return js2py.eval_js(scr+scr_end)

# raw = http.request('GET', "http://textage.cc/score/25/aa_rebld.html")
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
def retrieve_data(url, diff, lv):
    global data, failed, warning
    global cnt_comp, cnt_warn, cnt_errr
    ret = 0
    try:
        received_data = receive_song_data(url,lv)
        received_data[4].replace("～ ","~")
        if len(received_data[0])>0:
            converted_data, warn = convert.convert_chart(received_data)
            if lv=="a":
                data.append((converted_data,diff[3],url))
            elif lv=="h":
                data.append((converted_data,diff[2],url))
            elif lv=="n":
                data.append((converted_data,diff[1],url))
            # print("Data Successfully retrieved")
            if len(warn)!=0:
                warning.append((warn,url,lv))
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
        failed.append((url,lv,'convert_index'))
        cnt_errr += 1
    except TypeError as e:
        print(CONSOLE_RED+"Failed to retrieve data:Typeerror at convert.py"+CONSOLE_NORMAL)
        failed.append((url,lv,'convert_type'))
        cnt_errr += 1
    except js2py.internals.simplex.JsException as e:
        print(CONSOLE_RED+"Failed to retrieve data:js2py error"+CONSOLE_NORMAL)
        failed.append((url,lv,'js2py'))
        cnt_errr += 1
    except:
        print(CONSOLE_RED+"Failed to retrieve data:Unknown Error"+CONSOLE_NORMAL)
        failed.append((url,lv,'unknown'))
        cnt_errr += 1
    return ret

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
        print("Receiving from " + url + ", Difficulty Another...")
        retrieve_data(url,diff,"a")
        time.sleep(random.random()/2+0.25)
        print("Receiving from " + url + ", Difficulty Hyper...")
        retrieve_data(url,diff,"h")
        time.sleep(random.random()/2+0.25)
        print("Receiving from " + url + ", Difficulty Normal...")
        retrieve_data(url,diff,"n")
        time.sleep(random.random()/2+0.25)
        print(CONSOLE_GREEN+"saving..."+CONSOLE_NORMAL)
        np.save('rawdata.npy',np.array(data))
        np.save('failed.npy',np.array(failed))
        np.save('warning.npy',np.array(warning))
print("saving...")
np.save('rawdata.npy',np.array(data))
np.save('failed.npy',np.array(failed))
np.save('warning.npy',np.array(warning))
file_list.close()

