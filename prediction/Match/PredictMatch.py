from prediction.env import *


def initViews():
    cur.execute(VIEW_HOME)
    cur.execute(VIEW_AWAY)

def buildSelectPlayer():
    index = 0
    index2 = 0
    retour = ""
    VIRGULE = ""
    for playerIdColumns in match_players_colums:
        index += 1
        for playerCol in player_columns:
            index2 += 1
            retour += VIRGULE + " p" + str(index) + "." + playerCol
            VIRGULE = ","
        retour += ", p"+ str(index) +".jd as jd" + str(index)
    return retour

def buildInnerJoinPlayer():
    index = 0
    retour = ""
    for playerIdColumns in match_players_colums:
        index += 1
        retour += " INNER JOIN 'FinalPlayer' p" + str(index)
        retour += " ON m."+ playerIdColumns +" = p" + str(index) + ".player_api_id"
    return retour


def matchPlayerNotNull():
    index = 0
    request = ""
    for player_id in match_players_colums:
        index += 1
        if index != 1:
            request += "AND "
        request += player_id + " IS NOT NULL "
    return request

import random
def lastMatchRequest(idHome, idAway):
    SELECT = "SELECT strftime('%Y-%m-%d %H:%M:%S','now') as date, "
    SELECT += "mh." + ", mh.".join(home_players_colums)
    SELECT += ", ma." + ", ma.".join(away_players_colums)
    FROM = " FROM home_last_game as mh inner join away_last_game as ma where mh.home_team_api_id = {} and ma.away_team_api_id = {}".format(idHome, idAway)
    return SELECT + FROM

def getDbApiIdFromShortname(ShortName):
    sqlRequest = "SELECT team_api_id FROM 'Team' WHERE team_short_name LIKE '%" + ShortName + "%' LIMIT 0,1"
    AllMatch = pd.read_sql_query(sqlRequest, cnx)
    retour = None
    if len(AllMatch) == 1:
        retour = AllMatch["team_api_id"].values[0]
    return retour

def buildFullRequest(homeId, awayId):
    SELECT_REQUEST = "SELECT " + buildSelectPlayer()
    FROM_REQUESTS = " FROM (" + lastMatchRequest(homeId, awayId) + ") m " + buildInnerJoinPlayer()
    return SELECT_REQUEST + FROM_REQUESTS

def IAComportement(homeId, awayId):
    FULL_REQUEST = buildFullRequest(homeId, awayId)
    AllMatch = pd.read_sql_query(FULL_REQUEST, cnx)
    X_test_scaled = scaler.transform(AllMatch)
    return model.predict(X_test_scaled)[0]

def rbComportement(home_id, away_id):
    response = ""


    AllMatch = pd.read_sql_query(RB_REQUEST_SELECT.format(str(home_id), str(away_id)), cnx)

    if(len(AllMatch) > 0):
        return [AllMatch['home_goal'].iloc[0], AllMatch['away_goal'].iloc[0]]

    home_response = random.uniform(0, 3)
    away_response = random.uniform(0, 3)

    cur.execute(RB_REQUEST_INSERT.format(home_id, away_id, home_response, away_response))

    return [home_response, away_response]

def predictionBetweenTwoTeams(ShortNameHomeTeam, ShortNameAwayTeam):
    home_id = getDbApiIdFromShortname(ShortNameHomeTeam)
    away_id = getDbApiIdFromShortname(ShortNameAwayTeam)

    if home_id is None or away_id is None :
        if home_id is None:
            home_id = ShortNameHomeTeam
        if away_id is None:
            away_id = ShortNameAwayTeam

        return rbComportement(home_id, away_id)
    try:
        return IAComportement(home_id, away_id)
    except:
        return rbComportement(home_id, away_id)

def PredictTournament(ShortNameList):
    responses = {}
    for m1 in ShortNameList:
        valueM1 = m1.ShortName
        count = 0
        for m2 in ShortNameList:
            valueM2 = m2.ShortName
            if valueM1 != valueM2:
                resultPipelines = predictionBetweenTwoTeams(valueM1, valueM2)
                count += resultPipelines[0] - resultPipelines[1]
        responses[m1.ApiId] = count

    return {k: v for k, v in sorted(responses.items(), key=lambda item: item[1], reverse=True)}

