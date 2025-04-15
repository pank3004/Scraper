import os
import sys
import pymongo
import certifi
import pandas as pd
from src.exception import MyException
from src.logger import logging
from src.constants import DATABASE_NAME, MONGODB_URL_KEY

# Load the certificate authority file to avoid timeout errors when connecting to MongoDB
ca = certifi.where()

class MongoDBClient:
 
    client = None  # Shared MongoClient instance across all MongoDBClient instances

    def __init__(self, database_name: str = DATABASE_NAME) -> None:
        try:
            # Check if a MongoDB client connection has already been established; if not, create a new one
            if MongoDBClient.client is None:
                mongo_db_url = os.getenv(MONGODB_URL_KEY)  # Retrieve MongoDB URL from environment variables
                if mongo_db_url is None:
                    raise Exception(f"Environment variable '{MONGODB_URL_KEY}' is not set.")
                
                # Establish a new MongoDB client connection
                MongoDBClient.client = pymongo.MongoClient(mongo_db_url,tlsCAFile=ca)

                '''
                src.exception.MyException: Error occurred in python script: [C:\End to End MLOPS\Scraper\src\cloud_io\__init__.py] at line number [44]: SSL handshake failed: ac-bvzh9cu-shard-00-01.erdodxf.mongodb.net:27017: [WinError 10054] An existing connection was forcibly closed by the remote host (configured timeouts: connectTimeoutMS: 20000.0ms)
                '''
                
            # Use the shared MongoClient for this instance
            self.client = MongoDBClient.client
            self.database = self.client[database_name]  # Connect to the specified database
            self.database_name = database_name
            logging.info("MongoDB connection successful.")
            
        except Exception as e:
            # Raise a custom exception with traceback details if connection fails
            raise MyException(e, sys)
        

    def store_reviews(self, product_name: str, reviews: pd.DataFrame):
        try:
            logging.info('entered in store_review fn')
            collection_name = product_name.replace(" ", "_")
            collection = self.database[collection_name]  # Access the correct collection
            records = reviews.to_dict(orient='records')
            logging.info(f'inserting review of {product_name} in collection {collection_name}')
            collection.insert_many(records)
            logging.info(f"Reviews of product '{product_name}' successfully stored in collection '{collection_name}'.")
        except Exception as e:
            raise MyException(e, sys)

    def get_reviews(self, product_name: str):
        try:
            logging.info('entered in get_review fn: ')

            collection_name = product_name.replace(" ", "_")
            collection = self.database[collection_name]
            logging.info(f'geting review of {product_name} from collection {collection_name}')
            data = list(collection.find())  # Get all reviews from the collection
            logging.info(f'successfully fetched reviews of {product_name} from mongodb collection {collection_name}')
            return data
        except Exception as e:
            raise MyException(e, sys)


























# import pandas as pd
# from database_connect import mongo_operation as mongo
# import os, sys
# from src.constants import *
# from src.logger import logging
# from src.exception import CustomException

# class MongoIO: 
#     mongo_ins=None

#     def __init__(self): 
#         if MongoIO.mongo_ins is None: 
#             mongo_db_url=os.getenv(MONGODB_URL_KEY)
#             if mongo_db_url is None: 
#                 raise Exception(f'Environment key{MONGODB_URL_KEY}is not set')
            
#             MongoIO.mongo_ins=mongo(client_url=mongo_db_url,
#                                     database_name=DATABASE_NAME)
            
#             self.mongo_ins=MongoIO.mongo_ins

#         logging.info('mongodb connection established')

#     def store_reviews(self,
#                       product_name: str, reviews: pd.DataFrame):
#         try:
#             collection_name = product_name.replace(" ", "_")
#             self.mongo_ins.bulk_insert(reviews,
#                                        collection_name)

#         except Exception as e:
#             raise CustomException(e, sys)

#     def get_reviews(self,
#                     product_name: str):
#         try:
#             data = self.mongo_ins.find(
#                 collection_name=product_name.replace(" ", "_")
#             )

#             return data

#         except Exception as e:
#             raise CustomException(e, sys)
            
