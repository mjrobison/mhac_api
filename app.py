from functools import wraps

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import aliased
from sqlalchemy import and_, or_

import os
from datetime import datetime, timedelta

import utils

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

import jwt
import models


def token_required(f):
    @wraps(f)
    def _verify(*args, **kwargs):
        auth_headers = request.headers.get('Authorization', '').split()

        invalid_msg = {
            'message': 'Invalid token. Registeration and / or authentication required',
            'authenticated': False
        }
        expired_msg = {
            'message': 'Expired token. Reauthentication required.',
            'authenticated': False
        }

        # if len(auth_headers) != 2:
            # return jsonify(invalid_msg), 401

        try:
            token = auth_headers[0]
            data = jwt.decode(token, app.config['SECRET_KEY'])
            user = models.User.query.filter_by(email=data['sub']).first()
            if not user:
                raise RuntimeError('User not found')
            print(f)
            return f(user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            # 401 is Unauthorized HTTP status code
            return jsonify(expired_msg), 401
        except (jwt.InvalidTokenError, Exception) as e:
            print(e)
            return jsonify(invalid_msg), 401

    return _verify

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
    <tr><td>/getTeams/<id></td><td>Gets all teams when called without an id.
              With an id will return the info about an individual team.
    </td></tr>
    </table>
    </HTML>
    """

@app.route('/login/', methods=['POST'])
def login():
    data = request.get_json()
    user = models.User.authenticate(**data)

    if not user:
        return jsonify({'message': 'Invalid credentials', 'authenticated':False}), 401

    token = jwt.encode({
        'sub': user.email,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(minutes=30)
    },
    app.config['SECRET_KEY'])

    return jsonify({'token': token.decode('UTF-8')})


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
        data = models.Persons.query.filter(models.Persons.team_id==team).filter(models.Persons.person_type == '1')

    data_all = []
    for player in data:
        data_all.append(utils.row2dict(player))

    return jsonify(data_all)

@app.route('/addPlayer', methods=['POST'])
def addPlayers():
    data = request.get_json()

    first_name = None
    last_name = None
    birth_date = None
    position = None
    age = None
    height = None
    team_id = None
    player_number = None

    if 'first_name' in data:
        first_name = data['first_name']
    if 'last_name' in data:
        last_name = data['last_name']
    if 'birth_date' in data:
        birth_date = data['birth_date']
    else:
        return "Birth Date is required", 401
    if 'height' in data:
        height = data['height']
    if 'team_id' in data:
        # update active dates as well
        team_id = data['team_id']
    if 'position' in data:
        position = data['position']
    if 'age' in data:
        age = data['age']
    if 'number' in data:
        player_number= data['number']

    u = models.Persons(first_name=first_name, last_name=last_name, birth_date=birth_date, team_id=team_id, person_type='1',number=player_number, position=position)

    try:
        db.session.add(u)
        db.session.commit()
    except Exception as exc:
        print(str(exc))
        return str(exc), 400

    return jsonify(u.id), 200

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
@app.route('/getStandings/<season_id>', methods=['GET'])
def getStandings(season_id=None):
    if not season_id:
        seasons = db.session.query(models.Season, models.Level, models.Teams).join(models.Level).filter(models.Season.archive == None).filter(models.Level.level_name == '18U Boys').first()
        season_id = seasons.Season.id

    results = db.session.query(models.Standings, models.Teams).outerjoin(models.Teams).filter(models.Standings.season_id == season_id).order_by(models.Standings.win_percentage.desc(), models.Standings.losses.asc()).all()
    print
    if not results:
        return "No season found", 404

    standings = []
    i = 1
    leader= {}
    for team in results:
        if i == 1:
            leader['wins']= team.Standings.wins
            leader['losses'] = team.Standings.losses
            gb=0
        else:
            gb = utils.calcGamesBehind(leader=leader, wins=team.Standings.wins, losses=team.Standings.losses)
        data = {}
        data['team'] = team.Standings.team_id
        data['team_name'] = team.Teams.team_name
        data['wins'] = team.Standings.wins
        data['losses'] = team.Standings.losses
        data['games_played'] = team.Standings.games_played
        data['games_behind'] = gb
        standings.append(data)
        i += 1

    return jsonify(standings), 200

@app.route('/addGame', methods=['POST'])
def addGame():

    home_team = ''
    away_team = ''
    game_time = '00:00'
    game_date = ''
    season = ''
    neutral_site = None

    game = request.get_json()
    print(game)

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
    game_date = datetime.strptime(game_date, '%m/%d/%Y')
    season = game['season']

    if "time" in game:
        game_time = game['time']
        game_time= datetime.strptime(game_time, '%H:%M')

    g = models.Games(home_team_id=home_team,
                    away_team_id=away_team)
    try:
        db.session.add(g)
        db.session.commit()
    except Exception as exc:
        print(str(exc))
        return jsonify({"message": str(exc)}), 400

    s = models.Schedule(game_id=g.game_id, game_date=game_date, game_time=game_time, season_id = season)
    try:
        db.session.add(s)
        db.session.commit()
    except Exception as exc:
        print(str(exc))
        return jsonify({"message": str(exc)}), 400

    return jsonify({"message": "Game added to the schedule"}), 200


# @app.route('/getSchedule/<season_id>/<team_id>', methods=['GET'])
@app.route('/getSchedule/<team_id>', methods=['GET'])
def getSchedule(season_id=None, team_id=None):
    home_team = aliased(models.Teams, name='home_team')
    away_team = aliased(models.Teams, name='away_team')
    query = db.session.query(models.Schedule, models.Games, home_team, away_team)
    if season_id:
        query = db.session.query(models.Schedule, models.Games, home_team, away_team).join(models.Schedule).join(home_team, models.Games.home_team_id == home_team.id).join(away_team, models.Games.away_team_id == away_team.id).filter(models.Schedule.season_id == season_id).filter((home_team.id == team_id) | (away_team.id ==team_id))
    results = query.all()
    data_all = []
    print(results)
    for r in results:
        data = {}
        data['schedule_id']        = r.Schedule.id
        data['game_date'] = r.Schedule.game_date
        data['game_time'] = str(r.Schedule.game_time)
        data['game_id'] = r.Schedule.game_id
        home_team = {}
        home_team['id']   = r.home_team.id
        home_team['name'] = r.home_team.team_name
        data['home_team'] = home_team
        away_team = {}
        away_team['id']   = r.away_team.id
        away_team['name'] = r.away_team.team_name
        data['away_team'] = away_team
        final_score = {}
        final_score['home'] = r.Games.final_home_score
        final_score['away'] = r.Games.final_away_score
        data['final_score'] = final_score
        data_all.append(data)

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
    seasons = db.session.query(models.Season, models.Level, models.Sport).join(models.Level).join(models.Sport).filter(models.Season.archive == None)
    data_all = []
    for season in seasons:
        s={}
        s['season_id'] = season.Season.id
        s['level'] = season.Level.level_name
        s['season_name'] = season.Season.name
        s['roster_submission_deadline'] = season.Season.roster_submission_deadline
        s['sport'] = season.Sport.sport_name
        s['year'] = season.Season.year
        data_all.append(s)

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

@app.route('/addGameResults/<game_id>', methods=['POST'])
def addGameResults(game_id):
    data = request.get_json()
    if not 'game' in data:
        return 'Please ensure required fields are filled out', 400
    if not 'team' in data:
        return 'Please ensure required fields are filled out', 400

    game_id   = data['game']
    team_id   = data['team']
    game = db.session.query(models.Games).filter(models.Games.game_id == game_id).first_or_404()

    if 'scores' in data:
        home_final = 0
        away_final = 0
        for score in data['scores']:
            home_final += score['home']
            away_final += score['away']
            period = score['period']
            if score['period'] > 4:
                period = 'OT ' + score['period'] - 4
            gr = models.GameResults(game_id=game, period=period,home_score=score['home'], away_score=score['away'], game_order=score['period'])
            try:
                gr.save()
            except Exeption as exc:
                return str(exc), 500

        if home_final != data['final_scores']['home'] or away_final != data['final_scores']['away']:
            # Send back an alert
            pass
        # Alert if individual stats don't match final scores
        try:
            game.final_home_score = home_final
            game.final_away_score = away_final
            game.save()
            gr.commit()
            game.commit()
        except Exception as exc:
            return str(exc), 500

    if 'player_stats' in data:
        for player in data['player_stats']:
            message = addPlayerStats(player_id = player['id'], game_id=game_id, stats=data, team_id=team_id)
    return message

@app.route('/addPlayerStats/<player_id>/<game_id>/<team_id>', methods=['POST'])
def addPlayerStats(player_id, game_id, team_id, stats=None):
    two_points_attempted = 0
    two_points_made = 0
    three_points_attempted = 0
    three_points_made = 0
    free_throws_attempted = 0
    free_throws_made = 0
    assists = 0
    offensive_rebounds = 0
    defensive_rebounds = 0
    steals = 0
    blocks = 0
    turnovers = 0
    
    if not stats:
        data = request.get_json()
        stats = data

    if '2PA' in stats:
        two_points_attempted   = stats['2PA']
    if '2PM' in stats:
        two_points_made        = stats['2PM']
    if '3PM' in stats:
        three_points_attempted = stats['3PA']
    if '3PA' in stats:
        three_points_made      = stats['3PM']
    if 'FTA' in stats:
        free_throws_attempted  = stats['FTA']
    if 'FTM' in stats:
        free_throws_made       = stats['FTM']
    if 'assists' in stats:
        assists                = stats['assists']
    if 'offensive_rebounds' in stats:
        offensive_rebounds     = stats['offensive_rebounds']
    if 'defensive_rebounds' in stats:
        defensive_rebounds     = stats['defensive_rebounds']
    if 'steals' in stats:
        steals                 = stats['steals']
    if 'blocks' in stats:
        blocks                 = stats['blocks']

    game_stats = models.BasketballStats(game_id=game_id,
                                         team_id=team_id,
                                         player_id=player_id,
                                         field_goals_attempted=two_points_attempted,
                                         field_goals_made=two_points_made,
                                         three_pointers_attempted=three_points_attempted,
                                         three_pointers_made=three_points_made,
                                         free_throws_attempted=free_throws_attempted,
                                         free_throws_made=free_throws_made,
                                         total_points = utils.totalPoints(two_points_made, three_points_made, free_throws_made),
                                         assists=assists,
                                         offensive_rebounds=offensive_rebounds,
                                         defensive_rebounds=defensive_rebounds,
                                         total_rebounds=offensive_rebounds + defensive_rebounds,
                                         steals=steals,
                                         blocks=blocks
                                        )
    try:
        # game_stats.save()
        db.session.add(game_stats)
        # game_stats.commit()
        db.session.commit()

    except Exception as exc:
        return str(exc), 500
    
    return jsonify("Saved"), 200

@app.route('/getGameResults/<game_id>/<team_id>', methods=['GET'])
def getGameResults(game_id=None, team_id=None):

    results = db.session.query(models.Games, models.Teams, models.Persons, models.GameResults, models.BasketballStats).\
        join(models.Games, or_(models.Games.home_team_id == models.Teams.id, models.Games.away_team_id == models.Teams.id)).\
        join(models.Persons).filter(models.Persons.person_type == 1).\
        outerjoin(models.GameResults).\
        outerjoin(models.BasketballStats, and_(models.BasketballStats.game_id == models.Games.game_id, models.BasketballStats.player_id == models.Persons.id, models.BasketballStats.team_id == models.Teams.id)).\
        filter(models.Games.game_id == game_id).\
        filter(models.Teams.id == team_id).all()

    data_all = []
    for r in results:
        data={}
        data['team_id'] = r.Teams.id
        data['game_id'] = r.Games.game_id
        data['player_first_name'] = r.Persons.first_name
        data['player_last_name'] = r.Persons.last_name
        data['player_number'] = r.Persons.number
        stats = {}
        stats['2PA'] = 0
        stats['2PM'] = 0
        stats['3PA'] = 0
        stats['3PM'] = 0
        stats['FTA'] = 0
        stats['FTM'] = 0
        stats['total_points'] = 0
        stats['assists'] = 0
        stats['steals'] = 0
        stats['blocks'] = 0
        stats['offensive_rebounds'] = 0
        stats['defensive_rebounds'] = 0
        stats['total_rebounds'] = 0
        if r.BasketballStats:
            stats['2PA'] = r.BasketballStats.field_goals_attempted
            stats['2PM'] = r.BasketballStats.field_goals_made
            stats['3PA'] = r.BasketballStats.three_points_attempted
            stats['3PM'] = r.BasketballStats.three_points_made
            stats['FTA'] = r.BasketballStats.free_throws_attempted
            stats['FTM'] = r.BasketballStats.free_throws_made
            stats['total_points'] = r.BasketballStats.total_points
            stats['assists'] = r.BasketballStats.assists
            stats['steals'] = r.BasketballStats.steals
            stats['blocks'] = r.BasketballStats.blocks
            stats['offensive_rebounds'] = r.BasketballStats.offensive_rebounds
            stats['defensive_rebounds'] = r.BasketballStats.defensive_rebounds
            stats['total_rebounds'] = r.BasketballStats.total_rebounds
        data['player_stats'] = stats

        data_all.append(data)

    return jsonify(data_all), 200

@app.route('/addPlayerToRoster', methods=['POST'])
def addToRoster():
    data = request.get_json()
    print(data)

    if 'team_id' not in data.keys():
        return jsonify({'message': "Team is required"}), 401
    if 'player_id' not in data.keys():
        return jsonify({'message': "player is required"}), 401
    if 'level_id' not in data.keys():
        return jsonify({'message': "Level is required"}), 401

    player = models.TeamRoster(**data)
    db.session.add(player)
    db.session.commit()
    return jsonify({"message": "Player added to Roster"})





if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5001')

