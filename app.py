from functools import wraps

from flask import Flask, jsonify, request, url_for

from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import aliased
from sqlalchemy import and_, or_, func


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

    return jsonify({'token': token.decode('UTF-8') })


@app.route('/getTeams', methods=['GET'])
@app.route('/getTeams/<slug>', methods=['GET'])
def getTeam(slug=None):
    data_all = []
    if not slug:
        data = db.session.query(models.Teams).all()
        print("here")
        for team in data:
            data_all.append(utils.row2dict(team))
        return jsonify(team=data_all)

    data = models.Teams.query.filter(models.Teams.slug==slug)
    for team in data:
        data_all.append(utils.row2dict(team))

    return jsonify(team=data_all)


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
#    if 'birth_date' in data:
#        birth_date = data['birth_date']
#    else:
#        return "Birth Date is required", 401
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
    
    player.first_name = results.get('first_name')   
    player.last_name = results.get('last_name')
    player.birth_date = results.get('birth_date')
    player.height = results.get('height')   
    player.team_id = results.get('team_id')    
    player.person_type = results.get('person_type')

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

@app.route('/getStandings/', methods=['GET'])
@app.route('/getStandings/<season_id>', methods=['GET'])
def getStandings(season_id=None):
    if not season_id:
        seasons = db.session.query(models.Season, models.Level, models.Teams).join(models.Level).filter(models.Season.archive == None).filter(models.Level.level_name == '18U Boys').first()
        season_id = seasons.Season.id

    results = db.session.query(models.Standings, models.SeasonTeams).outerjoin(models.SeasonTeams, models.Standings.team_id == models.SeasonTeams.id).filter(models.Standings.season_id == season_id).order_by(models.Standings.win_percentage.desc()).all()
    print(results)
    
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
        data['team_name'] = team.SeasonTeams.team_name
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
    print(game['season'])

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

    ht_results = db.session.query(models.Teams, models.SeasonTeams).join(models.SeasonTeams).filter(models.Teams.slug == home_team).filter(models.SeasonTeams.season_id == game['season']).first_or_404()

    aw_results = db.session.query(models.Teams, models.SeasonTeams).join(models.SeasonTeams).filter(models.Teams.slug == away_team).filter(models.SeasonTeams.season_id == game['season']).first_or_404()

    home_team = ht_results.SeasonTeams.id
    away_team = aw_results.SeasonTeams.id

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

@app.route('/getSchedule/', methods=['GET'])
@app.route('/getSchedule/<season_id>', methods=['GET'])
@app.route('/getSchedule/<season_id>/<slug>', methods=['GET'])
def getSchedule(season_id=None, slug=None):

    home_team = aliased(models.SeasonTeams, name='home_team')
    away_team = aliased(models.SeasonTeams, name='away_team')
    query = db.session.query(models.Schedule, models.Games, home_team, away_team)

    if season_id and slug:
        query = db.session.query(models.Schedule, models.Games, home_team, away_team, models.Address).join(models.Schedule).join(home_team, models.Games.home_team_id == home_team.id).join(away_team, models.Games.away_team_id == away_team.id).join(models.Address, home_team.address_id == models.Address.id).filter(models.Schedule.season_id == season_id).filter(or_(home_team.slug == slug, away_team.slug == slug)).order_by(models.Schedule.game_date)
    elif season_id and not slug:
        query = db.session.query(models.Schedule, models.Games, home_team, away_team, models.Address).join(models.Schedule).join(home_team, models.Games.home_team_id == home_team.id).join(away_team, models.Games.away_team_id == away_team.id).join(models.Address, home_team.address_id == models.Address.id).filter(models.Schedule.season_id == season_id).order_by(models.Schedule.game_date)
    else:
        season_list = []
        seasons = db.session.query(models.Season, models.Level, models.Sport).join(models.Level).join(models.Sport).filter(models.Season.archive == None).all()
        for season in seasons:
            season_list.append(season.Season.id)
        query = db.session.query(models.Schedule, models.Games, home_team, away_team, models.Address).join(models.Schedule).join(home_team, models.Games.home_team_id == home_team.id).join(away_team, models.Games.away_team_id == away_team.id).join(models.Address, home_team.address_id == models.Address.id).filter(models.Schedule.season_id.in_(season_list)).order_by(models.Schedule.game_date)

    print(query)

    results = query.all()
    data_all = []
    for r in results:
        data = {}
        data['schedule_id']        = r.Schedule.id
        data['game_date'] = r.Schedule.game_date.strftime('%B %e')
        data['game_time'] = r.Schedule.game_time.strftime('%l:%M %p %Z')
        data['game_id'] = r.Schedule.game_id
        home_team = {}
        home_team['id']   = r.home_team.id
        home_team['name'] = r.home_team.team_name
        home_team['address_name'] = r.Address.name
        home_team['address_lines'] = r.Address.address_line_1 
        home_team['city_state_zip'] = r.Address.city  + ', ' + r .Address.state + ' ' + r.Address.postal_code
        home_team['team_level'] = r.home_team.level_name
        home_team['slug'] = r.home_team.slug
        data['home_team'] = home_team
        away_team = {}
        away_team['id']   = r.away_team.id
        away_team['name'] = r.away_team.team_name
        away_team['team_level'] = r.away_team.level_name
        away_team['slug'] = r.away_team.slug
        data['away_team'] = away_team
        final_score = {}
        final_score['home'] = r.Games.final_home_score
        final_score['away'] = r.Games.final_away_score
        data['final_score'] = final_score
        data_all.append(data)

    return jsonify(data_all), 200

