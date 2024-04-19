import time
import redis


class RateLimiter:
    def __init__(self, redis_client, key, capacity, refill_rate):
        self.redis_client = redis_client
        self.key = key
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.timestamp_key = f"{key}:timestamp"

    def acquire(self, tokens=1):
        current_time = time.time()
        last_refill_time = self.redis_client.get(self.timestamp_key)
        if last_refill_time is None:
            last_refill_time = current_time
            self.redis_client.set(self.timestamp_key, current_time)
        else:
            last_refill_time = float(last_refill_time.decode())

        refill_amount = (current_time - last_refill_time) * self.refill_rate
        current_tokens = min(
            refill_amount + float(self.redis_client.get(self.key) or 0), self.capacity
        )
        if current_tokens >= tokens:
            self.redis_client.set(self.key, current_tokens - tokens)
            self.redis_client.set(self.timestamp_key, current_time)
            return True
        else:
            return False


redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)

# Initialize a RateLimiter with a capacity of 10 tokens and a refill rate of 2 tokens per second
limiter = RateLimiter(redis_client, "my_bucket", 5, 1)

# Acquire tokens for a request
if limiter.acquire(3):
    print("Request allowed")
else:
    print("Request rate limited")

# Wait for some time to simulate token refill
time.sleep(1)

# Acquire tokens for another request
if limiter.acquire(5):
    print("Request allowed")
else:
    print("Request rate limited")
