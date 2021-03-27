# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import psycopg2
import re

conn = psycopg2.connect(host='localhost', dbname='YOUTUBE', user='postgres', password = "DIRAHR528", port='5432')
cursor = conn.cursor()

# driver = webdriver.Chrome(r"D:\chromedriver_win32\chromedriver.exe")  # 경로 설
driver = webdriver.Chrome() # 경로를 매번 설정하는 것이 귀찮다면 C:\Windows에 넣어주면 됨.
driver.maximize_window()
url = "https://www.youtube.com/feed/trending"

driver.get(url)

# 인기급상승동영상 정보 수
# 인기급상승동영상 url 
video_href_lst = []

for video_tag in driver.find_elements_by_css_selector("#video-title"):
    video_href_lst.append(video_tag.get_attribute("href"))

# 인기급상승동영상 재생시간 
video_time_lst = []

for video_time in driver.find_elements_by_css_selector("#overlays > ytd-thumbnail-overlay-time-status-renderer > span"):
   video_time_lst.append(video_time.get_attribute("aria-label"))

count = 0

for video_url in video_href_lst[0:50]:
    
    driver.get(video_url)
        
    title = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#container > h1 > yt-formatted-string'))).text
    
    view_count = driver.find_element_by_css_selector('#count > ytd-video-view-count-renderer').text
    view_count = int(re.sub("조회수 |,|회", "",view_count))           
    
    view_time = video_time_lst[count]                

    like = driver.find_elements_by_css_selector('a > #text')[0].get_attribute("aria-label")
    like = int(re.sub("좋아요 |,|개", "", like))
                                            
    dislike = driver.find_elements_by_css_selector('a > #text')[1].get_attribute("aria-label")
    dislike = int(re.sub("싫어요 |,|개", "", dislike))                                            

    date = driver.find_element_by_css_selector('#date > yt-formatted-string').text
                                               
    owner_sub_count = driver.find_element_by_css_selector('#owner-sub-count').text
    
    try:                                                      
        driver.find_element_by_css_selector('#more').click()      
    except:
        print(count)                                               
        
    description = driver.find_element_by_css_selector('#description > yt-formatted-string').text.replace("\n", "")
    #content
    hashtags = []
                                             
    for hashtag in driver.find_elements_by_css_selector('#description > yt-formatted-string > a'):
        if "#" in hashtag.text:
            hashtags.append(hashtag.text)
    
        
    hashtags = ' '.join(hashtags)
    
    url_code = video_url.split("=")[1]
    
    query = "INSERT INTO youtube_pop (title, view_count, video_time, like_count, dislike_count, date, owner_sub_count, description, hashtags, url_code) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    data = (title, view_count, view_time, like, dislike, date, owner_sub_count, description, hashtags, url_code)

    cursor.execute(query, data)
    count += 1

conn.commit()
conn.close()      
                                  
# meta 정보도 사용할 것인지 생각하기 
# soup.find("meta", {"name":"keywords"})["content"]  # 관련 키워드 

# 댓글 스크래핑
# 페이지 끝까지 스크롤하기 
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    time.sleep(0.5)
    
    new_height = driver.execute_script("return document.body.scrollHeight")
    
    if new_height == last_height:
        break
    
    last_height = new_height
    
