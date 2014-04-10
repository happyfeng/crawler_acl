#coding:utf-8
import optparse
import sys
import re
import urllib
import urllib2
from BeautifulSoup import BeautifulSoup
import os
import pickle
import time
reload( sys )
sys.setdefaultencoding('utf-8')
sleep_time = 20
#输出论文在谷歌学术的引用次数
class Article():
    def __init__(self):
        self.attrs = {'url_citations': [None, 'Citations list', 4]}
    def __getitem__(self, key):
        if key in self.attrs:
            return self.attrs[key][0]
        return None

    def __setitem__(self, key, item):
        if key in self.attrs:
            self.attrs[key][0] = item
        else:
            self.attrs[key] = [item, key, len(self.attrs)]

    def __delitem__(self, key):
        if key in self.attrs:
            del self.attrs[key]
    def as_txt(self):
        # Get items sorted in specified order:
        items = sorted(self.attrs.values(), key=lambda item: item[2])
        # Find largest label length:
        max_label_len = max([len(str(item[1])) for item in items])
        fmt = '%%%ds %%s' % max_label_len
        return '\n'.join([fmt % (item[1], item[0]) for item in items])

    def as_csv(self, header=False, sep='|'):
        # Get keys sorted in specified order:
        keys = [pair[0] for pair in \
                    sorted([(key, val[2]) for key, val in self.attrs.items()],
                           key=lambda pair: pair[1])]
        res = []
        if header:
            res.append(sep.join(keys))
        res.append(sep.join([unicode(self.attrs[key][0]) for key in keys]))
        return '\n'.join(res)
class ScholarParser():
    SCHOLAR_SITE = 'http://scholar.google.com'

    def __init__(self, site=None):
        self.soup = None
        self.article = None
        self.site = site or self.SCHOLAR_SITE
        self.year_re = re.compile(r'\b(?:20|19)\d{2}\b')

    def handle_article(self, art):
        """
        In this base class, the callback does nothing.
        """

    def parse(self, html):
        """
        This method initiates parsing of HTML content.
        """
        self.soup = BeautifulSoup(html)
        for div in self.soup.findAll(ScholarParser._tag_checker):
            self._parse_article(div)

    def _parse_article(self, div):
        self.article = Article()

        for tag in div:
            if not hasattr(tag, 'name'):
                continue

            if tag.name == 'div' and tag.get('class') == 'gs_rt' and \
                    tag.h3 and tag.h3.a:
                self.article['title'] = ''.join(tag.h3.a.findAll(text=True))
                self.article['url'] = self._path2url(tag.h3.a['href'])

            if tag.name == 'font':
                for tag2 in tag:
                    if not hasattr(tag2, 'name'):
                        continue
                    if tag2.name == 'span' and tag2.get('class') == 'gs_fl':
                        self._parse_links(tag2)

        if self.article['title']:
            self.handle_article(self.article)

    def _parse_links(self, span):
        for tag in span:
            if not hasattr(tag, 'name'):
                continue
            if tag.name != 'a' or tag.get('href') == None:
                continue
            if tag.get('href').startswith('/scholar?cites'):
                if hasattr(tag, 'string') and tag.string.startswith('Cited by'):
                    self.article['num_citations'] = \
                        self._as_int(tag.string.split()[-1])
                self.article['url_citations'] = self._path2url(tag.get('href'))
    @staticmethod
    def _tag_checker(tag):
        if tag.name == 'div' and tag.get('class') == 'gs_r':
            return True
        return False

    def _as_int(self, obj):
        try:
            return int(obj)
        except ValueError:
            return None

    def _path2url(self, path):
        if path.startswith('http://'):
            return path
        if not path.startswith('/'):
            path = '/' + path
        return self.site + path
class ScholarParser120726(ScholarParser):
    def _parse_article(self, div):
        self.article = Article()

        for tag in div:
            if not hasattr(tag, 'name'):
                continue

            if tag.name == 'div' and tag.get('class') == 'gs_ri':
              if tag.a:
                self.article['title'] = ''.join(tag.a.findAll(text=True))
                self.article['url'] = self._path2url(tag.a['href'])

              if tag.find('div', {'class': 'gs_a'}):
                year = self.year_re.findall(tag.find('div', {'class': 'gs_a'}).text)
                self.article['year'] = year[0] if len(year) > 0 else None

              if tag.find('div', {'class': 'gs_fl'}):
                self._parse_links(tag.find('div', {'class': 'gs_fl'}))

        if self.article['title']:
            self.handle_article(self.article)
