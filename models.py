from app import db, bcrypt
from sqlalchemy.dialects.postgresql import JSON, UUID
from uuid import uuid4
#from sqlalchemy.dialects.postgresql import UUID

class User(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True,nullable=False, default=uuid4)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, email, password, admin=False):
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()
        self.registered_on = datetime.datetime.now()
        self.admin = admin
    
    @classmethod
    def authenticate(cls, **kwargs):
        email = kwargs.get('email')
        password = kwargs.get('password')
        
        if not email or not password:
            return None

        user = cls.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            return None

        return user

    def to_dict(self):
        return dict(id=self.id, email=self.email)

class Address(db.Model):
    __tablename__ = 'addresses'
    __table_args__ = {"schema":"mhac"}

    id = db.Column(UUID(as_uuid=True), unique=True,
                   nullable=False, primary_key=True, default=uuid4)
    name = db.Column(db.String(150))
    address_line_1 = db.Column(db.String(150))
    address_line_2 = db.Column(db.String(150))
    city = db.Column(db.String(150))
    state = db.Column(db.String(2))
    postal_code = db.Column(db.String(10))
    teams = db.relationship('Teams',  backref=('Address'))

class Teams(db.Model):
    __tablename__ = 'teams'
    __table_args__ = {"schema":"mhac"}

    # Team color, website, Team Secondary, logo name color, logo name grey
    id = db.Column(UUID(as_uuid=True), unique=True,
                   nullable=False, primary_key=True, default=uuid4)
    team_name = db.Column(db.String(100))
    team_mascot = db.Column(db.String(150))
    address_id = db.Column(UUID(as_uuid=True), db.ForeignKey('mhac.addresses.id'))
    main_color = db.Column(db.String(6))
    secondary_color = db.Column(db.String(6))
    website = db.Column(db.String(150))
    logo_color = db.Column(db.String(150))
    logo_grey = db.Column(db.String(150))
    home_team = db.relationship('Games', backref=('home_teams'), foreign_keys="Games.home_team_id")
    away_team = db.relationship('Games', backref=('away_teams'), foreign_keys="Games.away_team_id")

    def __repr__(self):
        return '<id {}>'.format(self.id)

class PersonType(db.Model):
    __table__name = 'person_type'
    __table_args__ = {'schema':'mhac'}

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(100))
    persons = db.relationship('Persons', backref=('PersonType'))

class Persons(db.Model):
    __tablename__ = 'person'
    __table_args__ = {"schema":"mhac"}

    id = db.Column(UUID(as_uuid=True), unique=True, nullable=False, primary_key=True,default=uuid4)
    first_name= db.Column(db.String(100))
    last_name= db.Column(db.String(100))
    birth_date= db.Column(db.Date())
    height= db.Column(db.Integer)
    person_type = db.Column(db.Integer, db.ForeignKey('mhac.person_type.id'))
    team_id = db.Column(UUID(as_uuid=True), db.ForeignKey('mhac.teams.id'))
    number = db.Column(db.Integer)
    position = db.Column(db.String)

    def __repr__(self):
        return 'Person Name {} {}'.format(self.first_name, self.last_name)

class Level(db.Model):
    __tablename__ = 'levels'
    __table_args__ = {"schema":"mhac"}

    id = db.Column(db.Integer, primary_key=True)
    level_name = db.Column(db.String(50))

    def __repr__(self):
        return '{0}'.format(self.level_name)

class Sport(db.Model):
    __tablename__ = 'sports'
    __table_args__ = {"schema":"mhac"}

    id = db.Column(db.Integer, primary_key=True)
    sport_name = db.Column(db.String(100), nullable=False)
    db.relationship('Season', backref=('sport_season'))

