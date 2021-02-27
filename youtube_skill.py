#!/usr/bin/python3
# Requires PyAudio.
# -*- coding: utf-8 -*-

#Tạo thư mục mp3 trong thư mục vietbot

#Xử lý file và thư mục
import os
from os import listdir
from os import path
import sys
import re
#Xử lý thời gian
import time
import datetime
#Xử lý url
import pafy
import requests
import urllib
import re
import urllib.request
import urllib.parse
import datetime
#So sánh gần giống 2 chuỗi
from fuzzywuzzy import fuzz
#TTS Engine
from speaking import speak, short_speak 
from termcolor import colored
import random
#STT Engine
import stt_gg_cloud
import stt_gg_free
import stt_fpt
import stt_viettel
#Xử lý thread
import threading
#Play Audio và đọc file MP3
import pygame
from pygame import mixer
from mutagen.mp3 import MP3
mixer.init()
from pydub import AudioSegment

#Gọi Hotword
import pyaudio
import struct
import pvporcupine
#Đọc file config
import gih
sensitivities =gih.get_config('sensitivities')
keyword_paths=gih.get_config('keyword_paths')
re_speaker= gih.get_config('re_speaker')
if re_speaker == 1:
    import pixels
#Điều khiển led
    led_xanh = gih.get_config('led_xanh')
    led_do = gih.get_config('led_do')
    try:
        gpio.init()
        gpio.setcfg(led_xanh, 1)
        gpio.setcfg(led_do, 1)
        pixels.pixels.off()     
    except:
        pass
elif re_speaker == 2:  
    import usb_pixel_ring_v2 as led_control  
    led_control.find().off()
elif re_speaker == 3:
    from pixel_ring import pixel_ring
    pixel_ring.off()
volume=gih.get_config('volume')
stt_engine= gih.get_config('stt_engine')
ggcre = gih.get_config('google_application_credentials')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ggcre
request_offline=gih.get_request('request_offline')
request_online=gih.get_request('request_online')
request_music=gih.get_request('request_music')
request_next =gih.get_request('request_next')
request_pause =gih.get_request('request_pause')
request_continue =gih.get_request('request_continue')
request_reply =gih.get_request('request_reply')
request_exit =gih.get_request('request_exit')
request_adjust_incrase_volume=gih.get_request('request_adjust_incrase_volume')
request_adjust_decrase_volume=gih.get_request('request_adjust_decrase_volume')
request_reply=gih.get_request('request_reply')
mp3_list_files =os.listdir('mp3/')
compare_percent=gih.get_config('compare_percent')
data ='Anh muốn em sống sao' 


def main(data):

    print('[BOT]: XỬ LÝ CÂU LỆNH CHƠI NHẠC YOUTUBE: '+data)    
    if re_speaker == 1:
        pixels.pixels.off() 
    elif re_speaker ==2:
        led_control.find().off()       
    elif re_speaker ==3:    
        pixel_ring.off()                                    
    music_command = str([s for s in request_music if s in data])
    music_command = music_command.replace("['", "")
    music_command = music_command.replace("']", "") 
    data = data.replace(music_command,'')
    online_command = str([s for s in request_online if s in data])
    online_command = online_command.replace("['", "")
    online_command = online_command.replace("']", "") 
    data = data.replace(online_command,'')                
    offline_command = str([s for s in request_offline if s in data])
    offline_command = offline_command.replace("['", "")
    offline_command = offline_command.replace("']", "") 
    data = data.replace(offline_command,'')                  
    data = data.upper()
    if len(data) >0:
        a = 0
        for i in mp3_list_files:
            song_title=i.replace('_','')
            song_title=song_title.replace('-','')
            song_title=song_title.replace('-','')                
            song_title=song_title.replace('.mp3','')                
            song_title=song_title.upper()
            match_ratio=fuzz.token_sort_ratio(data, song_title)
            # print(data)
            # print(song_title)
            # print(str(match_ratio))
            if match_ratio > compare_percent:                    
                a=i
                break
        if a ==0:
            print('Nhạc cần phát '+data+' không có sẵn, phát nhạc trực tuyến')
            short_speak('Nhạc cần phát '+data+' không có sẵn, phát nhạc trực tuyến')
            url = "http://www.youtube.com/watch?v="+get_result(data)
            info = pafy.new(url)
            title = info.title
            file_name_m4a ='/tmp/'+get_result(data)+'.m4a'
            file_name_mp3 ='mp3/'+title+'.mp3'            
            audio = info.m4astreams[-1]
            audio = info.getbestaudio(preftype="m4a")
            audio.download(file_name_m4a, quiet=True)
            try:
                track = AudioSegment.from_file(file_name_m4a,'m4a')
                print('CONVERTING: ' + str(title))
                file_handle = track.export(file_name_mp3, format='mp3')
            except:
                print("ERROR CONVERTING " + str(file_name_m4a))
           # playback(file_name)
            run_thread(playback,file_name_mp3)
        else:
            nhac=a.replace('.mp3',"")
            nhac=nhac.replace('-'," ")
            nhac=nhac.replace('_'," ")
            nhac=nhac.replace('.'," ")
            print ('Nhạc cần phát  '+nhac+' có sẵn, phát nhạc cục bộ')
            speak('Nhạc cần phát  '+nhac+' có sẵn, phát nhạc cục bộ')                        
            run_thread(playback,'mp3/'+a)
        time.sleep(1)
        loop()
    else:
        print('Không có tên bài nhạc, quay lại')
        short_speak('Không có tên bài nhạc quay lại')
        pass        
   
        
