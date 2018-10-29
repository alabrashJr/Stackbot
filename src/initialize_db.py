from pymongo import MongoClient
from preprocessing.xml import iterate_over_xml
client = MongoClient('localhost', 27017)
