from asyncio import (
    new_event_loop, 
    set_event_loop
)
from typing import Coroutine

try:
    # We can use uvloop as event loop
    # on Linux systems, it's around 2x
    # faster than Python's default.
    from uvloop import new_event_loop
    FAST_EVENT_LOOP = True
except ModuleNotFoundError:
    FAST_EVENT_LOOP = False

__version__ = '4.0'

# Define and set global event loop
loop = new_event_loop()
set_event_loop(loop)

from . import api
from . import constants
from . import crypto
from . import db
from . import errors
from . import keys
from . import tools


__all__ = [
    'api',
    'constants',
    'crypto',
    'db',
    'errors',
    'keys',
    'tools',
    'loop',
    'sync',
    'new_event_loop',
    'FAST_EVENT_LOOP'
]

def sync(coroutine: Coroutine):
    """
    Will call asynchronous function
    in ``tgbox.loop`` and return result.
    """
    return loop.run_until_complete(coroutine)
