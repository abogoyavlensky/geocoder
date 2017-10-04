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
Please setup docker-engine and docker-compose before trying to start service.
You should create `.env` file in dir root of the project. Env file must 
contain at least one environment variable:
```bash
GOOGLE_MAPS_API_KEY=[secret]
```

## How to start
```bash
$ docker-compose up
```

## Usage
For example try next request in browser:
```bash
$ http://localhost:8000/geocode/?address=Москва,+Ботаничесикй+переулок+5
```

Or the same request in console with curl:
```bash
http://localhost:8000/geocode/?address=%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0,+
%D0%91%D0%BE%D1%82%D0%B0%D0%BD%D0%B8%D1%87%D0%B5%D1%81%D0%BA%D0%B8%D0%B9+
%D0%BF%D0%B5%D1%80%D0%B5%D1%83%D0%BB%D0%BE%D0%BA+5
```
