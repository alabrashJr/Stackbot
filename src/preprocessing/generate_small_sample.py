from parsing import iterate_over_xml, get_chunks
from pymongo import MongoClient
from random import randint
import sys
import argparse
import pymongo

def get_random_question(collection, max_id):
    """Gets randomly chosen question post from 'Posts' collection"""
    if len(get_random_question.rand_ints) < max_id:
        rand_int = randint(1, max_id)
        while rand_int in get_random_question.rand_ints:
            rand_int = randint(1, max_id)
        get_random_question.rand_ints.append(rand_int)
        ques = collection.find_one({'Id': str(rand_int)}, projection={ '_id': 0 })
        while ques is None or ques['PostTypeId'] != '1':
            ques = get_random_question(collection, max_id)
        return ques
    else:
        return None
get_random_question.rand_ints = []

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates small sets for development from mongo database')
    parser.add_argument('-i', '--input-database', required=True,
                        help='input database name')
    parser.add_argument('-o', '--output-database', default='stackbot_small_db',
                        help='output database name')
    parser.add_argument('-s', '--sample-number', type=int, default=5000,
                        help='Number of main samples to be in the set')
    args = vars(parser.parse_args())

    try:
        in_mongo_client = MongoClient()
        out_mongo_client = MongoClient()
        if args['input_database'] not in in_mongo_client.list_database_names():
            print(args['input_database'], 'database does not exist in the current session of MongoDB server.', file=sys.err)

        # Defining Input and Output db's collections
        in_db = in_mongo_client[args['input_database']]
        out_db = out_mongo_client[args['output_database']]
        posts_collection = in_db['Posts']
        postlinks_collection = in_db['PostLinks']
        tags_collection = in_db['Tags']
        comments = in_db['Comments']
        out_posts_collection = out_db['Posts']
        out_postlinks_collection = out_db['PostLinks']
        out_tags_collection = out_db['Tags']
        out_comments_collection = out_db['Comments']

        # Some parameters
        sample_num = args['sample_number']
        batch_size = 1000

        # Sets to be used
        post_ids = set()
        associated_tags = []

        print('Started generating random', sample_num ,'questions :')

        # Copy {sample_num} randomly chosen questions to output db posts collection
        print('Creating random set of questions...')
        batch = []; i = 0
        for i in range(sample_num):
            temp_post = get_random_question(posts_collection, 70000000)
            post_ids.add(temp_post['Id'])
            tags_list = temp_post.get('Tags')
            if tags_list is not None:
                associated_tags += tags_list
            batch.append(temp_post)
            i += 1
            if i > batch_size:
                out_posts_collection.insert_many(batch)
                batch = []; i = 0
        if len(batch) != 0:
            out_posts_collection.insert_many(batch)

        # Copy all post links associated with chosen questions into output db postlinks collection
        print('Copying post links set and adding related posts...')
        postlinks_cursor = postlinks_collection.find({ 'PostId': { '$in':list(post_ids) } }, projection={ '_id': 0 })
        related_posts = set()
        for chunk in get_chunks(postlinks_cursor, batch_size):
            out_postlinks_collection.insert_many(chunk)
            for postlink in chunk:
                related_posts.add(postlink['RelatedPostId'])

        # append related posts to output db post collection
        related_posts_cursor = posts_collection.find({'Id': {'$in': list(related_posts) } }, projection={ '_id': 0 })
        for chunk in get_chunks(related_posts_cursor, batch_size):
            out_posts_collection.insert_many(chunk)
        post_ids.union(related_posts)

        # Copy all comments associated with chosen questions into output db comments collection
        print('Copying comments set...')
        comments_cursor = comments.find({ 'PostId': { '$in':list(post_ids)}}, projection={ '_id': 0 })
        for chunk in get_chunks(comments_cursor, batch_size):
            out_comments_collection.insert_many(chunk)

        # Append chosen questions answers set into output db posts collection
        print('Copying answers set...')
        answers_cursor = posts_collection.find({ 'ParentId': { '$in':list(post_ids) } }, projection={ '_id': 0 })
        for chunk in get_chunks(answers_cursor, batch_size):
            out_posts_collection.insert_many(chunk)

        # Copy all tags associated with chosen questions into output db tags collection
        print('Copying tags set...')
        tags_cursor = tags_collection.find({ 'TagName': { '$in': list(set(associated_tags)) } }, projection={ '_id': 0 })
        for chunk in get_chunks(tags_cursor, batch_size):
            out_tags_collection.insert_many(chunk)

        # Indexing by Id
        out_posts_collection.create_index([('Id', pymongo.ASCENDING)],unique=True)
        out_comments_collection.create_index([('Id', pymongo.ASCENDING)],unique=True)
        out_postlinks_collection.create_index([('Id', pymongo.ASCENDING)],unique=True)
        out_tags_collection.create_index([('Id', pymongo.ASCENDING)],unique=True)

        # Indexing by other fields
        out_tags_collection.create_index([('TagName', pymongo.ASCENDING)], unique=True)
        out_comments_collection.create_index([('PostId', pymongo.ASCENDING)])
        out_posts_collection.create_index([('ParentId', pymongo.ASCENDING)])
        out_postlinks_collection.create_index([('PostId', pymongo.ASCENDING)])
        out_postlinks_collection.create_index([('RelatedPostId', pymongo.ASCENDING)])

    except Exception as e:
        print(e)
