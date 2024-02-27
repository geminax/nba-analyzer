import dash
import pickle
import pandas as pd
from dash import html, dcc, Input, Output, State, callback, dash_table
from nba_api.stats.endpoints import playergamelogs

dash.register_page(__name__, path='/')

stat_types = ['PTS', 'AST', 'REB', 'PTS/AST', 'PTS/REB', 'AST/REB', 'PTS/AST/REB']
players_dict = {}
player_names = []

with open("nba_players_dict.pkl", "rb") as source:
  players_dict = pickle.load(source)
  player_names = players_dict.keys()

players_frames_cache = {}

bottom_grid_cols = {
  "": ["Hit Rate", "Average"],
  "23/24": ['N/A', 'N/A'],
  "L5": ['N/A', 'N/A'],
  "L10": ['N/A', 'N/A'],
  "L20": ['N/A', 'N/A']
}
bottom_grid = pd.DataFrame(bottom_grid_cols)

layout = \
html.Div([
  html.Datalist(id='players', children=[
    html.Option(value=name, label=str(id), hidden=True) for name, id in players_dict.items()
  ]),
  dcc.Input(placeholder='Player', id='player-selector', list='players'),
  html.Br(),
  dcc.Input(placeholder='Prop Line', id='prop-line', type='number', step=0.5, value=0),
  html.Br(),
  html.Datalist(id='stat-types', children=[
    html.Option(value=statType, hidden=True) for statType in stat_types
  ]),
  dcc.Input(placeholder='Stat', id='stat-selector', list='stat-types', value='PTS'),
  html.Br(),
  html.Button('Refresh Player', id='refresh-player'),
  dcc.Graph(
    id='graph',
    figure={
      'data': [
        {'x': ['L5', 'L10', 'L15', 'Total'], 'y': [4, 1, 2, 3], 'type': 'bar', 'name': 'Anthony Davis'},
      ]
      # 'layout': {
      #   'title':'
      # }
    }
  ),
  dash_table.DataTable(bottom_grid.to_dict('records'),
    id='bottom-grid',                  
    style_cell={
      'height': 'auto',
      'minWidth': '50px', 'width': '50px', 'maxWidth': '50px',
      'whiteSpace': 'normal',
      'textAlign': 'center'
    })
  ]
)
  
@callback(
  Output('bottom-grid', 'data'),
  Input('player-selector', 'value'),
  Input('stat-selector', 'value'),
  Input('prop-line', 'value'),
  Input('refresh-player', 'n_clicks'),
  State('bottom-grid', 'data')
)
def update_data(player, stat, prop, n_clicks, data):
  if player not in player_names or stat not in stat_types or prop < 0:
    return bottom_grid.to_dict('records')
  
  if players_dict[player] in players_frames_cache.keys():
    print('invalidated')
    del players_frames_cache[players_dict[player]]
  
  df = None
  if players_dict[player] not in players_frames_cache.keys():
    print('querying')
    df = playergamelogs.PlayerGameLogs(player_id_nullable=players_dict[player], season_nullable="2023-24").get_data_frames()[0]
    df = df[['PTS', 'REB', 'AST']]
    df['PTS/REB'] = df[['PTS', 'REB']].sum(axis=1)
    df['PTS/AST'] = df[['PTS', 'AST']].sum(axis=1)
    df['AST/REB'] = df[['AST', 'REB']].sum(axis=1)
    df['PTS/AST/REB'] = df[['PTS', 'AST', 'REB']].sum(axis=1)
    players_frames_cache[players_dict[player]] = df.to_json()
  else:
    print('from cache')
    df = pd.read_json(players_frames_cache[players_dict[player]])

  # averages
  season = "{:.2f}".format(df[stat].mean())
  l20 = "{:.2f}".format(df.head(20)[stat].mean())
  l10 = "{:.2f}".format(df.head(10)[stat].mean())
  l5 ="{:.2f}".format(df.head(5)[stat].mean())

  data[1]['23/24'] = season
  data[1]['L20'] = l20
  data[1]['L10'] = l10
  data[1]['L5'] = l5

  # hit rate
  total_games = len(df[stat])
  count = 0
  for value in df[stat]:
    if value >= prop:
      count += 1

  total_hr = '%.2f%%' % (count / total_games * 100)

  count = 0
  for value in df.head(20)[stat]:
    if value >= prop:
      count += 1

  l20hr = '%.2f%%' % (count / 20 * 100)

  count = 0
  for value in df.head(10)[stat]:
    if value >= prop:
      count += 1

  l10hr = '%.2f%%' % (count / 10 * 100)
  
  count = 0
  for value in df.head(5)[stat]:
    if value >= prop:
      count += 1
  
  l5hr = '%.2f%%' % (count / 5 * 100)

  data[0]['23/24'] = total_hr
  data[0]['L20'] = l20hr
  data[0]['L10'] = l10hr
  data[0]['L5'] = l5hr

  return data
  