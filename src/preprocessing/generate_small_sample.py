from preprocessing.xml import iterate_over_xml
from pymongo import MongoClient
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates small sets for development from mongo database')
    parser.add_argument('-i', '--input-database', required=True,
                        help='input database name')
    parser.add_argument('-o', '--output-database', default='stackbot_small_db',
                        help='input database name')
    parser.add_argument('-m', '--main-collection-name', default='Posts',
                        help='Main collection name')
    parser.add_argument('-s', '--sample-number', type=int, default=10000
                        help='Number of main samples to be in the set')
    args = vars(parser.parse_args())


    try:
        mongo_client = MongoClient()
        if args['input_database'] not in mongo_client.list_database_names():
            print(args['input_database'], 'database does not exist in the current session of MongoDB server.', file=sys.err)
        in_db = mongo_client[args['input_database']]
        out_db = mongo_client[args['output_database']]
    except:
