import requests
import csv
from tqdm import tqdm

def fetch_items(word):
    url = f"url"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    
    items = response.json().get('items', [])[0][0][2][0] # 영어 단어를 검색했을 때 가장 상단에 있는 한글 단어 가져오기.
    return items.split(',') if items else []

def save_to_csv(word_list, output_csv):
    results = [[word, item] for word in tqdm(word_list) for item in fetch_items(word) or [f"{word} No items found"]]
    with open(output_csv, 'w', newline='', encoding='utf-8-sig') as f:
        csv.writer(f).writerows([['en_word', 'ko_word']] + results)

if __name__ == "__main__":
    csv_file_path = "words_items.csv"
    words_list = ["receipt", "apple", "computer", "table", "book", "created"]
    save_to_csv(words_list, csv_file_path)
    print("Saved results to words_items.csv")