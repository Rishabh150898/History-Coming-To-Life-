from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SelectField
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test1.db'
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
db = SQLAlchemy(app)
sqldb = SQLAlchemy()


db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(2))
    name = db.Column(db.String(50))

class Form(FlaskForm):
    state = SelectField('state', choices=[('7', 'Class 7'), ('8', 'Class 8'), ('9', 'Class 9')])
    city = SelectField('city', choices=[])

@app.route('/', methods=['GET', 'POST'])
def index():
    form = Form()




    return render_template('index.html', form=form)

@app.route('/city/<state>')
def city(state):
    cities = City.query.filter_by(state=state).all()

    cityArray = []
    for city in cities:
        cityObj = {}
        cityObj['id'] = city.id
        cityObj['name'] = city.name
        cityArray.append(cityObj)

    return jsonify({'cities' : cityArray})


@app.route('/result', methods=['GET', 'Post'])
def no():

    return render_template('from_ex.html')



if __name__ == '__main__':
    app.run(debug=True)