#!/usr/bin/env python
# Schedme v1.0
# Coded by: github.com/thelinuxchoice/schedme
# Image upload/resize adapted from: github.com/b3nab/instapy-cli

import requests
import random
from random import randint
import hmac
import hashlib
import uuid
import json
import time
import os
import datetime
from PIL import Image
import platform

ig_sig="4f8732eb9ba7d1c8e8897a75d6474d4eb3f5279137431b2aafb71fafe2abe178"
ENDPOINT_URL = 'https://i.instagram.com/api/v1'
HEADERS = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
user_agent="Instagram 10.26.0 Android (18/4.3; 320dpi; 720x1280; Xiaomi; HM 1SW; armani; qcom; en_US"
guid = str(uuid.uuid1())
device_id = 'android-%s' % guid
session = requests.Session()
session.headers.update({'User-Agent': user_agent})
media_id=''
caption=''
accounts_list=[]
passwords_list=[]
path_img_list=[]
amount_accounts=0
datetime_list=[]
date_list=[]
MIN_ASPECT_RATIO = 0.80
MAX_ASPECT_RATIO = 1.91

if platform.system().lower() == "windows":
    os.system('color')
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

try:
    input = raw_input
except NameError:
    pass

def banner():


        print('\033[1;77m      ____       _              _                 ')
        print('\033[1;77m     / ___|  ___| |__   ___  __| |\033[1;92m_ __ ___   ___  \033[0m')
        print('\033[1;77m     \___ \ / __| \'_ \ / _ \/ _` |\033[1;92m \'_ ` _ \ / _ \ \033[0m')
        print('\033[1;77m      ___) | (__| | | |  __/ (_| |\033[1;92m | | | | |  __/ \033[0m')
        print('\033[1;77m     |____/ \___|_| |_|\___|\__,_|\033[1;92m_| |_| |_|\___|\033[0mv1.0 ')

        print('\n\033[1;77m     github.com/thelinuxchoice/schedme\033[0m\n')


def login(username, password):
        data = json.dumps({
            'device_id': device_id,
            '_uuid': guid,
            'username': username,
            'password': password,
            '_csrftoken': 'missing',
            'login_attempt_count': 0
        })

        sig = hmac.new(ig_sig.encode('utf-8'),data.encode('utf-8'), hashlib.sha256).hexdigest()
        payload = 'signed_body=%s.%s&ig_sig_key_version=4' % (sig, data)
        resp = session.post(ENDPOINT_URL + '/accounts/login/', payload, headers=HEADERS)
        resp_json = resp.json()

        if resp_json.get('status') != 'ok':
            raise IOError(resp_json.get('message'))

def upload_photo(path,caption):

        data = {
            '_csrftoken': 'missing',
            'upload_id': int(time.time()),
            'device_id': device_id,
            '_uuid': guid,
            'image_compression': '{"lib_name":"jt","lib_version":"1.3.0","quality":"70"}',
            'filename': 'pending_media_{}.jpg'.format(time.time())
        }
        files = {'photo': open(path, 'rb')}
        resp = session.post(ENDPOINT_URL + '/upload/photo/', data, files=files)
        resp_json = resp.json()

        media_id = resp_json.get('upload_id')

        if media_id is None:
            raise IOError(resp_json.get('message'))

        configure_photo(media_id,caption)


def configure_photo(media_id, caption):
        data = json.dumps({
            'device_id': device_id,
            '_uuid': guid,
            '_csrftoken': 'missing',
            'media_id': media_id,
            'caption': caption,
            'device_timestamp': time.time(),
            'source_type': "5",
            'filter_type': "0",
            'extra': '{}',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        })

        sig = hmac.new(ig_sig.encode('utf-8'),data.encode('utf-8'), hashlib.sha256).hexdigest()

        payload = 'signed_body={}.{}&ig_sig_key_version=4'.format(sig,quote(data))

        resp = session.post(ENDPOINT_URL + '/media/configure/', payload, headers=HEADERS)
        resp_json = resp.json()

        if resp_json.get('status') != 'ok':
            raise IOError(resp_json.get('message'))


def cropImage(left, top, right, bottom, imageObject):
        area = (left, top, right, bottom)
        return imageObject.convert('RGB').crop(area)

def fixAspectRatio(original_img):
        width, height = original_img.size
        aspect_ratio = width/height

        if aspect_ratio < MIN_ASPECT_RATIO:
            # Add equal black borders on the right and left 
            new_width = MIN_ASPECT_RATIO * height
            left = 0 - ((new_width - width) / 2)
            top = 0
            right = width + ((new_width - width) / 2)
            bottom = height
            newImage = cropImage(left, top, right, bottom, original_img)
            return newImage
        elif aspect_ratio > MAX_ASPECT_RATIO:
            # Add equal black borders on top and bottom 
            new_height = width / MAX_ASPECT_RATIO
            left = 0
            top = 0 - ((new_height - height) / 2)
            right = width
            bottom = height + ((new_height - height) / 2)
            newImage = cropImage(left, top, right, bottom, original_img)
            return newImage
        else:
            return original_img

def adjust_image(pathFile):

        optimizedImage = None
        original_image_object = Image.open(pathFile)
        print("\033[1;77m[\033[0m\033[1;31m+\033[0m\033[1;77m]\033[0m\033[1;93m Fixing aspect ratio if not according to accepted dimensions..\033[0m")
        new_object = fixAspectRatio(original_image_object)
        print("\033[1;77m[\033[0m\033[1;31m+\033[0m\033[1;77m]\033[0m\033[1;93m Generating and saving optimized image..\033[0m")
        new_object.save("optimized.jpg", "JPEG", quality=100, optimize=True, progressive=True)
        optimizedImage = "optimized.jpg"


