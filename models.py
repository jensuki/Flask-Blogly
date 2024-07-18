"""Models for Blogly."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

user_icon_img = "https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png"

class User(db.Model):
    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    first_name = db.Column(db.String(25),
                           nullable=False)
    last_name = db.Column(db.String(25),
                          nullable=False)
    image_url = db.Column(db.Text,
                          nullable=False,
                          default=user_icon_img)

    def __repr__(self):
        return f"<User {self.first_name} {self.last_name}>"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

# connect db to flask app
def connect_db(app):
    db.app = app
    db.init_app(app)

