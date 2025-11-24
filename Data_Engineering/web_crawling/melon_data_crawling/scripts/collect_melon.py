# collect_melon.py
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time

driver = webdriver.Chrome()
url = 'https://www.melon.com/chart/day/index.htm'

driver.get(url)
time.sleep(3)
soup = BeautifulSoup(driver.page_source, 'html.parser')

date = ''.join(span.text.strip() for span in soup.select_one('.yyyymmdd').find_all('span'))
dates = [date] * 100

ranks = [tag.text.strip() for tag in soup.select('span.rank')[1:]]
titles = [tag.text.strip() for tag in soup.select('.ellipsis.rank01 a')]

artist_divs = soup.select('.ellipsis.rank02')

artists = []
for div in artist_divs:
    # 각 div 내 a 태그 텍스트 전부 수집
    artist_names = [a.get_text(strip=True) for a in div.find_all('a')]
    # 중복 제거 및 순서 유지
    unique_artists = list(dict.fromkeys(artist_names))
    # 쉼표로 연결
    artist_text = ', '.join(unique_artists)
    artists.append(artist_text)

print(len(dates), len(ranks), len(titles), len(artists))

df = pd.DataFrame({'date': dates, 'rank':ranks, 'title': titles, 'artist': artists})
df.to_csv('/Users/kangahhyun/ML-Engineer/Project/project_da/data/raw/melon_chart.csv', index=False)
driver.quit()