from redis import Redis
from Config.envConfig import Settings,get_settings

env:Settings = get_settings()

redisConnect = Redis(host=env.redis_host,port=env.redis_port)

if redisConnect.ping():
    print("Redis Connected")
else:
    print("Redis Not Connected")
