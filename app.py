from flask import Flask, jsonify, request
#from flask.ext.sqlalchemy import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
import os
from flask_cors import CORS


import utils

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)
db = SQLAlchemy(app)

# from models import Teams
import models


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


@app.route('/')
def index():
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))
    return """ <HTML><h1> MHAC api </h1>
    <table>
    <tr><td>call</td><td>description</td></tr>
    <tr><td>/getTeams/<id></td><td>Gets all teams when called without an id.  With an id will return the info about an individual team.</td></tr>
    </table>
    </HTML>
    """

@app.route('/getTeams', methods=['GET'])
@app.route('/getTeams/<id>', methods=['GET'])
def getTeam(id=None):
    data_all = []
    if not id:
        data = models.Teams.query.join(models.Address).all()
        for team in data:
            print(team.home_team)
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
@app.route('/getStandings/<season_id>')
def getStandings(season_id=None):
    if not season_id:
        return

    schedule = models.Schedule.query.filter(models.Schedule.season_id == season_id)


@app.route('/addGame', methods=['POST'])
def addGame():

    home_team = ''
    away_team = ''
    game_time = ''
    game_date = ''
    season = ''
    neutral_site = None


    year = request.args.get('year')
    data = request.get_json()

    game = data['data']

    if not "home_team" in game:
        return "Home Team is required", 400
    if not "away_team" in game:
        return "Away Team is required", 400
    if not "date" in game:
        return "Date is required", 400
    if not "season" in game:
        return "season is required", 400
    if "neutral_site" in game:
        neutral_site = game['neutral_site']

    home_team = game['home_team']
    away_team = game['away_team']
    game_date = game["date"]
    season = game['season']

    if "time" in game:
        time = game['time']

    g = models.Schedule(home_team_id=home_team,
                        away_team_id=away_team,
                        game_date=game_date,
                        game_time=game_time,
                        season_id=season,
                        neutral_site=netural_site)

    try:
        db.session.add(g)
        db.commit()
    except Exception as exc:
        app.logger(str(exc))
        return str(exc), 400

    return "Game added to the schedule", 200

@app.route('/getSchedule/<season_id>', methods=['GET'])
def getSchedule(season_id=None):
    schedule = models.Schedule.query.filter(models.Schedule.season_id == season_id)
    data_all = []
    for game in schedule:
        data_all.append(utils.row2dict(game))

    return jsonify(data_all), 200

@app.route('/getSeasons', methods=['GET'])
def getSeason():
    y = models.Season.query.all()
    data_all = []
    for year in y:
        data_all.append(utils.row2dict(year))

    return jsonify(data_all), 200

@app.route('/getCurrentSeasons', methods=['GET'])
def getCurrentSeason():
    seasons = models.Season.query.filter(models.Season.archive != False)
    data_all = []
    for season in seasons:
        data_all.append(utils.row2dict(season))

    return jsonify(data_all), 200

def archiveSeason(season_id):
    season = models.Season.query.filter(models.Season.id == season_id).first()
    season.archive = True

    try:
        db.session.add(season)
        db.commit()
    except Exception as exc:
        app.logger(str(exc))
        return str(exc), 400

    return '{} has been archived'.format(season)






if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
