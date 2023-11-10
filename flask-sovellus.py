import os
import click
from flask_migrate import Migrate
from app import create_app, db
from app.models import User, Role, Permission

flask_config = os.getenv('FLASK_CONFIG') or 'default'
print("app,FLASK_CONFIG:" + flask_config)
app = create_app(flask_config)
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Permission=Permission)

@app.cli.command()
@click.argument('test_names', nargs=-1)
def test(test_names):
    """Run the unit tests."""
    import unittest
    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