class Season(db.Model):
    __tablename__ = 'seasons'
    __table_args__ = {"schema": "mhac"}

    #Create an active flag/begin and endate/ deadline dates

    id = db.Column(UUID(as_uuid=True), unique=True,
                   nullable=False, primary_key=True, default=uuid4)
    name = db.Column(db.String(100))
    year = db.Column(db.String(4))
    level_id = db.Column(db.Integer, db.ForeignKey('mhac.levels.id'), nullable=False)
    sport_id = db.Column(db.Integer, db.ForeignKey('mhac.sports.id'), nullable=False)
    start_date = db.Column(db.DateTime)
    roster_submission_deadline = db.Column(db.DateTime)
    roster_addition_deadline = db.Column(db.DateTime)
    tournament_start_date = db.Column(db.DateTime)
    archive = db.Column(db.Boolean)
    schedule = db.relationship('Schedule', backref=('Season'), foreign_keys="Schedule.season_id")

    def __repr__(self):
        return '{0}'.format(self.name)

class Schedule(db.Model):
    __tablename__ = 'schedule'
    __table_args__ = {"schema": "mhac"}

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    game_id = db.Column(UUID(as_uuid=True), db.ForeignKey('mhac.games.game_id'))
    game_date = db.Column(db.DateTime)
    game_time = db.Column(db.DateTime)
    season_id = db.Column(UUID(as_uuid=True), db.ForeignKey('mhac.seasons.id'))
    neutral_site = db.Column(db.Boolean)

class Standings(db.Model):
    __tablename__ = 'standings'
    __table_args__ = {'schema':'mhac'}

    pk = db.Column(db.Integer, primary_key=True, nullable=False)
    team_id = db.Column(UUID(as_uuid=True), db.ForeignKey('mhac.teams.id'))
    season_id = db.Column(UUID(as_uuid=True), db.ForeignKey('mhac.seasons.id'))
    wins = db.Column(db.Integer)
    losses = db.Column(db.Integer)
    games_played = db.Column(db.Integer)
    win_percentage = db.Column(db.Numeric(precision=4, asdecimal=True))

class Games(db.Model):
    __tablename__ = 'games'
    __table_args__= {'schema':'mhac'}

    game_id = db.Column(UUID(as_uuid=True), unique=True, nullable=False, primary_key=True, default=uuid4)
    home_team_id = db.Column(UUID(as_uuid=True), db.ForeignKey('mhac.teams.id'))
    away_team_id = db.Column(UUID(as_uuid=True), db.ForeignKey('mhac.teams.id'))
    final_home_score = db.Column(db.Integer)
    final_away_score = db.Column(db.Integer)
    schedule = db.relationship('Schedule', backref=('Games'), foreign_keys="Schedule.game_id")



class GameResults(db.Model):
    __tablename__ = 'game_results'
    __table_args__= {'schema':'mhac'}

    pk = db.Column(db.Integer, primary_key=True, nullable=False)
    game_id = db.Column(UUID(as_uuid=True), db.ForeignKey('mhac.games.game_id'))
    period = db.Column(db.String(5))
    home_score = db.Column(db.Integer)
    away_score = db.Column(db.Integer)
    game_order = db.Column(db.Integer)

class BasketballStats(db.Model):
    __tablename__ = 'basketball_stats'
    __table_args__= {'schema':'mhac'}

    pk = db.Column(db.Integer, primary_key=True, nullable=False)
    game_id = db.Column(UUID(as_uuid=True), db.ForeignKey('mhac.games.game_id'))
    team_id = UUID(as_uuid=True), db.ForeignKey('mhac.teams.id')
    player_id = db.Column(UUID(as_uuid=True), db.ForeignKey('mhac.person.id'))
    field_goals_attempted = db.Column(db.Integer)
    field_goals_made = db.Column(db.Integer)
    three_pointers_attempted = db.Column(db.Integer)
    three_pointers_made = db.Column(db.Integer)
    free_throws_attempted = db.Column(db.Integer)
    free_throws_made = db.Column(db.Integer)
    total_points = db.Column(db.Integer)
    assists = db.Column(db.Integer)
    offensive_rebounds = db.Column(db.Integer)
    defensive_rebounds = db.Column(db.Integer)
    total_rebounds = db.Column(db.Integer)
    steals = db.Column(db.Integer)
    blocks = db.Column(db.Integer)


# Results?



