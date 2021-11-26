from asyncio import new_event_loop

__all__ = [
    'api',
    'constants',
    'crypto',
    'db',
    'errors',
    'keys',
    'tools',
    'loop'
]
# Define global event loop
loop = new_event_loop()
