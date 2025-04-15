import pandas as pd
import streamlit as st
from src.cloud_io import MongoDBClient
from src.constants import SESSION_PRODUCT_KEY
from src.scrapper.scrape import ScrepeReviews
from src.logger import logging

st.set_page_config('myntra-review-scrapper')

st.title('Myntra Review Scrapper')

st.session_state['data']=False


def form_input(): 
    product=st.text_input('Search Products')
    st.session_state[SESSION_PRODUCT_KEY]=product
    no_of_products=st.number_input('No of products to search', step=1, min_value=1)

    if st.button('Scrape Reviews'): 
        logging.info('creating object of ScrepeReviews class')
        scrapper=ScrepeReviews(product_name=product, no_of_products=int(no_of_products))
        logging.info('object created')

        logging.info('getting review from get_review_data fn(myntra website)')
        scrapped_data=scrapper.get_review_data()
        logging.info('data fetched from myntra website')

        if scrapped_data is not None: 
            st.session_state['data']=True
            mongoio=MongoDBClient()
            logging.info('stroring data to mongodb')
            mongoio.store_reviews(product_name=product,reviews=scrapped_data)
            logging.info('data stored at mongodb')
        st.dataframe(scrapped_data)

if __name__ == "__main__":
    data = form_input()