def config_accounts():
   
       amount_accounts=int(input('\033[1;77m[\033[0m\033[1;31m+\033[0m\033[1;77m]\033[0m\033[1;93m Amount accounts to schedule: \033[0m'))

       if amount_accounts > 1:

         for x in range(amount_accounts):
            num=x+1          
            accounts_list.append(input('\033[1;77m[\033[0m\033[1;31m+\033[0m\033[1;77m]\033[0m\033[1;93m Username account\033[0m\033[1;77m %d: \033[0m' % num))
            passwords_list.append(input('\033[1;77m[\033[0m\033[1;31m+\033[0m\033[1;77m]\033[0m\033[1;93m Password account\033[0m\033[1;77m %d: \033[0m' % num))


       else:
            accounts_list.append(input('\033[1;77m[\033[0m\033[1;31m+\033[0m\033[1;77m]\033[0m\033[1;93m Username account: \033[0m'))
            passwords_list.append(input('\033[1;77m[\033[0m\033[1;31m+\033[0m\033[1;77m]\033[0m\033[1;93m Password account: \033[0m'))
    
       config_data(accounts_list)
       print('\033[1;77m[\033[0m\033[1;31m+\033[0m\033[1;77m]\033[0m\033[1;93m Schedme started\033[0m')
       check_time()
def config_data(accounts_list):

        for x,e in enumerate(accounts_list):

         img=1
         while True:

           path_images=input('\033[1;77m[\033[0m\033[1;31m+\033[0m\033[1;77m]\033[0m\033[1;93m Account\033[0m\033[1;77m %s\033[0m\033[1;93m, Image\033[0m\033[1;77m %d\033[0m\033[1;93m Path\033[0m\033[1;77m (Only JPG)\033[0m\033[1;93m: \033[0m' % (accounts_list[x],img))
           path_img_list.append([e,path_images])
           caption=input('\033[1;77m[\033[0m\033[1;31m+\033[0m\033[1;77m]\033[0m\033[1;93m Account\033[0m\033[1;77m %s\033[0m\033[1;93m, Image\033[0m\033[1;77m %d\033[0m\033[1;93m Caption: \033[0m' % (accounts_list[x],img))
           date_list=input('\033[1;77m[\033[0m\033[1;31m+\033[0m\033[1;77m]\033[0m\033[1;93m Account\033[0m\033[1;77m %s\033[0m\033[1;93m, Image\033[0m\033[1;77m %d\033[0m\033[1;93m Date\033[0m\033[1;77m (DD/MM/YYYY): \033[0m' % (accounts_list[x],img))
           date_hour_list=input('\033[1;77m[\033[0m\033[1;31m+\033[0m\033[1;77m]\033[0m\033[1;93m Account\033[0m\033[1;77m %s\033[0m\033[1;93m, Image\033[0m\033[1;77m %d\033[0m\033[1;93m Hour\033[0m\033[1;77m (HH:MM): \033[0m' % (accounts_list[x],img))
           datetime_list.append([e,date_list,date_hour_list, path_images, caption])
           img=img+1
           new_img=input('\033[1;77m[\033[0m\033[1;31m+\033[0m\033[1;77m]\033[0m\033[1;93m Add new img for account\033[0m\033[1;77m %s\033[0m\033[1;93m ?\033[0m\033[1;92m [\033[0m\033[1;77my/n\033[0m\033[1;92m]\033[0m ' % accounts_list[x])
           if new_img in 'nN':
                  break 
          

def check_time():


        while True:
         current_time=datetime.datetime.now() 

         for z,w in enumerate(datetime_list): 

           if str("%02d" %(current_time.day))+'/'+str("%02d" %(current_time.month))+'/'+str(current_time.year) in w:

            for a,b in enumerate(datetime_list[z]):

             if str("%02d" %(current_time.hour))+':'+str("%02d" %(current_time.minute)) in b:

                print('\033[1;77m[\033[0m\033[1;31m+\033[0m\033[1;77m]\033[0m\033[1;93m Account:\033[0m\033[1;77m{}\033[0m\033[1;93m date:\033[0m\033[1;77m{}\033[0m\033[1;93m time:\033[0m\033[1;77m{}\033[0m'.format(datetime_list[z][0],datetime_list[z][1],datetime_list[z][2]))

                for c,d in enumerate(accounts_list):
                    if d == datetime_list[z][0]:
                         print('\033[1;77m[\033[0m\033[1;31m+\033[0m\033[1;77m]\033[0m\033[1;93m Preparing post for account\033[0m\033[1;77m {0}\033[0m\033[1;93m, image\033[0m\033[1;77m {1}\033[0m'.format(d,datetime_list[z][3]))
                         login(d,passwords_list[c])
                         adjust_image(datetime_list[z][3])
                         upload_photo("optimized.jpg",datetime_list[z][4])
                         os.remove("optimized.jpg") 

                datetime_list.pop(z)
                current_time=None
                current_time=datetime.datetime.now()
 
         if len(datetime_list) == 0:
                print('\033[1;77m[\033[0m\033[1;31m+\033[0m\033[1;77m]\033[0m\033[1;93m No remaining posts, exiting\033[0m')
                break
         time.sleep(5)
         current_time=None 
banner()
config_accounts()
