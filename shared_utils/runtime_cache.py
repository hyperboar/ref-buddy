from functools import wraps

from typing_extensions import Self

DB_CHANGED = 'the_change'
DB_SIGNIFICANT_CHANGE = 'the_important_change'

class RuntimeCache:

    cache:Self = None

    def __init__(self):
        self.storage = {}

    @classmethod
    def current_cache(cls) -> Self:
        if cls.cache is None:
            cls.cache = RuntimeCache()
        return cls.cache

    def increment(self, marker):
        if marker in self.storage:
            self.storage[marker] += 1
        else:
            self.storage[marker] = 1

    def clear(self, marker):
        if marker in self.storage:
            self.storage[marker] = 0

    def get_marker(self, marker):
        if marker in self.storage:
            return self.storage[marker]
        else:
            return 'oops'


def increment_marker(marker):
    def inner_1(func):
        def inner_2(*args, **kwargs):
            cache = RuntimeCache.current_cache()
            cache.increment(marker)
            print(marker, ': ', cache.get_marker(marker), ' at ', str(func))
            return func(*args, **kwargs)
        return inner_2
    return inner_1

def increment_marker_async(marker):
    def inner_1(func):
        @wraps(func)
        async def inner_2(*args, **kwargs):
            cache = RuntimeCache.current_cache()
            cache.increment(marker)
            print(marker, ': ', cache.get_marker(marker), ' at ', str(func))
            return await func(*args, **kwargs)
        return inner_2
    return inner_1

def clear_marker(func):
    cache = RuntimeCache.current_cache()
    cache.clear('the_change')
    return func

