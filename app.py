from flask import Flask, jsonify, request
#from flask.ext.sqlalchemy import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
import os

import utils

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#from models import Teams
import models

@app.route('/getTeams', methods=['GET'])
@app.route('/getTeams/<id>', methods=['GET'])
def getTeam(id=None):
    data_all = []
    if not id:
        data = models.Teams.query.join(models.Address).all()
        for team in data:
            data_all.append(utils.row2dict(team))
        return jsonify(team=data_all)
    data = models.Teams.query.get(id)
    return jsonify(utils.row2dict(data))

@app.route('/getPlayers', methods=['GET'])
@app.route('/getPlayers/<team>', methods=['GET'])
def getPlayers(team=None):
    print(team)
    if not team:
        data = models.Persons.query.all()
    else:
        data = models.Persons.query.filter(models.Persons.team_id==team)

    data_all = []
    for player in data:
        data_all.append(utils.row2dict(player))

    return jsonify(data_all)

@app.route('/addPlayer', methods=['POST'])
def addPlayers():
    user = request.get_json()
    u = models.Persons(first_name=user['player']['first'], last_name=user['player']['last'], birth_date=user['player']['birth_date'], team_id=user['player']['team_id'], person_type='1')
    try:
        db.session.add(u)
        db.session.commit()
    except Exception as exc:
        app.logger(str(exc))
        return str(exc), 400

    return "Player Succesfully Added", 200

@app.route('/updatePlayer', methods=['PUT'])
def updatePlayers():
    results = request.get_json()
    app.logger.info(results)


@app.route('/addCoach', methods=['POST'])
def addCoach():
    user = request.get_json()
    u = models.Persons(first_name=user['coach']['first'], last_name=user['coach']['last'], birth_date=user['coach']['birth_date'], team_id=user['coach']['team_id'], person_type='2')
    try:
        db.session.add(u)
        db.session.commit()
    except Exception as exc:
        app.logger(str(exc))
        return str(exc), 400

    return "Player Succesfully Added", 200

@app.route('/addGame', methods=['POST'])
def addGame():
    results = request.get_json()
    app.logger.info(results)

@app.route('/getStandings', methods=['GET'])
@app.route('/getStandings/<year>/<level>')
def getStandings(year=None,level=None):
    if division:
        pass

# @app.route('/getScheduleBy')
@app.route('/getScheduleBy/<year>/<level>/<id>')
def getSchedule(year=None, level=None):
    if lower(type) == 'year':
        # Query the schedule table with year as the filter
        pass
    elif lower(type) == 'team':
        # Query the schedule table with team as the filter
        pass
    else:
        # Query results by team_uuid
        pass

@app.route('/getStatsBy/<type>/<id>')
def getStats(type=None, id=None):
    pass




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
