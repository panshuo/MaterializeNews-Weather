#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Role, News, Weather, Favourite
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app()
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app,
                db=db,
                User=User,
                Role=Role,
                News=News,
                Weather=Weather,
                Favourite=Favourite
                )

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()

# if __name__ == '__main__':
#     app.run(host="0.0.0.0", port=5001)
