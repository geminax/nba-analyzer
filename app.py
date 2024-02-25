
import json
from basketball_reference_web_scraper import client
from basketball_reference_web_scraper.data import OutputType
from flask import Flask, render_template, redirect, url_for
import wtforms



# app = Flask(__name__)

# @app.route("/")
# def hello():
#     #registrationform = RegistrationForm()
#     reboundinput = wtforms.widgets.TextInput
#     return render_template('''
#         {{ reboundinput}}
#                            ''')

# if __name__ == '__main__':
#     app.run()

player_dict = {
    "Kevin Durant": "duranke01",
    "Joel Embiid": "embiijo01",
    "Luka Doncic": "doncilu01",
    "Nikola Jokic": "jokicni01",
    "Giannis Antetokounmpo": "antetgi01",
    "Shai Gilgeous-Alexander": "gilgesh01",
    "Anthony Davis": "davisan02"
}

# todo

class Condition:
    condition = None
    name = None
    magnitude = None

class PointsCondition(Condition):
    def __init__(self, p):
        self.name = "Points"
        self.magnitude = p
        self.condition = lambda x: (
            x.get('points_scored') >= p
        )

class ReboundsCondition(Condition):
    def __init__(self, r):
        self.name = "Rebounds"
        self.magnitude = r
        self.condition = lambda x: (
            x.get('defensive_rebounds') + x.get('offensive_rebounds') >= r
        )       

class AssistsCondition(Condition):
    def __init__(self, a):
        self.name = "Assists"
        self.magnitude = a
        self.condition = lambda x: (
            x.get('assists') >= a
        )

class PointsAndAssistsCondition(Condition):
    def __init__(self, paa):
        self.name = "PointsAndAssists"
        self.magnitude = paa
        self.condition = lambda x: (
            x.get('points_scored') + x.get('assists') >= paa
        ) 

class PointsAndReboundsCondition(Condition):
    def __init__(self, par):
        self.name = "PointsAndRebounds"
        self.magnitude = par
        self.condition = lambda x: (
            x.get('points_scored') + x.get('defensive_rebounds') + x.get('offensive_rebounds') >= par
        ) 

class ReboundsAndAssistsCondition(Condition):
    def __init__(self, raa):
        self.name = "ReboundsAndAssists"
        self.magnitude = raa
        self.condition = lambda x: (
            x.get('defensive_rebounds') + x.get('offensive_rebounds') + x.get('assists') >= raa
        ) 

class PointsAndAssistsAndReboundsCondition(Condition):
    def __init__(self, paaar):
        self.name = "PointsAndAssistsAndRebounds"
        self.magnitude = paaar
        self.condition = lambda x: (
            x.get('points_scored') + x.get('defensive_rebounds') + x.get('assists') + x.get('offensive_rebounds') >= paaar
        ) 


conditions = [
    PointsAndAssistsAndReboundsCondition(39.5)

]

last_x_games = 5
if last_x_games != None:
    print('Running against last %i games...' % last_x_games)

print("Conditions: ")
for condition in conditions:
    print("\t%s >= %.1f" % (condition.name, condition.magnitude))

for player in player_dict:
    data = client.regular_season_player_box_scores(
        player_identifier=player_dict[player],
        season_end_year=2024,
        output_type=OutputType.JSON
    )
    json_data = json.loads(data)
    if last_x_games != None:
        json_data = json_data[-1 * last_x_games:]

    total_game_count = len(json_data)
    filtered = json_data
    for condition in conditions:
        filtered = list(filter(condition.condition, filtered))
    print("%s hitrate is %.2f%%" % (player, len(filtered) / total_game_count * 100))



