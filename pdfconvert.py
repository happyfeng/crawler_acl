# -*- coding: utf-8 -*-
#import sys
import os

from pdfminer.pdfinterp import PDFResourceManager, process_pdf
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
outtype = "txt"
def pdfcn():
    laparams = LAParams()
    laparams.all_texts = True
    ###从之前程序崩溃的地方重新启动，查找转换的pdf
    filelist4 = []
    finallist = []
    path2 = r'D:\dataset\acl10_12_txt'
    filelist2 = os.listdir(path2)
    path3 = r'D:\dataset\acl10_12s'
    filelist3 = os.listdir(path3)
    for i in filelist2:
        filelist4.append(i[:-4])
    print filelist4
    for filename in filelist3:
        #print filename[:-4]
        if filename[:-4] not in filelist4:
            finallist.append(filename[:-4])
            #print finallist

    #path = r'D:\dataset\aclpdf2'
    #filelist = os.listdir(path)
    for pdf in finallist:
        try:
            outfile = "D:\\dataset\\acl10_12_txt\\"+pdf+".txt"
            codec = 'utf-8'
            args = [path3+'\\'+pdf+'.pdf']
            rsrc = PDFResourceManager()
            outfp = file(outfile, 'w')
            device = TextConverter(rsrc, outfp, codec=codec, laparams=laparams)
            for fname in args:
                fp = file(fname, 'rb')
                process_pdf(rsrc, device, fp, None, maxpages=0, password='')
                print '%s finishing ' % pdf
                fp.close()
        except:
            continue
    device.close()
    outfp.close()
if __name__ == '__main__':
    pdfcn()