@app.route('/getSeasons', methods=['GET'])
def getSeason():
    #y = models.Season.query.all()
    y = db.session.query(models.Season, models.Level).join(models.Level)

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
    if not 'team' in data:
        return 'Please ensure required fields are filled out', 400

    team_id = data['team']
    game = db.session.query(models.Games).filter(models.Games.game_id == game_id).first_or_404()
    #home_team = game.get('home_team')
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
    
    
    #finals = data.get('final_scores')
    
    #game.final_home_score = finals.get('home_score', 0)
    #game.final_away_score = finals.get('away_score', 0)
    #game.save()

    if 'final_scores' in data : #data['final_scores']['home_score'] != 0 and  data['final_scores']['away_score'] != 0:
        try:
            results = db.session.query(models.SeasonTeams).filter(models.SeasonTeams.team_id == game.home_team_id).all()
            if data['final_scores']['home_score'] > data['final_scores']['away_score']:
                standings = db.session.query(models.Standings).filter(models.Standings.team_id == game.home_team_id).first_or_404()
                standings.wins +=  1
                standings.games_played += 1
                db.session.commit()
                standings = db.session.query(models.Standings).filter(models.Standings.team_id == game.away_team_id).first_or_404()
                standings.losses +=  1
                standings.games_played += 1
                db.session.commit()
            else:
                standings = db.session.query(models.Standings).filter(models.Standings.team_id == game.home_team_id).first_or_404()
                standings.wins +=  1
                standings.games_played += 1
                db.session.commit()
                standings = db.session.query(models.Standings).filter(models.Standings.team_id == game.away_team_id).first_or_404()
                standings.losses +=  1
                standings.games_played += 1
                db.session.commit()

        except Exception as exc:
            return str(exc), 500

    updates = db.session()
    for player in data.get('player_stats', []):
        message = addPlayerStats(player_id = player['player_id'], game_id=game_id, stats=player, team_id=team_id, game_updates=updates)

    try:
        updates.commit()
    except Exception as exc:
        updates.rollback()
        return str(exc), 500

    return 'Results have been saved successfully', 200

@app.route('/addPlayerStats/<player_id>/<game_id>/<team_id>', methods=['POST'])
def addPlayerStats(player_id, game_id, team_id, stats=None, game_updates=None):
    if not stats:
        data = request.get_json()
        stats = data
    new_keys = {}
    new_keys['field_goals_attempted']   = stats.get('2PA', 0)
    new_keys['field_goals_made']        = stats.get('2PM', 0)
    new_keys['three_pointers_attempted'] = stats.get('3PA', 0)
    new_keys['three_pointers_made']      = stats.get('3PM', 0)
    new_keys['free_throws_attempted']  = stats.get('FTA', 0)
    new_keys['free_throws_made']       = stats.get('FTM', 0)
    new_keys['assists']                = stats.get('AST', 0)
    new_keys['offensive_rebounds']     = stats.get('OREB', 0)
    new_keys['defensive_rebounds']     = stats.get('DREB', 0)
    new_keys['steals']                 = stats.get('STEAL', 0)
    new_keys['blocks']                 = stats.get('BLK', 0)
    new_keys['turnovers']              = stats.get('TO', 0)
    new_keys['total_points']  = utils.totalPoints(new_keys['field_goals_made'], new_keys['three_pointers_made'], new_keys['free_throws_made'])

    try:
        new_keys['game_id'] = game_id
        new_keys['team_id'] = team_id
        new_keys['player_id'] = player_id

        game_stats = models.BasketballStats(**new_keys)
        game_updates.add(game_stats)

    except Exception as exc:
        db.session.query(models.BasketballStats).filter(models.BasketballStats.game_id == game_id).filter(models.BasketballStats.player_id == player_id).update(new_keys)
        db.session.commit()
        print(str(exc))

    if not game_updates:
        try:
            db.session.on_conflict_do_update(game_stats)
            db.session.commit()

        except Exception as exc:
            return str(exc), 500

    return jsonify(new_keys['total_points']), 200

