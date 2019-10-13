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

@app.route('/updatePlayer/<id>', methods=['PUT', 'POST'])
def updatePlayers(id):
    results = request.get_json()
    player = models.Persons.query.filter(models.Persons.id==id).filter(models.Persons.person_type == '1').first()
    if not player:
        return "No player to update", 404

    if 'first_name' in results:
        player.first_name = results['first_name']
    if 'last_name' in results:
        player.last_name = results['last_name']
    if 'birth_date' in results:
        player.birth_date = results['birth_date']
    if 'height' in results:
        player.height = results['height']
    if 'team_id' in results:
        # update active dates as well
        player.team_id = results['team_id']
    if 'person_type' in results:
        # update active dates as well
        player.person_type = results['person_type']

    app.logger.info(results)

    try:
        db.session.commit()
    except Exception as exc:
        return str(exc), 400

    return 'Player Updated Sucessfully', 200


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


@app.route('/addGame', methods=['POST'])
def addGame():

    home_team = ''
    away_team = ''
    game_time = ''
    game_date = ''
    level = ''

    year = request.args.get('year')
    data = request.get_json()

    game = data['data']

    if not "home_team" in game:
        return "Home Team is required", 400
    if not "away_team" in game:
        return "Away Team is required", 400
    if not "date" in game:
        return "Date is required", 400
    if not "level" in game:
        return "level is required", 400

    home_team = game['home_team']
    away_team = game['away_team']
    game_date = game["date"]
    level = game['level']

    if "time" in game:
        time = game['time']


    g = models.Schedule(home_team=home_team, away_team=away_team, date=game_date, time=game_time, level=level)

    try:
        db.session.add(g)
        db.commit()
    except Exception as exc:
        app.logger(str(exc))
        return str(exc), 400

    return "Game added to the schedule", 200


@app.route('/getSchedule', methods=['GET'])
def getSchedule():
    results = request.get_json()535e4hyg3t
    app.logger.info(results)

@app.route('/getYears', methods=['GET'])
def getYears():
    y = models.Season.query.all()
    data_all = []
    for year in y:
        data_all.append(utils.row2dict(player))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
