from flask import Flask, request, redirect, render_template
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, user_icon_img, Post

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///blogly"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 's3cr3tk3y'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

# Connect DB + Flask app
connect_db(app)
db.drop_all()
db.create_all()


@app.route('/')
def home():
    """Homepage redirects to list of users."""

    return redirect("/users")

@app.route('/users')
def users_list():
    """Show a page with a list of all users"""

    users = User.query.all()
    return render_template('users/index.html', users=users)


@app.route('/users/new', methods=["GET"])
def new_user_form():
    """Show add-user form"""

    return render_template('users/new.html')


@app.route("/users/new", methods=["POST"])
def add_user():
    """Handle form submission for adding a new user"""

    new_user = User(
        first_name=request.form['first_name'],
        last_name=request.form['last_name'],
        image_url=request.form['image_url'] or None)

    db.session.add(new_user)
    db.session.commit()

    return redirect("/users")


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show a page with info on a clicked user link"""

    user = User.query.get_or_404(user_id)
    return render_template('users/show.html', user=user)


@app.route('/users/<int:user_id>/edit')
def edit_user_form(user_id):
    """Show a form to edit an existing user"""

    user = User.query.get_or_404(user_id)
    return render_template('users/edit.html', user=user)


@app.route('/users/<int:user_id>/edit', methods=["POST"])
def update_user(user_id):
    """Handle form submission for updating an existing user"""

    user = User.query.get_or_404(user_id)
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.image_url = request.form['image_url'] or user_icon_img

    db.session.commit()

    return redirect("/users")


@app.route('/users/<int:user_id>/delete', methods=["POST"])
def delete_user(user_id):
    """Handle form submission for deleting an existing user"""

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect("/users")

##################### Post routes #####################

@app.route('/users/<int:user_id>/posts/new', methods=['GET', 'POST'])
def new_post_form(user_id):
    """Show a form to add a new post for a user"""

    user = User.query.get_or_404(user_id)

    if (request.method == "POST"):
        title = request.form['title']
        content = request.form['content']

        new_post = Post(title=title, content=content, user_id=user.id)
        db.session.add(new_post)
        db.session.commit()

        return redirect(f'/users/{user.id}')

    return render_template('posts/new_post.html', user=user)

@app.route('/posts/<int:post_id>')
def show_post_detail(post_id):
    """Show users specific post details"""

    post = Post.query.get_or_404(post_id)

    return render_template('posts/post_detail.html', post=post)

@app.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    """Show a form to edit the selected post"""

    post = Post.query.get_or_404(post_id)

    if(request.method == 'POST'):
        post.title = request.form['title']
        post.content = request.form['content']

        db.session.commit()

        return redirect(f'/users/{post.user_id}')

    return render_template('/posts/edit_post.html', post=post)

@app.route('/posts/<int:post_id>/delete', methods=["POST"])
def delete_post(post_id):
    """Handle form submission for deleting an existing user"""

    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()

    return redirect(f"/users/{post.user_id}")
