#--------------------------------------Imports----------------------------------------
from flask import Flask, flash, redirect, render_template, url_for, request, jsonify, make_response, session
from flask.helpers import make_response
from sqlalchemy.orm.mapper import validates
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_wtf import FlaskForm
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from wtforms import BooleanField, EmailField, PasswordField, SubmitField
from wtforms.validators import *
import json, os, bleach, jwt, uuid
from PIL import Image
from datetime import datetime, timedelta

# ------------------------------------ All configurations ------------------------------

app = Flask(__name__)
app.config['SECRET_KEY'] = 'learning-flask'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'blue'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config["MAIL_USE_SSL"] = True
app.config['MAIL_USERNAME'] = ''
app.config['MAIL_PASSWORD'] = ''
bcrypt = Bcrypt(app)
mail = Mail(app)
# ------------------------------------ All Functions ----------------------------------

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def signup(email, pswd):
  app.app_context().push()
  if User.query.filter_by(email=email).first():
    return 
  else:
    hashed_password = bcrypt.generate_password_hash(pswd).decode('utf-8')
    user = User()
    user.email = email
    user.password = hashed_password
    user.name = email.split('.')[0].capitalize()
    db.session.add(user)
    db.session.commit()
    print(f"Account with mail {email} created")

def save_picture(form_picture, complain_id, location):
  _, f_ext = os.path.splitext(form_picture.filename)
  filename = str(complain_id) + f_ext
  picture_path = os.path.join(app.root_path, f'static/{location}', filename)
  # output_size = (500, 500)
  i = Image.open(form_picture)
  w, h = i.size
  ratio = w / h
  if w > h:
    h = min(800, h)
    w = int(h / ratio)
  else:
    w = min(800, w)
    h = int(w * ratio)
  i.resize((w, h))
  i.save(picture_path)
  return filename

def add_complain(user_id, hostel, description, room, type, mobile, image):
  # app.app_context().push()
  user = User.query.filter_by(id=user_id).first()
  if user:
    new_complain = Hostel()
    new_complain.user_id = user_id
    new_complain.hostel = hostel
    new_complain.description = description
    new_complain.room = room
    new_complain.type = type
    new_complain.mobile = mobile    
    db.session.add(new_complain)
    db.session.commit()
    if image:
      new_complain.image = save_picture(image, new_complain.id, 'hostel')
      db.session.commit()
    print(f"New complain with mail {user.email} created")
    return new_complain.id
  else:
    print("No such user with this id")
    return None
def addfounditems(user_id, name, description, contact, image):
  user = User.query.filter_by(id=user_id).first()
  if user:
    item = Found()
    item.user_id = user_id
    item.name = name
    item.description = description
    item.contact = contact
    db.session.add(item)
    db.session.commit()
    item.image = save_picture(image, item.id, 'found_items')
    db.session.commit()
    print(f"New item with mail {user.email} created")
    return item.id
    
def delete_user(email):
  app.app_context().push()
  if User.query.filter_by(email=email).first():
    user = User.query.filter_by(email=email).first()
    db.session.delete(user)
    db.session.commit()
    print(f"Account with mail {email} deleted")
  else:
    print(f"Account with mail {email} not found")
 
def validate_email(email):
  user = User.query.filter_by(email=email).first()
  return user is not None

def send_mail(user):
  token = user.get_reset_token()
  print("Reached at send mail")
  msg = Message('Password Reset Request',sender='noreply@demo.com', recipients=[user.email])
  msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
  mail.send(msg)
  print(f"Mail sent to {user.email}")

def generate_jwt(user_mail):
  payload = {'email': user_mail, 'exp': datetime.utcnow() + timedelta(minutes=15)}
  secret_key = 'somethingnottobetold'  
  return jwt.encode(payload, secret_key)


# --------------------------------------- Models ---------------------------------------

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    complaints = db.relationship('Hostel', backref='user', lazy=True)
    found_items = db.relationship('Found', backref='found', lazy=True)
    def get_reset_token(self):
      serializer = Serializer(app.config['SECRET_KEY'], expires_in=1800)
      return serializer.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
      s = Serializer(app.config['SECRET_KEY'])
      try:
        user_id=s.loads(token)['user_id']
      except:
        return None
      return User.query.get(user_id)

    def __repr__(self):
      return f"User('{self.name}', '{self.email}', '{self.id}')"

