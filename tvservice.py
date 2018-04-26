#!/usr/bin/env python

import os
import sys
import click

from dotenv import load_dotenv
load_dotenv()

COVERAGE = os.getenv('COVERAGE')
if COVERAGE:
    import coverage
    COVERAGE = coverage.coverage(branch=True, include='app/*')
    COVERAGE.start()

from flask_migrate import Migrate, upgrade
from app import create_app, db
from app.models import (Origin, Group, Channel,
                        EpgChannel, Epg,
                        User, Role, Permission,
                        UserChannels, UserClients)

app = create_app()
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Origin=Origin, Group=Group, Channel=Channel,
                EpgChannel=EpgChannel, Epg=Epg,
                User=User, Role=Role, Permission=Permission,
                UserClients=UserClients, UserChannels=UserChannels)


@app.cli.command()
@click.option('--coverage/--no-coverage', default=False,
              help='Run tests under code coverage.')
def test(coverage):
    """Run the unit tests."""
    if coverage and not os.getenv('COVERAGE'):
        import subprocess
        os.environ['COVERAGE'] = '1'
        sys.exit(subprocess.call(sys.argv))

    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COVERAGE:
        COVERAGE.stop()
        COVERAGE.save()
        print('Coverage Summary:')
        COVERAGE.report()
        COVERAGE.erase()


@app.cli.command()
@click.option('--length', default=25,
              help='Number of functions to include in the profiler report.')
@click.option('--profile-dir', default=None,
              help='Directory where profiler data files are saved.')
def profile(length, profile_dir):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app,
                                      restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()


@app.cli.command()
@click.option('--module', default=None, help='')
def load_origins(module):
    """Load origins"""
    from app.coretv import load_origins
    load_origins(module)


@app.cli.command()
@click.option('--module', default=None, help='')
def load_epgs(module):
    """Load EPGs"""
    from app.coretv import load_epgs
    load_epgs(module)


@app.cli.command()
def deploy():
    """Run deployment tasks."""
    # migrate database to latest revision
    upgrade()
    # create or update user roles
    Role.deploy_roles()
    Channel.deploy_channels()
    User.deploy_users()
