import urllib3
import js2py
import numpy as np
import time

import convert
# raw = http.request('GET', "http://textage.cc/score/25/aa_rebld.html")
# raw = http.request('GET', "http://textage.cc/score/20/_ongaku.html")
# raw = http.request('GET', "http://textage.cc/score/7/spooky.html")
# raw = http.request('GET', "http://textage.cc/score/17/_valse17.html")
# raw = http.request('GET', "http://textage.cc/score/25/anagma.html")

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
    raw = raw.data.decode("shift_jis").split('\n')

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

r = "http://textage.cc/score/21/ancientl.html"
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
idx = 0
data = []
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
     
    url = link_basic + series + "/" + title + ".html"
    if title in data_title:
        diff = data_diff[data_title.index(title)]
        print("Receiving from " + url + ", Difficulty Another...")
        received_data = receive_song_data(url,"a")
        if len(received_data[0])>0:
            print(received_data)
            converted_data = convert.convert_chart(received_data)
            print("Data confirmed.")
            data.append((converted_data,diff[3]))
        """
        time.sleep(1)
        print("Receiving from " + url + ", Difficulty Hyper...")
        received_data = receive_song_data(url,"h")
        if len(received_data[0])>0:
            print("Data confirmed.")
            data.append((received_data,diff[2]))
        time.sleep(1)
        print("Receiving from " + url + ", Difficulty Normal...")
        received_data = receive_song_data(url,"n")
        if len(received_data[0])>0:
            print("Data confirmed.")
            data.append((received_data,diff[1]))
        time.sleep(1)"""
    idx += 1
    if idx > 1:
        break
print(data)
print("saving...")
np.save('rawdata.npy',np.array(data))
file_list.close()

