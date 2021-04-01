###############################################################################
#                                MAIN
# Demo for fields and production NCS
###############################################################################

# Setup - importing the packages needed for setting up dash dashboard
# Packages with prebuilt components, and style

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import copy
import pathlib
import plotly.express as px
import pandas as pd
import json

#spesific config and controls
from settings import config, about
from settings.controls import FIELDS, FIELDS_GEOL_AGE, FIELDS_TYPES

# App Instance
app = dash.Dash(name=config.name, assets_folder=config.root + "/application/static",
                  external_stylesheets=[dbc.themes.LUX, config.fontawesome])
app.title = config.name


#init datalocation
PATH = pathlib.Path(__file__).parent.parent
DATA_PATH = PATH.joinpath("data").resolve()


#Read data
df = pd.read_csv(str(DATA_PATH.joinpath("Fields_data.csv")), dtype={"id": str})
proddata = pd.read_csv(str(DATA_PATH.joinpath("field_production_yearly.csv")), dtype={"NPDID": str})

with open(str(DATA_PATH.joinpath("Fields2.geojson"))) as f:
    oilfields = json.load(f)

df1 = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')

# Create controls
fields_types_options = [
    {"label": str(FIELDS_TYPES[fieldtype]), "value": str(fieldtype)} for fieldtype in FIELDS_TYPES
]
fields_options = [
    {"label": str(FIELDS[field]), "value": str(field)} for field in FIELDS
]

fields_geol_age_options = [
    {"label": str(FIELDS_GEOL_AGE[fieldsgeolage]), "value": str(fieldsgeolage)} for fieldsgeolage in FIELDS_GEOL_AGE
]

# Layout Generic for mapbox
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=20, r=10, b=10, t=30),
    hovermode="closest",
    legend=dict(font=dict(size=10), orientation="h"),
    title="",
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="carto-positron",
        center=dict(lon=-78.05, lat=42.54),
        zoom=7,
    )
)

def make_sunburst():
    millyears = [0.005, 0.01, 2.57, 2.75, 17.7, 10.87, 22.1, 10, 34.5, 44.5, 18.5, 11, 27.2, 35.7, 10, 4.7, 7.2, 13.8,
                 25.95]

    # age
    epoch = ["Anthropocene", "Holocene", "Pleistocene", "Pliocene", "Miocene", "Oligocene", "Eocene",
             "Paleocene", "Upper", "Lower", "Upper", "Middle", "Lower", "Upper",
             "Middle", "Lower", "Lopingian", "Guadalupian", "Cisualian"]

    period = ["Quaternary", "Quaternary", "Quaternary", "Neogene", "Neogene", "Paleogene", "Paleogene",
              "Paleogene", "Cretaceous", "Cretaceous", "Jurassic", "Jurassic", "Jurassic", "Triassic",
              "Triassic", "Triassic", "Permian", "Permian", "Permian"]

    era = ["Cenozoic", "Cenozoic", "Cenozoic", "Cenozoic", "Cenozoic", "Cenozoic", "Cenozoic",
           "Cenozoic", "Mesozoic", "Mesozoic", "Mesozoic", "Mesozoic", "Mesozoic", "Mesozoic",
           "Mesozoic", "Mesozoic", "Paleozoic", "Paleozoic", "Paleozoic"]

    df = pd.DataFrame(
        dict(millyears=millyears, epoch=epoch, period=period, era=era)
    )
    # print(df)
    figure = px.sunburst(df, path=['era', 'period', 'epoch'], values='millyears', title="MAIN RESERVOIR", width=450)

    return figure


def create_map(df, oilfields):
    fig = px.choropleth_mapbox(df, geojson=oilfields,
                               locations='id',
                               featureidkey="properties.id",
                               hover_name='fldName',
                               color_continuous_scale="Viridis",
                               range_color=(0, 12),
                               center={"lat": 60, "lon": 4},
                               opacity=0.5,
                               labels={'fldName'},
                               color="fldHcType",
                               # width=600
                               )
    fig.update_layout(mapbox_style="carto-positron", mapbox_zoom=4)
    fig.update_layout(margin={"r": 0, "t": 40, "l": 25, "b": 0})
    fig.update_geos(projection_type="natural earth")
    return fig





# Navbar - to be included in the app layout buildup

