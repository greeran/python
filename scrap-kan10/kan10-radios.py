import requests
from bs4 import BeautifulSoup
import ssl
import re

player_url_list=[]
image_url_list=[]

def handle_image_content(images_content):
    for image_content in images_content:
        images=image_content.findAll('img')
        for image in images:
            image_url_list.append(image['src'])

def handle_metadata(metadata_url):
    metadata_r=requests.get(metadata_url)
    metadata_soup=BeautifulSoup(metadata_r.content)
    try:
        smil_url=metadata_soup.findAll("playbacklinks")[0]
        player_url_list.append(smil_url.contents[1].text)
    except Exception as identifier:
        print("failed to request ",metadata_url," error ",identifier)
        player_url_list.append("bad url")
        
    
    

def handle_player_content(player_content):
    player_iframe=player_content[0].find("iframe")
    player_url=player_iframe.get("src")
    player_r=requests.get(player_url)
    player_soup=BeautifulSoup(player_r.content,"html.parser")
    scripts=player_soup.find_all("script")
    for script in scripts:
        script_str=str(script)
        if "metadataURL" in script_str:
            text=script_str.splitlines()
            for line in text:
                if "metadataURL" in line:
                    metadata_url=re.search('\'(.*)\'',line)
                    handle_metadata(metadata_url.group(1))
                
def handle_stationid_url(stationid_url):
    r1=requests.get(stationid_url)
    c1=r1.content
    soup=BeautifulSoup(c1,"html.parser")
    player_content=soup.find_all("div",{"class":"player_content"})
    image_content=soup.find_all("div",{"class":"player_info_group"})
    
    handle_player_content(player_content)
    handle_image_content(image_content)

def main():
    ssl._create_default_https_context = ssl._create_unverified_context
    r=requests.get("https://www.kan.org.il/radio/")
    c=r.content
    soup=BeautifulSoup(c,"html.parser")

    base_radio_url="https://www.kan.org.il/radio/player.aspx?"
    station_list=[]

    radio_menus_dp=soup.find_all("div",{"class":"mega_menu_level2 w-dropdown w-hidden-main"})
    for radio_menu in radio_menus_dp:
        test_radio=radio_menu.find("div",{"class":"mega_menu_level2_link w-dropdown-toggle"})
        
        if test_radio.text.replace("\n","").replace(" ","") == 'רדיו':
            nav_class=radio_menu.find("nav",{"class":"mega_menu_droplist w-dropdown-list"})
            stations=nav_class.find_all("a",{"class":"mega_menu_droplink w-dropdown-link"})
            for station in stations:
                stationstr=station.get("href")
                if "?" in stationstr:
                    junk,stationid=stationstr.split("?")
                    station_list.append(base_radio_url+stationid)
                else:
                    station_list.append(stationstr)
            break
    for stationid_url in station_list:
        handle_stationid_url(stationid_url)

    for i in range(len(image_url_list)):
        print("player url:"+player_url_list[i])
        print("image_url"+image_url_list[i])

if __name__ == '__main__':
    main()