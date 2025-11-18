import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
from dash import no_update
import datetime as dt

#Create app
app = dash.Dash(__name__)

# Clear the layout and do not display exception till callback gets executed
app.config.suppress_callback_exceptions = True

# Read the wildfire data into pandas dataframe
# CORRECTED: Removed hidden character before pd.read_csv
df = pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/Historical_Wildfires.csv')

#Extract year and month from the date column
df['Month'] = pd.to_datetime(df['Date']).dt.month_name() #used for the names of the months
df['Year'] = pd.to_datetime(df['Date']).dt.year

#Layout Section of Dash
app.layout = html.Div(children=[
    
    #Task 2.1 Add the Title to the Dashboard
    html.H1('Australia Wildfire Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 26}),
    
    # CORRECTED: This Div is for controls
    html.Div([
        # First inner divsion for adding dropdown helper text for Selected Drive wheels
        html.Div([
            html.H2('Select Region:', style={'margin-right': '2em'}),
            #Radio items to select the region
            # CORRECTED: Removed the first dcc.RadioItems and kept the one with full labels
            dcc.RadioItems([
                {"label": "New South Wales", "value": "NSW"},
                {"label": "Northern Territory", "value": "NT"},
                {"label": "Queensland", "value": "QL"},
                {"label": "South Australia", "value": "SA"},
                {"label": "Tasmania", "value": "TA"},
                {"label": "Victoria", "value": "VI"},
                {"label": "Western Australia", "value": "WA"}
            ], "NSW", id='region', inline=True)
        ]), # End of Region Div
        
        # Dropdown to select year
        html.Div([
            html.H2('Select Year:', style={'margin-right': '2em'}),
            dcc.Dropdown(df.Year.unique(), value=2005, id='year')
        ]), # End of Year Div
    ]), # End of controls Div
    
    # NEW: Div for Summary Statistics
    html.Div(id='stats-output', style={'padding': '10px 20px'}),
    
    # CORRECTED: Created a new Div for the graphs, separate from the controls
    # TASK 2.3: Add two empty divisions for output inside the next inner division.
    html.Div([
        html.Div([], id='plot1'),
        html.Div([], id='plot2')
    ], style={'display': 'flex'}) # Added style to show side-by-side
    
]) #layout ends

#TASK 2.4: Add the Ouput and input components inside the app.callback decorator.
@app.callback(
    [Output(component_id='stats-output', component_property='children'),
     Output(component_id='plot1', component_property='children'),
     Output(component_id='plot2', component_property='children')],
    [Input(component_id='region', component_property='value'),
     Input(component_id='year', component_property='value')]
)
#TASK 2.5: Add the callback function.
def reg_year_display(input_region, input_year):
    
    #data
    region_data = df[df['Region'] == input_region]
    y_r_data = region_data[region_data['Year']==input_year]
    
    # NEW: Define month order for correct sorting
    months_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                    'July', 'August', 'September', 'October', 'November', 'December']
    
    # NEW: Calculate Summary Statistics
    total_area = y_r_data['Estimated_fire_area'].sum()
    total_count = y_r_data['Count'].sum()
    avg_brightness = y_r_data['Mean_estimated_fire_brightness'].mean()
    
    stats_component = html.Div([
        html.H3(f'Summary for {input_region} in {input_year}', style={'border-bottom': '1px solid #ccc'}),
        html.P(f"Total Estimated Fire Area: {total_area:.2f} km²"),
        html.P(f"Total Pixel Count: {total_count}"),
        html.P(f"Average Fire Brightness: {avg_brightness:.2f} K")
    ])
    
    #Plot one - Monthly Average Estimated Fire Area
    est_data = y_r_data.groupby('Month')['Estimated_fire_area'].mean().reset_index()
    # NEW: Sort by month
    est_data['Month'] = pd.Categorical(est_data['Month'], categories=months_order, ordered=True)
    est_data = est_data.sort_values('Month')
    
    # UPDATED: Changed from px.pie to px.line
    fig1 = px.line(est_data, x='Month', y='Estimated_fire_area', 
                   title="{} : Monthly Average Estimated Fire Area in year {}".format(input_region, input_year))
    
    #Plot two - Monthly Average Count of Pixels for Presumed Vegetation Fires
    veg_data = y_r_data.groupby('Month')['Count'].mean().reset_index()
    # NEW: Sort by month
    veg_data['Month'] = pd.Categorical(veg_data['Month'], categories=months_order, ordered=True)
    veg_data = veg_data.sort_values('Month')
    
    fig2 = px.bar(veg_data, x='Month', y='Count', title='{} : Average Count of Pixels for Presumed Vegetation Fires in year {}'.format(input_region, input_year))
    
    # UPDATED: Return 3 components
    return [stats_component, 
            dcc.Graph(figure=fig1),
            dcc.Graph(figure=fig2)]

if __name__ == '__main__':
   
    app.run(debug=True)

    #Install python packages required to run the application. Copy and paste the below command to the terminal.


#pip3.8 install setuptools

#python3.8 -m pip install packaging

#python3.8 -m pip install pandas dash

#pip3 install httpx==0.20 dash plotly
    # python3.8 Dash_wildfire.py
   