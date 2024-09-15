import dash
import os
from dash import html, dcc, Input, Output, State
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import create_engine
from dotenv import load_dotenv
import plotly.io as pio
import io

load_dotenv()

# Construct database URL from environment variables
db_url = create_engine(
    f"{os.getenv('ENGINE')}://{os.getenv('DATABASE_USER')}:{os.getenv('PASSWORD')}@{os.getenv('HOST')}:{os.getenv('PORT')}/{os.getenv('DATABASE')}"
)

# Query to fetch data
query = '''
SELECT 
    mf."Marksheet_fact_code" as Marksheet_fact_description, 
    mf."Name" as name,
    mf."Internal" as internal_description,
    mf."External" as external_description,
    mf."Year" as year,
	mf."Grade" as grade_description,
    s."Rollno" as rollno_description,                     
    s."Student_NAME" as student_name_description,             
    sg."SGPA" as sgpa_description,                     
    sg."semester" AS semester_description,                 
    sg."Total Marks Obt." as mark_description          
FROM 
    public."marksheet_fact" mf
JOIN 
    public."Student" s 
    ON mf."Rollno_code" = s."Rollno_code"  
JOIN 
    public."SGPA" sg 
    ON mf."SGPA_code" = sg."SGPA_code"; 
'''

df = pd.read_sql_query(query, db_url)

# Define default dropdown values function
def get_default_dropdown_values():
    default_semester = "3"
    default_name = ["Select All"]
    default_year = "2"
    default_rollno="2200540109014"
    default_student_name="Rajeev kushwaha"
    return default_semester, default_name, default_year,default_rollno,default_student_name

# Get default dropdown values
default_semester, default_name, default_year,default_rollno,default_student_name = get_default_dropdown_values()

