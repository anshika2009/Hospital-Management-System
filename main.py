from flask import Flask,render_template,request,session,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user
from flask_mail import Mail
from sqlalchemy import create_engine,text
from flask_mysqldb import MySQL
import sqlalchemy


#db connection
local_server= True
app = Flask(__name__)
app.secret_key='aneesrehmankhan'

user = 'root'
db = 'hms'

app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/hms'
db=SQLAlchemy(app)

mysql = MySQL(app)

engine = create_engine("mysql://root:@localhost/hms"
                           .format(user=user, db=db))

# this is for getting unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    email=db.Column(db.String(100))
    
class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50))
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(1000))

class Patients(db.Model):
    pid=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50))
    name=db.Column(db.String(50))
    gender=db.Column(db.String(50))
    slot=db.Column(db.String(50))
    disease=db.Column(db.String(50))
    time=db.Column(db.String(50),nullable=False)
    date=db.Column(db.String(50),nullable=False)
    dept=db.Column(db.String(50))
    number=db.Column(db.String(50))
    
class Doctors(db.Model):
    did=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50))
    doctorname=db.Column(db.String(50))
    dept=db.Column(db.String(50))

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/doctors',methods=['POST','GET'])
@login_required
def doctors():

    if request.method=="POST":

        email=request.form.get('email')
        doctorname=request.form.get('doctorname')
        dept=request.form.get('dept')

        newuser=Doctors(email=email,doctorname=doctorname,dept=dept)
        db.session.add(newuser)
        db.session.commit()
        flash("Noted","primary")

    return render_template('doctor.html')

@app.route("/patients",methods=['POST','GET'])
@login_required
def patients():
    doc=Doctors.query.all()

    if request.method=="POST":
        email=request.form.get('email')
        name=request.form.get('name')
        gender=request.form.get('gender')
        slot=request.form.get('slot')
        disease=request.form.get('disease')
        time=request.form.get('time')
        date=request.form.get('date')
        dept=request.form.get('dept')
        number=request.form.get('number')
        subject="HOSPITAL MANAGEMENT SYSTEM"
        # query=db.engine.execute(f"INSERT INTO `patients` (`email`,`name`, `gender`,`slot`,`disease`,`time`,`date`,`dept`,`number`) VALUES ('{email}','{name}','{gender}','{slot}','{disease}','{time}','{date}','{dept}','{number}')")
        newuser=Patients(email=email,name=name,gender=gender,slot=slot,disease=disease,time=time,date=date,dept=dept,number=number)
        db.session.add(newuser)
        db.session.commit()
        flash("Booking Confirmed","info")
    return render_template("patients.html",doc=doc)

@app.route("/bookings")
@login_required
def bookings():
    em=current_user.email
    stmt="SELECT * FROM `patients` WHERE email='{em}'"
    # with engine.connect() as conn:
    #     query = conn.execute(text(stmt))
    query=Patients.query.filter_by(email=em)   #query.all()
    return render_template('booking.html',query=query)

@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == "POST":
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')
        # print(username,email,password)
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email Already Exist","warning")
            print("Email Already Exist")
            return render_template('/signup.html')
        encpassword=generate_password_hash(password)
        newuser=User(username=username,email=email,password=encpassword)
        db.session.add(newuser)
        db.session.commit()
        flash("Signup Succes Please Login","success")
        return render_template("login.html")
    return render_template("signup.html")



@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == "POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login Success","primary")
            return redirect(url_for('index'))
        else:
            flash("invalid credentials","danger")
            return render_template('booking.html') 
    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return redirect(url_for('login'))

@app.route("/edit/<string:pid>",methods=['POST','GET'])
@login_required
def edit(pid):
    posts=Patients.query.filter_by(pid=pid).first()
    p=Patients.query.get_or_404(pid)
    if request.method=="POST":
        p.email=request.form.get('email')
        p.name=request.form.get('name')
        p.gender=request.form.get('gender')
        p.slot=request.form.get('slot')
        p.disease=request.form.get('disease')
        p.time=request.form.get('time')
        p.date=request.form.get('date')
        p.dept=request.form.get('dept')
        p.number=request.form.get('number')
        db.session.commit()
        
        return redirect('/bookings')
    return render_template('edit.html',posts=posts)

@app.route("/delete/<string:pid>",methods=['POST','GET'])
@login_required
def delete(pid):
    p=Patients.query.get_or_404(pid)
    try:
        db.session.delete(p)
        db.session.commit()
        flash("Slot Deleted Successfully","success")
    except:
        flash("Unable to delete your slot","danger")
        
    return redirect('/bookings')

@app.route('/search',methods=['POST','GET'])
@login_required
def search():
    if request.method=="POST":
        query=request.form.get('search')
        dept=Doctors.query.filter_by(dept=query).first()
        name=Doctors.query.filter_by(doctorname=query).first()
        if dept:

            flash("Doctor is Available","info")
        else:

            flash("Doctor is Not Available","danger")
    return render_template('index.html')

@app.route("/test")  
def test():
    try:
        Test.query.all()
        return 'Connected'
    except:
        return 'not'

app.run(debug=True)