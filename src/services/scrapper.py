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


def _create_sess() -> Session:
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
    return sess


num_threads = 4

sessqueue: Queue
# youtube channels links
ytqueue: Queue
# google plus id
gpidqueue: Queue
# google plus data
gpdata: Queue

with open('./configuration/api_config.json', 'r') as conf:
    api_config = json.load(conf)

baseurl = 'https://www.googleapis.com/plus/v1/people/'


def get_googleplus_data(youtubelinks):
    global ytqueue, gpidqueue, gpdata, sessqueue
    ytqueue = Queue()
    gpdata = Queue()
    gpidqueue = Queue()
    sessqueue = Queue()
    sessqueue.put(_create_sess())
    _get_gpid(youtubelinks)
    #ls=['104081254063203932826', '104319451239962260842', '104487478835903266614', '106528488452385868078', '112451707535616499039', '113740433288678746156', '110719646800892429857', '107832848514449228002', '111238679541272506057', '110527404192676344910', '108718900843208717959', '110773654355011852298', '112545988550231747941', '109015017883036265537', '111619384900361996101', '113571857327618029413', '108580465121265022570', '109009180927921808564', '106581110204409321492', '103803992344999251357', '117951264286553570960', '116977853486744240174', '112089568272026200961', '108433524314997470810', '113308914892491415112', '110697981199025316680', '114701697596238157461', '105800611595942566528', '100095580184649291412', '116165962067022614413', '117716226770031457123', '108292430794258203058', '105609333207494431408', '115588859755690438491', '111398643194880750326', '104390396343797261925', '104319451239962260842', '113350952341289716779', '103079001135126382170', '117803748324323995297', '108145359568012406896', '112259690809618755318', '117216985405973125932', '108443671844114454909', '107732078006115384622', '106944384481236051060', '114694320299332640062', '104364248092948726380', '110347570758352965377', '108407721709227749833']
    #for l in ls:
    #    gpidqueue.put(l)
    print("===============================")
    _get_usersData()
    return list(gpdata.queue)


def _get_gpid(youtubelinks):
    global ytqueue
    _ytlinks_toqueue(youtubelinks)
    _run_gpidworkers()
    ytqueue.join()


def _get_usersData():
    global gpidqueue
    _run_gpdataworkers()
    gpidqueue.join()


def _ytlinks_toqueue(youtubelinks):
    global ytqueue
    for ytlink in youtubelinks:
        if ytlink["authorChannelUrl"]:
            ytqueue.put(ytlink["authorChannelUrl"])


def _run_gpidworkers():
    global num_threads
    for i in range(num_threads):
        worker = Thread(target=_scrap_gpid)
        worker.setDaemon(True)
        worker.start()


def _scrap_gpid():
    global ytqueue, gpidqueue, sessqueue
    while True:
        ylink = ytqueue.get()
        if sessqueue.empty():
            sess = _create_sess()
        else:
            sess = sessqueue.get()
        sess.visit(ylink)
        for link in sess.xpath('//body/span[@itemprop = "author"]/link[@itemprop = "url"]'):
            parsedUrl = urlparse(link['href'])
            if parsedUrl.netloc == "plus.google.com":
                # parsedUrl.path returns google plus id with "/" at the
                # to remove the "/" we select all after element 0
                gpidqueue.put(parsedUrl.path[1:])
        ytqueue.task_done()
        sessqueue.put(sess)


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
        jsonres = requests.get(baseurl + gpid, params=api_config).json()
        data = _prepare_data(jsonres)
        if data:
            gpdata.put(data)
        gpidqueue.task_done()


def _prepare_data(data):
    relevant_data = dict()
    if 'gender' in data.keys():
        relevant_data.update({"gender": data['gender']})
    return relevant_data
