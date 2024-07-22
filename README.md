
## Documentation
![github-events-streamer container diagram](img/diagram.svg)
The application consists of 3 components:
- PostgreSQL database storing the events data.
- Events streamer that perpetually fetches data from GitHub Events API and saves it to the DB.
- REST API with 3 endpoints:
  - **/avg-pr-delay?repo=\<repo url\>** -- calculate the average time between pull requests for a given repository.  
  - **/events/count-by-type?offset=\<time offset in minutes\>** -- return the total number of events grouped by the event type for a given offset
  - **/events/pr-count-by-repo** -- helper endpoint to quickly find repos with multiple PR events

Note that GitHub Events API provides the events with 5 minutes delay, therefore offset<=5 will return no events.

## How to run
1. Make sure you have Docker installed.
2. Update the configuration in the `.env` file
3. `docker compose up -d`
4. API is now running on `localhost:5000`. Sample request: `http://localhost:5000/events/count-by-type?offset=10`

## Possible improvements:
- In production, I would use wait-for-it script to wait for database to initialize.
- In production, it could be better to use smth like Docker secrets for passwords etc.
- I have a concern about accuracy. Data processing rate is likely slower than data generation rate.
Plus, the rate limit is small -- 5000 per hour for authenticated requests. So it might be practically
impossible to process truly all events.