navbar = dbc.Nav(className="nav nav-pills", children=[
    ## logo/home
    dbc.NavItem(html.Img(src=app.get_asset_url("logo2.PNG"), height="120px")),

    ## logo/second
    dbc.NavItem(html.Img(src=app.get_asset_url("logo.PNG"), height="120px")),

    ## about
    dbc.NavItem(html.Div([
        dbc.NavLink("About", href="/", id="about-popover", active=False),
        dbc.Popover(id="about", is_open=False, target="about-popover", children=[
            dbc.PopoverHeader("How it works"), dbc.PopoverBody(about.txt)
        ])
    ])),
    ## links
    dbc.DropdownMenu(label="Links", nav=True, children=[
        dbc.DropdownMenuItem([html.I(className="fa fa-linkedin"), "  Contacts"], href=config.contacts, target="_blank"),
        dbc.DropdownMenuItem([html.I(className="fa fa-github"), "  Code"], href=config.code, target="_blank")
    ])
])

# Input - to be included in the app layout buildup

formGroup1 = dbc.FormGroup([
    # HEADER
    html.P("Filter by discovery date (or select range in histogram):", className="control_label", ),

    # Yearslider
    html.Br(),
    html.P("Select Year"),
    dcc.RangeSlider(
        id="year_slider1",
        min=1960,
        max=2017,
        value=[1990, 2010],
        className="dcc_control",
    ),

    # Filter
    html.Br(),
    html.P("Filter:", className="control_label"),
    dcc.RadioItems(
        id="fields_status_selector",
        options=[
            {"label": "  All ", "value": "all"},
            {"label": "  Producing ", "value": "prod"},
            {"label": "  Shut Down ", "value": "shutdown"},
            {"label": "  Approved for Production ", "value ": "approvedprod"},
        ],
        value="all",
        labelStyle={"display": "inline-block"},
        className="dcc_control"
    ),

    # Dropdown
    html.Br(),
    html.P("Fields"),
    dcc.Dropdown(
        id="fields_selector",
        options=fields_options,
        multi=False,
        # value=list(FIELDS.keys()),
        className="dcc_control",
    ),

    # Dropdown
    html.Br(),
    html.P("Field Types"),
    dcc.Dropdown(
        id="well_statuses",
        options=fields_types_options,
        multi=True,
        value=list(FIELDS_TYPES.keys()),
        className="dcc_control",
    ),

    # Dropdown
    html.Br(),
    html.P("Geological Age"),
    dcc.Dropdown(
        id="fields_types",
        options=fields_geol_age_options,
        multi=True,
        value=list(FIELDS_GEOL_AGE.keys()),
        className="dcc_control",
    )

])

graph1 = dbc.FormGroup([
    html.Div(
        [
            html.Div(
                [
                    dcc.Graph(id="graph-with-slider"),
                    dcc.Slider(
                        id='year-slider',
                        min=df1['year'].min(),
                        max=df1['year'].max(),
                        value=df1['year'].min(),
                        marks={str(year): str(year) for year in df1['year'].unique()},
                        step=None)
                ],
                className="pretty_container seven columns",
            ),
        ],
        className="row flex-display",
    )
])

#Make static figures

figsunburst = make_sunburst()
mapfig = create_map(df, oilfields)


# App Layout
# Divides into rows and columns each divided into 12 portions
#
app.layout = dbc.Container(fluid=True, children=[
    ## Top
    html.H1(config.name, id="nav-pills"),
    navbar,
    html.Br(), html.Br(), html.Br(),

    ## Body
    # 1st row
    dbc.Row([
        ### input + panel
        dbc.Col(md=4, children=[
            formGroup1,
            html.Br(), html.Br(), html.Br(),
        ]),
        dbc.Col(md=4, children=[
            graph1,
            html.Br(), html.Br(), html.Br()
        ])
    ]),
    # 2nd row
    dbc.Row([
        dbc.Col(md=6, children=[
            dcc.Graph(id="main_map", figure=mapfig),
            html.Br(), html.Br(), html.Br()
        ]),
        dbc.Col(md=6, children=[
            dcc.Graph(id="yearly_production_graph"),
            html.Br(), html.Br(), html.Br()
        ]),

    ]),
    # 3rd row
    dbc.Row([
        dbc.Col(md=6, children=[
            dcc.Graph(id="pie_graph"),
            html.Br(), html.Br(), html.Br()
        ]),
        dbc.Col(md=6, children=[
            dcc.Graph(id="sunburst_fig", figure=figsunburst),
            html.Br(), html.Br(), html.Br()
        ])
    ])
])


