import redis
import sys


def redis_connect() -> redis.client.Redis:
    try:
        client = redis.Redis(
            host="localhost",
            port=6379,
            db=0,
        )
        ping = client.ping()
        if ping is True:
            return client
    except redis.ConnectionError:
        print("Can't conenct to Redis")
        sys.exit(1)
