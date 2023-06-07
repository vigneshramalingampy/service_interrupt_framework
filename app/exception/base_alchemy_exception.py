from sqlalchemy.exc import OperationalError, ProgrammingError


class BaseAlchemyException(ProgrammingError, OperationalError):
    pass
