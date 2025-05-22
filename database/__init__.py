from importlib_metadata import version
from flask import Flask

flask_major_version = int(version("flask")[0])

import MySQLdb
from MySQLdb import cursors
from flask import current_app

app = Flask(__name__)


if flask_major_version >= 2:
    from flask import g
    ctx = g
else:
    from flask import _app_ctx_stack
    ctx = _app_ctx_stack.top

class MySQL:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize the `app` for use with this
        :class:`~flask_mysqldb.MySQL` class.
        This is called automatically if `app` is passed to
        :meth:`~MySQL.__init__`.

        :param flask.Flask app: the application to configure for use with
            this :class:`~flask_mysqldb.MySQL` class.
        """



        # Define MySQL configuration
        app.secret_key = 'nickson'
        app.config['MYSQL_HOST'] = 'localhost'
        app.config['MYSQL_USER'] = 'root'
        app.config['MYSQL_PASSWORD'] = ''
        app.config['MYSQL_DB'] = 'riceinsect_db'
        
        app.config["MYSQL_CONNECT_TIMEOUT"] = 100


        if hasattr(app, "teardown_appcontext"):
            app.teardown_appcontext(self.teardown)

    @property
    def connect(self):
        kwargs = {}

        if current_app.config["MYSQL_HOST"]:
            kwargs["host"] = current_app.config["MYSQL_HOST"]

        if current_app.config["MYSQL_USER"]:
            kwargs["user"] = current_app.config["MYSQL_USER"]

        if current_app.config["MYSQL_PASSWORD"]:
            kwargs["passwd"] = current_app.config["MYSQL_PASSWORD"]

        if current_app.config["MYSQL_DB"]:
            kwargs["db"] = current_app.config["MYSQL_DB"]
            
        if current_app.config["MYSQL_CONNECT_TIMEOUT"]:
            kwargs["connect_timeout"] = current_app.config["MYSQL_CONNECT_TIMEOUT"]

        return MySQLdb.connect(**kwargs)

    @property
    def connection(self):
        """Attempts to connect to the MySQL server.

        :return: Bound MySQL connection object if successful or `None` if unsuccessful.
        """

        if ctx is not None:
            if not hasattr(ctx, "mysql_db"):
                ctx.mysql_db = self.connect
            return ctx.mysql_db

    def teardown(self, exception):
        if hasattr(ctx, "mysql_db"):
            ctx.mysql_db.close()
