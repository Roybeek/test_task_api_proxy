import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.modules import SourceHandler

__all__ = (
    'schedule',
)

from src.schedule.tasks import check_sources

LOGGER = logging.getLogger('schedule')


def schedule(source_handler: SourceHandler):
    LOGGER.info('scheduler starting')

    scheduler = AsyncIOScheduler()

    scheduler.add_job(check_sources, 'interval', seconds=900)
