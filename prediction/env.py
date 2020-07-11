import sqlite3

from pickle import load
import pandas as pd
import numpy as np
import sklearn, os

from os import path
from google_drive_downloader import GoogleDriveDownloader as gdd

RESSOURCE_PATH = "./prediction/ressource/"

RB_REQUEST_SELECT = 'SELECT home_goal, away_goal FROM rbComportement WHERE id_home LIKE "%{}%" and id_away LIKE "%{}%" '
RB_REQUEST_INSERT = "INSERT INTO rbComportement (id_home, id_away, home_goal, away_goal) VALUES ('{}', '{}', {}, {})"

VIEW_HOME = "CREATE VIEW IF NOT EXISTS home_last_game AS SELECT * FROM 'Match' m GROUP BY home_team_api_id HAVING m.date = max(m.date)"
VIEW_AWAY = "CREATE VIEW IF NOT EXISTS away_last_game AS SELECT * FROM 'Match' m GROUP BY away_team_api_id HAVING m.date = max(m.date)"
VIEW_FINAL_PLAYER = "CREATE VIEW IF NOT EXISTS FinalPlayerView AS SELECT p.id as idp, p.player_api_id, p.birthday, pa.date as padate, height, weight, overall_rating, potential, preferred_foot, crossing, finishing, heading_accuracy, short_passing, volleys, dribbling, curve, free_kick_accuracy, long_passing, ball_control, acceleration, sprint_speed, agility, reactions, balance, shot_power, jumping, stamina, strength, long_shots, aggression, interceptions, positioning, vision, penalties, marking, standing_tackle, sliding_tackle, gk_diving, gk_handling, gk_kicking, gk_positioning, gk_reflexes FROM 'Player' p INNER JOIN 'Player_Attributes' pa on pa.player_api_id = p.player_api_id GROUP BY pa.player_api_id HAVING pa.date = max(pa.date)"
VIEW_FINAL_PLAYER_DELETE = "DROP VIEW IF EXISTS FinalPlayerView"

TABLE_FINAL_PLAYER = "CREATE TABLE IF NOT EXISTS FinalPlayer AS SELECT p.id as idp, p.player_api_id, p.birthday, pa.date as padate, height, weight, overall_rating, potential, preferred_foot, crossing, finishing, heading_accuracy, short_passing, volleys, dribbling, curve, free_kick_accuracy, long_passing, ball_control, acceleration, sprint_speed, agility, reactions, balance, shot_power, jumping, stamina, strength, long_shots, aggression, interceptions, positioning, vision, penalties, marking, standing_tackle, sliding_tackle, gk_diving, gk_handling, gk_kicking, gk_positioning, gk_reflexes, ((julianday(date('now')) - julianday(birthday)) / 365) as jd FROM 'Player' p INNER JOIN 'Player_Attributes' pa on pa.player_api_id = p.player_api_id GROUP BY pa.player_api_id HAVING pa.date = max(pa.date)"
TABLE_FINAL_PLAYER_DELETE = "DROP VIEW IF EXISTS FinalPlayer"

home_players_colums = ["home_player_1", "home_player_2", "home_player_3","home_player_4","home_player_5","home_player_6","home_player_7","home_player_8","home_player_9","home_player_10","home_player_11"]
away_players_colums = ["away_player_1","away_player_2","away_player_3","away_player_4","away_player_5","away_player_6","away_player_7","away_player_8","away_player_9","away_player_10","away_player_11"]

match_players_colums = home_players_colums + away_players_colums

player_columns = ['height', 'weight', 'overall_rating', 'potential', 'preferred_foot',
                                 'crossing', 'finishing',
                                   'heading_accuracy', 'short_passing', 'volleys', 'dribbling', 'curve',
                                   'free_kick_accuracy', 'long_passing', 'ball_control', 'acceleration', 'sprint_speed',
                                   'agility', 'reactions', 'balance', 'shot_power', 'jumping', 'stamina', 'strength',
                                   'long_shots', 'aggression', 'interceptions', 'positioning', 'vision', 'penalties',
                                   'marking', 'standing_tackle', 'sliding_tackle', 'gk_diving', 'gk_handling',
                                   'gk_kicking', 'gk_positioning', 'gk_reflexes']



REQUEST = "CREATE TABLE IF NOT EXISTS rbComportement (id_home TEXT NOT_NULL, id_away TEXT NOT NULL, home_goal REAL NOT NULL, away_goal REAL NOT NULL)"

def downloadSource():
    if not path.exists(RESSOURCE_PATH):
        os.mkdir(RESSOURCE_PATH)
        print("Download ./prediction/ressource/ File From google drive : ")
        gdd.download_file_from_google_drive(file_id='15exhYHdLNw_NBnbpv47edPzU53bq3edx',
                                            dest_path=RESSOURCE_PATH+'ressource.zip', unzip=True)
        os.remove(RESSOURCE_PATH+"/ressource.zip")

downloadSource()
cnx = sqlite3.connect(RESSOURCE_PATH + 'database.sql')

model = load(open(RESSOURCE_PATH + 'MLPModel.pkl', 'rb'))
scaler = load(open(RESSOURCE_PATH + 'MLPScaller.pkl', 'rb'))

cur = cnx.cursor()

cur.execute(REQUEST)