class Hostel(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  hostel = db.Column(db.String(80), nullable=False)
  status = db.Column(db.Integer, nullable=False, default=1)
  description = db.Column(db.String(255), nullable=False)
  date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
  room = db.Column(db.Integer, nullable=False)
  type = db.Column(db.String(20), nullable=False)
  mobile = db.Column(db.String(15), nullable=False)
  image = db.Column(db.String(16), nullable=True)

class Lost(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().date())
  # time_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
  description = db.Column(db.String(80), nullable=False)
  image = db.Column(db.String(16), nullable=False)
  contact = db.Column(db.String(15), nullable=False)

class Found(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
  name = db.Column(db.String(80), nullable=False)
  description = db.Column(db.String(80), nullable=False)
  image = db.Column(db.String(16), nullable=True)
  contact = db.Column(db.String(15), nullable=False)
  claimed_by = db.Column(db.Integer, nullable=True)

# --------------------------------------- Forms ---------------------------------------

class Login(FlaskForm):
  email = EmailField('Email', validators=[DataRequired(), Email()])
  password = PasswordField('Password', validators=[DataRequired()])
  remember = BooleanField('Remember Me')
  submit = SubmitField('Login')

class requestResetForm(FlaskForm):
  email = EmailField('Email', validators=[DataRequired(), Email()])
  submit = SubmitField('Login')

class resetPasswordForm(FlaskForm):
  password = PasswordField('New Password', validators=[DataRequired()])
  new_password = PasswordField('Confirm Password', validators = [DataRequired()])
  submit = SubmitField('Reset Password')

# --------------------------------------- Routes ---------------------------------------

@app.route('/', methods=['GET', 'POST'])
def index():
  if current_user.is_authenticated:
    return render_template('home.html')
  else:
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  form = Login()
  if form.validate_on_submit():
    user = User.query.filter_by(email=form.email.data).first()
    if user and bcrypt.check_password_hash(user.password, form.password.data):
      login_user(user, remember=True)
      return redirect(url_for('index'))
    elif user is None:
      flash('This mail does not exist', 'red')
    elif not(bcrypt.check_password_hash(user.password, form.password.data)) :
      flash('Oops! Incorrect password', 'red')
    else:
      flash("Oops! Incorrect password or email", "red")
  return render_template('login.html', title='login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/items', methods=['GET', 'POST'])
@login_required
def lostandfound():
  if current_user.is_authenticated:
    user_id = current_user.id
    items = Found.query.order_by(Found.date_posted).all()
    items.reverse()
    item_list={} 
    for item in items:
      image_path = os.path.join('static/found_items', item.image)
      item_list[item.id]={  # no image here
        'product_name': item.name,
        'product_description': item.description,
        'contact_number': item.contact,
        'date_posted': item.date_posted,
        'image': image_path,
        'claimed': 0
      }
      print('Here item id', item.claimed_by)
      if item.claimed_by:
        item_list[item.id]['claimed'] = 1
        item_list[item.id]['email'] = (User.query.filter_by(id=item.claimed_by).first()).email
    # print(item_list)
    if request.method == 'POST':
      token  = request.cookies.get('secure_token')
      try:
        decoded = jwt.decode(token, 'somethingnottobetold', algorithms=['HS256'])
      except:
        return make_response(jsonify({'message': 'Expired or invalid token, refresh and try again', 'status': False}))  # expired or invalid token 
      data = request.form
      print(data.get('product_name'), data.get('product_description'), data.get('contact_number'))
      if not (data.get('product_name') and data.get('product_description') and data.get('contact_number')):
        return make_response(jsonify({'message': 'Received incomplete or invalid data','status': False}))
      item_id=None
      if 'image' in request.files:
        # print(request.files['image'])
        image = request.files['image']
        _, f_ext = os.path.splitext(image.filename)
        if f_ext not in ['.jpg', '.jpeg', '.png']:
          return make_response(jsonify({'message': 'Image must be in png, jpg or jpeg, try again', 'status': False}))
        
        item_id = addfounditems(
          user_id=user_id, 
          name = data['product_name'],
          description = data['product_description'],
          contact = data['contact_number'],
          image = image
        )
      else:
        return make_response(jsonify({'message': 'No image found', 'status': False}))
      if item_id:
      #   items = Found.query.filter_by(id=complain_id).first()
      #   date_posted = items.date_posted.date()
      #   desc = items.description
      #   time_posted = items.time_posted
      #   image = items.image

        return make_response(jsonify({'message': 'Your item has been added', 'status': True}), 200)
      return make_response(jsonify({'message': 'Something went wrong and item was not added', 'status': False}))
    return render_template('lostandfound.html', title="Lost and Found", items=item_list)
  return redirect('login')

@app.route('/claim', methods=['POST'])
@login_required
def claim():
  if current_user.is_authenticated:
    print("Reached Claim function")
    item_id = request.get_json()
    item_id = item_id.get('id')
    if item_id is None:
      return make_response(jsonify({'message': 'No item id found', 'status': False}))
    user_id = current_user.id
    items = Found.query.filter_by(id=item_id).first()
    if items is None:
      return make_response(jsonify({'message': 'No item found', 'status': False}))
    items.claimed_by = (user_id)
    # print(items.claimed_by)
    if items.claimed_by:
      print('claimed', (Found.query.filter_by(id=item_id).first()).claimed_by)
    email = User.query.filter_by(id=user_id).first()
    return make_response(jsonify({'message': 'Item claimed', 'status': True, 'email': email.email}))
  return redirect('login')

@app.route('/mess-complaints')
def messcomplain():
  return render_template('messcomplain.html', title="Mess Complaints")

@app.route('/hostel-complaints', methods=['GET', 'POST'])
@login_required
def hostelcomplain():
  if current_user.is_authenticated:
    user_id = current_user.id
    v = Hostel.query.filter_by(user_id=user_id).all()
    complaints = {}
    cnta, cnts=0, 0
    for hc in v:
      complaints[hc.id] = {
        'status': hc.status,
        'desc': hc.description,
        'date_posted': hc.date_posted.date(),
        'type': hc.type,
      }
      cnta += int(hc.status)
    cnts = len(v) - cnta;
    if request.method == 'POST':
      token  = request.cookies.get('secure_token')
      print(token)
      try:
        decoded = jwt.decode(token, 'somethingnottobetold', algorithms=['HS256'])
      except:
        return make_response(jsonify({'message': 'Cannot add your complaint', 'status': 0}))  # expired or invalid token 
      data = request.form
      print(data)
      if not (data.get('hostel') and data.get('description') and data.get('room') and data.get('type') and data.get('mobile')):
        return make_response(jsonify({'message': 'Received incomplete or invalid data','status': False}))
      complain_id=None
      if 'image' in request.files:
        print(request.files['image'])
        image = request.files['image']
        _, f_ext = os.path.splitext(image.filename)
        if f_ext not in ['.jpg', '.jpeg', '.png']:
          return make_response(jsonify({'message': 'Image must be in png, jpg or jpeg, try again', 'status': False}))
        got_image = True
        complain_id = add_complain(
          user_id=current_user.id, 
          hostel = data['hostel'],
          description = data['description'], 
          room = data['room'], 
          type = data['type'], 
          mobile = data['mobile'],
          image = image
        )
      else:
        print("No image")
        complain_id = add_complain(
          user_id=current_user.id, 
          hostel = data['hostel'], 
          description = data['description'], 
          room = data['room'], 
          type = data['type'], 
          mobile = data['mobile'],
          image=None
        )
      if complain_id:
        complaint = Hostel.query.filter_by(id=complain_id).first()
        date_posted = complaint.date_posted.date()
        desc = complaint.description
        type = complaint.type
        return make_response(jsonify({'message': 'Your complaint has been added', 'count':cnta+1, 'complain_date': date_posted, 'complain_description': desc, 'complain_type': type, 'status': 1}), 200)
      return make_response(jsonify({'message': 'Something went wrong and complaint was not added'}))
    return render_template('hostelcomplain.html', title="Hostel Complaints", complaints=complaints, cnta=cnta, cnts=cnts)
  return redirect('login')


@app.route('/send' , methods=['POST'])
@login_required
def send():
  if current_user.is_authenticated:
    token = generate_jwt(current_user.email)
    res = make_response(jsonify({'message': 'Valid request'}))
    res.set_cookie('secure_token', 
      value=token,
      httponly=True,
      secure=True,
      max_age=60*15 #15 minutes expiration time
    )
    return res
  return make_response(jsonify({'message': 'Invalid request'}), 403)

@app.route('/products')
def buyandsell():
  return render_template('buyandsell.html', title="Products")

@app.route('/reset-password', methods=['GET', "POST"])
def reset_request():
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  if request.method == 'POST':
    data = request.get_json()
    if data.get('email') is None:
      return jsonify({"info": "Email is required"})
    else:
      email = data.get('email')
      validation_msg = validate_email(email=email)
      if validation_msg :
        user = User.query.filter_by(email=email).first()
        send_mail(user)
        return jsonify({"status": True})
      else:
        return jsonify({"status": False})
  elif request.method == 'GET':
      # return render_template('reset_password.html', title="Account Recovery", msg="Oops! Link is invalid or Expired.")
    return render_template('reset_request.html', title="Account Recovery")

@app.route('/reset-password/<token>', methods=['GET', "POST"])
def reset_token(token):
  if current_user.is_authenticated:
    return redirect(url_for('index'))
  user = User.verify_reset_token(token)
  print(user)
  if user is None:
    return redirect(url_for('reset_request'))
  form = resetPasswordForm()
  if form.validate_on_submit():
    print("Validated")
    hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
    user.password = hashed_password
    db.session.commit()
    print('Password changed')
    flash('Password changed successfully', 'green')
    return redirect(url_for('login'))
  print("Not Validated")
  return render_template("reset_token.html", title="Reset Password", form=form)

#---------------------------------------Main------------------------------------------

if __name__ == '__main__':
  with app.app_context():
    # db.create_all()
    # db.drop_all()
    app.run(debug=True, port=81, host='0.0.0.0')