# FIGURES (called initially by callbacks)
# Make the production figure
def make_yearly_prod_figure(fieldname):
    layout_individual = copy.deepcopy(layout)

    index = proddata.loc[proddata.FIELDNAME == fieldname]['YEAR']
    gas = proddata.loc[proddata.FIELDNAME == fieldname]['GAS']
    oil = proddata.loc[proddata.FIELDNAME == fieldname]['OIL']
    water = proddata.loc[proddata.FIELDNAME == fieldname]['WATER']

    annotation = dict(
        text="",
        x=0.5,
        y=0.5,
        align="center",
        showarrow=False,
        xref="paper",
        yref="paper"
    )
    layout_individual["annotations"] = [annotation]

    data = [
        dict(
            type="scatter",
            mode="lines+markers",
            name="Gas Produced (G Sm3)",
            x=index,
            y=gas,
            line=dict(shape="spline", smoothing=2, width=1, color="#fac1b7"),
            marker=dict(symbol="diamond-open")
        ),

        dict(
            type="scatter",
            mode="lines+markers",
            name="Oil Produced (MM Sm3)",
            x=index,
            y=oil,
            line=dict(shape="spline", smoothing=2, width=1, color="#a9bb95"),
            marker=dict(symbol="diamond-open")
        ),
        dict(
            type="scatter",
            mode="lines+markers",
            name="Water Produced (MM Sm3)",
            x=index,
            y=water,
            line=dict(shape="spline", smoothing=2, width=1, color="#92d8d8"),
            marker=dict(symbol="diamond-open")
        )
    ]
    layout_individual["title"] = fieldname
    figure = dict(data=data, layout=layout_individual)
    return figure


# Make the piefigure
def make_pie_figure(fieldname):
    gas = proddata.loc[proddata.FIELDNAME == fieldname]['GAS'].sum()
    oil = proddata.loc[proddata.FIELDNAME == fieldname]['OIL'].sum()
    water = proddata.loc[proddata.FIELDNAME == fieldname]['WATER'].sum()

    layout_pie = copy.deepcopy(layout)

    data3 = [
        dict(
            type="pie",
            labels=["Gas", "Oil", "Water"],
            values=[gas, oil, water],
            name="Production Breakdown",
            text=[
                "Total Gas Produced (G Sm3)",
                "Total Oil Produced (MM Sm3)",
                "Total Water Produced (MM Sm3)",
            ],
            hoverinfo="text+value+percent",
            textinfo="label+percent+name",
            hole=20,
            marker=dict(colors=["#fac1b7", "#a9bb95", "#92d8d8"]),
            domain={"x": [0, 0.45], "y": [0.2, 0.8]},
        )
    ]
    layout_pie["title"] = fieldname
    layout_pie["font"] = dict(color="#777777")
    layout_pie["legend"] = dict(
        font=dict(color="#CCCCCC", size="10"), orientation="h", bgcolor="rgba(0,0,0,0)")
    figure = dict(data=data3, layout=layout_pie)
    return figure



# New functions
# Bubble graph (to be changed)
@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('year-slider', 'value')])
def update_figure(selected_year):
    filtered_df = df1[df1.year == selected_year]

    fig = px.scatter(filtered_df, x="gdpPercap", y="lifeExp",
                     size="pop", color="continent", hover_name="country",
                     log_x=True, size_max=55, width=1280)

    fig.update_layout(transition_duration=500)

    return fig


# Update PIE-GRAPH
# Main map hover fields : extract the field name -> update the pie_graph (using helper function)
@app.callback(
    Output('pie_graph', 'figure'),
    [Input('main_map', 'hoverData')])
def update_pie_figure(main_map_hoverdata):
    if main_map_hoverdata is None:
        return make_pie_figure("TROLL")
    else:
        return make_pie_figure(main_map_hoverdata["points"][0]["hovertext"])


# Update Yearly production graph
# Main map hover fields : extract the field name -> update the yearly-production-graph
@app.callback(
    Output('yearly_production_graph', 'figure'),
    [Input('main_map', 'hoverData')])
def update_pie_figure(main_map_hoverdata):
    if main_map_hoverdata is None:
        return make_yearly_prod_figure("TROLL")
    else:
        return make_yearly_prod_figure(main_map_hoverdata["points"][0]["hovertext"])



# Python functions for about navitem-popover
@app.callback(output=Output("about", "is_open"), inputs=[Input("about-popover", "n_clicks")],
              state=[State("about", "is_open")])
def about_popover(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(output=Output("about-popover", "active"), inputs=[Input("about-popover", "n_clicks")],
              state=[State("about-popover", "active")])
def about_active(n, active):
    if n:
        return not active
    return active



