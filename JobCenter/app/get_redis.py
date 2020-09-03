import redis
from .config import REDIS_DB_URL
from .config import Config

# client = redis.Redis(host = '127.0.0.1', port = 6379)

# client.set('language', 'Python')
# print(client.get('language'))
#
# client.set('language', 'Python', px = 10000)
# print(client.get('language'))
# print(client.ttl('language'))

def connect_redis():
    return redis.Redis(host=REDIS_DB_URL.get('host'), port=REDIS_DB_URL.get('port'))
#
#
def get_redis_data(key):
    conn = connect_redis()
    data = conn.get(key)
    return data


def set_redis_data(key, value, ex):
    conn = connect_redis()
    conn.setex(key, value, ex)
    # conn.set(
    #     name=key,
    #     data=value,
    #     ex='120'  # 第三个参数表示Redis过期时间,不设置则默认不过期
    # )
    # 存到Redis
