'''
This Python script is a working proof of concept example of using Stack Overflow APIs for a User Report. 
If you run into difficulties, please leave feedback in the Github Issues.
'''

# Standard Python libraries
import argparse
import csv
import json
import os
import pickle
import time
import statistics

# Local libraries
from so4t_web_client import WebClient
from so4t_api_v2 import V2Client
from so4t_api_v3 import V3Client


def main():

    # Get command-line arguments
    args = get_args()

    if args.no_api:
        print("Skipping API calls and using data from JSON files in the data directory...")
        api_data = {}
        api_data['users'] = read_json('users.json')
        api_data['reputation_history'] = read_json('reputation_history.json')
        api_data['questions'] = read_json('questions.json')
        api_data['articles'] = read_json('articles.json')
        api_data['tags'] = read_json('tags.json')
        api_data['communities'] = read_json('communities.json')
        print("Data successfully loaded from JSON files.")
    else:
        api_data = get_api_data(args)

    if args.start_date:
        start_date = int(time.mktime(time.strptime(args.start_date, '%Y-%m-%d')))
    else:
        start_date = 0

    if args.end_date:
        end_date = int(time.mktime(time.strptime(args.end_date, '%Y-%m-%d')))
    else:
        end_date = 2524626000 # 2050-01-01

    users = process_api_data(api_data, start_date, end_date, args.output_name)
    create_user_report(users, args.start_date, args.end_date, args.output_name)


def get_args():

    parser = argparse.ArgumentParser(
        prog='so4t_user_report.py',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Uses the Stack Overflow for Teams API to create \
        a CSV report with user metrics.',
        epilog = 'Example for Stack Overflow Business: \n'
                'python3 so4t_user_report.py --url "https://stackoverflowteams.com/c/TEAM-NAME" '
                '--token "YOUR_TOKEN" \n\n'
                'Example for Stack Overflow Enterprise: \n'
                'python3 so4t_user_report.py --url "https://SUBDOMAIN.stackenterprise.co" '
                '--key "YOUR_KEY" --token "YOUR_TOKEN"\n\n')
    
    parser.add_argument('--url', 
                        type=str,
                        help='[REQUIRED] Base URL for your Stack Overflow for Teams instance.')
    parser.add_argument('--token',
                        type=str,
                        help='[REQUIRED] API token for your Stack Overflow for Teams instance.')
    parser.add_argument('--key',
                    type=str,
                    help='API key value. Required if using Stack Overflow Enterprise.')
    parser.add_argument('--start-date',
                        type=str,
                        help='[OPTIONAL] Start date for filtering API data. '
                        'Must be YYYY-MM-DD format. '
                        'If not specified, all data will be included.')
    parser.add_argument('--end-date',
                        type=str,
                        help='[OPTIONAL] End date for filtering API data. '
                        'Must be YYYY-MM-DD format. '
                        'If not specified, all data will be included.')
    parser.add_argument('--no-api',
                        action='store_true',
                        help='Skips API calls and uses data from JSON files in the data directory.')
    parser.add_argument('--api-start-date',
                        type=str,
                        help='[OPTIONAL] Start date for API data filtering. '
                        'Must be YYYY-MM-DD format. '
                        'This filters data at the API level to reduce response size.')
    parser.add_argument('--api-end-date',
                        type=str,
                        help='[OPTIONAL] End date for API data filtering. '
                        'Must be YYYY-MM-DD format. '
                        'This filters data at the API level to reduce response size.')
    parser.add_argument('--max-users',
                        type=int,
                        help='[OPTIONAL] Maximum number of users to process. '
                        'Useful for testing or processing subsets of large user bases.')
    parser.add_argument('--user-id-start',
                        type=int,
                        help='[OPTIONAL] Start user ID for processing. '
                        'Useful for processing users in chunks.')
    parser.add_argument('--user-id-end',
                        type=int,
                        help='[OPTIONAL] End user ID for processing. '
                        'Useful for processing users in chunks.')
    parser.add_argument('--output-name',
                        type=str,
                        help='[OPTIONAL] Custom name for output files. '
                        'If not specified, current date will be used.')
    # parser.add_argument('--web-client',
    #                     action='store_true',
    #                     help='Enables web-based data collection for data not available via API. Will '
    #                     'open a Chrome window and prompt user to login.')

    return parser.parse_args()


