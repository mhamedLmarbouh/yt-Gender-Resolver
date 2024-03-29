import sys
from queue import Queue
from threading import Thread
from urllib.parse import urlparse

from dryscrape import Session, start_xvfb

from src.services.googlerequest import gp_personnaldata



num_threads_crawler = 8
num_threads_googleplus=4

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


sessqueue: Queue
# youtube channels links
ytqueue: Queue
# google plus id
gpidqueue: Queue
# google plus data of type multiprocessing.Queue
gpdata: Queue


def get_googleplus_data(youtubeids):
    """this function will call the crawler to get the google plus ids
    and then launch the api calls to get the gender data"""
    global gpdata
    _init_queues()
    _get_gpid(youtubeids)
    _get_usersData()
    return list(gpdata.queue)


def _get_gpid(youtubeids):
    """this function will prepare the youtube pages urls and call the crawlers manager """
    global ytqueue, gpidqueue
    _ytlinks_toqueue(youtubeids)
    _run_gpidworkers()
    ytqueue.join()


def _ytlinks_toqueue(youtubeids):
    global ytqueue
    for id in youtubeids:
        ytqueue.put("https://www.youtube.com/channel/" + id["authorChannelId"])


def _get_usersData():
    """this function will call the api manager """
    global gpidqueue, gpdata
    _run_gpdataworkers()
    gpidqueue.join()


def _run_gpidworkers():
    """this function is a crawlers manager that will run the threads of crawler"""
    global num_threads
    for i in range(num_threads_crawler):
        worker = Thread(target=_scrap_gpid)
        worker.setDaemon(True)
        worker.start()


def _scrap_gpid():
    """this function will try to visit a youtube channel and crawl it for the google plus id
    if it exists it will add it to gpidquee"""
    global ytqueue, gpidqueue, sessqueue
    while True:
        # get the youtube channel url
        ylink = ytqueue.get()
        # verify if scrapper queue is empty
        if sessqueue.empty():
            # if empty create a new session
            sess = _create_sess()
        else:
            # if not empty get a session
            sess = sessqueue.get()
        # visit the url
        sess.visit(ylink)
        # get the google plus id if the owner has an account
        for link in sess.xpath('//body/span[@itemprop = "author"]/link[@itemprop = "url"]'):
            parsedUrl = urlparse(link['href'])
            if parsedUrl.netloc == "plus.google.com":
                # parsedUrl.path returns google plus id with "/" at the
                # to remove the "/" we select all after element 0
                gpidqueue.put(parsedUrl.path[1:])
        # declaring the previous task from the queue as done
        ytqueue.task_done()
        # put the scrapper session back to the que to avoid new instantiation
        sessqueue.put(sess)


def _run_gpdataworkers():
    """this function is a api manager that will run the threads of api callers"""
    global num_threads
    for i in range(num_threads_googleplus):
        worker = Thread(target=_fetch_gpdata)
        worker.setDaemon(True)
        worker.start()


def _fetch_gpdata():
    """this function will get a googleplus id from gpidquee and get the personal data of it's owner"""
    global gpidqueue, gpdata
    while True:
        gpid = gpidqueue.get()
        gender = gp_personnaldata(gpid)
        if gender is not None:
            gpdata.put(gender)
        gpidqueue.task_done()


def _init_queues():
    global ytqueue, gpdata, gpidqueue, sessqueue
    ytqueue = Queue()
    gpdata = Queue()
    gpidqueue = Queue()
    sessqueue = Queue()
    sessqueue.put(_create_sess())

