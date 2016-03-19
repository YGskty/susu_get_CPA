#coding=utf-8

import urllib2
import urllib
import sys
import cookielib
from bs4 import BeautifulSoup
import string
import re
import codecs


#函数定义，用于解析单个人的信息
#person_url :传入的个人信息界面url
def get_person_infor(person_url):
    #做一些网络、服务器异常处理
    try:
        response1 = urllib2.urlopen(person_url, timeout=10)
    except urllib2.URLError, e:
        if hasattr(e,"code"):
            print e.code
        if hasattr(e,"reason"):
            print e.reason
        return 0
    else:
        print "connect is OK" 
        html_doc = response1.read()    
        soup = BeautifulSoup(html_doc)
        #print(soup.prettify())


        #---1、获取person_info 信息---#
        person_info_list = soup.select("[class~=tdl]")
        #print type(person_info_list)

        #空列表,作为临时变量
        b=[] 
        for a in person_info_list:
            b.append(str(a))

        person_info_string = ''.join(b)
        #print type(person_info_string)

        #得到person_info 信息头列表
        person_info_list =[]
        person_info_doc = BeautifulSoup(person_info_string)
        for x in person_info_doc.stripped_strings:
            person_info_list.append(x)
            print x
        #print type(person_info_list)
        print "the length of person_info_list is :" + str(len(person_info_list))
        
        print '+++++++++++++++++++++++++++++++++++++++++'

        #---2、获取person_detail 信息---#
        person_detail_list = soup.select("[class~=data_tb_content]")
        #print type(person_detail_list)

        #空列表,作为临时变量
        b=[] 
        for a in person_detail_list:
            b.append(str(a))

        person_detail_string = ''.join(b)
        #print type(person_detail_string)
        

        #得到person_detail 内容列表
        person_detail_list =[]
        person_detail_doc = BeautifulSoup(person_detail_string)
        
        #for x in person_detail_doc.stripped_strings:
        for x in person_detail_doc.strings:
            if len(string.strip(x)) == 0:
                person_detail_list.append('no_data')
            else:
                person_detail_list.append(string.strip(x))
            print string.strip(x)
        #print type(person_detail_list)
            
        print "the length of person_detail_list is :" + str(len(person_detail_list))
       
        
        #断言：确保信息头和信息内容有相同长度，真实测试发现网页源代码编辑人员不严谨，
        #部分person_detail_list长度大于person_info_list长度，这里我们取消检查，
        #以person_info_list长度为准，多余的数据摒弃
        #assert len(person_info_list)==len(person_detail_list)
        
        #定义字典数据结构让信息一一对应，便于存储
        total_massage = {}
        for i in range(len(person_info_list)):
            total_massage[person_info_list[i]] = person_detail_list[i]
        
        #以名字为文件名保存每个人信息文件
        
        #file_name = ['D:\\susu\\', person_detail_list[0], '.txt']
        #详细路径一直写不进去，还是编码问题……跪了，好吧，全部写到D盘根目录下吧……
        
        file_name = ['D:\\', person_detail_list[0], '.txt']
        file_name =''.join(file_name)
        
        #fd = open(file_name,'w')

        fd = codecs.open(file_name, 'w', 'gbk')

        for j in range(len(person_info_list)):
            fd.write(person_info_list[j])
            fd.write(":")
            fd.write(person_detail_list[j])
            fd.write("\n")
            
        fd.flush()
        fd.close()
        return 1


for it in range(1,162):
    ##---------------------------------------
    #   一、抓取第it页会计师列表爬虫
    #   @tuthor:zhw
    #   @time:2015.10.13
    ##---------------------------------------

    #真正post网址
    url = "http://cmispub.cicpa.org.cn/cicpa2_web/PersonIndexAction.do"

    #查询的事务所名字，注意这里的字符串编码，必须为gb2312编码才能成功查询！！！
    #之前调试一直查不到数据问题就是出在这里
    querry_string = '立信会计师事务所'.decode('utf8').encode('gb2312')

    #查询的页码数
    querry_pageNum = it
    querry_pageNum = str(querry_pageNum)

    #post请求数据
    postdata= urllib.urlencode({
       'ascGuid':'',
       'isStock':'00',
       'method':'indexQuery',
       'offName':querry_string,
       'pageNum':querry_pageNum, 
       'pageSize':'15', 
       'perCode':'', 
       'perName':'', 
       'queryType':'2'
    })

    #增加头数据，欺骗服务器，伪装成win10_64位系统IE11访问网页，因为该服务器只支持IE访问……-_-!
    headers = {
        'Connection': 'Keep-Alive',
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
    }

    #初始化一个CookieJar来处理Cookie的信息 
    cookie = cookielib.CookieJar()

    #创建一个新的opener来使用CookieJar 
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))

    #定义一个请求
    req = urllib2.Request(url= url, data= postdata, headers= headers)

    #访问链接
    responce = opener.open(req)

    #读取网页
    content = responce.read()

    ##---------------------------------------
    #   二、解析获取该页所有人员id,生成所有个人链接
    ##---------------------------------------

    #定义用于存储人员id跳转标志的列表
    person_ids = []

    soup_everyone_per_page = BeautifulSoup(content)

    # 将正则表达式编译成Pattern对象 
    pattern = re.compile(r'javascript:viewDetail')

    #使用正则表达式匹配所有人员id跳转标志
    for link in soup_everyone_per_page.find_all('a'):
        if link.get('href') != None and pattern.search(link.get('href')):
            person_ids.append((link.get('href')).split('\'')[1])
    print type(person_ids)
    print person_ids

    ##---------------------------------------
    #   三、读取单个人员id信息,提取需要信息
    ##---------------------------------------

    for a in range(len(person_ids)):
        person_url = 'http://cmispub.cicpa.org.cn/cicpa2_web/07/' +person_ids[a]+'.shtml'
        #print person_url
        get_person_infor(person_url)

