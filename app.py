from flask import Flask, jsonify,request
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
    if not id:
        data = models.Teams.query.join(models.Address).all()
        for team in data:
            data_all.append(utils.row2dict(team))
        return jsonify(team=data_all)
    data = models.Teams.query.get(id)
    return jsonify(utils.row2dict(data))

@app.route('/getPlayers/', methods=['GET'])
@app.route('/getPlayers/<team_id>', methods=['GET'])
def getPlayers(team_id=None):
    if not team_id:
        data = models.Persons.query.all()
        data_all = []
        for player in data:
            data_all.append((player.id, player.first_name, player.last_name, player.team_id))
        return jsonify(team=data_all)
    data = models.Persons.query.all()#.filter(models.Persons.Team_id=team_id)

    return jsonify(utils.row2dict(data))

@app.route('/addPlayer/', methods=['POST'])
def addPlayers():
    results = request.get_json()
    app.logger.info(results)


@app.route('/updatePlayer/', methods=['PUT'])
def updatePlayers():
    results = request.get_json()
    app.logger.info(results)

@app.route('/addGame/', methods=['POST'])
def addGame():
    results = request.get_json()
    app.logger.info(results)

@app.route('/getStandings', methods=['GET'])
@app.route('/getStandings/<division>')
def getStandings(division=None):
    if division:
        pass

# @app.route('/getScheduleBy')
@app.route('/getScheduleBy/<type>/<id>')
def getSchedule(type=None, id=None):
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
