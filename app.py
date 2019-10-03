from flask import Flask, jsonify,request
#from flask.ext.sqlalchemy import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#from models import Teams
import models

@app.route('/')
def hello():
    return "Hello World!"


@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)

@app.route('/teams', methods=['GET'])
def getTeam():
    data = models.Teams.query.all()
    data_all = []
    for team in data:
        data_all.append((team.id, team.team_name, team.team_mascot))
    return jsonify(team=data_all)

@app.route('/players/', methods=['GET'])
def getPlayers(team_id=None):
    data = models.Persons.query.all()
    data_all = []
    for player in data:
        data_all.append((player.id, player.first_name, player.last_name, player.team_id))
    return jsonify(team=data_all)

    return data



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