def get_api_data(args):

    # Convert date strings to timestamps for API filtering
    api_fromdate = None
    api_todate = None
    
    if args.api_start_date:
        api_fromdate = int(time.mktime(time.strptime(args.api_start_date, '%Y-%m-%d')))
    if args.api_end_date:
        api_todate = int(time.mktime(time.strptime(args.api_end_date, '%Y-%m-%d')))

    # Only create a web session if the --web-client flag is used
    # if args.web_client:
    #     session_file = 'so4t_session'
    #     try:
    #         with open(session_file, 'rb') as f:
    #             web_client = pickle.load(f)
    #         if web_client.base_url != args.url or not web_client.test_session():
    #             raise FileNotFoundError # force creation of new session
    #     except FileNotFoundError:
    #         web_client = WebClient(args.url)
    #         with open(session_file, 'wb') as f:
    #             pickle.dump(web_client, f)
        
    # Instantiate V2Client and V3Client classes to make API calls
    v2client = V2Client(args.url, args.key, args.token)
    v3client = V3Client(args.url, args.token)
    
    # Get all questions, answers, comments, articles, tags, and SMEs via API
    so4t_data = {}
    so4t_data['users'] = get_users(v2client, v3client, args.max_users, args.user_id_start, args.user_id_end)
    so4t_data['reputation_history'] = get_reputation_history(v2client, so4t_data['users'])
    so4t_data['questions'] = get_questions_answers_comments(v2client, api_fromdate, api_todate) # also gets answers/comments
    so4t_data['articles'] = get_articles(v2client, api_fromdate, api_todate)
    so4t_data['tags'] = get_tags(v3client) # also gets tag SMEs

    # Get additional data via web scraping
    # if args.web_client:
    #     so4t_data['communities'] = web_client.get_communities()
    # else:
    #     so4t_data['communities'] = None

    # Export API data to JSON file
    for name, data in so4t_data.items():
        if args.output_name:
            export_to_json(f'{name}_{args.output_name}', data)
        else:
            export_to_json(name, data)

    return so4t_data


def get_users(v2client, v3client, max_users=None, user_id_start=None, user_id_end=None):

    # Filter documentation: https://api.stackexchange.com/docs/filters
    if 'soedemo' in v2client.api_url: # for internal testing
        filter_string = ''
    elif v2client.soe: # Stack Overflow Enterprise requires the generation of a custom filter
        filter_attributes = [
            "user.is_deactivated" # this attribute is only available in Enterprise and in API v2
        ]
        filter_string = v2client.create_filter(filter_attributes)
    else: # Stack Overflow Business or Basic
        filter_string = ''

    v2_users = v2client.get_all_users(filter_string)

    # Exclude users with an ID of less than 1 (i.e. Community user and user groups)
    v2_users = [user for user in v2_users if user['user_id'] > 1]

    # Apply user ID range filtering if specified
    if user_id_start is not None:
        v2_users = [user for user in v2_users if user['user_id'] >= user_id_start]
    if user_id_end is not None:
        v2_users = [user for user in v2_users if user['user_id'] <= user_id_end]

    # Apply max users limit if specified
    if max_users is not None:
        v2_users = v2_users[:max_users]
        print(f"Limited to {max_users} users for processing")

    if 'soedemo' in v3client.api_url: # for internal testing only
        v2_users = [user for user in v2_users if user['user_id'] > 28000]

    print(f"Processing {len(v2_users)} users...")

    v3_users = v3client.get_all_users()
    
    # Add additional user data from API v3 to user data from API v2
    # API v3 fields to add: 'email', 'jobTitle', 'department', 'externalId, 'role'
    
    # Create a lookup dictionary for v3 users for faster matching
    v3_users_lookup = {v3_user['id']: v3_user for v3_user in v3_users}
    
    # Track users that need individual API calls (deactivated users)
    deactivated_users = []
    
    for user in v2_users:
        v3_user = v3_users_lookup.get(user['user_id'])
        if v3_user:
            # User found in v3 data
            user['email'] = safe_get_user_field(v3_user, 'email', '')
            user['title'] = safe_get_user_field(v3_user, 'jobTitle', '')
            user['department'] = safe_get_user_field(v3_user, 'department', '')
            user['external_id'] = safe_get_user_field(v3_user, 'externalId', '')
            user['moderator'] = (safe_get_user_field(v3_user, 'role', '') == 'Moderator')
        else:
            # User not found in v3 data - likely deactivated
            deactivated_users.append(user)
    
    # Process deactivated users in batches to reduce API calls
    if deactivated_users:
        print(f"Found {len(deactivated_users)} deactivated users, processing in batches...")
        batch_size = 10  # Process 10 deactivated users at a time
        
        for i in range(0, len(deactivated_users), batch_size):
            batch = deactivated_users[i:i + batch_size]
            print(f"Processing deactivated users batch {i//batch_size + 1}/{(len(deactivated_users) + batch_size - 1)//batch_size}")
            
            for user in batch:
                try:
                    v3_user = v3client.get_user(user['user_id'])
                    user['email'] = safe_get_user_field(v3_user, 'email', '')
                    user['title'] = safe_get_user_field(v3_user, 'jobTitle', '')
                    user['department'] = safe_get_user_field(v3_user, 'department', '')
                    user['external_id'] = safe_get_user_field(v3_user, 'externalId', '')
                    user['is_deactivated'] = True
                    user['moderator'] = (safe_get_user_field(v3_user, 'role', '') == 'Moderator')
                except Exception as e:
                    print(f"Failed to get data for deactivated user {user['user_id']}: {e}")
                    # Set default values for failed users
                    user['email'] = ''
                    user['title'] = ''
                    user['department'] = ''
                    user['external_id'] = ''
                    user['is_deactivated'] = True
                    user['moderator'] = False
            
            # Add delay between batches to avoid rate limiting
            if i + batch_size < len(deactivated_users):
                time.sleep(1)  # 1 second delay between batches

    return v2_users


