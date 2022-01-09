#!/usr/bin/env python3

import logging

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, CallbackContext
from bs4 import BeautifulSoup
from datetime import datetime
from uuid import uuid4
import urllib, re, time, webbrowser

voucher="urbansportsclub"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def baeder(url):
 book = re.sub(r'^(.*\/)(\d*)\/$',r'\1redeem?voucher='+voucher+r'&subevent=\2',url)
 ret = {}
 try:
  with urllib.request.urlopen(url, timeout=10) as fp:
      soup = BeautifulSoup (fp.read(), 'html.parser')
  a = soup.find_all("div","alert")
  if len(a):
    aa=a[0].text.strip()
    if re.match(r'.*beendet.*',aa):
     ret = {'abort': 1, 'msg': aa }
    if re.match(r'.*beginnen.*',aa):
     ret = {'abort': 0, 'msg': aa}
  if len(ret): return ret

  with urllib.request.urlopen(book) as fp:
    soup = BeautifulSoup (fp.read(), 'html.parser')
  t = soup.find_all("div","info-row")[0].find_all("time")
  d = re.sub(r'^\s+', r'',soup.find_all("div","product-description")[0].text,flags=re.MULTILINE)
  p = soup.find_all("div","price")[0].text.strip()
  a = soup.find_all("div","availability-box")[0].text.strip()
  if a!="":
   ret = {'abort': 0, 'msg': a}
  else:
   ret = {'abort': 1, 'msg':d+p+"\n"+book}
 except:
   ret = {'abort': 1, 'msg': 'Something went wrong'}
 return ret


def start(update: Update, context: CallbackContext) -> None:
    obj = {'u': update, 'c': context}
    if len(context.job_queue.jobs())>0:
      update.message.reply_text(f'Process is started already')
      return
    if len(context.user_data)>0:
      update.message.reply_text(f'Start watching')
      context.job_queue.run_repeating(runner, 60, first=1, context=obj)
    else:
      update.message.reply_text(f'Nothing to do')

def runner(context: CallbackContext) -> None:
    u = context.job.context['u']
    c = context.job.context['c']
    to_remove=[]
    for key in c.user_data:
      book = baeder(c.user_data.get(key))
      if book["abort"] == 1:
        u.message.reply_text(f'{book["msg"]}',disable_web_page_preview=True)
        to_remove.append(key)
    for key in to_remove:
      del c.user_data[key]
    if (len(c.user_data) == 0):
      u.message.reply_text(f'No more URLs left, stopping. Add more URLs and /start again.')
      context.job.schedule_removal()


def watch_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    key = str(uuid4())
    value = update.message.text.partition(' ')[2]
    if value:
      if value in context.user_data.values():
        update.message.reply_text(f'Already in the list')
      else:
        context.user_data[key] = value
        update.message.reply_text(f'Watching at {value}, don\'t forget to /start',disable_web_page_preview=True)
#        logging.info(f'{key}: {value}')
    else:
      update.message.reply_text('Usage: /watch https://pretix.eu/Baeder/XXX/YYY/')


def list_urls(update: Update, context: CallbackContext) -> None:
    if len(context.user_data)>0:
      update.message.reply_text(f'Watching at:')
    else:
      update.message.reply_text(f'List is empty')
    for key in context.user_data:
      update.message.reply_text(f'{context.user_data.get(key)}',disable_web_page_preview=True)

def clear_urls(update: Update, context: CallbackContext) -> None:
    js = context.job_queue.jobs()
    if len(js)>0:
      update.message.reply_text(f'Stopping {len(js)} threads')
      for j in js:
        j.schedule_removal()
    update.message.reply_text(f'Clearing URLs')
    context.user_data.clear()

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'Usage:\n/help for this help\n/start to start watching\n/watch to add URL\n/list to list your URLs\n/clear to clear the list')

def main() -> None:
    tf = open('.token','r')
    t = tf.read()
    tf.close()
    updater = Updater(t)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("watch", watch_command))
    dispatcher.add_handler(CommandHandler("list", list_urls))
    dispatcher.add_handler(CommandHandler("clear", clear_urls))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()