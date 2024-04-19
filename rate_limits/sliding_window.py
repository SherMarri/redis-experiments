# Rate limit algorithm: Sliding Window

import redis
import time

redis_client = redis.Redis(host="localhost", port=6379, db=0)


class RateLimiter:
    """Rate limiter using sliding window algorithm"""

    def __init__(self, redis: redis.Redis):
        self.redis_conn = redis

    def rate_limit(self, key, limit, window):
        """Rate limit the key"""
        current_time = int(time.time())
        pipe = (
            self.redis_conn.pipeline()
        )  # Use pipeline to execute multiple commands atomically
        pipe.zremrangebyscore(
            key, "-inf", current_time - window
        )  # Remove the old timestamps
        pipe.zadd(
            key, {current_time: current_time}
        )  # Add the current time to the sorted set
        pipe.zcard(key)  # Get the current count
        pipe.expire(key, window)  # Set the expiry time
        items_removed, _, current_count, _ = (
            pipe.execute()
        )  # Execute the commands and get the results
        if items_removed:
            print(f"Removed {items_removed} items")
        return current_count <= limit


# Rate limit the key "user1" to 5 requests per 10 seconds
rate_limiter = RateLimiter(redis_client)


def simulation_1():
    # Simulate multiple requests, requests should fail after the limit is reached
    key = "user1"
    limit = 5
    window = 10

    for i in range(10):
        print(f"Request {i+1}: {rate_limiter.rate_limit(key, limit, window)}")
        time.sleep(1)  # Sleep for 1 second


def simulation_2():
    # Simulate requests after the window has expired
    key = "user2"
    limit = 5
    window = 10

    for i in range(10):
        print(f"Request {i+1}: {rate_limiter.rate_limit(key, limit, window)}")
        time.sleep(1)  # Sleep for 1 second
    time.sleep(window)  # Sleep for the window duration
    for i in range(5):
        print(f"Request {i+11}: {rate_limiter.rate_limit(key, limit, window)}")
        time.sleep(1)  # Sleep for 1 second


def simulation_3():
    """
    1. Make 3 requests each second for 3 seconds
    2. Wait for 5 seconds
    3. Make 6 requests each second, the last request should fail

    # Example:
        Second 0: []
        Second 1: [1]
        Second 2: [1, 1]
        Second 3: [1, 1, 1]
        Second 4: [1, 1, 1, 0]
        Second 5: [1, 1, 1, 0, 0, 0]
        Second 6: [1, 1, 1, 0, 0, 0, 0]
        Second 7: [1, 1, 1, 0, 0, 0, 0, 0]
        Second 8: [1, 1, 1, 0, 0, 0, 0, 0, 0]
        Second 9: [1, 1, 1, 0, 0, 0, 0, 0, 0, 1]
        Second 10: [1, 1, 0, 0, 0, 0, 0, 0, 1, 1]
        Second 11: [1, 0, 0, 0, 0, 0, 0, 1, 1, 1]
        Second 12: [0, 0, 0, 0, 0, 0, 1, 1, 1, 1]
        Second 13: [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
        Second 14: [0, 0, 0, 0, 1, 1, 1, 1, 1, 1]  # False
    """
    key = "user3"
    limit = 5
    window = 10

    for i in range(3):
        print(f"Request {i+1}: {rate_limiter.rate_limit(key, limit, window)}")
        time.sleep(1)

    time.sleep(5)

    for i in range(6):
        print(f"Request {i+4}: {rate_limiter.rate_limit(key, limit, window)}")
        time.sleep(1)


# simulation_1()
# simulation_2()
simulation_3()
