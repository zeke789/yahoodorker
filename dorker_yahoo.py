#!/usr/bin/env python
from multiprocessing.pool import ThreadPool
import requests
import random
import urllib
import re
import sys,os
import time
from tldextract import extract

proxy_file = open("socks4.txt", "r")
proxies = proxy_file.readlines()
proxy_file.close()

usagents_file = open("useragents.txt", "r")
usagents = usagents_file.readlines()
usagents_file.close()

dork_file = open("dorks.txt", "r")
dorks = dork_file.readlines()
dork_file.close()

blackList1=["cn","kr","ru","de","hr","tr","tw","hk","it","gr","ch"]
blackList2=["youtube","google","instagram","facebook","twitter","pinterest","amazon","ebay","wayfair"]

def getHeaders(usagent):
    return {
        'User-Agent': usagent, 
        'Cookie':'',
        'Host':'search.yahoo.com',
        'Connection':'Close',
        'Referer':'https://search.yahoo.com/',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }

def checkGoodRequest(resp,code):
    if(code==0 or code==403):
        if(resp.find("something went wrong") > -1):
            return [False,"swrong1"]
        return [False,"forbidden_or_null"] 
    return [True]
    
def getUrls(resp,blacklist):
    if(resp.find("did not find results for") == -1):
        urls = re.findall('td-hu" href="(.+?)" referrerpolicy', resp)
        retUrls=[]
        if(len(urls)>1):
            for x in range(0,len(urls)):
                retUrls.append(urls[x])
                # get domain ext and check if is black,  if not then append to urls[]
        else:
            urls = urls = re.findall('https://r.search.yahoo.com/_ylt=" href="(.+?)" referrerpolicy', resp)
            if(len(urls)>1):
                for x in range(0,len(urls)):
                    retUrls.append(urls[x])
            else:
                sdx=1
                #urls = re.findall('td-hu" href="(.+?)" referrerpolicy', resp)
        return retUrls
    return [];
    
def saveUrls(urls):
    file4 = open("urls.html", "a")
    rUrls = "";
    for x in range(0,len(urls)):
        black=0
        findUrl = re.findall('RO=10/RU=(.+?)/RK=2', urllib.unquote(urls[x]))
        if( len(findUrl) > 0 ):
            if(findUrl[0].find("=") > --1):
                tsd, td, tsu = extract(findUrl[0])
                for d in blackList1:
                    if(d == tsu):
                        black++
                for d in blackList2:
                    if(d == td):
                        black++
                if(black==0):
                    rUrls+= findUrl[0]  + "\n"
    file4.write(rUrls)
    file4.close()
    
def getNextPage(resp):
    next = re.findall('class="next" href="(.+?)" referrerpolicy', resp)
    if(len(next) < 1):
        return False;
    return next[0]
    
def hitNextPage(page,count):
    # return [url,false] if not have next url
    goodReq=False
    while(goodReq == False):
        try:
            usagent=usagents[random.randint(0,len(usagents)-1)].replace("\n", "");
            headers = getHeaders( usagent );
            rand = random.randint(1, (len(proxies)-1) )
            proxi ="socks4://"+proxies[rand].replace("\n", "")
            proxy = {'https': proxi}
            #print("\n"+page+"\n")
            response = requests.get(page, headers=headers ,  timeout=6.54 )
            code = response.status_code
            resp=response.content;
            good = checkGoodRequest(resp,code)
            if(good[0] == True):
                goodReq=True
                urls=getUrls(resp,blackList1)
                nextPage=getNextPage(resp)
                if(nextPage != False):
                    return [urls,nextPage,count+1,resp,usagent];
                else:
                    return [urls,False,count+1,resp,usagent]
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            if(str(exc_type).find("exceptions.ConnectionError") == -1 and str(exc_type).find("exceptions.ConnectTimeout") == -1 ):
                print(exc_type, fname, exc_tb.tb_lineno)
   

  

urls = []
#for x in range(0,len(dorks)-1):
for x in range(0,500):
  x=int(x)
  dorkEncoded = dorks[x].replace(" ","+").replace("\n","").replace("'","%27").replace("\"","%22").replace("?","%3F").replace("=","%3D").replace("/","%2F")
  urls.append(["https://search.yahoo.com/search;_ylt=As;_ylc=dsdas--?p="+dorkEncoded+"&fr2=sb-top&fr=sfp",dorks[x]])


def fetch_url(url):
    time.sleep(18.4)
    done=False
    while(done == False):
        goodRequest=False;
        while(goodRequest == False):
            usagent=usagents[random.randint(0,len(usagents)-1)].replace("\n", "");
            headers = getHeaders( usagent );
            rand = random.randint(1, (len(proxies)-1) )
            proxi ="socks4://"+proxies[rand].replace("\n", "")
            try:
                proxy = {'https': proxi}
                response = requests.get(url[0], headers=headers ,timeout=6.45)
                code = response.status_code
                resp=response.content;
                good = checkGoodRequest(resp,code)
                if(good[0] == True):
                    urls= getUrls(resp,blackList1)
                    count=0;
                    if(len(urls) > 0):
                        saveUrls(urls)
                        print("Saved_1 " + str(len(urls)) + " urls --")
                        nextPage=getNextPage(resp)
                        if( nextPage != False):
                            #print("NEXT PAGE:: " + nextPage)
                            nextResult =["","continue.."];
                            while(nextResult[1] != False):
                                time.sleep(6.4)
                                nextResult = hitNextPage(nextPage,count)
                                urls = nextResult[0]
                                count= nextResult[2]
                                usagent = nextResult[4]
                                if(len(urls) > 0):
                                    print("Saved_2 " + str(len(urls)) + " urls --")
                                    saveUrls(urls)
                                else:
                                    print("___ 2 ___ no more results for " + nextPage )
                                nextPage=nextResult[1];
                        else:
                            print("next page false 1")
                    else:
                        print("___ 1 ___ no more results for " + url[0])
                        file4 = open("test_yahoo_no_urls.html", "a")
                        file4.write(resp + "\n============================================================================================================================================================================================================================================================================================================================\n\n"+ usagent +" \n\n\n\n")
                        file4.close()
                    goodRequest=True
                    done=True
                    print("DORK PASED -- "  + "Pages fetched for "  + url[1].replace("\n","")  + " => " +  str(count) )
                    return url[1], resp,proxi, code,None
                else:
                    file3 = open("test_yahoo_err_or.html", "a")
                    file3.write(resp)
                    file3.close()
                    goodRequest=False
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                if(str(exc_type).find("exceptions.ConnectionError") == -1 and str(exc_type).find("exceptions.ConnectTimeout") == -1 ):
                    print(exc_type, fname, exc_tb.tb_lineno)
                goodRequest=False



results = ThreadPool(2).imap_unordered(fetch_url, urls)
for url, html, proxyresp ,code,error in results:
    if error is None:
        x=1
    else:
        print("error fetching %r: %s" % (url + "=>", proxyresp))
        ###



