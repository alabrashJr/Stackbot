from pymongo import MongoClient
from preprocessing.xml import iterate_over_xml, StreamArray
import pymongo
import argparse

def xml_to_collection(xml_file, db, collection_name):
    """Reads xml rows from xml files and add them to mongodb collection"""
    collection = db[collection_name]
    collection.create_index([('Id', pymongo.ASCENDING)],unique=True)
    stream_array = StreamArray(iterate_over_xml(xml_file))
    collection.insert_many(stream_array)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Transfers data into mongodb database for more flexible processing')
    parser.add_argument('-p', '--files-path', required=True,
                        help='Path of the files to be processed')
    parser.add_argument('-n', '--db-name', default='Stackbot',
                        help='Path of the file to be written to')
    parser.add_argument('-f', '--files-list', nargs='+',
                        help='List of the files to be parsed and added to db')
    args = vars(parser.parse_args())
    mongo_client = MongoClient('localhost', 27017)
    db = mongo_client[args['db_name']]
    for file in args['files_list']:
        print('Creating collection with name', file[:file.rfind('.')], 'from', args['files_path'] + file)
        xml_to_collection(args['files_path'] + file, db, file[:file.rfind('.')])
