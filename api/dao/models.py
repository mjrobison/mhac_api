
# from app import db, bcrypt
from sqlalchemy.dialects.postgresql import JSON, UUID
from uuid import uuid4
import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Numeric
from sqlalchemy.orm import relationship

from .database import Base

class User(Base):
    """ User Model for storing user related details """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), unique=True,nullable=False, default=uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    registered_on = Column(DateTime, nullable=False)
    admin = Column(Boolean, nullable=False, default=False)

    def __init__(self, email, password, admin=False):
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, 15
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
        if not user or not bcrypt.check_password_hash(user.password, password):
            return None

        return user

    def to_dict(self):
        return dict(id=self.id, email=self.email)

class Address(Base):
    __tablename__ = 'addresses'
    __table_args__ = {"schema":"mhac"}

    id = Column(UUID(as_uuid=True), unique=True,
                   nullable=False, primary_key=True, default=uuid4)
    name = Column(String(150))
    address_line_1 = Column(String(150))
    address_line_2 = Column(String(150))
    city = Column(String(150))
    state = Column(String(2))
    postal_code = Column(String(10))
    teams = relationship('Teams',  backref=('Address'))

# class Teams(Base):
#     __tablename__ = 'teams'
#     __table_args__ = {"schema":"mhac"}

#     # Team color, website, Team Secondary, logo name color, logo name grey
#     id = Column(UUID(as_uuid=True), unique=True,
#                    nullable=False, primary_key=True, default=uuid4)
#     team_name = Column(String(100))
#     team_mascot = Column(String(150))
#     address_id = Column(UUID(as_uuid=True), ForeignKey('mhac.addresses.id'))
#     main_color = Column(String(6))
#     secondary_color = Column(String(6))
#     website = Column(String(150))
#     logo_color = Column(String(150))
#     logo_grey = Column(String(150))
#     # home_team = relationship('Games', backref=('home_teams'), foreign_keys="Games.home_team_id")
#     # away_team = relationship('Games', backref=('away_teams'), foreign_keys="Games.away_team_id")
#     slug = Column(String(150))

#     def __repr__(self):
#         return '<id {}>'.format(self.id)


class Level(Base):
    __tablename__ = 'levels'
    __table_args__ = {"schema":"mhac"}

    id = Column(Integer, primary_key=True)
    level_name = Column(String(50))

    def __repr__(self):
        return '{0}'.format(self.level_name)

class PersonType(Base):
    __tablename__ = 'person_type'
    __table_args__ = {'schema':'mhac'}

    id = Column(Integer, primary_key=True)
    type = Column(String(100))
    persons = relationship('Persons', backref=('PersonType'))

class Persons(Base):
    __tablename__ = 'person'
    __table_args__ = {"schema":"mhac"}

    id = Column(UUID(as_uuid=True), unique=True, nullable=False, primary_key=True,default=uuid4)
    first_name= Column(String(100))
    last_name= Column(String(100))
    birth_date= Column(Date())
    height= Column(String(10))
    person_type = Column(Integer, ForeignKey('mhac.person_type.id'))
    team_id = Column(UUID(as_uuid=True), ForeignKey('mhac.teams.id'))
    number = Column(Integer)
    position = Column(String)

    def __repr__(self):
        return 'Person Name {} {}'.format(self.first_name, self.last_name)

class Sport(Base):
    __tablename__ = 'sports'
    __table_args__ = {"schema":"mhac"}

    id = Column(Integer, primary_key=True)
    sport_name = Column(String(100), nullable=False)
    relationship('Season', backref=('sport_season'))

class Season(Base):
    __tablename__ = 'seasons'
    __table_args__ = {"schema": "mhac"}

    #Create an active flag/begin and endate/ deadline dates

    id = Column(UUID(as_uuid=True), unique=True,
                   nullable=False, primary_key=True, default=uuid4)
    name = Column(String(100))
    year = Column(String(4))
    level_id = Column(Integer, ForeignKey('mhac.levels.id'), nullable=False)
    sport_id = Column(Integer, ForeignKey('mhac.sports.id'), nullable=False)
    start_date = Column(DateTime)
    roster_submission_deadline = Column(DateTime)
    roster_addition_deadline = Column(DateTime)
    tournament_start_date = Column(DateTime)
    archive = Column(Boolean)
    schedule = relationship('Schedule', backref=('Season'), foreign_keys="Schedule.season_id")

    def __repr__(self):
        return '{0}'.format(self.name)



