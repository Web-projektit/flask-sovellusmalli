# Huom. väliviiva ei ole sallittu waitress-palvelimella, esim:
# waitress-serve --port 8000 flask-sovellus:app, tai
# waitress-serve --listen 127.0.0.1:5000 flask-sovellus:app
# Tässä on siksi sama sovellus väliviivalla ja ilman.
import os
import click
from flask_migrate import Migrate
from app import create_app, db
from app.models import User, Role, Permission

flask_config = os.getenv('FLASK_CONFIG') or 'default'
app = create_app(flask_config)
print("app,FLASK_FONFIG:" + flask_config)
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

