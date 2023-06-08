import dash
from dash import dcc, html
from dash.dependencies import Input, Output


import pandas as pd
from pandasql import sqldf
import plotly.express as px

# Load the CSV file into a Pandas DataFrame
df = pd.read_csv('data/2015_16.csv')

# Define your SQL query
query = '''
WITH TEAM_CTE AS (
    SELECT DISTINCT [Hometeam] as [Team]
    FROM df
    ),

    HOME_CTE AS (
    SELECT
        [Hometeam] as [Home Team],
        sum([FTHG]) as [Goals Scored],
        sum([FTAG]) as [Goals Conceded],
        sum([FTHG])-sum([FTAG]) as [Goal Difference],
        sum(CASE WHEN [FTR] = "H" THEN 3
            WHEN [FTR] = "D" THEN 1
            WHEN [FTR] = "A" THEN 0
        END) AS [Points]
    FROM df
    GROUP BY [Hometeam]
),
        
AWAY_CTE AS (
    SELECT
        [Awayteam] as [Away Team],
        sum([FTAG]) as [Goals Scored],
        sum([FTHG]) as [Goals Conceded],
        sum([FTAG])-sum([FTHG]) as [Goal Difference],
        sum(CASE WHEN [FTR] = "H" THEN 0
            WHEN [FTR] = "D" THEN 1
            WHEN [FTR] = "A" THEN 3
        END) AS [Points]
    FROM df
    GROUP BY [Awayteam]
)

SELECT
    [Team],
    HOME_CTE.[Goals Scored] + AWAY_CTE.[Goals Scored] as [Goals Scored],
    HOME_CTE.[Goals Conceded] + AWAY_CTE.[Goals Conceded] as [Goals Conceded],
    HOME_CTE.[Goal Difference] + AWAY_CTE.[Goal Difference] as [Goal Difference],
    HOME_CTE.[Points] + AWAY_CTE.[Points] AS [Points]
FROM TEAM_CTE
INNER JOIN HOME_CTE
ON TEAM_CTE.[Team] = HOME_CTE.[Home Team]
INNER JOIN AWAY_CTE
ON TEAM_CTE.[Team] = AWAY_CTE.[Away Team]
GROUP BY [Team]
ORDER BY [Points] DESC
'''

# Execute the SQL query using the sqldf() function
season_result_df = sqldf(query, globals())

bar_fig = px.bar(data_frame=season_result_df, x='Team', y='Points', title='Premier League 2015-16 total points')

app = dash.Dash(__name__, update_title=None)
# Datacamp simply uses app = dash.Dash()
# Notice how we use: app = dash.Dash(__name__, assets_folder=get_assets_folder(), update_title=None)


# app.layout = dcc.Graph(id='example-graph', figure=bar_fig,)
# We use this in our index.py file


#### CALLBACK EXAMPLE
app.layout = html.Div(
    children=[
        html.H1("Select a variable"),
        dcc.Dropdown(
            id="title_dd",
            options=[
                {"label": "Goals Scored", "value": "Goals Scored"},
                {"label": "Goals Conceded", "value": "Goals Conceded"},
                {"label": "Goal Difference", "value": "Goal Difference"},
                {"label": "Points", "value": "Points"},
            ],
            value="Points",  # Set a default value for the dropdown
        ),
        dcc.Graph(id='example_graph', figure=bar_fig)
    ]
)


@app.callback(
    Output(component_id="example_graph", component_property="figure"),
    Input(component_id="title_dd", component_property="value"),
)
def update_plot(selected_var):
    fig_df = season_result_df.copy()
    bar_fig = px.bar(
        data_frame=fig_df,
        title=f"Premier League 2015-16 {selected_var}",
        x='Team',
        y=selected_var,
    )
    return bar_fig


if __name__ == '__main__':
    app.run_server(debug=True)