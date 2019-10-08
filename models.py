from app import db
from sqlalchemy.dialects.postgresql import JSON, UUID
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

    def __repr__(self):
        return '<id {}>'.format(self.id)

class Persons(db.Model):
    __tablename__ = 'person'
    __table_args__ = {"schema":"mhac"}

    id = db.Column(UUID(as_uuid=True), unique=True, nullable=False, primary_key=True)
    first_name= db.Column(db.String(100))
    last_name= db.Column(db.String(100))
    birth_date= db.Column(db.Date())
    height= db.Column(db.Integer)
    person_type= db.Column(db.Integer, db.ForeignKey('mhac.person_type.id'))
    team_id=db.Column(UUID(as_uuid=True), db.ForeignKey('mhac.teams.id'))

# class divisions(db.Model):
#     __tablename__ = 'divisions'
#     __table_args__ = ["schema":"mhac"]

#     id = db.Column()


