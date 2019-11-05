from app import db
import models

# Patriots
a = models.Address(name='First Church of the Nazarene', address_line_1='5455 North Terrace', city='Chattanooga', state='TN', postal_code='37411')
db.session.add(a)
db.session.commit()
t = models.Teams(team_name='Chattanooga', team_mascot='Patriots', address_id=a.id)
db.session.add(t)
db.session.commit()

# Western Ky
a = models.Address(name='Oakland Baptist Church', address_line_1='410 Church St', city='Oakland', state='KY', postal_code='42159')
db.session.add(a)
db.session.commit()
models.Teams(team_name='Western Kentucky', team_mascot='Trailblazers', address_id=a.id)
db.session.add(t)
db.session.commit()

# Royals
a = models.Address(name='Madison Church of Christ', address_line_1='106 Gallatin Pike N', city='Madison', state='TN', postal_code='37115')
db.session.add(a)
db.session.commit()
models.Teams(team_name='Hendersonville', team_mascot='Royals', address_id=a.id, website='https://hendersonvilleroyals.com')
db.session.add(t)
db.session.commit()

# TN Heat
a = models.Address(name='Smithson Craighead Academy', address_line_1='Neely\'s Bend Rd', city='Nashville', state='TN', postal_code='37115')
db.session.add(a)
db.session.commit()
models.Teams(team_name='Tennessee', team_mascot='Heat', address_id=a.id)
db.session.add(t)
db.session.commit()

# Daniel 1
a = models.Address(name='', address_line_1='180 CC Camp Rd', city='Cookeville', state='TN', postal_code='')
db.session.add(a)
db.session.commit()
models.Teams(team_name='Daniel 1 Academy', team_mascot='Lions', address_id=a.id)
db.session.add(t)
db.session.commit()

# CCA
a = models.Address(name='Friendship Baptist Church', address_line_1='3217 Village Dr SW', city='Huntsville', state='AL', postal_code='35805')
db.session.add(a)
db.session.commit()
models.Teams(team_name='Covenant Christian Academy', team_mascot='', address_id=a.id)
db.session.add(t)
db.session.commit()

# LCA
a = models.Address(name='Monrovia Community Center ', address_line_1='254 Allen Drake Dr', city='Huntsville', state='AL', postal_code='')
db.session.add(a)
db.session.commit()
models.Teams(team_name='Life Christian Academy', team_mascot='Lions', address_id=a.id)
db.session.add(t)
db.session.commit()

# # Western Ky
# models.Address(name='Oakland Baptist Church', address_line_1='410 Church St' city='Oakland', state='KY', postal_code='42159')
# db.session.add(a)
# db.session.commit()
t = models.Teams(team_name='Nashville Central Christian',
             team_mascot='Warriors')
db.session.add(t)
db.session.commit()

sport = models.Sport(sport_name='Basketball')
db.session.add(sport)
db.session.commit()

l = models.Level(level_name='18U Boys')
db.session.add(l)
db.session.commit()

season = models.Season(name='2019-2020 Fall', year='2019', level_id=l.id, sport_id=sport.id, start_date='2019-11-01', roster_submission_deadline='2019-11-01')
db.session.add(season)
db.session.commit()

pt = models.PersonType(type='Player')
db.session.add(pt)
db.session.commit()

pt = models.PersonType(type='Coach')
db.session.add(pt)
db.session.commit()

