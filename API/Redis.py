import redis

class RCache:
    # Define a constructor
    def __init__(self, host, port):
        self.redis_obj = redis.StrictRedis(host=host, port=port, db=0)

    # Set the element in the stack
    def push(self, key, data):
        self.redis_obj.set(key, data, 3600*1) #defaul is 1 hour

    # Get the element saved in stack
    def pop(self, key):
        data = self.redis_obj.get(key)
        return data
