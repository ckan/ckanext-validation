# encoding: utf-8

import logging
import six

from ckan.lib.redis import connect_to_redis

log = logging.getLogger(__name__)

REDIS_PREFIX = 'ckanext-validation:'


class RedisHelper:

    def __init__(self, prefix=REDIS_PREFIX):
        self.prefix = prefix

    def _get_cache_key(self, path):
        return self.prefix + path

    def get(self, key):
        ''' Get a value from the cache, if available.
        Returned values will be converted to text type instead of bytes.
        '''
        cache_key = self._get_cache_key(key)
        try:
            redis_conn = connect_to_redis()
            cache_value = redis_conn.get(cache_key)
        except Exception as e:
            log.error("Failed to connect to Redis cache: %s", e)
            cache_value = None
        if cache_value is not None and hasattr(six, 'ensure_text'):
            cache_value = six.ensure_text(cache_value)
        return cache_value

    def pop(self, key):
        ''' Get a value from the cache, if available, clearing the cache.
        Returned values will be converted to text type instead of bytes.
        '''
        cache_key = self._get_cache_key(key)
        try:
            redis_conn = connect_to_redis()
            cache_value = redis_conn.get(cache_key)
            redis_conn.delete(cache_key)
        except Exception as e:
            log.error("Failed to connect to Redis cache: %s", e)
            cache_value = None
        if cache_value is not None and hasattr(six, 'ensure_text'):
            cache_value = six.ensure_text(cache_value)
        return cache_value

    def put(self, key, value, expiry=None):
        ''' Set a URL value in the cache, if available, with the
        specified expiry (seconds). If expiry is None, no action is taken.
        '''
        if expiry:
            cache_key = self._get_cache_key(key)
            try:
                redis_conn = connect_to_redis()
                redis_conn.set(cache_key, str(value), ex=expiry)
            except Exception as e:
                log.error("Failed to connect to Redis cache: %s", e)

    def delete(self, key):
        ''' Delete a value from the cache, if available.
        '''
        cache_key = self._get_cache_key(key)
        try:
            redis_conn = connect_to_redis()
            redis_conn.delete(cache_key)
        except Exception as e:
            log.error("Failed to connect to Redis cache: %s", e)
