import pandas as pd
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import plotly.graph_objects as go
import plotly.express as px
import dash_bootstrap_components as dbc


def load_file():
    #Reading csv files
    df_costs = pd.read_csv('costs_2022.csv')
    df_revenue = pd.read_csv('revenue_2022.csv')

    month_order = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,
                'Jul':7,'Aug':8,'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}

    #Creating final dataframes to be processed
    df_costs = pd.melt(df_costs,id_vars= ['Line Of Business'], value_vars=df_costs.keys()[3:15], var_name='months', value_name='total_cost')
    df_costs_grouped = df_costs.groupby(['Line Of Business','months']).sum().reset_index()
    df_costs_grouped['order_month'] = df_costs_grouped['months'].apply(lambda x: month_order[x])
    df_costs_grouped = df_costs_grouped.sort_values(by=['Line Of Business','order_month'],ascending=True)
    df_costs_grouped['Source']='Costs'

    df_revenue = pd.melt(df_revenue,id_vars= ['Line Of Business'], value_vars=df_revenue.keys()[3:15], var_name='months', value_name='total_cost')
    df_revenue['total_cost'] = df_revenue['total_cost'].apply(lambda c: c.replace('$','').replace("'",'').replace(',','')).astype(float)
    df_revenue['total_cost'] = pd.to_numeric(df_revenue['total_cost'])
    df_revenue_grouped = df_revenue.groupby(['Line Of Business','months']).sum().reset_index()
    df_revenue_grouped['order_month'] = df_revenue_grouped['months'].apply(lambda x: month_order[x])
    df_revenue_grouped = df_revenue_grouped.sort_values(by=['Line Of Business','order_month'],ascending=True)
    df_revenue_grouped['Source']='Revenue'
    df_total = pd.concat([df_costs_grouped,df_revenue_grouped])
    
    return df_total


def create_dash(df_total):

    # Initialize the app and incorporating a Dash Bootstrap theme
    external_stylesheets = [dbc.themes.CERULEAN]
    app = Dash(__name__, external_stylesheets=external_stylesheets)

    # App layout
    app.layout = dbc.Container([
        dbc.Row([
            html.Div('Costs and Revenue Dashboard', className="text-primary text-center fs-3"),
        ]),
        
        
        dbc.Row([
            html.Br(),
            dbc.RadioItems(options=[{"label": x, "value": x} for x in list(df_total['Source'].unique())],
                        value=df_total['Source'].unique()[0],
                        inline=True,
                        id='radio_buttons_source',
                        style={'width': '15%'}),
            dcc.Dropdown(
                        list(df_total['Line Of Business'].unique()),
                        placeholder="Select a bussiness line",
                        multi=True,
                        id='dropdown_bussiness_lines',
                        style={'width': '60%'}
            ),
        ]),
        
        dcc.Graph(id='bar_gragh'),   
        
    ], fluid=True)

    @app.callback(
        Output( 'bar_gragh', 'figure' ),
        Input( 'dropdown_bussiness_lines', 'value' ),
        Input( 'radio_buttons_source', 'value' )
    )
    def update_figure(dropdown_bussiness_lines, radio_buttons_source):
        
        df_filtered=df_total.loc[df_total['Source'] == radio_buttons_source]
        
        if dropdown_bussiness_lines:
            df_filtered = df_filtered.loc[df_filtered['Line Of Business'].isin(dropdown_bussiness_lines)]    
        
        TrendChart = px.bar(data_frame=df_filtered, x=df_filtered['months'], y=df_filtered['total_cost'],
                            barmode='group',
            color='Line Of Business',
            title="Data for the " + radio_buttons_source + " of the company",
            labels={'Request': 'Request', radio_buttons_source: radio_buttons_source, 'total_cost':'Total ' + radio_buttons_source},
            
        ).update_traces(textposition='outside')

        return TrendChart


    @app.callback(
        Output( 'dropdown_bussiness_lines', 'options' ),
        Input( 'radio_buttons_source', 'value' )
    )
    def updateDropdown(source):
        return list(df_total['Line Of Business'].loc[df_total['Source'] == source].unique())
    
    return app
        
def main():
    df = load_file()
    app = create_dash(df)
    app.run()
    
# Run the app
if __name__ == '__main__':
    main()