external_stylesheets = [
    {
        "href": "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css",
        "rel": "stylesheet",
    },
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Marksheet"

app.layout = html.Div(
    className="content-wrapper",
    children=[
        # Sidebar
        html.Div(
            style={'flex': '0 1 320px', 'padding': "10px", "boxSizing": "border-box"},
            children=[
                html.H1(
                    "Select parameters to get charts",
                    className="parameter-data",
                    style={'fontSize': "15px", 'fontWeight': 'normal', 'marginBottom': '25px', "marginTop": "20px"}
                ),
                 html.Div(
                    children=[
                        html.Div(children="Rollno", className="menu-title"),
                        dcc.Dropdown(
                            id="rollno-dropdown",
                            options=[{'label': i, 'value': i} for i in df['rollno_description'].unique()],
                            placeholder="rollno",
                            searchable=False,
                            clearable=False,
                            className="dropdown",
                            value=default_rollno,
                            style={"fontSize": "12px"}
                        ),
                    ],
                    style={'marginBottom': '0px'}
                ),
                 html.Div(
                    children=[
                        html.Div(children="Student Name", className="menu-title"),
                        dcc.Dropdown(
                            id="student-name-dropdown",
                            options=[{'label': i, 'value': i} for i in df['student_name_description'].unique()],
                            placeholder="Student Name",
                            searchable=False,
                            clearable=False,
                            className="dropdown",
                            value=default_student_name,
                            style={"fontSize": "12px"}
                        ),
                    ],
                    style={'marginBottom': '0px'}
                ),
                html.Div(
                    children=[
                        html.Div(children="Year", className="menu-title"),
                        dcc.Dropdown(
                            id="year-dropdown",
                            options=[{'label': i, 'value': i} for i in df['year'].unique()],
                            placeholder="year",
                            searchable=False,
                            clearable=False,
                            className="dropdown",
                            value=default_year,
                            style={"fontSize": "12px"}
                        ),
                    ],
                    style={'marginBottom': '0px'}
                ),
                html.Div(
                    children=[
                        html.Div(children="Semester", className="menu-title"),
                        dcc.Dropdown(
                            id="semester-dropdown",
                            options=[{'label': i, 'value': i} for i in df['semester_description'].unique()],
                            placeholder="semester",
                            multi=False,
                            searchable=False,
                            clearable=False,
                            className="dropdown",
                            value=default_semester,
                            style={"fontSize": "12px"}
                        ),
                    ],
                    style={'marginBottom': '0px'}
                ),
                html.Div(
                    children=[
                        html.Div(children="Subject Name", className="menu-title"),
                        dcc.Dropdown(
                            id="subject-dropdown",
                            options=[{'label': "Select All", 'value': "Select All"}] + [{'label': i, 'value': i} for i in df['name'].unique()],
                            placeholder="Subject_Name",
                            multi=True,
                            searchable=False,
                            clearable=False,
                            className="dropdown",
                            value=default_name,
                            style={"fontSize": "12px"}
                        ),
                    ],
                    style={'marginBottom': '0px'}
                ),
                
                html.Button(
                    'Apply', id='plot-button', n_clicks=0, className='mr-1',
                    style={
                        'width': '100%',
                        'background': 'radial-gradient(circle, #0a266c 0, #085858 3%, #0a266c 94%)',
                        'color': 'white',
                        'border': 'none',
                        'padding': '10px 20px',
                        'text-align': 'center',
                        'font-size': '16px',
                        'margin': '15px 0',
                        'cursor': 'pointer',
                        'border-radius': '8px',
                        'marginTop': '30px',
                        'marginBottom': '0px'
                    }
                ),
                html.Button(
                    'Download', id='download-svg-button', n_clicks=0, className='mr-1',
                    style={
                        'width': '100%',
                        'background': 'radial-gradient(circle, #0a266c 0, #085858 3%, #0a266c 94%)',
                        'color': 'white',
                        'border': 'none',
                        'padding': '10px 20px',
                        'font-size': '16px',
                        'margin': '20px 0',
                        'cursor': 'pointer',
                        'border-radius': '8px',
                        'marginBottom': '0px'
                    }
                ),
            ]
        ),
        # Graph area
        html.Div(
            style={'flex': '1', 'padding': '20px', 'position': 'relative', 'text-align': 'center', 'height': 'calc(100% - 50px)'},
            children=[
                dcc.Loading(
                    id="loading-graph",
                    type="circle", color='#83b944',
                    children=[
                        html.Div(
                            id='graph-container',
                            style={'width': '100%', 'height': '650px'},
                            children=[
                                html.Div(
                                    className="loader",
                                    id="loading-circle",
                                    style={"position": "absolute", "top": "50%", "left": "50%", "transform": "translate(-50%, -50%)"}
                                ),
                                dcc.Graph(
                                    id="plot-output",
                                    config={"displayModeBar": False},
                                    style={'width': '100%', 'height': 'calc(100% - 50px)'}
                                ),
                            ]
                        ),
                    ]
                ),
            ],
        ),
        dcc.Download(id="download"),
        # Interval component to trigger default plot
        dcc.Interval(
            id='interval-component',
            interval=1*1000,  # Interval in milliseconds
            n_intervals=0,
            max_intervals=1  # Ensure it runs only once
        )
    ]
)
# Update student name dropdown based on rollno selection
@app.callback(
    Output("student-name-dropdown", "options"),
    [Input("rollno-dropdown", "value")]
)
def update_year_dropdown(rollno):
    filtered_df = df[df['rollno_description'] == rollno]
    student_name = filtered_df["student_name_description"].unique()
    return [{"label":  student_name , "value":  student_name } for  student_name in  student_name]

# Update semester dropdown based on year selection
@app.callback(
    Output("semester-dropdown", "options"),
    [Input("year-dropdown", "value")]
)
def update_year_dropdown(year):
    filtered_df = df[df['year'] == year]
    semester = filtered_df["semester_description"].unique()
    return [{"label": semester, "value": semester} for semester in semester]

# Update subject dropdown based on semester selection
@app.callback(
    Output("subject-dropdown", "options"),
    [Input("semester-dropdown", "value")]
)
def update_name_dropdown(sem):
    filtered_df = df[df['semester_description'] == sem]
    subject = filtered_df['name'].unique()
    return [{'label': "Select All", 'value': "Select All"}] + [{"label": subject, "value": subject} for subject in subject]

@app.callback(
    Output("plot-output", "figure"),
    [Input('plot-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')],
    [State("subject-dropdown", "value"),
     State("semester-dropdown", "value"),
     State("year-dropdown", "value"),
     State("rollno-dropdown","value"),
     State("student-name-dropdown","value")]
)
def update_plot(n_clicks, n_intervals, name, semester, year,rollno,student):
    ctx = dash.callback_context
    if not ctx.triggered:
        button_id = None
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Handle "Select All" logic
    if "Select All" in name:
        filtered_df = df[(df['year'] == year) & (df['semester_description'] == semester) & (df['rollno_description'] == rollno) & (df['student_name_description'] == student)]
    else:
        filtered_df = df[(df['year'] == year) &
                         (df['semester_description'] == semester) &
                         (df['name'] & (df['rollno_description'] == rollno) &
                        (df['student_name_description'] == student).isin(name))]

    # Filter out rows where 'internal_description' is missing
    filtered_df = filtered_df.dropna(subset=['internal_description'])

    # Extract unique SGPA values and concatenate them into a string for the x-axis title
    unique_sgpa = ", ".join(map(str, filtered_df['sgpa_description'].unique()))
    Total_Marks=", ".join(map(str, filtered_df['mark_description'].unique()))

    # Create the figure
    fig = go.Figure()

    if n_clicks > 0 or n_intervals == 1:
        # Plot external marks
        fig.add_trace(go.Scatter(
            x=filtered_df["name"],
            y=filtered_df["external_description"],
            mode="lines+markers",
            name="External Marks",
            marker=dict(size=15),
            line=dict(color='blue')
        ))

        # Plot internal marks
        fig.add_trace(go.Scatter(
            x=filtered_df["name"],
            y=filtered_df["internal_description"],
            mode="lines+markers",
            name="Internal Marks",
            marker=dict(size=15),
            line=dict(color='red')
        ))
        # Update layout with dynamic SGPA values in x-axis title
        fig.update_layout(
            xaxis={"title": f"Subject Name (SGPA: {unique_sgpa})"},
            yaxis={"title": f"Total Marks obtained {Total_Marks}"},
            hovermode="closest",
            legend_title="Marks and SGPA"
        )

    return fig



@app.callback(
    Output("download", "data"),
    Input("download-svg-button", "n_clicks"),
    State("plot-output", "figure"),
    prevent_initial_call=True
)
def download_svg(n_clicks, figure):
    if n_clicks > 0:
        try:
            # Convert the figure to an SVG string
            svg_str = pio.to_image(go.Figure(figure), format="svg")
            return dcc.send_bytes(svg_str, "plot.svg")
        except Exception as e:
            print(f"Error converting figure to SVG: {e}")
            return None


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_ui=False, dev_tools_props_check=False, port=4574)
