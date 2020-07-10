import requests
import json
import pandas as pd



url = "https://api-football-v1.p.rapidapi.com/v2/"

headers = {
    'x-rapidapi-host': "api-football-v1.p.rapidapi.com",
    'x-rapidapi-key': "9009a233fbmsh256544d3494b770p1f94cbjsnd73ca9a54738"
}

## response = requests.request("GET", url, headers=headers)
def exec(request):
    return requests.request("GET", url + request, headers=headers)

def getTeamStatsGoal(leagueId, teamid):
    return exec("statistics/" + str(leagueId) + "/" + str(teamid))

def getShortNameByApiId(idTeam):
    response = getTeamStatsGoal(idTeam).json()["api"]["teams"][0]["code"]
    if response is None:
        response = str(idTeam)
    return response

def getTeamStatsGoal(idTeam):
    return exec("teams/team/{}/".format(str(idTeam)))

def getTwoTeamsFeatures(home_team_id, away_team_id):
    request = "fixtures/h2h/"+ str(home_team_id) +"/" + str(away_team_id)
    return exec(request)

def getFixturesByLeagueId(leagueid):
    request = "fixtures/league/" + str(leagueid)
    return exec(request)

def getAllLigues():
    request = "leagues"
    return exec(request)

def getPredictByFixture(FixtureId):
    request = "predictions/" + str(FixtureId)
    return exec(request)

def getLastFixtureIdBetweenTwoTeam(homeid, awayid):
    predict = getTwoTeamsFeatures(homeid, awayid)
    predict_json = json.loads(predict.content)
    fixture_json = predict_json["api"]['fixtures']

    allFixtures = pd.DataFrame(eval(str(fixture_json)))

    allFixtures = allFixtures.sort_values(by=['event_timestamp'], ascending=False)

    allFixtures = allFixtures[allFixtures['event_timestamp'] == allFixtures['event_timestamp'].max()]

    return allFixtures["fixture_id"].values[0]


def getPredictionBetweenTwoTeams(homeid, awayid):
    fixtureId = getLastFixtureIdBetweenTwoTeam(33, 34)
    result = getPredictByFixture(fixtureId)
    return json.loads(result.content)

class winning_percent:
    def __init__(self, home, away, draws):
        self.home = home
        self.away = away
        self.draws = draws

class Predict:
  def __init__(self, percent_winning):
    self.percent_winning = percent_winning

def predictFromTeamIds(home_team_id, away_team_id, idRequest):
    result = getPredictionBetweenTwoTeams(home_team_id,away_team_id)
    predictions = result["api"]['predictions'][0]

    percent_winning = predictions['winning_percent']
    percent_winning = winning_percent(percent_winning['home'], percent_winning['away'], percent_winning['draws'])

    PredictResult = json.dumps(percent_winning.__dict__)

    thisdict = '{"percent_winning": ' + PredictResult + ', "id": "' + idRequest

    return thisdict


class Team:
  def __init__(self, ApiId, ShortName):
    self.ApiId = ApiId
    self.ShortName = ShortName

def teamAPIIdToShortName(list):
    shortNameList = []
    for i in list:
        name = getShortNameByApiId(str(i))
        if name is None:
            name = str(i)
        team = Team(str(i), name)
        shortNameList.append(team)

    return shortNameList

