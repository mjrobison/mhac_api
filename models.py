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

    id = db.Column(UUID(as_uuid=True), unique=True, nullable=False, primary_key=True)
    team_name = db.Column(db.String(100))
    team_mascot = db.Column(db.String(150))
    address_id = db.Column(UUID(as_uuid=True), db.ForeignKey('mhac.addresses.id'))
    schedule = db.Relationship('Schedule', backref=('Teams'))

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

    def __repr__(self):
        return 'Person Name {} {}'.format(self.first_name, self.last_name)

class level(db.Model):
    __tablename__ = 'levels'
    __table_args__ = ["schema":"mhac"]

    id = db.Column(db.Integer, primary_key=True)
    level_name = db.Column(db.String(50))

    def __repr__(self):
        return '{}'.format(self.level_name)

class Season(db.Model):
    __tablename__ = 'seasons'
    __table_args__ = ['"schema':"mhac"]

    id = db.Column(UUID(as_uuid=True), unique=True,
                   nullable=False, primary_key=True, default=uuid4)
    name = db.Column(db.String(100))
    year = db.Column(db.String(4))

    def __repr__(self):
        return '{}'.format(name)

class Schedule(db.Model):
    __tablename__ = 'schedule'
    __table_args__ = {"schema": "mhac"}

    id = db.Column(db.Integer, primary_key=True)
    home_team = db.Column(UUID(as_uuid=True, db.ForeignKey('mhac.teams.id')))
    away_team = db.Column(UUID(as_uuid=True, db.ForeignKey('mhac.teams.id')))
    home_score = db.Column(db.String(3))
    away_score = db.Column(db.String(3))
    game_date = db.Column(db.DateTime)
    season = db.Column(UUID(as_uuid=True, db.ForeignKey('mhac.seasons.id')))
    neutral_site = db.Column(db.Boolean)


