import logging

from src.helpers import BadRequest
from src.modules import SourceHandler

__all__ = (
    'check_sources'
)
LOGGER = logging.getLogger('schedule')


async def check_sources():
    try:
        source_handler = SourceHandler()
        await source_handler.check_source_1_for_updates()
        await source_handler.check_source_2_for_updates()
    except BadRequest as e:
        LOGGER.error(str(e))
