# -*- coding: utf-8 -*-
import cPickle
import urllib
import urllib2
import re
import os
from BeautifulSoup import BeautifulSoup
# 抓取2010年到2013年的论文

def getsite(url):
    page = urllib.urlopen(url)
    soup = BeautifulSoup(page)
    links = soup.findAll('a')
    # print links
    listone = []
    number = 0
    diclink = {}
    full_link_list = []
    for i in links:
        newlink = i['href']  # 输出href后面的内容
        # print newlink
        match_link = re.match('.+/.+1[0-3]/', newlink)  # 匹配合适的网址
        if match_link:
            # print match_link.group()
            listone.append(match_link.group())
            # print len(listone)
            for j in listone:
                full_link = url + j
            full_link_list.append(full_link)  # 第二层完整的链接
    for m in set(full_link_list):
        sub_page = urllib.urlopen(m)
        sub_soup = BeautifulSoup(sub_page)

        sub_link = sub_soup.findAll('p')
        # print sub_link
        for n in sub_link:
            try:  # 第33组会出现错误return self._getAttrMap()[key]
                sub_links = n.a['href']
                sub_link2 = re.match('.+1[0-3]-.+.pdf', sub_links)
                if sub_link2:
                    sub_newlink = sub_link2.group()
                full_sublink = url + sub_newlink
                # print full_sublink
                namelist = n.findAll('i')
                if namelist:
                    for prename in namelist:
                        midname = str(prename)[3:-4]
                        fullname = re.sub('[:&#;]', ' ', '%s' % midname)
                        # print fullname
                    urllib.urlretrieve(
                        full_sublink, r'D:\dataset\acl10_12' + '\\' + fullname + '.pdf')
                    print u'下载完成第%d篇' % number
                    number += 1
            except:
                continue
            # list_pdf.append(full_sublink)
            # dic.write(full_sublink+'\n')
        # print diclink
        print 'go on!'

getsite('http://www.aclweb.org/anthology/')
