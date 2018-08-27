def gen_kshfiles(dirpath):
    import os
    kshfiles=[]
    for (path, _, files) in os.walk(dirpath): # _ == dir
        for filename in files:
            ext = os.path.splitext(filename)[-1]
            if ext == '.ksh':
                kshfiles.append(path+'/'+filename)
    return kshfiles

def readksh(filepath):
    from re import split
    fileobj=open(filepath,'rt', encoding='UTF-8-sig')
    file_content=fileobj.read() #file_content is 'str'
    fileobj.close()

    header={}
    chart_content=[]
    lsplit=split('\n+',file_content)
    for i in range(len(lsplit)):
        if (lsplit[i]=='--'):
            for j in range(i):
                line_split=lsplit[j].split('=')
                header[line_split[0]]=line_split[1] #0 ~ i-1
            chart_content=lsplit[i:] #i ~ end
            break
    return header, chart_content

def pardir(filepath):
    #return parent directory
    import os
    return os.path.abspath(os.path.join(filepath, os.pardir)) 

def copytree(src, dst, symlinks=False, ignore=None):
    import os
    import shutil
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)