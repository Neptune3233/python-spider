import os, sys
import re
import requests
import json
import multiprocessing
import urllib

from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
from HTMLParser import HTMLParser

api_url = 'https://rjartschool.com/api/work/page?size=32&page={}'
basic_url = 'https://rjartschool.com/'
basic_pick_url = 'https://rjartschool.com/pick'
basic_dir = 'E:\RjArtSchool'


class PickCrawler():
    def __init__(self, board_url, download_dir):
        self.board_url = board_url
        self.download_dir = download_dir
        self.image_urls = []

    def get_pins(self):
        response = requests.get(self.board_url, timeout=10)
        if response.status_code != 200:
            print 'Network Error !'
            sys.exit(1)
        response_text = response.content
        prog = re.compile(r'data-img="(.*?)"')
        self.image_urls = prog.findall(response_text)

    def download_images(self):
        self.get_pins()
        pins_length = len(self.image_urls)
        print '{} images in all-pic board ...'.format(pins_length)

        pool = ThreadPool(4)
        #pool = Pool(5)
        for url, image_num in zip(self.image_urls, range(1, pins_length + 1)):
            pool.apply_async(pick_download_method, (url, self.download_dir, '{} / {}'.format(image_num, pins_length)))
        pool.close()
        pool.join()

class AllCrawler():
    def __init__(self, api_url, download_dir):
        self.api_url = api_url
        self.download_dir = download_dir
        self.image_pins = []

    def get_pins(self):
        response = requests.get(self.api_url.format(1), timeout=10)
        if response.status_code != 200:
            print 'Network Error !'
            sys.exit(1)
        first_data = json.loads(response.content)
        self.total_count = int(first_data['total'])
        for index in range(self.total_count / 32 + 1):
            self.get_single_page(index + 1)

    def get_single_page(self, page_index):
        response = requests.get(self.api_url.format(page_index), timeout=10)
        page_data = json.loads(response.content)
        for single_item in page_data['data']:
            self.image_pins.append(single_item['picture'])

    def download_images(self):
        self.get_pins()
        pins_length = len(self.image_pins)
        print '{} images in all-pic board ...'.format(pins_length)

        pool = ThreadPool(4)
        #pool = Pool(5)
        for pin, image_num in zip(self.image_pins, range(1, pins_length + 1)):
            pool.apply_async(all_download_method, (pin, self.download_dir, '{} / {}'.format(image_num, pins_length)))
        pool.close()
        pool.join()

def all_download_method(pin, download_dir, image_num):
    image_url = basic_url + pin
    image_name = pin.split('/')[-1]
    image_dir = os.path.join(download_dir, image_name)
    if os.path.exists(image_dir):
        print 'Image {} {} existed ...'.format(image_num, image_name)
        return
    urllib.urlretrieve(image_url, image_dir)
    print 'Image {} {} downloaded ...'.format(image_num, image_name)

def pick_download_method(url, download_dir, image_num):
    image_name = url.split('/')[-1]
    image_dir = os.path.join(download_dir, image_name)
    if os.path.exists(image_dir):
        print 'Image {} {} existed ...'.format(image_num, image_name)
        return
    urllib.urlretrieve(url, image_dir)
    print 'Image {} {} downloaded ...'.format(image_num, image_name)

def make_dir(dir):
    is_exist = os.path.exists(dir)
    if is_exist:
        print 'DIR ' + dir + ' existed ...'
    else:
        os.makedirs(dir)

if __name__ == '__main__':
    crawl_all = input('Crawl all-pic board ? ')
    crawl_pick = input('Crawl pick-pic board ? ')

    if crawl_all:
        print 'Begin to crawl the all-pic page ...'
        download_dir = basic_dir
        make_dir(download_dir)
        ac = AllCrawler(api_url, download_dir)
        ac.download_images()

    if crawl_pick:
        print 'Begin to crawl the pick-pic page ...'
        download_dir = os.path.join(basic_dir, 'Pick')
        make_dir(download_dir)
        pc = PickCrawler(basic_pick_url, download_dir)
        pc.download_images()

    print 'Job done ...'