import redis
import time
from concurrent.futures import ProcessPoolExecutor

redis_client = redis.Redis(host="localhost", port=6379, db=0)


class DistributedLockUtil:

    @staticmethod
    def acquire_lock(lock_name, timeout=10):
        return redis_client.set(lock_name, "lock", ex=timeout, nx=True)

    @staticmethod
    def release_lock(lock_name):
        return redis_client.delete(lock_name)


# Simulation of two processes trying to acquire the lock
lock_name = "lock1"

# Use ProcessPoolExecutor to simulate two processes
with ProcessPoolExecutor() as executor:
    future1 = executor.submit(DistributedLockUtil.acquire_lock, lock_name)
    future2 = executor.submit(DistributedLockUtil.acquire_lock, lock_name)

    print(f"Process 1: {future1.result()}")
    print(f"Process 2: {future2.result()}")

    # Release the lock
    DistributedLockUtil.release_lock(lock_name)
    # Or wait for the lock to expire
    # time.sleep(10)

    # Try to acquire the lock again
    future3 = executor.submit(DistributedLockUtil.acquire_lock, lock_name)
    print(f"Process 3: {future3.result()}")
