import os, re, sys
import json
import requests
import sys
import multiprocessing
import urllib
import configparser


basic_url = 'https://huaban.com/boards/{}/'


class HuabanCrawler():
    def __init__(self, basic_url):
        self.basic_url = basic_url
        self.image_pins = []

    def _get_home_page(self):
        response = requests.get(self.basic_url, timeout=10)
        if response.status_code == 200:
            return response
        else:
            print 'GET HOME PAGE ERROR!'
            sys.exit(1)

    def _get_extend_pins(self):
        last_pin_id = self.image_pins[-1]['pin_id']
        extend_url = '{}?max={}&limit=20&wfl=1'.format(self.basic_url, last_pin_id)
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
        board_dict = json.loads(app_board[0][20:-1])

        self.board_title = board_dict['title']
        self.user_info = board_dict['user']

        return board_dict

    def get_image_pins(self, max_num=20):
        resp_home = self._get_home_page()
        board_dict = self._process_data(resp_home)

        self.board_dir = os.path.join(basic_dir, self.user_info['username'] + '_' + self.board_title)
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
        pool = multiprocessing.Pool(4)
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
            print 'Image {} invalid ...'.format(pin_info['file']['key'])
            return
        image_url = 'https://hbimg.huabanimg.com/{}'.format(pin_info['file']['key'])
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

def config_parse():
    cp = configparser.ConfigParser(allow_no_value=True)
    cp.read('huaban.conf')
    configs = cp.items('HUABAN')
    config_dict = {}
    for item in configs:
        config_dict[item[0]] = item[1]
    return config_dict

if __name__ == '__main__':
    conf_dict = config_parse()
    basic_dir = conf_dict['basic_dir']
    board_id = input('Input board ID: ')

    print 'Download images from board {} to {} ...'.format(board_id, basic_dir)
    make_dir(basic_dir)
    board_url = 'https://huaban.com/boards/{}/'.format(board_id)
    hh = HuabanCrawler(board_url)
    hh.get_image_pins(max_num=30)

    make_dir(hh.board_dir)
    json.dump(hh.user_info, file(os.path.join(hh.board_dir, '___user_info.txt'), 'w'))

    print '{} pins in the board ...'.format(len(hh.image_pins))
    hh.download_image()






#                  .,,       .,:;;iiiiiiiii;;:,,.     .,,
#                rGB##HS,.;iirrrrriiiiiiiiiirrrrri;,s&##MAS,
#               r5s;:r3AH5iiiii;;;;;;;;;;;;;;;;iiirXHGSsiih1,
#                  .;i;;s91;;;;;;::::::::::::;;;;iS5;;;ii:
#                :rsriii;;r::::::::::::::::::::::;;,;;iiirsi,
#             .,iri;;::::;;;;;;::,,,,,,,,,,,,,..,,;;;;;;;;iiri,,.
#          ,9BM&,            .,:;;:,,,,,,,,,,,hXA8:            ..,,,.
#         ,;&@@#r:;;;;;::::,,.   ,r,,,,,,,,,,iA@@@s,,:::;;;::,,.   .;.
#          :ih1iii;;;;;::::;;;;;;;:,,,,,,,,,,;i55r;;;;;;;;;iiirrrr,..
#         .ir;;iiiiiiiiii;;;;::::::,,,,,,,:::::,,:;;;iiiiiiiiiiiiri
#         iriiiiiiiiiiiiiiii;;;::::::::::::::::;;;iiiiiiiiiiiiiiiir;
#        ,riii;;;;;;;;;;;;;:::::::::::::::::::::::;;;;;;;;;;;;;;iiir.
#        iri;;;::::,,,,,,,,,,:::::::::::::::::::::::::,::,,::::;;iir:
#       .rii;;::::,,,,,,,,,,,,:::::::::::::::::,,,,,,,,,,,,,::::;;iri
#       ,rii;;;::,,,,,,,,,,,,,:::::::::::,:::::,,,,,,,,,,,,,:::;;;iir.
#       ,rii;;i::,,,,,,,,,,,,,:::::::::::::::::,,,,,,,,,,,,,,::i;;iir.
#       ,rii;;r::,,,,,,,,,,,,,:,:::::,:,:::::::,,,,,,,,,,,,,::;r;;iir.
#       .rii;;rr,:,,,,,,,,,,,,,,:::::::::::::::,,,,,,,,,,,,,:,si;;iri
#        ;rii;:1i,,,,,,,,,,,,,,,,,,:::::::::,,,,,,,,,,,,,,,:,ss:;iir:
#        .rii;;;5r,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,sh:;;iri
#         ;rii;:;51,,,,,,,,,,,,,,,Neptune3233,,,,,,,,,,,,.:hh:;;iir,
#          irii;::hSr,.,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,.,sSs:;;iir:
#           irii;;:iSSs:.,,,,,,,,,,,,,,,,,,,,,,,,,,,..:135;:;;iir:
#            ;rii;;:,r535r:...,,,,,,,,,,,,,,,,,,..,;sS35i,;;iirr:
#             :rrii;;:,;1S3Shs;:,............,:is533Ss:,;;;iiri,
#              .;rrii;;;:,;rhS393S55hh11hh5S3393Shr:,:;;;iirr:
#                .;rriii;;;::,:;is1h555555h1si;:,::;;;iirri:.
#                  .:irrrii;;;;;:::,,,,,,,,:::;;;;iiirrr;,
#                     .:irrrriiiiii;;;;;;;;iiiiiirrrr;,.
#                        .,:;iirrrrrrrrrrrrrrrrri;:.
#                              ..,:::;;;;:::,,.


