import math

def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d

def calcWinPercentage(wins, losses):
    return wins/(wins+losses)

def totalPoints(twos=0, threes=0, free_throws=0):
    points = (int(twos) *2) + (int(threes) * 3) + (int(free_throws) * 1)

    return points

def calcGamesBehind(leader, wins, losses):
    #return  -(leader['wins']+losses)/2 + math.sqrt(((leader['wins'] + losses)*(leader['wins'] + losses)) - (4 * leader['wins']*losses) + ((4*wins * leader['losses'])/2))
    return round((((leader['wins']-leader['losses'])-(wins-losses))/2),2)


games = [
        {
          'game': '1',
          'date': 'February 6th',
          'time': '10:00 am',
          'matchup': {
            'team1': 'Chattanooga Patriots',
            'scoreTeam1': '17',
            'team2': 'Tennessee Heat',
            'scoreTeam2': '36'
          },
          'location': {
            'address': '106 Bluegrass Commons Blvd, Hendersonville, TN 37075',
            'name': 'First Baptist Church'
          },
          'level': '14U Boys'
        },
        {
          'game': '2',
          'date': 'February 6th',
          'time': '11:00 am',
          'matchup': {
            'team1': 'Covenant Christian Academy',
            'scoreTeam1': '23',
            'team2': 'Nashville Warriors',
            'scoreTeam2': '49'
          },
          'location': {
            'address': '106 Bluegrass Commons Blvd, Hendersonville, TN 37075',
            'name': 'First Baptist Church'
          },
          'level': '14U Boys'
        },
        {
          'game': '3',
          'date': 'February 6th',
          'time': '12:00 pm',
          'matchup': {
            'team1': 'Hendersonville Royals',
            'scoreTeam1': '35',
            'team2': 'Daniel 1 Academy',
            'scoreTeam2': '52'
          },
          'location': {
            'address': '106 Bluegrass Commons Blvd, Hendersonville, TN 37075',
            'name': 'First Baptist Church'
          },
          'level': '14U Boys'
        },
        {
          'game': '4',
          'date': 'February 6th',
          'time': '1:00 pm',
          'matchup': {
            'team1': 'Life Christian Academy',
            'scoreTeam1': '24',
            'team2': 'Western Kentucky Trailblazers',
            'scoreTeam2': '68'
          },
          'location': {
            'address': '106 Bluegrass Commons Blvd, Hendersonville, TN 37075',
            'name': 'First Baptist Church'
          },
          'level': '14U Boys'
        },
        {
          'game': '5',
          'date': 'February 6th',
          'time': '8:00 am',
          'matchup': {
            'team1': 'Nashville Warriors',
            'scoreTeam1': '33',
            'team2': 'Chattanooga Patriots',
            'scoreTeam2': '53'
          },
          'location': {
            'address': '1045 Bison Trail, Gallatin, TN 37066',
            'name': 'Welch College Gym'
          },
          'level': '18U Boys'
        },
        {
          'game': '6',
          'date': 'February 6th',
          'time': '9:30 am',
          'matchup': {
            'team1': 'Tennessee Heat',
            'scoreTeam1': '53',
            'team2': 'Hendersonville Royals',
            'scoreTeam2': '55'
          },
          'location': {
            'address': '1045 Bison Trail, Gallatin, TN 37066',
            'name': 'Welch College Gym'
          },
          'level': '18U Boys'
        },
        {
          'game': '7',
          'date': 'February 6th',
          'time': '11:00 am',
          'matchup': {
            'team1': 'Covenant Christian Academy',
            'scoreTeam1': '40',
            'team2': 'Western Kentucky Trailblazers',
            'scoreTeam2': '50'
          },
          'location': {
            'address': '1045 Bison Trail, Gallatin, TN 37066',
            'name': 'Welch College Gym'
          },
          'level': '18U Boys'
        },
        {
          'game': '8',
          'date': 'February 6th',
          'time': '12:30 pm',
          'matchup': {
            'team1': 'Daniel 1 Academy',
            'scoreTeam1': '29',
            'team2': 'Life Christian Academy',
            'scoreTeam2': '60'
          },
          'location': {
            'address': '1045 Bison Trail, Gallatin, TN 37066',
            'name': 'Welch College Gym'
          },
          'level': '18U Boys'
        },
        {
          'game': '9',
          'date': 'February 6th',
          'time': '2:00 pm',
          'matchup': {
            'team1': 'Daniel 1 Academy',
            'scoreTeam1': '55',
            'team2': 'Hendersonville Royals',
            'scoreTeam2': '47'
          },
          'location': {
            'address': '1045 Bison Trail, Gallatin, TN 37066',
            'name': 'Welch College Gym'
          },
          'level': '16U Boys'
        },
        {
          'game': '10',
          'date': 'February 6th',
          'time': '3:00 pm',
          'matchup': {
            'team1': 'Covenant Christian Academy',
            'scoreTeam1': '41',
            'team2': 'Tennessee Heat',
            'scoreTeam2': '43'
          },
          'location': {
            'address': '1045 Bison Trail, Gallatin, TN 37066',
            'name': 'Welch College Gym'
          },
          'level': '16U Boys'
        },
        {
          'game': '11',
          'date': 'February 6th',
          'time': '4:00 pm',
          'matchup': {
            'team1': 'Life Christian Academy',
            'scoreTeam1': '25',
            'team2': 'Chattanooga Patriots',
            'scoreTeam2': '47'
          },
          'location': {
            'address': '1045 Bison Trail, Gallatin, TN 37066',
            'name': 'Welch College Gym'
          },
          'level': '16U Boys'
        },
        {
          'game': '12',
          'date': 'February 6th',
          'time': '12:30 pm',
          'matchup': {
            'team1': 'Western Kentucky Trailblazers',
            'scoreTeam1': '1',
            'team2': 'Bye',
            'scoreTeam2': '0'
          },
          'location': {
            'address': '1045 Bison Trail, Gallatin, TN 37066',
            'name': 'Welch College Gym'
          },
          'level': '16U Boys'
        },

        {
          'game': '13',
          'date': 'February 7th',
          'time': '8:00 am',
          'matchup': {
            'team1': 'Covenant Christian Academy',
            'scoreTeam1': '24',
            'team2': 'Hendersonville Royals',
            'scoreTeam2': '25'
          },
          'location': {
            'address': '1045 Bison Trail, Gallatin, TN 37066',
            'name': 'Welch College Gym'
          },
          'level': '14U Boys'
        },
        {
          'game': '14',
          'date': 'February 7th',
          'time': '9:00 am',
          'matchup': {
            'team1': 'Chattanooga Patriots',
            'scoreTeam1': '41',
            'team2': 'Life Christian Academy',
            'scoreTeam2': '22'
          },
          'location': {
            'address': '1045 Bison Trail, Gallatin, TN 37066',
            'name': 'Welch College Gym'
          },
          'level': '14U Boys'
        },
        {
          'game': '15',
          'date': 'February 7th',
          'time': '10:00 am',
          'matchup': {
            'team1': 'Nashville Warriors',
            'scoreTeam1': '44',
            'team2': 'Daniel 1 Academy',
            'scoreTeam2': '38'
          },
          'location': {
            'address': '1045 Bison Trail, Gallatin, TN 37066',
            'name': 'Welch College Gym'
          },
          'level': '14U Boys'
        },
        {
          'game': '16',
          'date': 'February 7th',
          'time': '11:00 am',
          'matchup': {
            'team1': 'Tennessee Heat',
            'scoreTeam1': '27',
            'team2': 'Western Kentucky Trailblazers',
            'scoreTeam2': '44'
          },
          'location': {
            'address': '1045 Bison Trail, Gallatin, TN 37066',
            'name': 'Welch College Gym'
          },
          'level': '14U Boys'
        },
        {
          'game': '17',
          'date': 'February 7th',
          'time': '12:00 pm',
          'matchup': {
            'team1': 'Tennessee Heat',
            'scoreTeam1': '41',
            'team2': 'Chattanooga Patriots',
            'scoreTeam2': '33'
          },
          'location': {
            'address': '1045 Bison Trail, Gallatin, TN 37066',
            'name': 'Welch College Gym'
          },
          'level': '16U Boys'
        },
        {
          'game': '18',
          'date': 'February 7th',
          'time': '1:00 pm',
          'matchup': {
            'team1': 'Daniel 1 Academy',
            'scoreTeam1': '36',
            'team2': 'Western Kentucky',
            'scoreTeam2': '48'
          },
          'location': {
            'address': '1045 Bison Trail, Gallatin, TN 37066',
            'name': 'Welch College Gym'
          },
          'level': '16U Boys'
        },
        {
          'game': '19',
          'date': 'February 7th',
          'time': '2:00 pm',
          'matchup': {
            'team1': 'Covenant Christian Academy',
            'scoreTeam1': '',
            'team2': ' Nashville Warriors',
            'scoreTeam2': ''
          },
          'location': {
            'address': '1045 Bison Trail, Gallatin, TN 37066',
            'name': 'Welch College Gym'
          },
          'level': '18U Girls'
        },
        {
          'game': '20',
          'date': 'February 7th',
          'time': '3:30 pm',
          'matchup': {
            'team1': 'Daniel 1 Academy',
            'scoreTeam1': '',
            'team2': 'Chatanooga Patriots',
            'scoreTeam2': ''
          },
          'location': {
            'address': '1045 Bison Trail, Gallatin, TN 37066',
            'name': 'Welch College Gym'
          },
          'level': '18U Girls'
        },
        {
          'game': '21',
          'date': 'February 7th',
          'time': '5:00 pm',
          'matchup': {
            'team1': 'Tennessee Heat',
            'scoreTeam1': '',
            'team2': 'Covenant Christian Academy',
            'scoreTeam2': ''
          },
          'location': {
            'address': '1045 Bison Trail, Gallatin, TN 37066',
            'name': 'Welch College Gym'
          },
          'level': '18U Boys'
        },
        {
          'game': '22',
          'date': 'February 7th',
          'time': '6:30 pm',
          'matchup': {
            'team1': 'Daniel 1 Academy',
            'scoreTeam1': '',
            'team2': 'Nashville Warriors',
            'scoreTeam2': ''
          },
          'location': {
            'address': '1045 Bison Trail, Gallatin, TN 37066',
            'name': 'Welch College Gym'
          },
          'level': '18U Boys'
        },
        {
          'game': '23',
          'date': 'February 7th',
          'time': '8:00 pm',
          'matchup': {
            'team1': 'Hendersonville Royals',
            'scoreTeam1': '',
            'team2': 'Western Kentucky Trailblazers',
            'scoreTeam2': ''
          },
          'location': {
            'address': '1045 Bison Trail, Gallatin, TN 37066',
            'name': 'Welch College Gym'
          },
          'level': '18U Boys'
        },
        {
          'game': '24',
          'date': 'February 7th',
          'time': '9:30 pm',
          'matchup': {
            'team1': 'Chattanooga Patriots',
            'scoreTeam1': '',
            'team2': 'Life Christian Academy',
            'scoreTeam2': ''
          },
          'location': {
            'address': '1045 Bison Trail, Gallatin, TN 37066',
            'name': 'Welch College Gym'
          },
          'level': '18U Boys'
        },
        {
          'game': '25',
          'date': 'February 8th',
          'time': '8:00 am',
          'matchup': {
            'team1': 'Covenant Christian Academy',
            'scoreTeam1': '',
            'team2': 'Life Christian Academy',
            'scoreTeam2': ''
          },
          'location': {
            'address': '1045 Bison Trail, Gallatin, TN 37066',
            'name': 'Welch College Gym'
          },
          'level': '16U Boys'
        },
        {
          'game': '26',
          'date': 'February 8th',
          'time': '9:00 am',
          'matchup': {
            'team1': 'Loser Game 19',
            'scoreTeam1': '',
            'team2': 'Loser Game 20',
            'scoreTeam2': ''
          },
          'location': {
            'address': '1045 Bison Trail, Gallatin, TN 37066',
            'name': 'Welch College Gym'
          },
          'level': '18U Girls'
        },
        {
          'game': '27',
          'date': 'February 8th',
          'time': '10:00 am',
          'matchup': {
            'team1': 'Daniel 1 Academy',
            'scoreTeam1': '',
            'team2': 'Winner Game 25',
            'scoreTeam2': ''
          },
          'location': {
            'address': '1045 Bison Trail, Gallatin, TN 37066',
            'name': 'Welch College Gym'
          },
          'level': '16U Boys'
        },
        {
          'game': '28',
          'date': 'February 8th',
          'time': '12:00 pm',
          'matchup': {
            'team1': 'Nashville Warriors',
            'scoreTeam1': '',
            'team2': 'Western Kentucky Trailblazers',
            'scoreTeam2': ''
          },
          'location': {
            'address': '1045 Bison Trail, Gallatin, TN 37066',
            'name': 'Welch College Gym'
          },
          'level': '14U Boys'
        },
        {
          'game': '29',
          'date': 'February 8th',
          'time': '2:00 pm',
          'matchup': {
            'team1': 'Tennessee Heat',
            'scoreTeam1': '',
            'team2': 'Western Kentucky',
            'scoreTeam2': ''
          },
          'location': {
            'address': '1045 Bison Trail, Gallatin, TN 37066',
            'name': 'Welch College Gym'
          },
          'level': '16U Boys'
        },
        {
          'game': '30',
          'date': 'February 8th',
          'time': '4:00 pm',
          'matchup': {
            'team1': 'Winner Game 19',
            'scoreTeam1': '',
            'team2': 'Winner Game 20',
            'scoreTeam2': ''
          },
          'location': {
            'address': '1045 Bison Trail, Gallatin, TN 37066',
            'name': 'Welch College Gym'
          },
          'level': '18U Girls'
        },
        {
          'game': '31',
          'date': 'February 8th',
          'time': '6:00 pm',
          'matchup': {
            'team1': 'Winner Game 23',
            'scoreTeam1': '',
            'team2': 'Winner Game 24',
            'scoreTeam2': ''
          },
          'location': {
            'address': '1045 Bison Trail, Gallatin, TN 37066',
            'name': 'Welch College Gym'
          },
          'level': '18U Boys'
        }
]
