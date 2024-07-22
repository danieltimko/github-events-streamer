from collections import defaultdict
from datetime import datetime, timedelta
from flask import jsonify, Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import os

from models import Event


DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')

app = Flask(__name__)
url = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}'
engine = create_engine(url)


@app.route('/avg-pr-delay')
def avg_pr_delay():
    repo = request.args.get('repo')
    if not repo:
        return "The 'repo' parameter is required.", 400
    with Session(engine) as session:
        events = (session.query(Event)
                  .filter(Event.repo == repo)
                  .filter(Event.type == 'PullRequestEvent')
                  .order_by(Event.created_at)
                  .all())
    if len(events) < 2:
        return jsonify({'avg_time_seconds': 'N/A'}), 200
    sum_times = 0
    for i in range(1, len(events)):
        sum_times += (events[i].created_at - events[i-1].created_at).total_seconds()
    avg_time = round(sum_times / (len(events)-1), 3)
    return jsonify({'avg_time_seconds': avg_time}), 200


@app.route('/events/count-by-type')
def events_by_type():
    offset = request.args.get('offset')
    if not offset:
        return "The 'offset' parameter is required.", 400
    try:
        offset = int(offset)
    except ValueError:
        return "The 'offset' parameter must be integer.", 400
    t = datetime.now() - timedelta(minutes=offset)
    with Session(engine) as session:
        events = session.query(Event).filter(Event.created_at > t).all()
    result = defaultdict(lambda: 0)
    for e in events:
        result[e.type] += 1
    return result, 200


@app.route('/events/pr-count-by-repo')
def pr_by_repo():
    with Session(engine) as session:
        events = session.query(Event).filter(Event.type == 'PullRequestEvent').all()
    result = defaultdict(lambda: 0)
    for e in events:
        result[e.repo] += 1
    return result, 200


if __name__ == '__main__':
    app.run(debug=True)
