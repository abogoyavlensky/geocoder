# Task

Develop in Python a caching service for an "unstable backend" (you could implement it by your own,
for example you could use https://maps.googleapis.com API with random lags).
Caching service should expose one endpoint:

```bash
GET /geocode?address="some address"
```

which returns and caches all successful responses from backend.
"Unstable backend" might occasionally return 5xx errors or respond slowly.
Errors should not be cached because backend (most probably) will respond successfully next time.
Clients await the response from your service for 2 sec at max.

You should probably pay attention to:
1. The service returns answer in no more than 2 seconds.
2. The service tries to get correct answer from unstable backend "insistently".
3. Caching
4. Scaling

## Setup
Please setup `docker-engine` and `docker-compose` before trying to run service.
If you want to add some configuration you could create `.env` file in root dir
of the project. Env file could contain several environment variables:
```bash
GOOGLE_MAPS_API_KEY=[secret]
IS_CACHE_ENABLED=True | False  # `True` by default 
```

## How to run
Following command should start for you `backend`, `redis` and several 
containers with `service`-app:
```bash
$ docker-compose up
```

## Usage
Now you could request geocoding for any address. For example, please try 
following request in browser:
```bash
$ http://localhost:8000/geocode/?address=Moscow,+Tulskaya+10
```

Or the same request in console using `curl` and `time` to check response time:
```bash
$ time curl http://localhost:8000/geocode/?address=Moscow,+Tulskaya+10
```


## Tests
```bash
$ docker-compose run -f docker-compose.tests.yml build
$ docker-compose run -f docker-compose.tests.yml up
```

To run tests in watching mode for developing:
```bash
$ docker-compose -f docker-compose.tests.yml run service ptw
```
