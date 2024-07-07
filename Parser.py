import requests
from bs4 import BeautifulSoup
import csv
import re
import time
from fake_useragent import UserAgent
from googletrans import Translator

link1 = r'Scripts\Python space\\' #Specify the path to the folder where you want to save the output data file "Anime_data.csv", if you leave the brackets empty, the default path will be used. (the same place where the script is located)
# path example: r'Scripts\Python space\\' two slashes are required at the end.
# According to my calculations, on 06/09/2024, 36-38 pages are parsed there, the rest are empty. But this information may not be relevant.
page = 3   # just put a number on the page where you want the script to stop working. 
# If it is None or 0, the script will run indefinitely until you manually disable it.

class ParseAnime():
    
    def parse(self): 
        self.__create_csv()
        
        ua = UserAgent()
        user_agent = ua.random
        
        num = 1
        while True:
            headers = {
                'accept': '*/*',
                'accept-language': 'en-EN,en;q=0.9,en-US;q=0.8,en;q=0.7',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
               'origin': 'https://jut.su',
                'referer': 'https://jut.su/anime/',
                'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': user_agent,
                'x-requested-with': 'XMLHttpRequest',
            }

            data = {
                'ajax_load': 'yes',
                'start_from_page': num,
                'show_search': '',
                'anime_of_user': '',
            }
            
            response = requests.post('https://jut.su/anime/', headers=headers, data=data)

            soup = BeautifulSoup(response.content, 'lxml')

            cards = soup.find_all('div', class_='all_anime_global')
            
            names = []
            links = []
            episodes = []
            current_string = ""
            
            replacements = {
                'сезонов': 'seasons',
                'сезона': 'seasons',
                'сезон': 'season',
                'серий': 'episodes',
                'серии': 'episodes',
                'серия': 'episode',
                'фильмов': 'films',
                'фильм': 'film'
            }

            pattern = r'(\d+)\s*(сезонов|сезона|сезон|серий|серии|серия|фильмов|фильм)'
            
            for i,v in enumerate(cards):
                name = v.find('div', class_='aaname')
                link = v.find('a')
                link = 'https://jut.su' + link.get('href')
                episode = v.find('div', class_='aailines')
                episode = self.extract_data(pattern, replacements, episode.text)
                names.insert(i, name.text)
                links.insert(i, link)
                episodes.insert(i, episode)
            
            for name in names:
                if current_string:
                    current_string += f" / {name}"
                else:
                    current_string = name
            
            names.clear()
            names.append(current_string)
                            
            
            result1 = self.name_translation(names[0])
            names.clear()
            names.insert(0, result1)
            
            names = [name.strip() for name in names[0].split('/')]
            
            self.save_csv(num, names, episodes, links)
            print(f'[+] The page {num} is saved.')
            if type(page) == int and page is not None and page > 0:
                if num == page:
                    break
            num += 1
            time.sleep(2)
        
    def __create_csv(self):
        with open(rf'{link1}Anime_data.csv', mode='w', newline="") as file:
            writer = csv.writer(file)
            writer.writerow(['№', 'Title', 'Number of episodes' , 'Link'])
        
    def save_csv(self, num, names, episodes, links):
        with open(rf'{link1}Anime_data.csv', mode='a', newline="") as file:
            writer = csv.writer(file)
            num -= 1
            for i,name in enumerate(names):
                writer.writerow([str(i + 1 + (30 * num)) + ')',
                                name,
                                episodes[i],
                                links[i]])
                
    def extract_data(self, pattern, replacements, s):
        s = s.strip()
        matches = re.findall(pattern, s)
        
        seasons = 0
        episodes = 0
        films = 0
        
        for match in matches:
            number, word = match
            number = int(number)
            word = replacements.get(word, word)
            
            if word in ['seasons', 'season']:
                seasons += number
            elif word in ['episodes', 'episode']:
                episodes += number
            elif word in ['films', 'film']:
                films += number
        
        result = []
        if seasons > 0:
            result.append(f"Seasons: {seasons}")
        if episodes > 0:
            result.append(f"Episodes: {episodes}")
        if films > 0:
            result.append(f"Films: {films}")
        
        return ', '.join(result)

                
    def name_translation(self, string):
        translator = Translator()
        result = translator.translate(text=str(string), src='ru', dest='en')
        return result.text
            
if __name__ == "__main__":
    parser = ParseAnime()
    parser.parse()