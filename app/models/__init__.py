import inspect

from sqlalchemy import Engine, create_engine, NullPool
from sqlalchemy.orm import sessionmaker

from shared_utils.Env import Env

class DatabaseEnvironment:
    _engine = None
    _session_maker = None

    _sessions = []

    @classmethod
    def update_db_connection(cls, testing=False) -> None:

        if cls._engine is not None:
            [s.close() for s in cls._sessions]
            cls._engine.dispose()

        if testing:
            cls._engine = create_engine(f'sqlite:///{Env.DB_FILE}', poolclass=NullPool)
        else:
            cls._engine = create_engine(f'sqlite:///{Env.DB_FILE}')

        cls._session_maker = sessionmaker(bind=cls._engine)

    @classmethod
    def engine(cls) -> Engine:
        return cls._engine

    @classmethod
    def session(cls) -> sessionmaker:
        s = cls._session_maker()
        cls.track_session(s)
        return s

    @classmethod
    def track_session(cls, s):
        print('opened new session! caller: ' + str(inspect.stack()[1][0]))
        cls._sessions.append((s, inspect.stack()[1][0]))
        return s

    @classmethod
    def print_sessions_info(cls):
        [print('   active:', item[0].is_active, ' from:', item[1]) for item in cls._sessions]

# for the sake not modifying the rest of the code too much
def Session() -> sessionmaker:
    return DatabaseEnvironment.session()

def get_engine() -> Engine:
    return DatabaseEnvironment.engine()