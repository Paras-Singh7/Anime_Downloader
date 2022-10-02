from IPython.display import display, HTML
display(HTML('<style> .container{width : 100%} </style>'))

import subprocess
import os
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

url = input('Enter animefreak.site link here: ') #https://animefreak.site/anime/sword-art-online-alicization-war-of-underworld

from_ep = int(input('Download from episode no: '))

class json_io:
    
    def read(name):
        with open(name, 'r') as f:
            data = json.load(f)
            f.close()
        return data
            
    def write(name, mode, fdata):
        if mode == 'a':
            data = json_io.read(name)
            data.update(fdata)
        else:
            data = fdata
        with open(name, 'w') as f:
            s = json.dumps(data, indent = 4)
            print(s, file = f)

class Anime:
    
    def __init__(self, url):
        self.url = url
        self.link_name = url.split('/')[-1]
        self.name = self.link_name.replace('-', ' ').title()
        self.episode = self.extract_ep()
        
    def extract_ep(self):
        
        if 'animefreak.site' in  self.url:
            episode = {}
            t_url = f'https://animefreak.site/watch/{self.link_name}-episode-1'
            t_r = requests.get(t_url)
            t_soup = BeautifulSoup(t_r.content, 'html.parser')
            for i in t_soup.find_all('a', {'class' : ['ssl-item ep-item', 'ssl-item ep-item active']}):
                episode[i.get('title')] = f"https://animefreak.site{i.get('href')}"
            episode = dict(reversed(episode.items()))

            return episode
        
        if 'gogoanime2.org' in  self.url:
            episode = {}
            t_r = requests.get(self.url)
            t_soup = BeautifulSoup(t_r.content, 'html.parser')
            for i in t_soup.find_all('div', {'class':'anime_video_body'})[0].find_all('a'):
                episode[i.find('div').text.replace('  ','')] = f"https://ww3.gogoanime2.org{i.get('href')}"

            return episode

class browser:
    
    __path = 'C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe'
    __headers =  {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win 64; x64; rv:84.0) Gecko/20100101 FireFox/84.0',
    'Accept-Language' : 'en-GB,en;q=0.5',
    'Referer' : 'https:google.com',
    'DNT' : '1'
    }
    
    def initiate(url):
        
        options = Options()
        options.binary_location = browser.__path
        options.add_argument('--headless')
        
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'performance' : 'ALL'}
        
        driver = webdriver.Chrome(executable_path = 'backend/chromedriver.exe',desired_capabilities = caps, options = options)
        driver.request_interceptor = browser.__headers
        
        driver.get(url)
        sleep(2)
        perf = driver.get_log('performance')
        driver.close()
        
        return perf

def extract_m3u8(y):
    for a in y:
        if '.m3u8' in str(a):
            for b in str(a).split(','):
                if '.m3u8' in b:
                    link = b[7:-2]
                    break
            break
    return link

def cli_command(li, name):
    
    link = extract_m3u8(li)
    
    curr_dir = os.getcwd()
    ffmpeg_path = curr_dir + '\\backend\\ffmpeg\\bin\\ffmpeg'
    op = curr_dir + '\\' + output_path + '\\' + name + '.mkv'

    string = f"{ffmpeg_path} -i {link} -c copy -bsf:a aac_adtstoasc {op}"
    
    return string

anime = Anime(url)

log = {anime.name : { 'url' : anime.url,
              'episode': anime.episode}}

json_io.write(f'{anime.name}.json', 'w', log)

output_path = f"Download\\{anime.name.replace(' ', '_')}"
if not os.path.exists(output_path):
    os.mkdir(output_path)

for i in log:
    for j in list(log[i]['episode'])[from_ep:]:

        name = j.split()[-1]
        print(name)
        web_link = log[i]['episode'][j]

        y = browser.initiate(web_link)

        cmd = cli_command(y, name)

        os.system(cmd)
        
        log[i]['episode'].pop(j)

        json_io.write(f'{anime.name}.json', 'w', log)

    os.remove(f'{anime.name}.json')
