"""Flask app for feedback"""

from flask import Flask, request, redirect, render_template, jsonify, session
from models import db, connect_db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm
from werkzeug.exceptions import Unauthorized

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:developer@localhost:5432/feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = "SECRET!"

connect_db(app)
db.create_all()

# from flask_debugtoolbar import DebugToolbarExtension

# debug = DebugToolbarExtension(app)

##############################
# /////////////////#############
#   VIEW ROUTES         ########
# /////////////////#############
##############################

@app.route("/")
def home_page():
    """Display Homepage"""

    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register_page():
    """Handles display and registration"""

    if "user" in session:
        return redirect(f"/users/{session['user']}")

    form = RegisterForm()

    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        username = form.username.data
        password = form.password.data
        new_user = User.register(username, password, first_name, last_name, email)
        db.session.add(new_user)
        db.session.commit()
        session["user"] = new_user.username
        return redirect("/")
    else:
        return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login_page():
    """Login view"""

    form = LoginForm()

    if "user" in session:
        return redirect(f"/users/{session['user']}")

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.login(username, password)
        print(user)
        if user:
            session["user"] = user.username
            return redirect("/")
        else:
            form.password.errors = ["Invalid username/password"]
            return render_template("login.html", form=form)

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    """Log the current user out, remove him from session"""
    session.pop("user")

    return redirect("/")


@app.route("/users/<username>")
def show_profile(username):
    """Show the users profile page"""

    user = User.query.filter_by(username=username).first()

    if User.is_signed_in(session):
        return render_template("profile.html", user=user)
    else:
        return redirect("/login")


@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    """Delete specified user and posts associated"""

    if "user" not in session or username != session['user']:
        raise Unauthorized()

    user = User.query.filter_by(username=username).first()

    db.session.delete(user)
    db.session.commit()
    session.pop("user")

    return redirect("/login")


@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def feedback_add_form(username):
    """Add user created feedback"""

    user = User.query.filter_by(username=username).first()

    if User.is_signed_in(session) == False or session["user"] != username:
        # Flash fail
        return redirect("/login")

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        feedback = Feedback(title=title, content=content, username=user.username)
        
        db.session.add(feedback)
        db.session.commit()
        # Flash success
        return redirect(f"/users/{user.username}")

    return render_template("feedback_add.html", form=form, user=user)


@app.route("/feedback/<feedback_id>/update", methods=["GET", "POST"])
def feedback_edit(feedback_id):

    feedback = Feedback.query.get_or_404(feedback_id)

    if "user" not in session or feedback.user.username != session['user']:
        raise Unauthorized()

    edit_form = FeedbackForm(obj=feedback)

    if edit_form.validate_on_submit():
        feedback.title = edit_form.title.data
        feedback.content = edit_form.content.data
        db.session.commit()
        return redirect(f"/users/{feedback.user.username}")
    
    return render_template("feedback_edit.html", form=edit_form, feedback=feedback)


@app.route("/feedback/<feedback_id>/delete", methods=["POST"])
def feedback_delete(feedback_id):
    """Deletes specified feedback"""

    feedback = Feedback.query.get_or_404(feedback_id)
    if "user" not in session or feedback.user.username != session['user']:
        raise Unauthorized()

    db.session.delete(feedback)
    db.session.commit()

    return redirect(f"/users/{feedback.username}")


