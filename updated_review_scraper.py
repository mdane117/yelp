import requests
import csv
import os
import pandas as pd

def scrape_reviews(base_url, restaurant_page_id, review_page_count, input_id, input_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
    }
    
    extracted_data = []

    for start in range(0, review_page_count, 10):  # Adjust the range as needed
        url = f"{base_url}{restaurant_page_id}/props?start={start}"
        response = requests.get(url, headers=headers)
        print("Processing " + url)
        
        if response.status_code == 200:
            json_data = response.json()

            restaurant_json_url = url
            restaurant_id = json_data.get('bizDetailsPageProps', {}).get('businessId', '')
            restaurant_name = json_data.get('bizDetailsPageProps', {}).get('businessName', '')
            advertiser_flag = json_data.get('bizDetailsPageProps', {}).get('businessIsAdvertiser', False)
            review_count = json_data.get('bizDetailsPageProps', {}).get('reviewFeedQueryProps', {}).get('pagination', {}).get('totalResults', 0)
            reviews_per_page = json_data.get('bizDetailsPageProps', {}).get('reviewFeedQueryProps', {}).get('pagination', {}).get('resultsPerPage', 0)
            start_review = json_data.get('bizDetailsPageProps', {}).get('reviewFeedQueryProps', {}).get('pagination', {}).get('startResult', 0)
            
            reviews = json_data.get('bizDetailsPageProps', {}).get('reviewFeedQueryProps', {}).get('reviews', [])

            for review in reviews:
                review_data = {
                    'input_id': input_id,
                    'input_url': input_url,
                    'restaurant_page_id': restaurant_page_id,
                    'rating_count': review_page_count,
                    'restaurant_id': restaurant_id,
                    'restaurant_name': restaurant_name,
                    'advertiser_flag': advertiser_flag,
                    'review_id': review.get('id', ''),
                    'reviewer_id': review.get('userId', ''),
                    'review_date': review.get('localizedDate', ''),
                    'review_rating': review.get('rating', ''),
                    'photo_count': review.get('totalPhotos', 0),
                    'useful_count': review.get('feedback', {}).get('counts', {}).get('useful', 0),
                    'funny_count': review.get('feedback', {}).get('counts', {}).get('funny', 0),
                    'cool_count': review.get('feedback', {}).get('counts', {}).get('cool', 0),
                    'is_updated': review.get('feedback', {}).get('isUpdated', False),
                    'restaurant_replies': review.get('feedback', {}).get('businessOwnerReplies', ''),
                    'review_content': review.get('comment', {}).get('text', ''),
                    'review_count': review_count,
                    'reviews_per_page': reviews_per_page,
                    'start_review': start_review,
                    'restaurant_json_url': restaurant_json_url
                }
                extracted_data.append(review_data)

    return extracted_data

def export_to_csv(data, filename, output_folder):
    headers = [
        'input_id', 'input_url', 'restaurant_page_id', 'rating_count', 'restaurant_json_url', 'restaurant_id', 'restaurant_name', 'advertiser_flag', 'review_id', 'reviewer_id',
        'review_date', 'review_rating', 'photo_count', 'useful_count', 'funny_count',
        'cool_count', 'is_updated', 'restaurant_replies', 'review_content',
        'review_count', 'reviews_per_page', 'start_review'
    ]
    filepath = os.path.join(output_folder, filename)
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=headers)
        csv_writer.writeheader()
        for row in data:
            csv_writer.writerow(row)
    print(f"{output_filename} successfully exported to {output_folder}")

if __name__ == "__main__":
    # Read restaurant_page.csv
    restaurant_df = pd.read_csv('C:\\Users\\Matthew Dane\\Desktop\\Coding\\python\\Yelp\\output\\restaurant_page.csv', encoding='ISO-8859-1')

    base_url = "https://www.yelp.com/biz/"

    output_folder = "C:\\Users\\Matthew Dane\\Desktop\\Coding\\python\\Yelp\\output"
    output_filename = "reviews.csv"

    all_data = []
    
    for _, row in restaurant_df.iterrows():
        restaurant_page_id = row['restaurant_page_id']
        review_page_count = int(row['rating_count'])
        input_id = row['input_id']
        input_url = row['input_url']

        scraped_data = scrape_reviews(base_url, restaurant_page_id, review_page_count, input_id, input_url)
        all_data.extend(scraped_data)

    export_to_csv(all_data, output_filename, output_folder)
    