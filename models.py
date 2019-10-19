from app import db
from sqlalchemy.dialects.postgresql import JSON, UUID
from uuid import uuid4
#from sqlalchemy.dialects.postgresql import UUID

class Address(db.Model):
    __tablename__ = 'addresses'
    __table_args__ = {"schema":"mhac"}

    id = db.Column(UUID(as_uuid=True), unique=True, nullable=False, primary_key=True)
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
    id = db.Column(UUID(as_uuid=True), unique=True, nullable=False, primary_key=True)
    team_name = db.Column(db.String(100))
    team_mascot = db.Column(db.String(150))
    address_id = db.Column(UUID(as_uuid=True), db.ForeignKey('mhac.addresses.id'))
    main_color = db.Column(db.String(6))
    secondary_color = db.Column(db.String(6))
    website = db.Column(db.String(150))
    logo_color = db.Column(db.String(150))
    logo_grey = db.Column(db.String(150))
    home_team = db.relationship('Schedule', backref=('home_teams'), foreign_keys="Schedule.home_team_id")
    away_team = db.relationship('Schedule', backref=('away_teams'), foreign_keys="Schedule.away_team_id")

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
        return '{}'.format(self.level_name)

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
        return '{}'.format(name)

class Schedule(db.Model):
    __tablename__ = 'schedule'
    __table_args__ = {"schema": "mhac"}

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    home_team_id = db.Column(UUID(as_uuid=True), db.ForeignKey('mhac.teams.id'))
    away_team_id = db.Column(UUID(as_uuid=True), db.ForeignKey('mhac.teams.id'))
    home_score = db.Column(db.String(3))
    away_score = db.Column(db.String(3))
    game_date = db.Column(db.DateTime)
    game_time = db.Column(db.DateTime)
    season_id = db.Column(UUID(as_uuid=True), db.ForeignKey('mhac.seasons.id'))
    neutral_site = db.Column(db.Boolean)
   # home_team = db.relationship("Teams", foreign_keys=[home_team_id])
   # away_team = db.relationship("Teams", foreign_keys=[away_team_id])
   # season = db.relationship("Season", foreign_keys=[season_id])



# Results?
# Standings
# Scores?


