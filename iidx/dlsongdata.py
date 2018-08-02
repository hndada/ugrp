import urllib3

# receive each data
http = urllib3.PoolManager()
r = http.request('GET', "http://textage.cc/score/15/rokmenow")
print(r.status,r.data)



# import sys
# import urllib3 as ul
# 
# link = "http://textage.cc/score/15/rokmenow?1N600"
# f = ul.urlopen(link)           
# myfile = f.readline()  
# print(myfile)

