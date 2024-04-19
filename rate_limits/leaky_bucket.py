import time
import redis


class RateLimiter:
    def __init__(self, capacity, leak_rate, redis_host="localhost", redis_port=6379):
        self.capacity = capacity
        self.leak_rate = leak_rate
        self.redis = redis.StrictRedis(
            host=redis_host, port=redis_port, decode_responses=True
        )

    def _get_timestamp(self):
        return int(time.time())

    def _leak(self, key, current_tokens, last_leak_time):
        now = self._get_timestamp()
        time_diff = now - last_leak_time
        leaked_tokens = time_diff * self.leak_rate
        new_tokens = min(self.capacity, current_tokens + leaked_tokens)
        self.redis.set(key, new_tokens)
        return new_tokens, now

    def _check_request(self, key, tokens):
        current_tokens = int(self.redis.get(key) or 0)
        if current_tokens >= tokens:
            return True
        return False

    def allow_request(self, key, tokens=1):
        current_tokens = int(self.redis.get(key) or self.capacity)
        last_leak_time = int(
            self.redis.get(f"{key}:last_leak_time") or self._get_timestamp()
        )
        current_tokens, last_leak_time = self._leak(key, current_tokens, last_leak_time)

        if self._check_request(key, tokens):
            self.redis.set(f"{key}:last_leak_time", last_leak_time)
            self.redis.decrby(key, tokens)
            return True
        return False


# Initialize rate limiter with a capacity of 10 tokens and a leak rate of 2 tokens per second
limiter = RateLimiter(capacity=10, leak_rate=2)


# Define a key to identify the rate limiting bucket
key = "user123"


def simulation_1():
    # Simple simulation of a request
    # Check if a request is allowed
    if limiter.allow_request(key):
        print("Request allowed")
    else:
        print("Request denied. Rate limit exceeded.")


def simulation_2():
    # Simulation of a burst of requests
    # Check if a request is allowed
    for i in range(15):
        if limiter.allow_request(key):
            print(f"Request {i + 1}: Allowed")
        else:
            print(f"Request {i + 1}: Denied. Rate limit exceeded.")


def simulation_3():
    # Simulation of a request needing 8 tokens
    # Check if a request is allowed
    if limiter.allow_request(key, tokens=8):
        print("Request allowed")
    else:
        print("Request denied. Rate limit exceeded.")

    # Request 8 tokens again
    if limiter.allow_request(key, tokens=8):
        print("Request allowed")
    else:
        print("Request denied. Rate limit exceeded.")


# simulation_1()
# simulation_2()
simulation_3()