@app.route('/getRoster/<season_team>/')
def getRoster(season_team):
    query = db.session.query(models.TeamRoster, models.Persons).join(models.SeasonTeams, models.TeamRoster.season_team_id == models.SeasonTeams.id).join(models.Persons).join(models.Teams).filter(models.TeamRoster.season_team_id==season_team)
    
    results = query.all()
    roster= []
    for result in results:
        player = {}
        player['player_id'] = result.TeamRoster.player_id
        player['first_name'] = result.Persons.first_name
        player['last_name'] = result.Persons.last_name
        player['number'] = result.Persons.number
        roster.append(player)

    return jsonify(roster), 200

@app.route('/getGameResults/<game_id>/<team_id>', methods=['GET'])
def getGameResults(game_id=None, team_id=None):
    game_roster = db.session.query(models.TeamRoster.season_team_id, 
                                   models.Persons.id, 
                                   models.Persons.first_name, 
                                   models.Persons.last_name, 
                                   models.Persons.number, 
                                   models.Games.game_id)\
                .join(models.SeasonTeams, models.TeamRoster.season_team_id == models.SeasonTeams.id)\
                .join(models.Games, or_(models.Games.home_team_id == models.SeasonTeams.id, models.Games.away_team_id == models.SeasonTeams.id))\
                .join(models.Persons).join(models.Teams)\
                .filter(models.TeamRoster.season_team_id==team_id)\
                .filter(models.Games.game_id == game_id)\
                .cte('game_roster')
    #print(game_roster)
    roster = aliased(game_roster, name="roster")
    
    query = db.session.query(
                roster.c.id.label('id'), 
                roster.c.first_name, 
                roster.c.last_name, 
                roster.c.number, 
                func.coalesce(models.BasketballStats.field_goals_made, 0).label('field_goals_made'),
                func.coalesce(models.BasketballStats.field_goals_attempted, 0).label('field_goals_attempted'),
                func.coalesce(models.BasketballStats.three_pointers_made, 0).label('three_pointers_made'),
                func.coalesce(models.BasketballStats.three_pointers_attempted, 0).label('three_pointers_attempted'),
                func.coalesce(models.BasketballStats.free_throws_made, 0).label('free_throws_made'),
                func.coalesce(models.BasketballStats.free_throws_attempted, 0).label('free_throws_attempted'),
                func.coalesce(models.BasketballStats.total_points, 0).label('total_points'),
                func.coalesce(models.BasketballStats.assists, 0).label('assists'),
                func.coalesce(models.BasketballStats.offensive_rebounds, 0).label('offensive_rebounds'),
                func.coalesce(models.BasketballStats.defensive_rebounds, 0).label('defensive_rebounds'),
                func.coalesce(models.BasketballStats.total_rebounds, 0).label('total_rebounds'),
                func.coalesce(models.BasketballStats.steals, 0).label('steals'),
                func.coalesce(models.BasketballStats.blocks, 0).label('blocks'),
                func.coalesce(models.BasketballStats.turnovers, 0).label('turnovers')
            )\
            .outerjoin(models.BasketballStats, 
                        and_(roster.c.game_id == models.BasketballStats.game_id, 
                        roster.c.id == models.BasketballStats.player_id))
    
    
    results = query.all()
    

    
    game = {}
    game['game_id'] = game_id
    game['team_id'] = team_id


    data_all = []
    for r in results:
        data={}
        data['player_id'] = r.id
        data['player_first_name'] = r.first_name
        data['player_last_name'] = r.last_name
        data['player_number'] = r.number
        stats = {}
        stats['2PA'] = r.field_goals_attempted
        stats['2PM'] = r.field_goals_made
        stats['3PA'] = r.three_pointers_attempted
        stats['3PM'] = r.three_pointers_made
        stats['FTA'] = r.free_throws_attempted
        stats['FTM'] = r.free_throws_made
        stats['total_points'] = r.total_points
        stats['assists'] = r.assists
        stats['steals'] = r.steals
        stats['blocks'] = r.blocks
        stats['offensive_rebounds'] = r.offensive_rebounds
        stats['defensive_rebounds'] = r.defensive_rebounds
        stats['total_rebounds'] = r.total_rebounds
        data['player_stats'] = stats

        data_all.append(data)
    game['player_stats'] = data_all

    return jsonify(game), 200

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

@app.route('/getLevels', methods=['GET'])
def getLevels():
    results = db.session.query(models.Level)

    data_all=[]
    for r in results:
        data_all.append(utils.row2dict(r))

    return jsonify(data_all), 200





if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5001')

