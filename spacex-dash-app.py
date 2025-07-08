# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Dropdown para selección de sitio de lanzamiento
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] + 
                [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True,
        style={'width': '80%', 'margin': '0 auto'}
    ),
    html.Br(),

    # TASK 2: Gráfico de tarta para mostrar éxito de lanzamientos
    html.Div(
        dcc.Graph(id='success-pie-chart'),
        style={'width': '80%', 'margin': '0 auto'}
    ),
    html.Br(),

    html.P("Payload range (Kg):", style={'textAlign': 'center'}),
    
    # TASK 3: Slider para seleccionar rango de carga útil
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # TASK 4: Gráfico de dispersión para correlación entre carga útil y éxito
    html.Div(
        dcc.Graph(id='success-payload-scatter-chart'),
        style={'width': '80%', 'margin': '0 auto'}
    ),
])

# TASK 2: Callback para el gráfico de tarta
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Caso: Todos los sitios
        success_counts = spacex_df[spacex_df['class'] == 1]['Launch Site'].value_counts()
        fig = px.pie(
            names=success_counts.index,
            values=success_counts.values,
            title='Distribución de Éxitos por Sitio de Lanzamiento',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
    else:
        # Caso: Sitio específico
        site_data = spacex_df[spacex_df['Launch Site'] == selected_site]
        success_count = site_data['class'].sum()
        failure_count = len(site_data) - success_count
        
        fig = px.pie(
            names=['Éxitos', 'Fallos'],
            values=[success_count, failure_count],
            title=f'Resultados en {selected_site}',
            color=['Éxitos', 'Fallos'],
            color_discrete_map={'Éxitos':'#00cc96', 'Fallos':'#ff6699'}
        )
    
    # Estilos comunes
    fig.update_layout(
        title_x=0.5,
        title_font_size=18,
        margin=dict(t=80, b=30)
    )
    return fig

# TASK 4: Callback para el gráfico de dispersión
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    # Filtrar por rango de carga útil
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                           (spacex_df['Payload Mass (kg)'] <= high)]
    
    # Filtrar por sitio si no es "ALL"
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    
    # Crear gráfico de dispersión
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Correlación entre Carga Útil y Resultado de Lanzamiento',
        labels={'class': 'Resultado del Lanzamiento (1=Éxito, 0=Fallo)'},
        hover_data=['Launch Site', 'Booster Version']
    )
    
    # Mejorar visualización
    fig.update_layout(
        title_x=0.5,
        yaxis=dict(tickvals=[0, 1], ticktext=['Fallo', 'Éxito']),
        legend_title_text='Versión del Cohete',
        xaxis_title='Masa de Carga Útil (kg)',
        yaxis_title='Resultado'
    )
    fig.update_traces(marker=dict(size=12, opacity=0.7))
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)