import datetime

from sqlalchemy import text
from . import db
from . import scheduler


def load_epgs():
    """Load EPGs"""
    with scheduler.app.app_context():
        from app.coretv import load_epgs
        load_epgs()
        db.engine.execute(
            text('delete from epgs where date_stop < :date_stop')\
                .execution_options(autocommit=True),
            date_stop = datetime.datetime.now() - datetime.timedelta(hours=2))

def load_origins():
    """Load ORIGINS"""
    with scheduler.app.app_context():
        from app.coretv import load_origins
        load_origins()