class ScholarQuerier():
    SCHOLAR_URL = 'http://scholar.google.com/scholar?hl=en&q=%(query)s+author:%(author)s&btnG=Search&as_subj=eng&as_sdt=1,5&as_ylo=&as_vis=0'
    NOAUTH_URL = 'http://scholar.google.com/scholar?hl=en&q=%(query)s&btnG=Search&as_subj=eng&as_std=1,5&as_ylo=&as_vis=0'
    #UA = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.64 Safari/537.31'

    class Parser(ScholarParser120726):
        def __init__(self, querier):
            ScholarParser.__init__(self)
            self.querier = querier

        def handle_article(self, art):
            self.querier.add_article(art)

    def __init__(self, author='', scholar_url=None, count=0):
        self.articles = []
        self.author = author
        # Clip to 100, as Google doesn't support more anyway
        self.count = min(count, 100)

        if author == '':
            self.scholar_url = self.NOAUTH_URL
        else:
            self.scholar_url = scholar_url or self.SCHOLAR_URL

        if self.count != 0:
            self.scholar_url += '&num=%d' % self.count

    def query(self, search):
        #休眠几秒
        #time.sleep(sleep_time)
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.64 Safari/537.31','Referer':'http://scholar.google.com'}
        url = self.scholar_url % {'query':urllib.quote(search.encode('utf-8')),'author': urllib.quote(self.author)}
        print url
        #proxy_support = urllib2.ProxyHandler({'http':'http://218.94.1.166:82'})
        #opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
        #urllib2.install_opener(opener)
        req = urllib2.Request(url=url,headers=headers)
        hdl = urllib2.urlopen(req)
        html = hdl.read()
        self.parse(html)

    def parse(self, html):
        """
        This method allows parsing of existing HTML content.
        """
        parser = self.Parser(self)
        parser.parse(html)

    def add_article(self, art):
        self.articles.append(art)



def txt(query, author, count):
    querier = ScholarQuerier(author=author, count=count)
    querier.query(query)
    articles = querier.articles
    if count > 0:
        articles = articles[:count]
    for art in articles:
        print art.as_txt() + '\n'

def csv(query, author, count, header=False, sep='|'):
    querier = ScholarQuerier(author=author, count=count)
    querier.query(query)
    articles = querier.articles
    #if count > 0:
    articles = articles[:1]
    for art in articles:
        result = art.as_csv(header=header, sep=sep)
        #print result.encode('utf-8')
        header = False
        tem_list = result.split('|')
        #只输出列表的最后一个元素，引用次数
        pri_list = tem_list[-1:]
        for i in pri_list:
            return i.encode('utf-8')

def url(title, author):
    querier = ScholarQuerier(author=author)
    querier.query(title)
    articles = querier.articles
    for article in articles:
        if "".join(title.lower().split()) == "".join(article['title'].lower().split()):
            return article['url'], article['year']
    return None, None

def titles(author):
    querier = ScholarQuerier(author=author)
    querier.query('')
    articles = querier.articles
    titles = []
    for article in articles:
      titles.append(article['title'])
    return titles
dic = {}
def main():
    usage = """scholar.py [options] <query string>
A command-line interface to Google Scholar."""

    fmt = optparse.IndentedHelpFormatter(max_help_position=50,
                                         width=100)
    parser = optparse.OptionParser(usage=usage, formatter=fmt)
    parser.add_option('-a', '--author',
                      help='Author name')
    parser.add_option('--csv', action='store_true',
                      help='Print article data in CSV format (separator is "|")')
    parser.add_option('--csv-header', action='store_true',
                      help='Like --csv, but print header line with column names')
    parser.add_option('--txt', action='store_true',
                      help='Print article data in text format')
    parser.add_option('-c', '--count', type='int',
                      help='Maximum number of results')
    parser.set_defaults(count=0, author='')
    options, args = parser.parse_args()
    n = 1
    dic = pickle.load(open(r'D:\dataset\citation.dump','r'))
    filename_list = dic.keys()
    #print filename_list
    filelist = os.listdir(r'D:\dataset\test')
    print len(filelist)
    for i in filelist:
        if i[:-4] not in filename_list:
            args.append(i[:-4])
    print len(args)
    if len(args) == 0:
        print 'Hrrrm. I  need a query string.'
        sys.exit(1)
    for query in args:
        #query = ' '.join(j)
    #if options.csv:
        numcit = csv(query, author=options.author, count=options.count)
        print query
        print numcit
        if numcit == None or numcit == 'None':
            numcit = 0
        dic[query] = int(numcit)
        print 'the %d is finishing' %n
        n += 1
        pickle.dump(dic,open(r'D:\dataset\citation.dump','wb'))
    #elif options.csv_header:
     #   csv(query, author=options.author, count=options.count, header=True)
    #else:
    #    txt(query, author=options.author, count=options.count)

if __name__ == "__main__":
    main()
