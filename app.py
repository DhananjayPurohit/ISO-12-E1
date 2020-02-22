from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from classifier import Classify

app = Flask(__name__)

# Database Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.sqlite3'
db = SQLAlchemy(app)

CORS(app)

######  MODELS ######

class Teacher(db.Model):
    __tablename__ = 'teacher'

    id = db.Column(db.Integer, primary_key=True)
    name = db.relationship('Names', backref="teacher", cascade="all, delete-orphan" , lazy='dynamic')

    def __repr__(self):
        return "<Teacher %r>"% self.name


class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    ques_1 = db.Column(db.String(150), nullable=False)
    ques_2 = db.Column(db.String(150), nullable=False)
    ques_3 = db.Column(db.String(150), nullable=False)
    ques_4 = db.Column(db.String(150), nullable=False)
    opinion = db.Column(db.String(300), nullable=True)
    teacher = db.Column(db.String, db.ForeignKey('teacher.name'), nullable=False)

    def __repr__(self):
        return "<Feedback %r>"% self.opinion


##### API #####

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
    
    if positive_score > 0.6:
        feedback_obj = Feedback(ques_1=ques_1, ques_2=ques_2, ques_3=ques_3,
                                ques_4=ques_4, opinion=opinion, teacher=teacher_obj)
        db.session.add(feedback_obj)
        db.session.commit()

        return make_response("Feedback Posted Successfully!")
    else:
        return make_response("Invalid Feedback. Please check your language quality")
        

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)