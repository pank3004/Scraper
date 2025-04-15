from selenium import webdriver
from selenium.webdriver.common.by import By
from src.exception import MyException
from bs4 import BeautifulSoup as bs
import pandas as pd
import os, sys
import time
from selenium.webdriver.chrome.options import Options
from urllib.parse import quote
from src.logger import logging


class ScrepeReviews: 
    def __init__(self, product_name:str, no_of_products:int): 
        options=Options()

        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-dev-shm-usage")
        # options.add_argument('--headless')

        self.driver=webdriver.Chrome(options=options)
        self.product_name=product_name
        self.no_of_products=no_of_products
    
    def scrape_product_urls(self, product_name): 
        try: 
            logging.info('Trying... to scrape product urls..')
            search_string=product_name.replace(" ","-")
            encoded_query=quote(search_string)
            #eg: search_string : men's-shoes-&-sandals
            #encoded_query: men%27s-shoes-%26-sandals
            self.driver.get(f'https://www.myntra.com/{search_string}?rawQuery={encoded_query}')

            myntra_text=self.driver.page_source
            myntra_html=bs(myntra_text, 'html.parser')

            pclass=myntra_html.find_all('ul', {'class': 'results-base'})

            product_links=[]
            for ul in pclass: 
                lis = ul.find_all('li', class_='product-base')
                for li in lis: 
                    href=li.find_all('a', href=True)
                    t=(href[0]['href'])
                    product_link='https://www.myntra.com/'+t
                    product_links.append(product_link)
            return product_links
        except Exception as e: 
            raise MyException(e,sys)
        
    
    def extract_review(self, product_link): 
        try: 
            self.driver.get(product_link)
            prodRes=self.driver.page_source
            prodRes_html=bs(prodRes,'html.parser')


            product_des=prodRes_html.find_all('div',{'class':'pdp-description-container'})

            for i in product_des: 
                self.product_title=i.find('h1', {'class':'pdp-title'}).text
                self.product_name=i.find('h1',{'class':'pdp-name'}).text
                self.product_rating_value=i.find('div', {'class':'index-overallRating'}).find('div').text
                self.product_price=i.find('span',{'class':'pdp-price'}).find('strong').text



            # title_h=prodRes_html.find_all('title')
            # self.product_title=title_h[0].txt

            # overallRating=prodRes_html.find_all('div', {'class':'index-overallRating'})
            # #self.product_rating_value=overallRating.find('div').text
            # for i in overallRating:
            #     self.product_rating_value = i.find("div").text

            # price_container=prodRes_html.find_all('p',{'class':'pdp-discount-container'})
            # for i in price_container: 
            #     price=i.find('span')
            #     price=price.find('strong')
            #     self.product_price=price.text

            product_all_reviews=prodRes_html.find('a',{'class':'detailed-reviews-allReviews'})

            if not product_all_reviews: 
                return None
            return product_all_reviews
        
        except Exception as e: 
            raise MyException(e,sys)


    def scroll_to_load_all_reviews(self, max_wait_time=60):
        self.driver.set_window_size(1920, 1080)
        start_time = time.time()

        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while True:
            self.driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(3)
            
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                break
            
            if time.time() - start_time > max_wait_time:
                print("Scroll timed out.")
                break

            last_height = new_height
    
    def extract_products(self, product_all_reviews:list): 
        try:    
            t2=product_all_reviews['href']
            product_all_reviews_link='https://www.myntra.com'+t2
            self.driver.get(product_all_reviews_link)
            self.scroll_to_load_all_reviews()

            reviews_page=self.driver.page_source
            reviews_html=bs(reviews_page, 'html.parser')

            reviews=reviews_html.find_all('div', class_='detailed-reviews-userReviewsContainer')
            for i in reviews: 
                user_rating = i.find_all('div', class_='user-review-starWrapper')
                user_comment = i.find_all('div', class_='user-review-reviewTextWrapper')
                user_name_and_date = i.find_all('div', class_='user-review-left')

            reviewsData=[]
            for i in range(len(user_rating)): 
                try: 
                    rating=user_rating[i].text
                except: 
                    rating='No rating given'
                try: 
                    comment=user_comment[i].text
                except: 
                    comment='No comment Given'
                try:     
                    name=user_name_and_date[i].find('span').text
                except: 
                    name='No Name given'
                try: 
                    date=user_name_and_date[i].find_all('span')[1].text
                except: 
                    date='No date given'

                mydict = {
                    'Product Name': self.product_name,
                    "Product Title": self.product_title,
                    "Over_All_Rating": self.product_rating_value,
                    "Price": self.product_price,
                    "Date": date,
                    "Rating": rating,
                    "Name": name,
                    "Comment": comment,
                }
                reviewsData.append(mydict)

            reviews_df=pd.DataFrame(reviewsData,columns=[  "Product Name",
                                                           "Product Title",
                                                            "Over_All_Rating",
                                                            "Price",
                                                            "Date",
                                                            "Rating",
                                                            "Name",
                                                            "Comment"])
            return reviews_df
        
        except Exception as e: 
            raise MyException(e,sys)
        
    def skip_products(self, search_string, no_of_products, skip_index): 
        product_urls:list=self.scrape_product_urls(search_string)
        product_urls.pop(skip_index)


    def get_review_data(self)->pd.DataFrame: 
        try: 
            product_urls=self.scrape_product_urls(product_name=self.product_name)

            product_details=[]
            review_len=0

            while review_len<self.no_of_products: 
                product_url=product_urls[review_len]
                review=self.extract_review(product_url)

                if review: 
                    product_detail=self.extract_products(review)
                    product_details.append(product_detail)

                    review_len+=1

                else: 
                    product_urls.pop(review_len)

            self.driver.quit()

            data=pd.concat(product_details, axis=0)

            data.to_csv('data.csv', index=False)

            return data
        
        except Exception as e: 
            raise MyException(e,sys)