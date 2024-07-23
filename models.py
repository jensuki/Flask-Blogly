"""Models for Blogly."""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

user_icon_img = "https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png"

class User(db.Model):
    """User model"""

    __tablename__ = 'users'

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

    # create relationship between User & Post
    # only use delete-orphan from ONE to many
    posts = db.relationship('Post', backref='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User {self.first_name} {self.last_name}>"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Post(db.Model):
    """Post model"""

    __tablename__ = 'posts'

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime,
                           nullable=False,
                           default=datetime.now)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id'),
                        nullable=False)

    # relationship to Tag <--> PostTags
    tags = db.relationship('Tag', secondary="post_tags", backref="posts")

    def __repr__(self):
        return f"<Post {self.title} {self.content} {self.created_at}>"

# format date
    @property
    def formatted_date(self):
        return self.created_at.strftime("%B %d, %Y at %I:%M %p")

class Tag(db.Model):
    """Tag model"""

    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    def __repr__(self):
        return f"<Tag {self.name}>"


class PostTag(db.Model):
    """PostTag model (JOINER) table"""

    __tablename__ = 'post_tags'

    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', primary_key=True))
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key=True)



    def __repr__(self):
        return f"<PostTag {self.post_id} {self.tag_id}>"


# connect db to flask app
def connect_db(app):
    db.app = app
    db.init_app(app)

