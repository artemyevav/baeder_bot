#!/usr/bin/env python3

from bs4 import BeautifulSoup
import urllib, re, time, webbrowser
from datetime import datetime

#url = "https://pretix.eu/Baeder/71/2476701/"
#url = "https://pretix.eu/Baeder/71/2478495/"
voucher="urbansportsclub"

def log(text):
  print("[ "+str(datetime.now())+"]: "+text)

book = re.sub(r'^(.*\/)(\d*)\/$',r'\1redeem?voucher='+voucher+r'&subevent=\2',url)

while True:
 with urllib.request.urlopen(url) as fp:
     soup = BeautifulSoup (fp.read(), 'html.parser')
 a = soup.find_all("div","alert")[0].text.strip()
 if re.match(r'.*beendet.*',a):
   print(a)
   exit()

 if re.match(r'.*beginnen.*',a):
   print(a)

 with urllib.request.urlopen(book) as fp:
     soup = BeautifulSoup (fp.read(), 'html.parser')

 t = soup.find_all("div","info-row")[0].find_all("time")
 d = re.sub(r'^\s+', r'',soup.find_all("div","product-description")[0].text,flags=re.MULTILINE)
 p = soup.find_all("div","price")[0].text.strip()
 a = soup.find_all("div","availability-box")[0].text.strip()
 #a = (book,a)[a!=""]
 if a!="":
   log(t[0].text+" "+t[1].text+" "+t[2].text,)
   log(a)
   time.sleep(300)
 else:
   log(t[0].text+" "+t[1].text+" "+t[2].text,)
   log(d+p+"\n"+book)
   webbrowser.open(book)
   exit()