def get_result(data):
    global list_results
    data = data.lower()
    query_string = urllib.parse.urlencode({"search_query" : data})
    html_content = urllib.request.urlopen("https://www.youtube.com/results?" + query_string)
    list_results = re.findall(r"watch\?v=(\S{11})", html_content.read().decode())
    # print(list_results)
    return list_results[0]
        
def playback(data):    
    if re_speaker == 1:
        pixels.pixels.speak() 
    elif re_speaker ==2:
        led_control.find().speak()       
    elif re_speaker ==3:    
        pixel_ring.speak()                                    
    global player
    player = mixer.music
    player.load(data)
    player.set_volume(volume)            
    player.play()
    audio = MP3(data)
    t = float (audio.info.length)
    print ('Time delay :'+ str(t))
    time.sleep(round(t)+1)                                
    # deamon = False
    return player
def loop():    
    print(colored('[BOT]: CHỜ RA LỆNH...','green'))
    porcupine = None
    pa = None
    audio_stream = None    
    # try:
        # porcupine = pvporcupine.create(keywords=keywords,sensitivities=sensitivities)
    porcupine = pvporcupine.create(keyword_paths=keyword_paths,sensitivities=sensitivities)        
    pa = pyaudio.PyAudio()
    audio_stream = pa.open(
                    rate=porcupine.sample_rate,
                    channels=1,
                    format=pyaudio.paInt16,
                    input=True,
                    frames_per_buffer=512)
    # short_speak(random.choice(list_response_ask_wakeup))           
    while str(player.get_busy()) =='1':      
        # pcm = audio_stream.read(512)
        pcm = audio_stream.read(512,exception_on_overflow=False)                
        exception_on_overflow = False
        pcm = struct.unpack_from("h" * 512, pcm)
        keyword_index = porcupine.process(pcm)
        # print(str(keyword_index))
        if keyword_index >= 0:
            if re_speaker == 1:
                pixels.pixels.wakeup() 
            elif re_speaker ==2:
                led_control.find().wakeup()
            elif re_speaker ==3:    
                pixel_ring.wakeup()                    
            # play_ding()
            # print('[BOT]: Phát hiện khẩu lệnh đúng '+ keywords[keyword_index] +'xin mời ra lệnh')
            porcupine.delete()
            pa.terminate()
            audio_stream.close()
            voice_control()
            break
    else: 
        short_speak('Đã phát nhạc xong')        
        daemon = False
        pass            
def voice_control():           
    current_volume = player.get_volume()
    player.pause()                
    data = getText()
    if data is not None:
        data = data.upper()        
        if any(item in data for item in request_adjust_incrase_volume):         
            if player.get_volume() <0.7:
                new_volume = player.get_volume()+0.3
                player.set_volume(new_volume)                
                #run_thread(speak,'Giá trị âm lượng hiện tại là: '+str(player.get_volume()))                        
                player.unpause()
                back_to_loop()
                pass
            else:
                player.set_volume(1.0)                
                player.unpause()                    
                #run_thread(speak,'Giá trị âm lượng hiện tại là: '+str(player.get_volume()))                                                
                back_to_loop()
                pass
        elif any(item in data for item in request_adjust_decrase_volume):         
            if player.get_volume() >0.3:
                new_volume = player.get_volume()-0.3
                player.set_volume(new_volume)                
                player.unpause()                    
                #run_thread(speak,'Giá trị âm lượng hiện tại là: '+str(player.get_volume()))                                                
                back_to_loop()
                pass                        
            else:
                player.set_volume(0.1)                
                player.unpause()                    
                #run_thread(speak,'Giá trị âm lượng hiện tại là: '+str(player.get_volume()))                                                
                back_to_loop()
                pass                        
        elif any(item in data for item in request_reply): 
            player.rewind()                
            back_to_loop()                
            pass                
        elif any(item in data for item in request_pause): 
            player.pause()
            back_to_loop()
            pass                                
        elif any(item in data for item in request_continue): 
            player.unpause()
            back_to_loop()
            pass                                
        elif any(item in data for item in request_exit): 
            player.stop()
            daemon = False                                
            pass                                
        else:
            player.set_volume(current_volume)            
            player.unpause()
            back_to_loop()
            pass                
    else:
        player.set_volume(current_volume)
        player.unpause()
        back_to_loop()
        pass

def getText():
    #time.sleep(1)
#   Dùng STT Google Free
    if stt_engine == 0:
        data=input("Nhập lệnh cần thực thi:  ")
    elif stt_engine == 1:
        print(colored('---------------DÙNG STT GOOGLE FREE-----------------------','red'))
        data = stt_gg_free.main() 
#   Dùng STT Google Cloud
    elif stt_engine == 2:
        print(colored('---------------DÙNG STT GOOGLE CLOUD-----------------','green'))
        data = stt_gg_cloud.main()
#   Dùng STT VTCC
    elif stt_engine == 3:
        print(colored('---------------DÙNG STT VIETTEL-------------','blue'))        
        data = stt_viettel.main()        
    elif stt_engine == 4:
        print(colored('---------------DÙNG STT VIETTEL-------------','blue'))        
        data = stt_viettel_test.main()
#   Dùng STT FPT
    elif stt_engine == 5:
        print(colored('---------------DÙNG STT FPT-------------','yellow'))
        data = stt_fpt.py.main()
#   Sử dụng text input
    return data                           

def run_thread(func,data):
        t = threading.Thread(target = func, args = (data,), daemon = True) 
        t.setDaemon(True)
        t.start()
        # t.join()

def back_to_loop():
    if re_speaker == 1:
        pixels.pixels.speak() 
    elif re_speaker ==2:
        led_control.find().speak()       
    elif re_speaker ==3:    
        pixel_ring.speak()                                    
    loop()

if __name__ == '__main__':
    main(data)

