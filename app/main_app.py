from dash import Dash, dcc, html, Input, Output, callback, State
import psycopg2
import json

app = Dash(__name__)

server = app.server

if __name__ == '__main__':
    # dev server
    host = 'localhost'
    port = "32768"
    password = "Open"
else:
    # nginx server
    host = 'postgres'
    port = "5432"
    password = open('/run/secrets/db-password', "r").read()

# To remove existing DB
# conn = psycopg2.connect(host=host, user="postgres", password=password)
# conn.set_session(autocommit=True)
# with conn.cursor() as cur:
#     cur.execute("DROP DATABASE IF EXISTS my_db")
#     cur.execute("CREATE DATABASE my_db")
# conn.close()

# Keep existing DB if exists else create it
conn = psycopg2.connect(host=host, user="postgres", port=port, password=password)
conn.set_session(autocommit=True)
with conn.cursor() as cur:
    cur.execute("SELECT datname FROM pg_database")
    list_dbs = cur.fetchall()
    if ("my_db",) not in list_dbs:
        cur.execute("CREATE DATABASE my_db")
conn.close()

with psycopg2.connect(host=host, user="postgres", port=port, password=password, database="my_db") as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        list_tables = cur.fetchall()
        if ('my_table',) not in list_tables:
            cur.execute("CREATE TABLE my_table (input VARCHAR(20))")
conn.close()

app.layout = html.Div([
    html.Img(id='my-image', alt="TEST website", src="assets/Artboard.png"),
    html.Br(),
    dcc.Input(id='my-input', value='initial value', type='text'),
    html.Br(),
    html.Div(id='my-output'),
    html.Button(id="my-button", children="Send to DB"),
    html.Div(id='my-data'),
])


@callback(
    Output('my-output', 'children'),
    Input('my-input', 'value')
)
def update_output_div(input_value):
    return f'Output: {input_value}'


@callback(
    Output('my-data', 'children'),
    Input('my-button', 'n_clicks'),
    State('my-input', 'value'),
    prevent_initial_call=True,
)
def add_data(_, value):
    with psycopg2.connect(host=host, user="postgres", port=port, password=password, database="my_db") as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO my_table VALUES (%s)", [value])
            cur.execute("SELECT * FROM my_table")
            row_headers = [x[0] for x in cur.description]
            results = cur.fetchall()
    conn.close()

    json_data = [dict(zip(row_headers, result)) for result in results]
    return json.dumps(json_data)


if __name__ == '__main__':
    app.run(debug=True)
