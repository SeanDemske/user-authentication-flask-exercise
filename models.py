"""Models for feedback app."""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class User(db.Model):
    """User"""

    __tablename__ = "users"

    username = db.Column(db.String(20),
                    primary_key=True,
                    nullable=False,
                    unique=True)
    password = db.Column(db.Text,
                    nullable=False)
    email = db.Column(db.String(50),
                    nullable=False,
                    unique=True)
    first_name = db.Column(db.String(30),
                    nullable=False)
    last_name = db.Column(db.String(30),
                    nullable=False)

    feedback = db.relationship("Feedback", backref="user", cascade="all,delete")

    @classmethod
    def register(cls, username, password, first_name, last_name, email):
        """Register user with hashed password"""

        hashed = bcrypt.generate_password_hash(password)

        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        return cls(username=username, password=hashed_utf8, first_name=first_name, last_name=last_name, email=email)

    @classmethod
    def login(cls, username, password):
        """Authenticates user login"""

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False

    @classmethod
    def is_signed_in(cls, session):
        """Checks if user is signed in"""

        if "user" in session:
            return True
        else:
            return False

class Feedback(db.Model):
    """Feedback"""

    __tablename__ = "feedback"

    id = db.Column(db.Integer,
                autoincrement=True,
                primary_key=True)
    title = db.Column(db.String(100),
                nullable=False)
    content = db.Column(db.Text,
                nullable=False)
    username = db.Column(db.String(20),
                db.ForeignKey("users.username"),
                nullable=False)