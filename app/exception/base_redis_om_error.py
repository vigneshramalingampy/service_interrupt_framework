from redis_om.model.model import NotFoundError, QueryNotSupportedError, RedisModelError


class BaseRedisOmError(
    RedisModelError,
    NotFoundError,
    QueryNotSupportedError,
):
    pass
