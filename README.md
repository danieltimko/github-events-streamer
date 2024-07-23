
## Documentation
![github-events-streamer container diagram](img/diagram.svg)

The application consists of 3 components:
- PostgreSQL database storing the events data.
- Events streamer that perpetually fetches data from GitHub Events API and saves it to the DB.
- REST API with 4 endpoints:
  - **/avg-pr-delay?repo=\<repo url\>** -- calculate the average time between pull requests for a given repository.  
  - **/events/count-by-type?offset=\<time offset in minutes\>** -- return the total number of events grouped by the event type for a given offset
  - **/events/count-by-type/plot?offset=\<time offset in minutes\>** -- same as previous, but returns a plot visualization instead of json.
  - **/events/pr-count-by-repo** -- helper endpoint to quickly find repos with multiple PR events

Note that GitHub Events API provides the events with 5 minutes delay, therefore offset<=5 will return no events.

## How to run
1. Make sure you have Docker installed.
2. Generate a GitHub API token.
3. Add the token (along with the other configuration items) to the configuration in the `.env` file.
4. `docker compose up -d`
5. API is now running on `localhost:5000`. Sample request: `http://localhost:5000/events/count-by-type?offset=10`

## Possible improvements:
- In production, I would use wait-for-it script to wait for database to initialize.
- In production, it could be better to use smth like Docker secrets for passwords etc.
- I have a concern about the true accuracy. Even for authenticated request there is a limit of 5000/hour
so data processing rate likely needs to be manually decreased (sleep in between fetches, POOL_INTERVAL_SECONDS)
in order not to run out of quota. However, then a question is if some events are not missed in between.
If the data generation rate is too big, it might be practically impossible to process truly all events.
- Time series chart for a specific event could be interesting.
