from app import db
import models


def addSeasonTeam(levels, team_id, season_id):
    ids=[]
    for level in levels:
        st = models.SeasonTeams(season_id=season_id, team_id=team_id, level_id=level.id)
        db.session.add(st)
        db.session.commit()
        ids.append(st.id)
    return ids

def addPlayers(players, seasonTeam=None):

    for player in players:
        p = models.Persons(**player)
        db.session.add(p)
        db.session.commit()
        if seasonTeam:
            r = models.TeamRoster(
                        season_team_id=seasonTeam.id, player_id=p.id)
            db.session.add(r)
            db.session.commit()


def run():
    #Seed the validation data
    sport = models.Sport(sport_name='Basketball')
    db.session.add(sport)
    db.session.commit()


    pt = models.PersonType(type='Player')
    db.session.add(pt)
    db.session.commit()

    pt = models.PersonType(type='Coach')
    db.session.add(pt)
    db.session.commit()

    season = models.Season(name='2019-2020 Fall', year='2019',
                        sport_id=sport.id, start_date='2019-11-01', roster_submission_deadline='2019-11-01')
    db.session.add(season)
    db.session.commit()


    levels = ['18U Boys', '18U Girls', '16U Boys', '16U Girls', '14U Boys', '14U Girls']
    for l in levels:
        level = models.Level(level_name=l)
        db.session.add(level)
        db.session.commit()

    levels = models.Level.query.all()

    #Create a user
    user = models.User(email='matthew.robison@outlook.com',
                    password='Devilrays1', admin=True)
    db.session.add(user)
    db.session.commit()

    # Patriots
    a = models.Address(name='First Church of the Nazarene', address_line_1='5455 North Terrace', city='Chattanooga', state='TN', postal_code='37411')
    db.session.add(a)
    db.session.commit()
    t = models.Teams(team_name='Chattanooga', team_mascot='Patriots', address_id=a.id)
    db.session.add(t)
    db.session.commit()

    csthea = addSeasonTeam(levels, t.id, season.id)


    players = { '18U Girls': [
                    {'first_name': 'Sharayah', 'last_name': 'Daves', 'number': '1', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Morgan', 'last_name': 'Sliger','number': '21', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Megan', 'last_name': 'Meyer',                     'number': '14', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Gretta', 'last_name': 'Pitts',                  'number': '2', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Tori', 'last_name': 'Hall',                  'number': '22', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Raylee', 'last_name': 'Evans',                  'number': '32', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Sydney', 'last_name': 'Petty',                  'number': '13', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Emmaline', 'last_name': 'Carlisle',                  'number': '24', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Gabriella', 'last_name': 'Grundy',                  'number': '31', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Shanel', 'last_name': 'Daves',                  'number': '23', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Moriah', 'last_name': 'Meyer',                  'number': '4', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Alyssa', 'last_name': 'Moore',                  'number': '5', 'team_id': t.id, 'person_type': 1},
                 ],
                 '18U Boys': [
                    {'first_name': 'Caden', 'last_name': 'Posey' ,'number': '11', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Nate', 'last_name': 'Birkhead' ,'number': '1', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Jacob', 'last_name': 'Wellwood' ,'number': '30', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Noah', 'last_name': 'Huffman' ,'number': '33', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Evan', 'last_name': 'Neel' ,'number': '2', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Josiah', 'last_name': 'Myaing' ,'number': '15', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Gavin', 'last_name': 'Calhoun' ,'number': '3', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Joel', 'last_name': 'Davis' ,'number': '5', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Garrett', 'last_name': 'Kramer' ,'number': '40', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Jonathan', 'last_name': 'Swanson' ,'number': '13', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Gabe', 'last_name': 'Teichroew' ,'number': '31', 'team_id': t.id, 'person_type': 1},
                 ],
                '16U Boys': [
                    {'first_name': 'Evan', 'last_name': 'Neel' ,'number': '2', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Josiah', 'last_name': 'Myaing' ,'number': '15', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Charlie', 'last_name': 'Sewell' ,'number': '10', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Gavin', 'last_name': 'Calhoun' ,'number': '3', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Joel', 'last_name': 'Davis' ,'number': '5', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Garrett', 'last_name': 'Kramer' ,'number': '40', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Isaiah', 'last_name': 'Harbin' ,'number': '22', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Jonathan', 'last_name': 'Swanson' ,'number': '13', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Sam', 'last_name': 'Khoury' ,'number': '44', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Gabe', 'last_name': 'Teichroew' ,'number': '31', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Logan', 'last_name': 'Thompson' ,'number': '23', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Jayden', 'last_name': 'Hall' ,'number': '32', 'team_id': t.id, 'person_type': 1},

                ],
                '14U Boys': [
                    {'first_name': 'Shaw', 'last_name': 'Daves' ,'number': '1', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Maguire', 'last_name': 'Evans' ,'number': '32', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Andrew', 'last_name': 'Amor' ,'number': '23', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Jayden', 'last_name': 'Estrada' ,'number': '24', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Donovan', 'last_name': 'Jenkins' ,'number': '13', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Braden', 'last_name': 'Calton' ,'number': '20', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Macrae', 'last_name': 'Sims' ,'number': '35', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Wisly', 'last_name': 'Johnson' ,'number': '3', 'team_id': t.id, 'person_type': 1},
                    {'first_name': 'Aiden', 'last_name': 'Nakamine' ,'number': '5', 'team_id': t.id, 'person_type': 1},
                ]
    }

    for key, value in players.items():
        level = models.Level.query.filter(
            models.Level.level_name == key).first()
        seasonTeam = db.session.query(models.SeasonTeams).filter(models.SeasonTeams.level_id == level.id,
                                                                     models.SeasonTeams.season_id == season.id, models.SeasonTeams.team_id == t.id).first()
        addPlayers(players=value, seasonTeam=seasonTeam)

    # Western Ky
    a = models.Address(name='Oakland Baptist Church', address_line_1='410 Church St', city='Oakland', state='KY', postal_code='42159')
    try:
        db.session.add(a)
        db.session.commit()
    except Exception as exc:
        print(str(exc))
    t = models.Teams(team_name='Western Kentucky',
                    team_mascot='Trailblazers', address_id=a.id)
    db.session.add(t)
    db.session.commit()

    addSeasonTeam(levels, t.id, season.id)

    # Royals
    a = models.Address(name='Madison Church of Christ', address_line_1='106 Gallatin Pike N', city='Madison', state='TN', postal_code='37115')
    db.session.add(a)
    db.session.commit()
    t = t = models.Teams(team_name='Hendersonville', team_mascot='Royals', address_id=a.id, website='https://hendersonvilleroyals.com')
    db.session.add(t)
    db.session.commit()

    players = [
        {'first_name': 'Sanders', 'last_name': 'McMurty',
            'team_id': t.id, 'person_type': 1},
        {'first_name': 'Logan', 'last_name': 'Goins',
            'team_id': t.id, 'person_type': 1},
        {'first_name': 'Jayden', 'last_name': 'Hillis',
            'team_id': t.id, 'person_type': 1},
        {'first_name': 'Keaton', 'last_name': 'Sadler',
            'team_id': t.id, 'person_type': 1},
        {'first_name': 'Luke', 'last_name': 'Vierkantz',
            'team_id': t.id, 'person_type': 1},
        {'first_name': 'Wes', 'last_name': 'Luisi ',
            'team_id': t.id, 'person_type': 1},
        {'first_name': 'Toren', 'last_name': 'Gilbert ',
            'team_id': t.id, 'person_type': 1},
        {'first_name': 'Preston', 'last_name': 'Burkeen ',
            'team_id': t.id, 'person_type': 1},
        {'first_name': 'Jack', 'last_name': 'Pierce',
            'team_id': t.id, 'person_type': 1},
        {'first_name': 'Wes', 'last_name': 'Luisi',
            'team_id': t.id, 'person_type': 1},
        {'first_name': 'Toren', 'last_name': 'Gilbert',
            'team_id': t.id, 'person_type': 1},
        {'first_name': 'Preston', 'last_name': 'Burkeen',
            'team_id': t.id, 'person_type': 1},
        {'first_name': 'Silas', 'last_name': 'Kingsbury',
            'team_id': t.id, 'person_type': 1},
        {'first_name': 'Jace', 'last_name': 'Mortimer',
            'team_id': t.id, 'person_type': 1},
        {'first_name': 'Hudson', 'last_name': 'Mortimer',
            'team_id': t.id, 'person_type': 1},
        {'first_name': 'Canyon', 'last_name': 'Gilbert',
            'team_id': t.id, 'person_type': 1},
        {'first_name': 'Ellis', 'last_name': 'Bass',
            'team_id': t.id, 'person_type': 1},
        {'first_name': 'Carson', 'last_name': 'Harris ',
            'team_id': t.id, 'person_type': 1},
        {'first_name': 'Kris', 'last_name': 'Ware ',
            'team_id': t.id, 'person_type': 1},
        {'first_name': 'Christian', 'last_name': 'Luisi',
            'team_id': t.id, 'person_type': 1},
        {'first_name': 'Harrison', 'last_name': 'Burkeen',
            'team_id': t.id, 'person_type': 1},
        {'first_name': 'Owen', 'last_name': 'Bass',
            'team_id': t.id, 'person_type': 1},
        {'first_name': 'Jude', 'last_name': 'Kimmel',
            'team_id': t.id, 'person_type': 1},
        {'first_name': 'Silas', 'last_name': 'Kingsbury ',
            'team_id': t.id, 'person_type': 1},
            ]

    for player in players:
        p = models.Persons(**player)
        db.session.add(p)
        db.session.commit()

    addSeasonTeam(levels, t.id, season.id)

    # TN Heat
    a = models.Address(name='Smithson Craighead Academy', address_line_1='Neely\'s Bend Rd', city='Nashville', state='TN', postal_code='37115')
    db.session.add(a)
    db.session.commit()
    t = models.Teams(team_name='Tennessee', team_mascot='Heat', address_id=a.id)
    db.session.add(t)
    db.session.commit()

    addSeasonTeam(levels, t.id, season.id)

    # Daniel 1
    a = models.Address(name='', address_line_1='180 CC Camp Rd', city='Cookeville', state='TN', postal_code='')
    db.session.add(a)
    db.session.commit()
    t = models.Teams(team_name='Daniel 1 Academy', team_mascot='Lions', address_id=a.id)
    db.session.add(t)
    db.session.commit()

    addSeasonTeam(levels, t.id, season.id)

    # CCA
    a = models.Address(name='Friendship Baptist Church', address_line_1='3217 Village Dr SW', city='Huntsville', state='AL', postal_code='35805')
    db.session.add(a)
    db.session.commit()
    t = models.Teams(team_name='Covenant Christian Academy', team_mascot='', address_id=a.id)
    db.session.add(t)
    db.session.commit()

    players = [
        {'first_name': 'Aidan', 'last_name': 'Sorrells' ,'number': '10', 'team_id': t.id, 'person_type': 1},
        {'first_name': 'Eli', 'last_name': 'Huskey' ,'number': '15', 'team_id': t.id, 'person_type': 1},
        {'first_name': 'Jacob', 'last_name': 'Walter' ,'number': '5', 'team_id': t.id, 'person_type': 1},
        {'first_name': 'Jason', 'last_name': 'Blakeley' ,'number': '43', 'team_id': t.id, 'person_type': 1},
        {'first_name': 'Lucian', 'last_name': 'Borchers' ,'number': '11', 'team_id': t.id, 'person_type': 1},
        {'first_name': 'Kai', 'last_name': 'Parsons' ,'number': '52', 'team_id': t.id, 'person_type': 1},
        {'first_name': 'Levi', 'last_name': 'Carter' ,'number': '20', 'team_id': t.id, 'person_type': 1},
        {'first_name': 'Lincoln', 'last_name': 'Turney' ,'number': '1', 'team_id': t.id, 'person_type': 1},
        {'first_name': 'Aiden', 'last_name': 'Vanderberg' ,'number': '45', 'team_id': t.id, 'person_type': 1},
        {'first_name': 'Landon', 'last_name': 'Burnette' ,'number': '30', 'team_id': t.id, 'person_type': 1},
        {'first_name': 'Luca', 'last_name': 'Basurovic' ,'number': '42', 'team_id': t.id, 'person_type': 1},
        {'first_name': 'Micah', 'last_name': 'Carter' ,'number': '54', 'team_id': t.id, 'person_type': 1},
        {'first_name': 'Hayden', 'last_name': 'Bobkowski' ,'number': '12', 'team_id': t.id, 'person_type': 1},
        {'first_name': 'Kenneth', 'last_name': 'McCormick' ,'number': '21', 'team_id': t.id, 'person_type': 1},
        {'first_name': 'Tyler', 'last_name': 'Schlapman' ,'number': '53', 'team_id': t.id, 'person_type': 1},
        {'first_name': 'Jalon', 'last_name': 'Jones' ,'number': '14', 'team_id': t.id, 'person_type': 1},
        {'first_name': 'Ben', 'last_name': 'Lewis' ,'number': '4', 'team_id': t.id, 'person_type': 1},
        {'first_name': 'Carter', 'last_name': 'Long' ,'number': '22', 'team_id': t.id, 'person_type': 1},
        {'first_name': 'Isaac', 'last_name': 'Carter' ,'number': '50', 'team_id': t.id, 'person_type': 1},
        {'first_name': 'Luke', 'last_name': 'Minor' ,'number': '44', 'team_id': t.id, 'person_type': 1},
        {'first_name': 'Nate', 'last_name': 'Turney' ,'number': '35', 'team_id': t.id, 'person_type': 1},
        {'first_name': 'Peyton', 'last_name': 'York' ,'number': '40', 'team_id': t.id, 'person_type': 1},
        {'first_name': 'Samuel', 'last_name': 'Hill' ,'number': '34', 'team_id': t.id, 'person_type': 1},
        {'first_name': 'Samuel', 'last_name': 'Borchers' ,'number': '51', 'team_id': t.id, 'person_type': 1},
        {'first_name': 'Ryan', 'last_name': 'Cagle' ,'number': '31', 'team_id': t.id, 'birth_date': ' 08/10/01',  'height': '5-10',  'person_type': 1},
        {'first_name': 'Dylan', 'last_name': 'Mai' ,'number': '2', 'team_id': t.id, 'birth_date': ' 07/06/01',  'height': '5-10',  'person_type': 1},
        {'first_name': 'Jalon', 'last_name': 'Jones' ,'number': '14', 'team_id': t.id, 'birth_date': ' 01/05/04',  'height': '5-10',  'person_type': 1},
        {'first_name': 'Ben', 'last_name': 'Lewis' ,'number': '4', 'team_id': t.id, 'birth_date': ' 12/30/02',  'height': '5-9',  'person_type': 1},
        {'first_name': 'Allen', 'last_name': 'Harman' ,'number': '3', 'team_id': t.id, 'birth_date': ' 07/29/02',  'height': '5-9',  'person_type': 1},
        {'first_name': 'Jonathan', 'last_name': 'Sillivant' ,'number': '41', 'team_id': t.id, 'birth_date': ' 02/04/01',  'height': '6-4',  'person_type': 1},
        {'first_name': 'Connor', 'last_name': 'Rigby' ,'number': '25', 'team_id': t.id, 'birth_date': ' 09/18/01',  'height': '6-0',  'person_type': 1},
        {'first_name': 'David', 'last_name': 'Lewis' ,'number': '13', 'team_id': t.id, 'birth_date': ' 02/24/01',  'height': '6-1',  'person_type': 1},
        {'first_name': 'Harley', 'last_name': 'McMahan' ,'number': '23', 'team_id': t.id, 'birth_date': ' 02/11/02',  'height': '6-0',  'person_type': 1},
        {'first_name': 'Ethan', 'last_name': 'Carter' ,'number': '0', 'team_id': t.id, 'birth_date': ' 07/27/02',  'height': '6-0',  'person_type': 1},
        {'first_name': 'Carson', 'last_name': 'Goode' ,'number': '24', 'team_id': t.id, 'birth_date': ' 10/07/02',  'height': '6-2',  'person_type': 1},
        {'first_name': 'Jack', 'last_name': 'Massengill' ,'number': '32', 'team_id': t.id, 'birth_date': ' 01/04/02',  'height': '6-6',  'person_type': 1},
        {'first_name': 'Jon-Wesley', 'last_name': 'Hill' ,'number': '55', 'team_id': t.id, 'birth_date': ' 02/05/01',  'height': '6-3',  'person_type': 1},
        {'first_name': 'David', 'last_name': 'Webster' ,'number': '33', 'team_id': t.id, 'birth_date': ' 07/04/02',  'height': '6-3',  'person_type': 1},
    ]
    for player in players:
        p = models.Persons(**player)
        db.session.add(p)
        db.session.commit()

    addSeasonTeam(levels, t.id, season.id)

    # LCA
    a = models.Address(name='Monrovia Community Center ', address_line_1='254 Allen Drake Dr', city='Huntsville', state='AL', postal_code='')
    db.session.add(a)
    db.session.commit()
    t = models.Teams(team_name='Life Christian Academy', team_mascot='Lions', address_id=a.id)
    db.session.add(t)
    db.session.commit()

    lca = addSeasonTeam(levels, t.id, season.id)

    # lca = t.id

    # NCC
    # models.Address(name='Oakland Baptist Church', address_line_1='410 Church St' city='Oakland', state='KY', postal_code='42159')
    # db.session.add(a)
    # db.session.commit()
    t = models.Teams(team_name='Nashville Central Christian',
                team_mascot='Warriors')
    db.session.add(t)
    db.session.commit()

    ncc = addSeasonTeam(levels, t.id, season.id)

    # ncc = t.id
    games = [[st, i] for st in lca for i in ncc]


    for g in games:
        game = models.Games(home_team_id=g[0], away_team_id=g[1])
        db.session.add(game)
        db.session.commit()
        game = models.Games(home_team_id=g[1], away_team_id=g[0])
        db.session.add(game)
        db.session.commit()



    # game = models.Games(home_team_id=lca, away_team_id=ncc)
    # db.session.add(game)
    # db.session.commit()

    # game = models.Games(home_team_id=ncc, away_team_id=ncc)
    # db.session.add(game)
    # db.session.commit()
