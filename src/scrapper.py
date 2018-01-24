import json
import sys
from queue import Queue
from threading import Thread
from urllib.parse import urlparse

import requests
from dryscrape import Session, start_xvfb

if 'linux' in sys.platform:
    # start xvfb in case no X is running. Make sure xvfb
    # is installed, otherwise this won't work!
    start_xvfb()

sess = Session()
# session prop
sess.set_attribute('auto_load_images', False)
sess.set_attribute('dns_prefetch_enabled', False)
sess.set_attribute('plugins_enabled', False)
sess.set_attribute('private_browsing_enabled', False)
sess.set_attribute('javascript_can_open_windows', False)
sess.set_attribute('javascript_can_access_clipboard', False)
sess.set_attribute('offline_storage_database_enabled', False)
sess.set_attribute('offline_web_application_cache_enabled', False)
sess.set_attribute('local_storage_enabled', False)
sess.set_attribute('local_storage_database_enabled', False)
sess.set_attribute('local_content_can_access_file_urls', False)
sess.set_attribute('accelerated_compositing_enabled', True)
sess.set_attribute('site_specific_quirks_enabled', False)

# youtube channels links
ytqueue = Queue
# google plus id
gpidqueue = Queue
# google plus data
gpdata = Queue

num_threads = 8

with open('./configuration/api_config.json', 'r') as conf:
    api_config = json.load(conf)

baseurl = 'https://www.googleapis.com/plus/v1/people/'


def _get_gpid(youtubelinks):
    global ytqueue
    _ytlinks_toqueue(youtubelinks)
    _run_gpidworkers()
    ytqueue.join()


def _ytlinks_toqueue(youtubelinks):
    global ytqueue
    for ytlink in youtubelinks:
        ytqueue.put(ytlink)


def _run_gpidworkers():
    global num_threads
    for i in range(num_threads):
        worker = Thread(target=_scrap_gpid)
        worker.setDaemon(True)
        worker.start()


def _scrap_gpid():
    global ytqueue
    global gpidqueue
    while True:
        ylink = ytqueue.get()
        sess.visit(ylink)
        for link in sess.xpath('//body/span[@itemprop = "author"]/link[@itemprop = "url"]'):
            parsedUrl = urlparse(link['href'])
            if parsedUrl.netloc == "plus.google.com":
                # parsedUrl.path returns google plus id with "/" at the
                # to remove the "/" we select all after element 0
                gpidqueue.put(parsedUrl.path[1:])
        ytqueue.task_done()


def _get_usersData():
    global gpidqueue
    _run_gpdataworkers()
    gpidqueue.join()


def _run_gpdataworkers():
    global num_threads
    for i in range(num_threads):
        worker = Thread(target=_fetch_gpdata)
        worker.setDaemon(True)
        worker.start()


def _fetch_gpdata():
    global gpidqueue, api_config, gpdata
    while True:
        gpid = gpidqueue.get()
        res = requests.get(baseurl + gpid, params=api_config)
        data = _prepare_data(res)
        gpdata.put(data)
        ytqueue.task_done()


def _prepare_data(data):
    relevant_data = dict()
    if 'gender' in data.keys():
        relevant_data.update({"gender": data['gender']})
    return relevant_data
