""" Creates the Dash app"""

import dash
from dash import dcc, html
from dash.dependencies import Input, Output

import pandas as pd
from pandasql import sqldf
import plotly.express as px
    

import pandas as pd
from pandasql import sqldf


# Load the CSV file into a Pandas DataFrame
df = pd.read_csv('data/2015_16.csv')

# Define your SQL query
query = '''
WITH
    TEAM_CTE AS (
    SELECT DISTINCT [HomeTeam] as [Team]
    FROM df
    ),
    
    HOME_CTE AS (
        SELECT 
        [HomeTeam]
        ,SUM([FTHG]) AS [Goals_Scored]
        ,SUM([FTAG]) AS [Goals_Conceded]
        ,SUM([FTHG]) - SUM([FTAG]) AS [Goal_Difference]
        ,SUM(
            CASE WHEN [FTR] = "H" THEN 3
                WHEN [FTR] = "D" THEN 1
                ELSE 0
            END
        ) AS [Points]
        FROM df
        GROUP BY [HomeTeam]
    ),
    
    AWAY_CTE AS (
        SELECT 
        [AwayTeam]
        ,SUM([FTAG]) AS [Goals_Scored]
        ,SUM([FTHG]) AS [Goals_Conceded]
        ,SUM([FTAG]) - SUM([FTHG]) AS [Goal_Difference]
        ,SUM(
            CASE WHEN [FTR] = "A" THEN 3
                WHEN [FTR] = "D" THEN 1
                ELSE 0
            END
        ) AS [Points]
        FROM df
        GROUP BY [AwayTeam]
    )
    
    SELECT
        TEAM,
        HOME_CTE.[Goals_Scored]+AWAY_CTE.[Goals_Scored] as [Goals_Scored],
        HOME_CTE.[Goals_Conceded] + AWAY_CTE.[Goals_Conceded] as [Goals_Conceded],
        HOME_CTE.[Goal_Difference] + AWAY_CTE.[Goal_Difference] as [Goal_Difference],
        HOME_CTE.[Points] + AWAY_CTE.[Points] AS [Points]
        
    FROM TEAM_CTE
    INNER JOIN HOME_CTE
    ON TEAM_CTE.[TEAM] = HOME_CTE.[HomeTeam]
    INNER JOIN AWAY_CTE
    ON TEAM_CTE.[TEAM] = AWAY_CTE.[AwayTeam]
    
    GROUP BY [Team]
    ORDER BY [POINTS] DESC
    
'''

# Execute the SQL query using the sqldf() function
season_result_df = sqldf(query, globals())


bar_fig = px.bar(data_frame=season_result_df, x='Team', y='Points', title='Premier League 2015-16 total Points')

app = dash.Dash(__name__, update_title=None)
app.layout = html.Div(
    children=[
        html.H1("Select a variable"),
        dcc.Dropdown(
            id="title_dd",
            options=[
                {"label": "Goals Scored", "value": "Goals_Scored"},
                {"label": "Goals Conceded", "value": "Goals_Conceded"},
                {"label": "Goal Difference", "value": "Goal_Difference"},
                {"label": "Points", "value": "Points"},
            ],
            value="Points",  # Set a default value for the dropdown
        ),
        dcc.Graph(id='example_graph', figure=bar_fig)
    ]
)

@app.callback(
    Output(component_id='example_graph', component_property='figure'),
    Input(component_id='title_dd', component_property='value')
)
def update_plot(selected_var):
    fig_df = season_result_df.copy()
    bar_fig = px.bar(
        data_frame = fig_df,
         x='Team',
         y=selected_var,
         title=f"Premier League 2015-16 total {selected_var}"
    )
    return bar_fig

if __name__ == '__main__':
    app.run_server(debug=True)