def get_reputation_history(v2client, users):

    user_ids = [user['user_id'] for user in users]
    reputation_history = v2client.get_reputation_history(user_ids)

    return reputation_history


def get_questions_answers_comments(v2client, fromdate=None, todate=None):
    
    # The API filter used for the /questions endpoint makes it so that the API returns
    # all answers and comments for each question. This is more efficient than making
    # separate API calls for answers and comments.
    # Filter documentation: https://api.stackexchange.com/docs/filters
    if v2client.soe: # Stack Overflow Enterprise requires the generation of a custom filter
        filter_attributes = [
            # "answer.body",
            # "answer.body_markdown",
            "answer.comment_count",
            "answer.comments",
            "answer.down_vote_count",
            "answer.last_editor",
            "answer.link",
            "answer.share_link",
            "answer.up_vote_count",
            # "comment.body",
            # "comment.body_markdown",
            "comment.link",
            "question.answers",
            # "question.body",
            # "question.body_markdown",
            "question.comment_count",
            "question.comments",
            "question.down_vote_count",
            "question.favorite_count",
            "question.last_editor",
            "question.notice",
            "question.share_link",
            "question.up_vote_count"
        ]
        filter_string = v2client.create_filter(filter_attributes)
    else: # Stack Overflow Business or Basic
        filter_string = '!X9DEEiFwy0OeSWoJzb.QMqab2wPSk.X2opZDa2L'
    questions = v2client.get_all_questions(filter_string, fromdate=fromdate, todate=todate)

    return questions


def get_articles(v2client, fromdate=None, todate=None):

    # Filter documentation: https://api.stackexchange.com/docs/filters
    if v2client.soe:
        filter_attributes = [
            # "article.body",
            # "article.body_markdown",
            "article.comment_count",
            "article.comments",
            "article.last_editor",
            "comment.body",
            "comment.body_markdown",
            "comment.link"
        ]
        filter_string = v2client.create_filter(filter_attributes)
    else: # Stack Overflow Business or Basic
        filter_string = '!*Mg4Pjg9LXr9d_(v'

    articles = v2client.get_all_articles(filter_string, fromdate=fromdate, todate=todate)

    return articles


