from flask import Flask, request, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from classifier import Classify
from extract import *
from werkzeug.utils import secure_filename
from recommendation import Trends, getCONTENT
import random

UPLOAD_FOLDER = '/uploadsflask'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Database Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3'
app.config['CORS_HEADERS'] = 'Content-Type'
db = SQLAlchemy(app)

CORS(app, resources={r"/*": {"origins": "*"}})

######  MODELS ######

class Teacher(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(90), nullable=False)
    feedbacks = db.relationship('Feedback', backref='teacher',
                                cascade="all, delete-orphan", lazy='dynamic')

    def __repr__(self):
        return "<Teacher %r>"% self.id


class Feedback(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    ques_1 = db.Column(db.Integer, nullable=False)
    ques_2 = db.Column(db.Integer, nullable=False)
    ques_3 = db.Column(db.Integer, nullable=False)
    ques_4 = db.Column(db.Integer, nullable=False)
    opinion = db.Column(db.Text, nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))

    def __repr__(self):
        return "<Feedback %r>"% self.id

class Content(db.Model):
    _tablename_ = 'content'

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(150), nullable=False)
    topic = db.Column(db.String(500), nullable=False)
    video_content = db.Column(db.Boolean)
    content = db.Column(db.Text)
    votes = db.Column(db.Integer, default=0)

class Subject_list(db.Model):
    __tablename__ = 'subject_list'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    user = db.Column(db.String(200))
    password = db.Column(db.String(200))
    year = db.Column(db.Integer)
    branch = db.Column(db.String(20))

class branch_subject(db.Model):
    __tablename__ = 'branch_subject'

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    branch = db.Column(db.String(20))
    subject = db.Column(db.String(150), nullable=False)
    syllabus = db.Column(db.LargeBinary)

##### API #####

@app.route('/add_syllabus', methods=['POST'])
def add_subject():
    subject_ = request.form.get('subject')
    year_ = request.form.get('year')
    branch_ = request.form.get('branch')
    f = request.files['syllabus']

    f.save(secure_filename(f.filename))

    item = branch_subject(subject=subject_,year=year_,
                        branch=branch_,syllabus=f.read())
    db.session.add(item)
    db.session.commit()

    return make_response("Syllabus Added Successfully")

@app.route('/login', methods=['POST'])
def user_login():
    username = request.json.get('username')
    password = request.json.get('password')
    Opass = Subject_list.query.filter_by(user=username).first()
    Opass1 = Opass.password
    if password == Opass1:
        sub_list = branch_subject.query.filter_by(year=Opass.year).filter_by(branch=Opass.branch).all()
        subjects = []
        for i in sub_list:
            subjects.append(i.subject)

        resp_ = make_response(str(subjects))
        resp_.set_cookie('subjects', str(subjects))
        return resp_
    else:
        return make_response("Error, Login again")

@app.route('/register', methods=['POST'])
def user_signup():
    name_ = request.form.get('name')
    user_ = request.form.get('username')
    password_ = request.form.get('password')
    year_ = request.form.get('year')
    branch_ = request.form.get('branch')

    item = Subject_list(name=name_,user=user_,password=password_,year=year_,
                        branch=branch_)
    db.session.add(item)
    db.session.commit()

    return make_response("User registered Successfully")

@app.route('/get_content', methods=['GET'])
def get_content():
    sub = request.args.get('sub', type = str)
    sub = sub.replace("%20", " ")
    subject_resp = Content.query.filter_by(subject=sub).all()
    resp_list = ""
    for i in subject_resp:
        resp_list+=str(i.__dict__)

    return jsonify(resp_list)

##### API #####
@app.route('/add', methods=['GET'])
def add_topic():
    list = Topic_extractor(Pdf_reader("ds.pdf").full_text).final_list
    for i in list:
        topics = i.split(",")
        for topic_ in topics:
            t = random.choice([True,False])
            try:
                tpic = Content(subject='Data Structure', topic=topic_, video_content=t, content=getCONTENT(t, [topic_]).summary)
                db.session.add(tpic)
                db.session.commit()
                print("new entry")
            except Exception as e:
                print(e)
                pass

    return make_response("User registered Successfully")

@app.route('/post_feedback', methods=['POST'])
def save_feedback():
    ques_1 = request.form.get('ques_1')
    ques_2 = request.form.get('ques_2')
    ques_3 = request.form.get('ques_3')
    ques_4 = request.form.get('ques_4')
    opinion = request.form.get('opinion')

    teacher = request.form.get('teacher')
    teacher_obj = Teacher.query.filter(Teacher.name == teacher).one()

    positive_score = Classify(opinion).classify()

    if positive_score > 0.75:
        feedback_obj = Feedback(ques_1=ques_1, ques_2=ques_2, ques_3=ques_3,
                                ques_4=ques_4, opinion=opinion, teacher=teacher_obj.id)
        db.session.add(feedback_obj)
        db.session.commit()

        return make_response("Feedback Posted Successfully!")
    else:
        return make_response("Invalid Feedback. Please check your language quality")


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
