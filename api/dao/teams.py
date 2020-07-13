from sqlalchemy import Column, String
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Numeric

from sqlalchemy.sql import text # type: ignore
from typing import TypedDict, List, Dict, Any
from uuid import uuid4
from sqlalchemy.dialects.postgresql import JSON, UUID

from database import db

DB = db()

class Team(TypedDict):
    id: str 
    team_name: str
    team_mascot: str
    # address_id: address.address_id
    main_color: str
    secondary_color: str
    website: str
    logo_color: str
    logo_grey: str
    slug: str

def row_mapper(row) -> Team:
    Team = {
        'team_id': row['id'],
        'team_name': row['team_name'],
        'team_mascot': row['team_mascot'],
        'main_color': row['main_color'],
        'secondary_color': row['secondary_color'],
        'website': row['website'],
        'logo_color': row['logo_color'],
        'logo_grey': row['logo_grey'],
        'slug': row['slug']
    }
    return Team


def get(slug: str) -> Team:
    stmt = text('''SELECT * FROM mhac.season_teams_with_names WHERE slug = :slug''')

    stmt = stmt.bindparams(slug = slug)
    result = DB.execute(stmt)
    row = result.fetchone()
    result.close()
    if row is None:
        raise LookupError(f'Could not find key value with id: {id}')
    else:
        key = row_mapper(row)
        return key

def get_list() -> List[Team]:
    team_list = []
    stmt = text('''SELECT * FROM mhac.teams''')
    result = DB.execute(stmt)
    print(result)
    for row in result:
        print(row)
        team_list.append(row_mapper(row))
    
    return team_list



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