def get_tags(v3client):

    # While API v2 is more robust for collecting tag data, it does not return the tag ID field, 
    # which is needed to get the SMEs for each tag. Therefore, API v3 is used to get the tag ID
    tags = v3client.get_all_tags()

    # Get subject matter experts (SMEs) for each tag. This API call is only available in v3.
    # Process tags with SMEs in batches to reduce API calls
    tags_with_smes = [tag for tag in tags if tag['subjectMatterExpertCount'] > 0]
    
    if tags_with_smes:
        print(f"Found {len(tags_with_smes)} tags with SMEs, processing in batches...")
        batch_size = 5  # Process 5 tags at a time
        
        for i in range(0, len(tags_with_smes), batch_size):
            batch = tags_with_smes[i:i + batch_size]
            print(f"Processing tag SMEs batch {i//batch_size + 1}/{(len(tags_with_smes) + batch_size - 1)//batch_size}")
            
            for tag in batch:
                try:
                    tag['smes'] = v3client.get_tag_smes(tag['id'])
                except Exception as e:
                    print(f"Failed to get SMEs for tag {tag['id']}: {e}")
                    tag['smes'] = {'users': [], 'userGroups': []}
            
            # Add delay between batches to avoid rate limiting
            if i + batch_size < len(tags_with_smes):
                time.sleep(0.5)  # 500ms delay between batches
    
    # Set empty SMEs for tags without SMEs
    for tag in tags:
        if tag['subjectMatterExpertCount'] == 0:
            tag['smes'] = {'users': [], 'userGroups': []}

    return tags


def process_api_data(api_data, start_date, end_date, output_name=None):

    users = api_data['users']
    users = add_new_user_fields(users)
    users = process_tags(users, api_data['tags'])
    users = process_questions(users, api_data['questions'])
    users = process_articles(users, api_data['articles'])
    users = process_reputation_history(users, api_data['reputation_history'])
    users = process_users(users, start_date, end_date)

    # tags = process_communities(tags, api_data.get('communities'))

    if output_name:
        export_to_json(f'user_metrics_{output_name}', users)
    else:
        export_to_json('user_metrics', users)
    
    return users


def add_new_user_fields(users):

    for user in users:
        user['questions'] = []
        user['question_count'] = 0
        user['questions_with_no_answers'] = 0
        user['question_upvotes'] = 0
        user['question_downvotes'] = 0

        user['answers'] = []
        user['answer_count'] = 0
        user['answer_upvotes'] = 0
        user['answer_downvotes'] = 0
        user['answers_accepted'] = 0
        user['answer_response_times'] = []
        user['answer_response_time_median'] = 0

        user['articles'] = []
        user['article_count'] = 0
        user['article_upvotes'] = 0

        user['comments'] = []
        user['comment_count'] = 0

        user['total_upvotes'] = 0
        user['reputation_history'] = []
        user['net_reputation'] = 0

        user['searches'] = []
        user['communities'] = []
        user['sme_tags'] = []
        user['watched_tags'] = []

        user['account_longevity_days'] = round(
            (time.time() - user['creation_date'])/60/60/24)
        user['account_inactivity_days'] = round(
            (time.time() - user['last_access_date'])/60/60/24)
        
        try:
            if user['is_deactivated']:
                user['account_status'] = 'Deactivated'
            else:
                user['account_status'] = 'Active'
        except KeyError: # Stack Overflow Business or Basic
            user['account_status'] = 'Registered'
    return users


def process_reputation_history(users, reputation_history):

    for user in users:
        for event in reputation_history:
            if event['user_id'] == user['user_id']:
                    user['reputation_history'].append(event)

    return users


def process_tags(users, tags):
    '''
    Iterate through each tag, find the SMEs, and add the tag name to a new field
    on the user object, indicating which tags they're a SME for
    In some situations, a user may be listed as both an individual SME and a group SME
    '''
    for tag in tags:
        for user in users:
            for sme in tag['smes']['users']:
                if user['user_id'] == sme['id']:
                    user['sme_tags'].append(tag['name'])
                    continue # if user is an individual SME, skip the group SME check
            for sme in tag['smes']['userGroups']:
                if user['user_id'] == sme['id']:
                    user['sme_tags'].append(tag['name'])
        
    return users


def process_questions(users, questions):

    for question in questions:
        asker_id = validate_user_id(question['owner'])
        user_index = get_user_index(users, asker_id)

        if user_index == None: # if user was deleted, add them to the list
            deleted_user = initialize_deleted_user(asker_id, question['owner']['display_name'])
            users.append(deleted_user)
            user_index = get_user_index(users, asker_id)

        users[user_index]['questions'].append(question)

        if question.get('answers'):
            users = process_answers(users, question['answers'], question)

        if question.get('comments'):
            users = process_comments(users, question)

    return users

        
