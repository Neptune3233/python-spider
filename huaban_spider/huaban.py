import os
import re
import json
import requests
import sys
import multiprocessing
import urllib


base_dir = 'E:\Huaban_DL'


class Huaban():
    def __init__(self, base_url):
        self.base_url = base_url
        self.image_pins = []

    def _get_home_page(self):
        response = requests.get(self.base_url, timeout=10)
        if response.status_code == 200:
            return response
        else:
            print 'GET HOME PAGE ERROR!'
            sys.exit(1)

    def _get_extend_pins(self):
        last_pin_id = self.image_pins[-1]['pin_id']
        extend_url = '{}?max={}&limit=20&wfl=1'.format(self.base_url, last_pin_id)
        response = requests.get(extend_url, timeout=5)
        board_dict = self._process_data(response)
        for pin in board_dict['pins']:
            self.image_pins.append(pin)
        if len(board_dict['pins']) > 0:
            self._get_extend_pins()
        return None

    def _process_data(self, resp_page):
        prog = re.compile(r'app\.page\["board"\].*')
        app_board = prog.findall(resp_page.content)
        board_str = app_board[0][20:-1]
        board_dict = eval(board_str[20:-1])

        self.board_title = board_dict['title']
        self.user_info = board_dict['user']

        return board_dict

    def get_image_pins(self, max_num=20):
        resp_home = self._get_home_page()
        board_dict = self._process_data(resp_home)

        self.user_dir = os.path.join(base_dir, self.user_info['username'])
        self.board_dir = os.path.join(self.user_dir, self.board_title)
        for pin in board_dict['pins']:
            self.image_pins.append(pin)

        self._get_extend_pins()

    def download_method(self, pin_info):
        pin_type = pin_info['file']['type'].split('/')
        if pin_type[0] == 'image':
            if pin_type[1] == 'png' and pin_info['file']['width'] == 658 and pin_info['file']['height'] == 658:
                return

            image_url = 'https://hbimg.huabanimg.com/{}'.format(pin_info['file']['key'])
            file_name = '{}.{}'.format(pin_info['file']['key'], pin_type[1])
            file_dir = os.path.join(self.board_dir, file_name)
            urllib.urlretrieve(image_url, file_dir)
            print 'Image {} downloaded!'.format(pin_info['file']['key'])

    def download_image(self):
        pool = multiprocessing.Pool(10)
        for pin_info in self.image_pins:
            pool.apply_async(download_method, (pin_info, self.board_dir))
        pool.close()
        pool.join()
        """
        for pin_info in self.image_pins:
            self.download_method(pin_info)
                    """
        print('All images downloaded.')

def download_method(pin_info, board_dir):
    pin_type = pin_info['file']['type'].split('/')
    if pin_type[0] == 'image':
        if pin_type[1] == 'png' and pin_info['file']['width'] == 658 and pin_info['file']['height'] == 658:
            return
        image_url = 'https://hbimg.huabanimg.com/{}'.format(pin_info['file']['key'])
        board_dir = os.path.join(base_dir, board_dir)
        file_name = '{}.{}'.format(pin_info['file']['key'], pin_type[1])
        file_dir = os.path.join(board_dir, file_name)
        if os.path.exists(file_dir):
            print 'Image {} existed ...'.format(pin_info['file']['key'])
            return
        urllib.urlretrieve(image_url, file_dir)
        print 'Image {} downloaded ...'.format(pin_info['file']['key'])

def make_dir(dir):
    is_exist = os.path.exists(dir)
    if not is_exist:
        os.makedirs(dir)

if __name__ == '__main__':
    make_dir(base_dir)
    #is_board = input('Download from board? ')
    #if not is_board:
    #    sys.exit(1)
    board_id = '59866280'
    #board_id = input('Input board id: ')
    board_url = 'https://huaban.com/boards/{}/'.format(board_id)
    hh = Huaban(board_url)
    hh.get_image_pins(30)

    make_dir(hh.user_dir)
    make_dir(hh.board_dir)
    json.dump(hh.user_info, file(os.path.join(hh.user_dir, hh.user_info['username'] + '.txt'), 'w'))

    print '{} pins in the board ...'.format(len(hh.image_pins))
    hh.download_image()


