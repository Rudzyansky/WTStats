#!/usr/bin/env python3

import os
from enum import Enum
from time import sleep
from json import dumps
from datetime import datetime
from configparser import ConfigParser

import requests
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

CONFIG_PATH: str = '/opt/wtstats/data/config.ini'

CFG: ConfigParser


def load():
    global CFG
    CFG = ConfigParser()
    try:
        CFG.read_file(open(CONFIG_PATH, 'r'))
    except OSError:
        CFG.read_dict({'Miner': {'id': ''}, 'Telegram': {'token': '', 'chat_id': '', 'message_id': ''}})
        CFG.write(open(CONFIG_PATH, 'w'))
        print('Fill Config File')
        exit(1)


def update_message_id(message_id):
    global CFG
    CFG['Telegram']['message_id'] = str(message_id)
    CFG.write(open(CONFIG_PATH, 'w'))


class MinerType(Enum):
    WEB = '#/account'
    API = 'api/accounts'


class TelegramAction(Enum):
    SEND_PHOTO = 'sendPhoto'
    EDIT_MESSAGE_MEDIA = 'editMessageMedia'


class TelegramError(Enum):
    NOT_FOUND = 'Bad Request: message to edit not found'


def get_miner_url(type: MinerType) -> str:
    return f"https://eth.clona.ru/{type.value}/{CFG['Miner']['id']}"


def get_tg_url(action: TelegramAction) -> str:
    return f"https://api.telegram.org/bot{CFG['Telegram']['token']}/{action.value}"


def get_options() -> Options:
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--width=640')
    options.add_argument('--height=1280')
    return options


def generate_text(data) -> str:
    found = data.get('stats').get('blocksFound', 0)
    share = datetime.fromtimestamp(data.get('stats').get('lastShare', 0)).strftime('%H:%M %d.%m')
    current = data.get('currentHashrate') / 1000000.0  # 30 minutes
    average = data.get('hashrate') / 1000000.0  # 3 hours
    return f'`Found   `*{found}*\n`Share   `*{share}*\n`Current `*{current:.2f}* _MH/s_\n`Average `*{average:.2f}* _MH/s_'


def edit_message(text, photo) -> requests.Response:
    media = {'type': 'photo', 'media': 'attach://photo', 'caption': text, 'parse_mode': 'Markdown'}
    params = {'chat_id': CFG['Telegram']['chat_id'], 'message_id': CFG['Telegram']['message_id'], 'media': dumps(media)}
    return requests.post(get_tg_url(TelegramAction.EDIT_MESSAGE_MEDIA), params, files={'photo': photo})


def new_message(text, photo) -> requests.Response:
    params = {'chat_id': CFG['Telegram']['chat_id'], 'caption': text, 'parse_mode': 'Markdown'}
    return requests.post(get_tg_url(TelegramAction.SEND_PHOTO), params, files={'photo': photo})


def do_it(text, path) -> requests.Response:
    def extract_error(response):
        return response.json().get('description')

    resp = edit_message(text, open(path, 'rb'))
    if resp.ok:
        return resp
    if extract_error(resp) == TelegramError.NOT_FOUND.value:
        resp = new_message(text, open(path, 'rb'))
        if resp.ok:
            update_message_id(resp.json().get('result').get('message_id'))
            return resp
    raise RuntimeError(extract_error(resp))


def take_screenshot(path: str = '/tmp/screenshot.png') -> str:
    driver = Firefox(options=get_options(), service_log_path=os.devnull)
    sleep(1)
    driver.get(get_miner_url(MinerType.WEB))
    sleep(3)
    driver.find_elements_by_class_name('container')[1].screenshot(path)
    driver.quit()
    return path


def take_text() -> str:
    return generate_text(requests.get(get_miner_url(MinerType.API)).json())


if __name__ == '__main__':
    load()
    path = take_screenshot()
    text = take_text()
    do_it(text, path)
