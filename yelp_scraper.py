import requests
from bs4 import BeautifulSoup
import os
import csv
import re

def scrape_restaurant_page(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        data = []

        # Scrape restaurant name
        restaurant_name_tag = soup.find('h1', class_='css-1se8maq')
        restaurant_name = restaurant_name_tag.get_text() if restaurant_name_tag else None

        # Scrape restaurant URL and phone number
        restaurant_info_tag = soup.find_all('p', class_='css-1p9ibgf')
        if len(restaurant_info_tag) >= 2:
            restaurant_url = restaurant_info_tag[-3].get_text()
            restaurant_phone = restaurant_info_tag[-2].get_text()
        else:
            restaurant_url = None
            restaurant_phone = None

        # Scrape restaurant Yelp URL
        restaurant_yelp_url_tag = soup.find_all('a', class_='css-1idmmu3')
        if len(restaurant_info_tag) >= 2:
            restaurant_yelp_url_ext = restaurant_yelp_url_tag[-4].get('href')
            restaurant_yelp_url = "https://www.yelp.com" + restaurant_yelp_url_ext
        else:
            restaurant_yelp_url = None

        # Extract restaurant ID
        restaurant_page_id = extract_restaurant_id(restaurant_yelp_url)  

        # Scrape restaurant address
        restaurant_address_tag = soup.find('p', class_='css-qyp8bo')
        restaurant_address = restaurant_address_tag.get_text() if restaurant_address_tag else None

        # Scrape restaurant overall rating
        overall_rating_tag = soup.find('span', class_='css-1fdy0l5')
        overall_rating = overall_rating_tag.get_text() if overall_rating_tag else None

        # Scrape review count
        review_count_tag = soup.find('a', class_='css-19v1rkv')
        review_count_text = review_count_tag.get_text() if review_count_tag else None
        #review_count = int(re.search(r'\d+', review_count_text).group()) if review_count_text else None
        if review_count_text:
            review_count = int(''.join(re.findall(r'\d+', review_count_text)))
        else:
            review_count = None
        
        # Scrape popular dishes
        popular_dish_name_tag = soup.find_all('p', class_='css-nyjpex')
        popular_dish_names = '|'.join([name.get_text() for name in popular_dish_name_tag]) if popular_dish_name_tag else None

        # Scrape popular dishes photo count
        popular_dish_photo_count_tag = soup.find_all('span', class_='css-chan6m')
        filtered_photo_count_tags = [
            photo_count for photo_count in popular_dish_photo_count_tag
            if not photo_count.find('span', class_='css-ralh0w') and scrape_exceptions not in photo_count.get_text()
        ]
        popular_dish_photo_count = '|'.join([photo_count.get_text() for photo_count in filtered_photo_count_tags]) if filtered_photo_count_tags else None

        # Scrape popular dishes review count
        popular_dish_review_count_tag = soup.find_all('span', class_='css-j9i001')
        popular_dish_review_count = '|'.join([review_count.get_text() for review_count in popular_dish_review_count_tag]) if popular_dish_review_count_tag else None

        data.append([restaurant_name, restaurant_url, restaurant_yelp_url, restaurant_page_id, 
            restaurant_phone, restaurant_address, overall_rating, review_count, 
            popular_dish_names, popular_dish_photo_count, popular_dish_review_count])
        return data
    else:
        print(f"Failed to fetch the URL. Status code: {response.status_code}")

def extract_restaurant_id(yelp_url):
    if yelp_url:
        # Use regex to match the restaurant ID including underscores
        match = re.search(r'src_bizid=([^&]+)', yelp_url)
        if match:
            return match.group(1)
    return None

def export_to_csv(data, filename, output_folder):
    if data:
        filepath = os.path.join(output_folder, filename)
        is_file_empty = not (os.path.isfile(filepath) and os.path.getsize(filepath) > 0)
        with open(filepath, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile) 
            if is_file_empty:
            	writer.writerow(['input_id', 'input_url', 'restaurant_name', 'restaurant_url', 
                    'restaurant_yelp_url', 'restaurant_page_id', 'restaurant_phone', 'restaurant_address', 
                    'overall_rating', 'rating_count', 'popular_dish_names' , 'popular_dish_photo_count', 
                    'popular_dish_review_count'])
            writer.writerows(data)
        print(f"{input_url} data exported to {filename} successfully.")
    else:
        print("No data to export.")

if __name__ == "__main__":
    # Exceptions the scraper should ignore in the HTML
    scrape_exceptions = "months ago"

    input_filename = "" # Add path to input list
    output_folder = "" # Add path to output location
    output_filename = "restaurant_page.csv"
    with open(input_filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader) # skip header row
        for row in reader:
            input_id, input_url = row
            scraped_data = scrape_restaurant_page(input_url)
            if scraped_data:
                for i in range(len(scraped_data)):
                    scraped_data[i] = [input_id, input_url] + scraped_data[i]

                export_to_csv(scraped_data, output_filename, output_folder)
