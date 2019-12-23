import math

def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d

def calcWinPercentage(wins, losses):
    return wins/(wins+losses)

def totalPoints(twos=0, threes=0, free_throws=0):
    return (twos *2) + (threes * 3) + (free_throws * 1)

def calcGamesBehind(leader, wins, losses):
    #return  -(leader['wins']+losses)/2 + math.sqrt(((leader['wins'] + losses)*(leader['wins'] + losses)) - (4 * leader['wins']*losses) + ((4*wins * leader['losses'])/2))
    return round((((leader['wins']-leader['losses'])-(wins-losses))/2),2)


