import requests
from bs4 import BeautifulSoup
import re
import json
#from get_leaders_function import get_leaders
#from extract_soup import get_first_paragraph
from alive_progress import alive_bar
from functools import lru_cache

#Set your parameters here
root_url = "https://country-leaders.herokuapp.com"
status_url = "status"
country_url = "countries"
cookie_url = "cookie"
leaders_url = "leaders"

s = requests.session()
@lru_cache(maxsize=None)
def get_leaders():
    
    
    s = requests.Session()
    leaders_per_country = {}
    cookie = s.get(f"{root_url}/{cookie_url}")
    countries = s.get(f"{root_url}/{country_url}", cookies=cookie.cookies)
    country_list = json.loads(countries.content)
    current_country = {}
    for country in range(len(country_list)):
        current_country = s.get(f"{root_url}/{leaders_url}", cookies=cookie.cookies, params=f"country={country_list[country]}")
        leaders_per_country[country_list[country]] = json.loads(current_country.content)
        
        
    return leaders_per_country   

@lru_cache(maxsize=None)
def get_first_paragraph (wikipedia_url):
      
    html_doc = s.get(wikipedia_url)
    soup = BeautifulSoup(html_doc.text,"html.parser")
    first_paragraph = ""    
    product=soup.find('div',id="mw-content-text")
    product=product.find_all('p')
    for elements in product:
        if elements.find("b"):
            first_paragraph = elements.text
            break
    
    first_paragraph = re.sub("\/.*?\/ \(listen\).*?\[.*?\]","",first_paragraph)
    first_paragraph = re.sub("\(\/.*?/.*?\)","",first_paragraph)
    first_paragraph = re.sub("\( uitspraak \(info / uitleg\)\)","",first_paragraph)
    first_paragraph = re.sub("uitspraak \(info / uitleg\)","",first_paragraph)
    first_paragraph = re.sub("\[.*?]","",first_paragraph)
    first_paragraph = re.sub("\\n","",first_paragraph)
    return first_paragraph
   

'''Creating files for end results. There is a text and json file.
Those should contain the data for all the countries the scraper goes through'''
all_leaders_txt = open("Leaders_all.txt","w+",encoding="utf-8")
all_leaders_json = open("leaders_all.json","w+",encoding="utf-8")


req = s.get(f"{root_url}/{status_url}")
if req.status_code == 200:
    print(req.text)
else:
    print(req.status_code) 

cookies = requests.get(f"{root_url}/{cookie_url}")
countries = requests.get(f"{root_url}/{country_url}",cookies=cookies.cookies)
countries = json.loads(countries.content)
countries.sort()
leaders_all = get_leaders()
total_leaders = 0
for country in countries:
    total_leaders += len(leaders_all[country])
print(f"Total leaders to fetch - {total_leaders}")

with alive_bar(total_leaders) as bar:
    for country in countries:
        '''Here you n change the naming scheme for per country files.
        Default is capitalized two letter code leaders (i.e BE leaders)'''
        current_country_file = open(f"{country.upper()} leaders","w+")
        current_country = {}
        print(f"Current country: {country}, leaders: {len(leaders_all[country])}")
        i=0
        for leader in leaders_all[country]:
            first_paragraph = get_first_paragraph(leader["wikipedia_url"])
            leaders_all[country][i]["first_paragraph"] = first_paragraph
            print(leaders_all[country][i]["first_paragraph"] + "\n",file=all_leaders_txt)
            current_country = leaders_all[country]
            current_country [i]["first_paragraph"] = first_paragraph
            i+=1;bar()
        print("\n\n",file=all_leaders_txt)    
            
        json.dump(current_country, current_country_file)

#print(f"{leaders_all}\n\n",file=all_leaders_txt)
json.dump(leaders_all, all_leaders_json)
