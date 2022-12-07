from IPython.display import display, HTML
display(HTML('<style> .container{width:100%} </style>'))

import os
import math
import requests
import numpy as np
from bs4 import BeautifulSoup
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import  Options

ffmpeg_path = 'backend/ffmpeg/bin/ffmpeg'
browser_path = 'C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe'
chromedriver_path = 'backend/chromedriver.exe'

def load(url):
    options = Options()
    options.binary_location = browser_path
    options.add_argument('--headless')
    driver = webdriver.Chrome(service = Service(chromedriver_path), options = options)
    driver.get(url)
    req = driver.requests
    return req

def batch(li, m):
    split_in = math.ceil(len(li) / m) 
    splits = np.array_split(li, split_in)
    return splits

def episodes(url):
    
    r = requests.get(url)
    s = BeautifulSoup(r.content, 'html.parser')
    
    if 'https://animefreak.site/' in url:
        name = s.find('h2').text
        ep_link = s.find('a', {'class':'btn btn-radius btn-primary btn-play'}).get('href')
        ep_list = []
        r = requests.get('https://animefreak.site/' + ep_link)
        s = BeautifulSoup(r.content, 'html.parser')
        for ele in s.find_all('a', {'class': ['ssl-item ep-item', 'ssl-item ep-item active']}):
            ep_list.append('https://animefreak.site/' + ele.get('href'))
        ep_list.reverse()
        return name, ep_list
    
    if 'https://ww3.gogoanime2.org/' in url:
        name = s.find('div', {'class':'anime_info_episodes'}).find('h2').text
        ep_list = []
        for ele in s.find('ul', {'id' : 'episode_related'}).find_all('a'):
            ep_list.append('https://ww3.gogoanime2.org' + ele.get('href').strip())
        return name, ep_list
    
    if 'https://kissanime.com.ru/' in url:
        name = name = s.find('h2').text
        ep_list = []
        for ele in s.find('div', {'class':'listing listing8515 full'}).find_all('a'):
            ep_list.append(ele.get('href').strip())
        ep_list.reverse()
        return name, ep_list
    
    if 'https://animeheaven.ru/' in url:
        name = s.find('h1').text
        ep_list = []
        for ele in s.find('div', {'class':'infoepbox'}).find_all('a'):
            ep_list.append(ele.get('href').strip())
        return name, ep_list

def mk_dir(name):
    name = name.replace(':', ' ').strip()
    if not os.path.isdir(f'Download/{name}') and name != '':
        os.mkdir(f'Download/{name}')
    return f'Download/{name}'

def m3u8(url):
    
    r = load(url)
    for ele in r:
        if 'm3u8' in str(ele):
            return ele.url

def cli_command(name, link):
    curr_dir = os.getcwd()
    ffmpeg_path = f'{curr_dir}\\backend\\ffmpeg\\bin\\ffmpeg'
    op = f'{curr_dir}\\{output_path}\\{name}.mkv'
    string = f'{ffmpeg_path} -i "{link}" -c copy -bsf:a aac_adtstoasc "{op}"'
    return string

url = input('Enter anime url: ')
from_ep = int(input('Download from episode no: '))

name, ep_list = episodes(url)
total_episodes = len(ep_list)

output_path = mk_dir(name)

os.system(cli_command(str(from_ep), m3u8(ep_list[from_ep])))
