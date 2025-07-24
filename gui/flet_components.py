import flet as ft
import plotly.graph_objects as go
from flet.plotly_chart import PlotlyChart

def create_pie_chart(title, usage_percentage):
    """Creates a pie chart to display resource usage."""
    labels = ['Used', 'Free']
    values = [usage_percentage, 100 - usage_percentage]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.4,
        marker_colors=['#1f77b4', '#aec7e8'],
        textinfo='percent',
        hoverinfo='label+percent',
        insidetextorientation='radial'
    )])

    fig.update_layout(
        title_text=f"{title} Usage",
        title_x=0.5,
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20),
        height=200,
        width=200,
        font=dict(size=10)
    )

    return PlotlyChart(fig, expand=True)
