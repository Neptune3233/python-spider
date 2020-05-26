import os, sys
import time
import requests
import urllib
import multiprocessing
import json

from tkinter import *

LOG_LINE_NUM = 0
DEFAULT_DIR = 'E:\HuabanDL'

class Window():
    def __init__(self, init_window):
        self.init_window = init_window
        self.image_pins = []

    def set_window(self):
        self.init_window.title('Huaban Board Download Tool V0.1')
        self.init_window.geometry('705x520')
        self.url_label = Label(self.init_window, text='Board URL')
        self.dir_label = Label(self.init_window, text='Basic DIR')
        self.url_text = Text(self.init_window, width=60, height=1)
        self.dir_text = Text(self.init_window, width=60, height=1)
        self.url_label.grid(row=0, column=3)
        self.dir_label.grid(row=2, column=3)
        self.url_text.grid(row=0, column=4, rowspan=1, columnspan=12)
        self.dir_text.grid(row=2, column=4, rowspan=1, columnspan=12)

        self.log_label = Label(self.init_window, text='Execute Log')
        self.log_label.grid(row=4, column=3)
        self.log_text = Text(self.init_window, width=100, height=30)
        self.log_text.grid(row=5, column=2, columnspan=12)

        self.start_btn = Button(self.init_window, text='Start',
                                width=10, command=self.start_dl)
        self.start_btn.grid(row=3, column=10)
        self.cancel_btn = Button(self.init_window, text='Cancel',
                                 width=10, command=self.cancel_dl)
        self.cancel_btn.grid(row=3, column=11)

        self.dir_text.insert(1.0, DEFAULT_DIR)

    def start_dl(self):
        url_input = self.url_text.get(0.0, END).encode().replace('\n', '')
        dir_input = self.dir_text.get(0.0, END).encode().replace('\n', '')

        if not url_input or not dir_input:
            self.output_log('Input Error!')
            return
        self.output_log('Download images from board {} to {} ...'.
                        format(url_input, dir_input))
        self.hc = HuabanCrawler(url_input, dir_input, window=self)

    def cancel_dl(self):
        pass

    def get_current_time(self):
        current_time = time.strftime('%Y-%m-%d %H:%M:%S',
                                     time.localtime(time.time()))
        return str(current_time)

    def output_log(self, log_msg):
        global LOG_LINE_NUM
        current_time = self.get_current_time()
        output_msg = current_time + ' ' + str(log_msg) + '\n'
        if LOG_LINE_NUM < 30:
            self.log_text.insert(END, output_msg)
            LOG_LINE_NUM = LOG_LINE_NUM + 1
        else:
            self.log_text.delete(1.0, 2.0)
            self.log_text.insert(END, output_msg)


class HuabanCrawler():
    def __init__(self, basic_url, basic_dir, window):
        self.basic_url = basic_url
        self.basic_dir = basic_dir
        self.window = window
        self.image_pins = []
        self.start_download()

    def start_download(self):
        make_dir(self.basic_dir)
        self.get_image_pins(max_num=30)

        make_dir(self.user_dir)
        make_dir(self.board_dir)
        json.dumps(self.user_info, file(os.path.join(self.user_dir, self.user_info['username'] + '.txt'), 'w'))
        self.window.output_log('{} pins in the board ...'.format(len(self.image_pins)))

        self.download_image()
        #self.download_image()

    def _get_home_page(self):
        response = requests.get(self.basic_url, timeout=10)
        if response.status_code == 200:
            return response
        else:
            self.window.output_log('Get Home Page ERROR!')
            self.window.output_log(self)
            del self

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

        self.user_dir = os.path.join(self.basic_dir, self.user_info['username'])
        self.board_dir = os.path.join(self.user_dir, self.board_title)
        for pin in board_dict['pins']:
            self.image_pins.append(pin)

        self._get_extend_pins()

    def download_image(self):
        pool = multiprocessing.Pool(5)
        for pin_info in self.image_pins:
            pool.apply_async(download_method, (pin_info, self.board_dir)).get()
        pool.close()
        pool.join()
        self.window.output_log('All images downloaded.')
        del self


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

if __name__ == '__main__':
    main_window = Tk()
    global window_portal
    window_portal = Window(main_window)
    window_portal.set_window()

    main_window.mainloop()





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

