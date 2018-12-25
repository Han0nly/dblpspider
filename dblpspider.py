# -*- coding: utf-8 -*-
import re
import requests
from lxml import etree
from optparse import OptionParser
import xlwt
from google.cloud import translate

search_url = "https://dblp.org/search?q="
source = ""

def geturl(filename):
    with open(filename, 'r') as f:
        urllist = []
        while True:
            line = f.readline()
            if not line:
                break
            line.strip()
            line = line.replace("\n", "")
            urllist.append(line)
    return urllist

def spide_down(url):
    global source
    count=1
    source_re = "[^/]+(?!.*/)"
    regax = re.compile(source_re)
    source = regax.findall(url)[0][:-5]
    print "正在下载" + source + "的论文信息"
    table = init_sheet(source)
    r = requests.get(url)
    html = etree.HTML(r.content)
    # 匹配期刊论文格式
    a = html.xpath("//li[contains(@class, 'entry') and contains(@class, 'article')]/@id")
    # 匹配会议论文格式
    if not a:
        a = html.xpath("//li[contains(@class, 'entry') and contains(@class, 'inproceedings')]/@id")
    # 每一篇文章
    for i in a:
        # print i
        # print "//*[@id=\""+i+"\"]/div[@class,\"data\"]/span[@itemprop,\"author\"]/a/span[@itemprop,\"name\"]/text()"
        author = html.xpath("//*[@id=\""+i+"\"]/div[@class=\"data\"]/span[@itemprop=\"author\"]/a/span[@itemprop=\"name\"]/text()")
        title = html.xpath("//*[@id=\""+i+"\"]/div[@class=\"data\"]/span[@class=\"title\"]/text()")
        # print "文章名："+title[0]
        table.write(count, 0, str(count))
        table.write(count, 1, title[0])
        authors = ""
        # /span[@itemprop,\"author\"]/a/span[@itemprop,\"name\"]/text()
        for j in author:
            authors = authors+j+", "
        table.write(count,2,authors)
        doi_url = html.xpath("//*[@id=\""+i+"\"]/nav/ul/li[1]/div[2]/ul/li[1]/a/@href")
        table.write(count,3,doi_url[0])
        table.write(count,4,source)
        count = count + 1

def search_word(keyword):
    global search_url
    url = search_url + keyword
    spide_down(url)

def init_sheet(source):
    table = file.add_sheet(source)
    table.write(0, 0, "id")
    table.write(0, 1, "tltle")
    table.write(0, 2, "authors")
    table.write(0, 3, "doi_url")
    table.write(0, 4, "source")
    return table

if __name__ == '__main__':
    parser = OptionParser(usage="%prog [options]")
    parser.add_option("-n", "--name", action="store", type="string", dest="keyword", help="the keyword to be searched")
    parser.add_option("-f", "--file", action="store", type="string", dest="filename", help="the file to be read")
    (options, args) = parser.parse_args()
    # Instantiates a client
    translate_client = translate.Client()
    if options.keyword:
        print "正在下载"+options.keyword+"的相关论文资料..."
        file = xlwt.Workbook()
        table = init_sheet(options.keyword)
        search_word(options.keyword)
        print "已将搜索结果保存到当前目录下的papers文件中"
    if options.filename:
        file = xlwt.Workbook()
        # file_all = xlwt.Workbook()
        urls = geturl(options.filename)
        for a in urls:
            spide_down(a)
        file.save('paper_sheets.xls')
        # file_all.save('paper_all.xls')
        print "已将所有搜索结果格式化保存到当前目录下的paper.xls文件中"