def process_answers(users, answers, question):

    for answer in answers:
        answerer_id = validate_user_id(answer['owner'])
        user_index = get_user_index(users, answerer_id)

        if user_index == None:
            deleted_user = initialize_deleted_user(answerer_id, answer['owner']['display_name'])
            users.append(deleted_user)
            user_index = get_user_index(users, answerer_id)

        users[user_index]['answers'].append(answer)
        answer_response_time_hours = (answer['creation_date'] - question['creation_date'])/60/60
        users[user_index]['answer_response_times'].append(answer_response_time_hours)

        if answer.get('comments'):
            users = process_comments(users, answer)

    return users


def process_comments(users, object_with_comments):

    for comment in object_with_comments['comments']:
        commenter_id = validate_user_id(comment['owner'])
        user_index = get_user_index(users, commenter_id)

        if user_index == None:
            deleted_user = initialize_deleted_user(commenter_id, comment['owner']['display_name'])
            users.append(deleted_user)
            user_index = get_user_index(users, commenter_id)

        users[user_index]['comments'].append(comment)

    return users


def process_articles(users, articles):

    for article in articles:
        author_id = validate_user_id(article['owner'])
        user_index = get_user_index(users, author_id)
        if user_index == None:
            deleted_user = initialize_deleted_user(author_id, article['owner']['display_name'])
            users.append(deleted_user)
            user_index = get_user_index(users, author_id)

        users[user_index]['articles'].append(article)

        # As of 2023.05.23, Article comments are slightly innaccurate due to a bug in the API
        # if article.get('comments'):
        #     for comment in article['comments']:
        #         commenter_id = validate_user_id(comment)
        #         tag_contributors[tag]['commenters'] = add_user_to_list(
        #             commenter_id, tag_contributors[tag]['commenters']
        #         )
        
    return users


def process_users(users, start_date, end_date):


    for user in users:
        for question in user['questions']:
            if question['creation_date'] > start_date and question['creation_date'] < end_date:
                user['question_count'] += 1
                user['question_upvotes'] += question['up_vote_count']
                user['question_downvotes'] += question['down_vote_count']
                if question['answer_count'] == 0:
                    user['questions_with_no_answers'] += 1

        for answer in user['answers']:
            if answer['creation_date'] > start_date and answer['creation_date'] < end_date:
                user['answer_count'] += 1
                user['answer_upvotes'] += answer['up_vote_count']
                user['answer_downvotes'] += answer['down_vote_count']
                if answer['is_accepted']:
                    user['answers_accepted'] += 1

        for article in user['articles']:
            if article['creation_date'] > start_date and article['creation_date'] < end_date:
                user['article_count'] += 1
                user['article_upvotes'] += article['score']

        for comment in user['comments']:
            if comment['creation_date'] > start_date and comment['creation_date'] < end_date:
                user['comment_count'] += 1

        for event in user['reputation_history']:
            if event['creation_date'] > start_date and event['creation_date'] < end_date:
                user['net_reputation'] += event['reputation_change']

        for answer_response_time in user['answer_response_times']:
            if answer_response_time <= 0:
                user['answer_response_times'].remove(answer_response_time)

        if user['answer_response_times']:
            user['answer_response_time_median'] = round(
                statistics.median(user['answer_response_times']), 2)
        else:
            user['answer_response_time_median'] = ''

        user['total_upvotes'] = user['question_upvotes'] + user['answer_upvotes'] + \
            user['article_upvotes']
        user['total_downvotes'] = user['question_downvotes'] + user['answer_downvotes']

    return users


