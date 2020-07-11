import pika, os

from apiRequest.main import *
from prediction.Match.PredictMatch import *
from prediction.Tournament import *


# Access the CLODUAMQP_URL environment variable and parse it (fallback to localhost)
url = os.environ.get('CLOUDAMQP_URL', 'amqp://migmnpgf:D0y8DZ6E25ziu6A4Aa3igR9UxdBZjBGT@squid.rmq.cloudamqp.com/migmnpgf')
params = pika.URLParameters(url)
connection = pika.BlockingConnection(params)
channel = connection.channel() # start a channel

def postPredictMatchResponse(result):
    print(result)
    channel.queue_declare(queue='predict_match_response')  # Declare a queue
    channel.basic_publish(exchange='',
                          routing_key='predict_match_response',
                          body=result)

def postPredictTournamentResponse(result):
    print(result)
    channel.queue_declare(queue='predict_tournament_response')  # Declare a queue
    channel.basic_publish(exchange='',
                          routing_key='predict_tournament_response',
                          body=result)

def jsonL(request_json):

    request_json["home_name"] = getShortNameByApiId(request_json['home_id'])
    request_json["away_name"] = getShortNameByApiId(request_json['away_id'])

    if request_json["home_name"] is None:
        request_json["home_name"] = request_json["home_id"]

    if request_json["away_name"] is None:
        request_json["away_name"] = request_json["away_id"]

    return request_json

def requesToResponse(request):
    response_json = None
    print(request)
    try:
        request_json = jsonL(json.loads(request))
        response = predictFromTeamIds(request_json['home_id'], request_json['away_id'], request_json['id'])
        predictionIA = predictionBetweenTwoTeams(request_json["home_name"], request_json["away_name"])
        responseString = ", 'home_goal_prediction':'{}', 'away_goal_prediction':'{}'".format(predictionIA.item(0), predictionIA.item(1))
        response_json = response + responseString + "}"
        postPredictMatchResponse(response_json)
    except KeyError as e:
        print(e)
        print("key error")
        response_json = "Error"
    except:
        response_json = "Error"
    return response_json


def callback(ch, method, properties, body):
    print(body)

def predictMatchCallBack(ch, method, properties, body):
    print(body)
    requesToResponse(body)

def predictTournamentCallBack(ch, method, properties, body):
    response = None
    try:
        request = json.loads(body)
        shortNameList = teamAPIIdToShortName(request["id_team_list"])
        response = PredictTournament(shortNameList)
        response = '"id": "{}", "response" : {}'.format(str(request["id"]), str(response))
        response = "{" + response + "}"
    except ValueError:
        response = str(ValueError)
    postPredictTournamentResponse(response)



initViews()

print("serveur chargé")

channel.queue_declare(queue='predict_match')
channel.queue_declare(queue='predict_match')
channel.queue_declare(queue='predict_tournament')
channel.queue_declare(queue='hi')

channel.basic_consume(queue="hi", on_message_callback=callback, auto_ack=True)
channel.basic_consume(queue="predict_match", on_message_callback=predictMatchCallBack, auto_ack=True)
channel.basic_consume(queue="predict_tournament", on_message_callback=predictTournamentCallBack, auto_ack=True)

channel.start_consuming()