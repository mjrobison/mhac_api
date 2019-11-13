from flask_script import Manager

from app import app, db
import build_dev_db

manager = Manager(app)

@manager.command
def createdb(drop_first=False, build=False):
    """Creates the database."""
    if drop_first:
        db.drop_all()
    db.create_all()
    if build:
        build_dev_db.run()


if __name__ == '__main__':
    manager.run()
