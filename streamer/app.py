from dateutil import parser
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
import requests
import os
import time

from models import Base, Event

GITHUB_EVENTS_API_URL = 'https://api.github.com/events'
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')

POOL_INTERVAL = int(os.getenv('POOL_INTERVAL_SECONDS'))


def fetch_events():
    page = 1
    all_events = []
    while True:
        headers = {'Authorization': f'token {GITHUB_TOKEN}'}
        params = {'page': page, 'per_page': 100}
        response = requests.get(GITHUB_EVENTS_API_URL,
                                params=params, headers=headers)
        requests_left = int(response.headers.get('X-RateLimit-Remaining', 0))
        print(requests_left)
        if requests_left == 0:
            print('Requests quota exhausted. Waiting to reset.')
            return all_events
        events = response.json()
        # Possible improvement: keep ID of last saved event to break earlier
        try:
            response.raise_for_status()
        except:
            break
        for e in events:
            print(e['created_at'], e['repo']['url'], e['type'])
        all_events.extend(events)
        page += 1
    return all_events


def save_to_db(db_session, events):
    events = list(filter(lambda e: e['type'] in ['WatchEvent',
                                                 'PullRequestEvent',
                                                 'IssuesEvent'],
                         map(lambda e: {
                             'github_id': int(e['id']),
                             'type': e['type'],
                             'created_at': parser.isoparse(e['created_at']),
                             'repo': e['repo']['url']
                         }, events)))
    # Duplicates could happen, skip them
    query = insert(Event).values(events).on_conflict_do_nothing(
        index_elements=['github_id'])
    db_session.execute(query)
    db_session.commit()


if __name__ == '__main__':
    # Wait for DB initialization, in production replace by wait-for-it script
    time.sleep(5)

    url = (f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@'
           f'{DB_HOST}:5432/{DB_NAME}')
    engine = create_engine(url)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        while True:
            events = fetch_events()
            save_to_db(session, events)
            time.sleep(POOL_INTERVAL)