def create_user_report(users, start_date, end_date, output_name):

    # Create a list of user dictionaries, sorted by net reputation
    sorted_users = sorted(users, key=lambda k: k['net_reputation'], reverse=True)

    # Select fields for the user report
    user_metrics = []
    for user in sorted_users:
        user_metric = {
            'User ID': safe_get_user_field(user, 'user_id', ''),
            'Display Name': safe_get_user_field(user, 'display_name', ''),
            'Net Reputation': safe_get_user_field(user, 'net_reputation', 0),
            'Account Longevity (Days)': safe_get_user_field(user, 'account_longevity_days', 0),
            'Account Inactivity (Days)': safe_get_user_field(user, 'account_inactivity_days', 0),

            'Questions': safe_get_user_field(user, 'question_count', 0),
            'Questions With No Answers': safe_get_user_field(user, 'questions_with_no_answers', 0),
            # 'Question Upvotes': user['question_upvotes'],
            # 'Question Downvotes': user['question_downvotes'],

            'Answers': safe_get_user_field(user, 'answer_count', 0),
            # 'Answer Upvotes': user['answer_upvotes'],
            # 'Answer Downvotes': user['answer_downvotes'],
            'Answers Accepted': safe_get_user_field(user, 'answers_accepted', 0),
            'Median Answer Time (Hours)': safe_get_user_field(user, 'answer_response_time_median', 0),

            'Articles': safe_get_user_field(user, 'article_count', 0),
            # 'Article Upvotes': user['article_upvotes'],

            'Comments': safe_get_user_field(user, 'comment_count', 0),

            'Total Upvotes': safe_get_user_field(user, 'total_upvotes', 0),
            'Total Downvotes': safe_get_user_field(user, 'total_downvotes', 0),

            # 'Searches': user['searches'],
            # 'Communities': user['communities'],
            'SME Tags': ', '.join(safe_get_user_field(user, 'sme_tags', [])),
            # 'Watched Tags': user['watched_tags'],

            'Account Status': safe_get_user_field(user, 'account_status', ''),
            'Moderator': safe_get_user_field(user, 'moderator', False),

            'Email': safe_get_user_field(user, 'email', ''),
            'Title': safe_get_user_field(user, 'title', ''),
            'Department': safe_get_user_field(user, 'department', ''),
            'External ID': safe_get_user_field(user, 'external_id', ''),
            'Account ID': safe_get_user_field(user, 'account_id', '')
        }
        user_metrics.append(user_metric)
    

    # Export user metrics to CSV
    if output_name:
        export_to_csv(f'user_metrics_{output_name}', user_metrics)
    elif start_date and end_date:
        export_to_csv(f'user_metrics_{start_date}_to_{end_date}', user_metrics)
    else:
        export_to_csv('user_metrics', user_metrics)


def get_user_index(users, user_id):

    for index, user in enumerate(users):
        if user['user_id'] == user_id:
            return index
    
    return None # if user is not found


def initialize_deleted_user(user_id, display_name):

    user = {
        'user_id': user_id,
        'display_name': f"{display_name} (DELETED)",

        'questions': [],
        'question_count': 0,
        'questions_with_no_answers': 0,
        'question_upvotes': 0,
        'question_downvotes': 0,

        'answers': [],
        'answer_count': 0,
        'answer_upvotes': 0,
        'answer_downvotes': 0,
        'answers_accepted': 0,
        'answer_response_times': [],

        'articles': [],
        'article_count': 0,
        'article_upvotes': 0,

        'comments': [],
        'comment_count': 0,

        'total_upvotes': 0,
        'reputation_history': [],
        'net_reputation': 0,

        'searches': [],
        'communities': [],
        'sme_tags': [],
        'watched_tags': [],
        
        'moderator': '',
        'email': '',
        'title': '',
        'department': '',
        'external_id': '',
        'account_id': '',
        'account_longevity_days': '',
        'account_inactivity_days': '',
        'account_status': 'Deleted'
    }

    return user


def safe_get_user_field(user, field, default=''):
    """
    Safely get a user field, returning a default value if the field doesn't exist.
    This prevents KeyError exceptions when processing user data.
    """
    try:
        return user[field]
    except (KeyError, TypeError):
        return default


def validate_user_id(user):
    """
    Checks to see if a user_id is present. If not, the user has been deleted. In this case, the
    user_id can be extracted from the display_name. For example, if a deleted user's display_name
    is 'user123', the user_id will be 123."""

    try:
        user_id = user['user_id']
    except KeyError: # if user_id is not present, the user was deleted
        try:
            user_id = int(user['display_name'].split('user')[1])
        except IndexError:
            # This shouldn't happen, but if it does, the user_id will be the display name
            # This seems to only happen in the internal testing environment
            user_id = user['display_name']

    return user_id


def export_to_csv(data_name, data):

    date = time.strftime("%Y-%m-%d")
    file_name = f"{date}_{data_name}.csv"

    csv_header = [header for header in list(data[0].keys())]
    with open(file_name, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(csv_header)
        for tag_data in data:
            writer.writerow(list(tag_data.values()))
        
    print(f'CSV file created: {file_name}')


def export_to_json(data_name, data):
    
    file_name = data_name + '.json'
    directory = 'data'

    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, file_name)

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

    print(f'JSON file created: {file_name}')


def read_json(file_name):
    
    directory = 'data'
    file_path = os.path.join(directory, file_name)
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        raise FileNotFoundError
    
    return data


if __name__ == '__main__':

    main()
