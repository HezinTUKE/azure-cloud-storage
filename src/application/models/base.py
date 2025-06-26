from functools import wraps

import sqlalchemy.ext.declarative as dec
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from application import config_db

db_url = f"""postgresql+asyncpg://{config_db.get("username")}:{config_db.get("password")}@{config_db.get("host")}:{config_db.get("port")}/{config_db.get("db_name")}"""

engine = create_async_engine(db_url, connect_args={})

Base = dec.declarative_base()


def with_session(retries: int = 3):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, session: AsyncSession = None, **kwargs):
            if session is None:
                session = AsyncSession(engine)
                should_close_session = True
            else:
                should_close_session = False

            for attempt in range(retries):
                try:
                    result = await func(*args, session=session, **kwargs)
                    await session.commit()
                    return result
                except Exception as ex:
                    last_exception = ex
                    await session.rollback()
                    if attempt == retries - 1:
                        raise last_exception
                except Exception as ex:
                    raise
                finally:
                    if should_close_session:
                        await session.close()
            raise RuntimeError("Unexpected error: retry loop exhausted without result")

        return wrapper

    return decorator
