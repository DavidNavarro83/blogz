from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:root@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.username

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    text = db.Column(db.String(4000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, name, text, owner):
        self.name = name
        self.text = text
        self.owner = owner


def get_users():
    return User.query.order_by(User.username).all()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', users=get_users())


@app.route("/login", methods=['GET', 'POST'])
def login():

    error1 = "Username does not exist."
    error2 = "Password is incorrect."

    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = User.query.filter_by(username=username)
        if users.count() == 1:
            user = users.first()
            if password == user.password:
                session['user'] = user.id
                flash('welcome back, '+user.username)
                return redirect("/newpost")
            return render_template("login.html", error2=error2)
        flash('bad username or password')
        return render_template("login.html", error1=error1)

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        # if not is_email(email):
        #     flash('zoiks! "' + email + '" does not seem like an email address')
        #     return redirect('/register')
        username_db_count = User.query.filter_by(username=username).count()
        if username_db_count > 0:
            flash('yikes! "' + username + '" is already taken and password reminders are not implemented')
            return redirect('/register')
        if password != verify:
            flash('passwords did not match')
            return redirect('/register')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.id
        return redirect("/")
    else:
        return render_template('register.html')


@app.route("/logout", methods=['POST'])
def logout():
    if 'user' in session:
        del session['user']
    return redirect("/")




def get_all_blogs():
    return Blog.query.order_by(Blog.name).all()

def get_blog_by_id():
    return Blog.query.get()

@app.route('/blog', methods=['GET'])
def get_blog_page():

    username = request.args.get("user")
    blog_id = request.args.get("id")
    if blog_id:
        blog = Blog.query.get(blog_id)
        return render_template('blog.html', blog=blog, user=blog.owner, title="Buil-a-Blog")
    elif username:
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template('blog.html', list_of_blogs=user.blogs, user=user, title="Buil-a-Blog")
    # for blog in blogs:
    #     print ('blog.name = ' + blog.name)

    return render_template('blog.html', blogs=get_all_blogs())




@app.route('/newpost', methods=['GET'])
def newpost():
    return render_template('newpost.html',title="Add a Blog Entry")


@app.route('/add_blog_entry', methods=['POST'])
def add_blog_entry():
    user_id = session['user']
    owner = User.query.filter_by(id=user_id).first()

    if not owner:
        return redirect("/signup")

    blog_name = request.form['blog_name']
    blog_text = request.form['blog_text']
    error1 = "Please name your blog."
    error2 = "Please input text into field."

    if ((not blog_name) or (blog_name.strip() == "")) and ((not blog_text) or (blog_text.strip() == "")):
        return render_template("newpost.html", error1=error1, error2=error2)

    elif (not blog_name) or (blog_name.strip() == ""):
        return render_template("newpost.html", error1=error1)
    
    elif (not blog_text) or (blog_text.strip() == ""):
        return render_template("newpost.html", error2=error2)

    blog = Blog(blog_name, blog_text, owner)
    # text = Blog(blog_text)
    # db.session.add(name, text)
    db.session.add(blog)
    db.session.commit()
    return redirect('/blog?id=' + str(blog.id))



authenticated_routes = ['newpost', 'add_blog_entry']


@app.before_request
def require_login():

    if request.endpoint in authenticated_routes:
        if not 'user' in session:
            print('in require_login | user not in session |  url = ' + request.endpoint)
            return redirect("/signup")









# In a real application, this should be kept secret (i.e. not on github)
# As a consequence of this secret being public, I think connection snoopers or
# rival movie sites' javascript could hijack our session and act as us,
# perhaps giving movies bad ratings - the HORROR.
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'

if __name__ == '__main__':
    app.run()