class SeasonTeams(Base):
    __tablename__ = 'season_teams_with_names'
    __table_args__ = {"schema": "mhac"}

    id = Column(UUID(as_uuid=True), unique=True,
                   nullable=False, primary_key=True, default=uuid4)
    season_id = Column(UUID(as_uuid=True), ForeignKey('mhac.seasons.id'), nullable=False)
    #level_id = Column(Integer, ForeignKey('mhac.levels.id'), nullable=False)
    team_id = Column(UUID(as_uuid=True), ForeignKey('mhac.teams.id'), nullable=False)
    team_name = Column(String(100))
    team_mascot = Column(String(150))
    address_id = Column(UUID(as_uuid=True), ForeignKey('mhac.addresses.id'))
    main_color = Column(String(6))
    secondary_color = Column(String(6))
    website = Column(String(150))
    logo_color = Column(String(150))
    logo_grey = Column(String(150))
    slug = Column(String(150))
    level_name = Column(String(50))

#    home_team = relationship('Games', backref=(
#            'home_teams'), foreign_keys="Games.home_team_id")
#    away_team = relationship('Games', backref=(
#        'away_teams'), foreign_keys="Games.away_team_id")

class TeamRoster(Base):
    __tablename__ = 'team_rosters'
    __table_args__ = {"schema": "mhac"}

    roster_id = Column(Integer, primary_key=True, autoincrement=True)
    season_team_id = Column(UUID(as_uuid=True)) #, ForeignKey('mhac.season_teams.id'))
    player_id = Column(UUID(as_uuid=True), ForeignKey('mhac.person.id'))

class Schedule(Base):
    __tablename__ = 'schedule'
    __table_args__ = {"schema": "mhac"}

    id = Column(Integer, primary_key=True, nullable=False)
    game_id = Column(UUID(as_uuid=True), ForeignKey('mhac.games.game_id'))
    game_date = Column(DateTime)
    game_time = Column(DateTime)
    season_id = Column(UUID(as_uuid=True), ForeignKey('mhac.seasons.id'))
    neutral_site = Column(Boolean)

class Standings(Base):
    __tablename__ = 'standings'
    __table_args__ = {'schema':'mhac'}

    pk = Column(Integer, primary_key=True, nullable=False)
    team_id = Column(UUID(as_uuid=True), ForeignKey('mhac.teams.id'))
    season_id = Column(UUID(as_uuid=True), ForeignKey('mhac.seasons.id'))
    wins = Column(Integer)
    losses = Column(Integer)
    games_played = Column(Integer)
    win_percentage = Column(Numeric(precision=4, asdecimal=True))

class Games(Base):
    __tablename__ = 'games'
    __table_args__= {'schema':'mhac'}

    game_id = Column(UUID(as_uuid=True), unique=True, nullable=False, primary_key=True, default=uuid4)
    home_team_id = Column(UUID(as_uuid=True))
    away_team_id = Column(UUID(as_uuid=True))
    final_home_score = Column(Integer)
    final_away_score = Column(Integer)
    schedule = relationship('Schedule', backref=('Games'), foreign_keys="Schedule.game_id")


class GameResults(Base):
    __tablename__ = 'game_results'
    __table_args__= {'schema':'mhac'}

    pk = Column(Integer, primary_key=True, nullable=False)
    game_id = Column(UUID(as_uuid=True), ForeignKey('mhac.games.game_id'))
    period = Column(String(5))
    home_score = Column(Integer)
    away_score = Column(Integer)
    game_order = Column(Integer)

class BasketballStats(Base):
    __tablename__ = 'basketball_stats'
    __table_args__= {'schema':'mhac'}

    pk = Column(Integer, primary_key=True, nullable=False)
    game_id = Column(UUID(as_uuid=True), ForeignKey('mhac.games.game_id'))
    team_id = Column(UUID(as_uuid=True))
    player_id = Column(UUID(as_uuid=True), ForeignKey('mhac.person.id'))
    field_goals_attempted = Column(Integer)
    field_goals_made = Column(Integer)
    three_pointers_attempted = Column(Integer)
    three_pointers_made = Column(Integer)
    free_throws_attempted = Column(Integer)
    free_throws_made = Column(Integer)
    total_points = Column(Integer)
    assists = Column(Integer)
    offensive_rebounds = Column(Integer)
    defensive_rebounds = Column(Integer)
    total_rebounds = Column(Integer)
    steals = Column(Integer)
    blocks = Column(Integer)
    turnovers = Column(Integer)
