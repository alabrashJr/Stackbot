from parsing import iterate_over_xml
from pymongo import MongoClient
import sys
import argparse
from random import randint

def get_random_question(collection, max_id):
    if len(get_random_question.rand_ints) < max_id:
        rand_int = randint(1, max_id)
        while rand_int in get_random_question.rand_ints:
            rand_int = randint(1, max_id)
        get_random_question.rand_ints.append(rand_int)
        ques = collection.find_one({'Id': str(rand_int)})
        while ques is None or ques['PostTypeId'] != '1':
            ques = get_random_question(collection, max_id)
        return ques
    else:
        return None
get_random_question.rand_ints = []

def get_list_by_query(collection, query_dict):
    rows = [x for x in collection.find(query_dict)]
    return rows

def remove_tags(line):
    if line is None:
        return []
    tags = line.split('><')
    if len(tags) == 0:
        return []
    tags[0] = tags[0][1:]
    tags[-1] = tags[-1][:-1]
    return tags

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
        mongo_client = MongoClient()
        if args['input_database'] not in mongo_client.list_database_names():
            print(args['input_database'], 'database does not exist in the current session of MongoDB server.', file=sys.err)
        in_db = mongo_client[args['input_database']]
        out_db = mongo_client[args['output_database']]
        posts_collection = in_db['Posts']
        postlinks_collection = in_db['PostLinks']
        tags_collection = in_db['Tags']
        comments = in_db['Comments']
        out_posts_collection = out_db['Posts']
        out_postlinks_collection = out_db['PostLinks']
        out_tags_collection = out_db['Tags']
        out_comments_collection = out_db['Comments']
        sample_num = args['sample_number']
        batch_size = 1000
        post_ids = []
        associated_tags = []
        print('Started generating random', sample_num ,'questions :')
        # Copy {sample_num} randomly chosen questions to output db posts collection
        print('Creating random set of questions...')
        batch = []; i = 0
        for i in range(sample_num):
            temp_post = get_random_question(posts_collection, 70000000)
            post_ids.append(temp_post['Id'])
            batch.append(temp_post)
            associated_tags += remove_tags(temp_post.get('Tags'))
            i += 1
            if i > batch_size:
                out_posts_collection.insert_many(batch)
                batch = []; i = 0
        if len(batch) != 0:
            out_posts_collection.insert_many(batch)

        # Copy all comments associated with chosen questions into output db comments collection
        print('Copying comments set...')
        comments_cursor = comments.find({ 'PostId': { '$in':post_ids}})
        batch = []; i = 0
        for comment in comments_cursor:
            batch.append(comment)
            i += 1
            if i > batch_size:
                out_comments_collection.insert_many(batch)
                batch = []; i = 0
        if len(batch) != 0:
            out_comments_collection.insert_many(batch)

        # Append chosen questions answers set into output db posts collection
        print('Copying answers set...')
        answers_cursor = posts_collection.find({ 'ParentId': { '$in':post_ids } })
        batch = []; i = 0
        for answer in answers_cursor:
            batch.append(answer)
            i += 1
            if i > batch_size:
                out_posts_collection.insert_many(batch)
                batch = []; i = 0
        if len(batch) != 0:
            out_posts_collection.insert_many(batch)

        # Copy all post links associated with chosen questions into output db postlinks collection
        print('Copying post links set...')
        postlinks_cursor = postlinks_collection.find({ 'PostId': { '$in':post_ids }, 'RelatedPostId': { '$in' : post_ids } })
        batch = []; i = 0
        for postlink in postlinks_cursor:
            batch.append(postlink)
            i += 1
            if i > batch_size:
                out_postlinks_collection.insert_many(batch)
                batch = []; i = 0
        if len(batch) != 0:
            out_postlinks_collection.insert_many(batch)

        # Copy all tags associated with chosen questions into output db tags collection
        print('Copying tags set...')
        associated_tags = list(set(associated_tags))
        tags_cursor = tags_collection.find({'TagName': { '$in': associated_tags } })
        batch = []; i = 0
        for tag in tags_cursor:
            batch.append(tag)
            i += 1
            if i > batch_size:
                out_tags_collection.insert_many(batch)
                batch = []; i = 0
        if len(batch) != 0:
            out_tags_collection.insert_many(batch)

    except Exception as e:
        print(e)
