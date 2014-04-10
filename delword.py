# -*- coding: gbk -*-
"""
Created on Fri Nov 16 14:32:09 2012

@author: che
"""
######################删除文本里的字母数字等符号#####
import re, os
path_txt = r'D:\dataset\acl10_12_txt'
path_txt2 = r'D:\dataset\acl10_12_txt2'
def delw():
    filelist=os.listdir(path_txt)
    while(len(filelist)>0):
        try:
            name=filelist.pop()
            path=path_txt+'\\'+name
            path2=path_txt2+'\\'+name
            content=open(path,'r')
            r = re.sub('[^a-zA-Z]', " ", content.read())
            #r = re.sub('[0-9\[\!\$\?\-\(\)\.\_\`\=\'\:\;\"\{\}\+\\n\’\×\+\*\?\°\~\<\>\/\\"\,\[\]\@\#\\\&\*\%]', " ",
            #        content.read())
            content2=open(path2,'w')
            content2.write(r)
            content.close()
            content2.close()
        except:
            continue
    finish = '转换完成'
    return finish
if __name__ == '__main__':
    delw()
