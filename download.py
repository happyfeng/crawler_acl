# -*- coding: utf-8 -*-
import cPickle
import urllib
import os
def download_acl():
    lists = []
    links = os.listdir(r'D:\dataset\new')
    num = 1
    doc = cPickle.load(open(r'D:\dataset\list_pdfnew.dump','r'))
    linklist = doc.keys()
    print len(linklist)
    for pdflink in linklist:
        if doc[pdflink]+'.pdf' not in links:
            lists.append(pdflink)
    print len(lists)
    for i in lists:
        try:
            urllib.urlretrieve(i,r'D:\dataset\new'+'\\'+doc[i]+'.pdf')
            print '下载完成%d'%num
            num +=1
        except:
            continue
if __name__ == '__main__':
	download_acl()
