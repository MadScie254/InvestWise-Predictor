import altair as alt
import pandas as pd

# Data for the chart
data = pd.DataFrame({
    'month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    'value': [1200, 1500, 1700, 2100, 1900, 2500]
})

# Create the Altair chart
chart = alt.Chart(data).mark_line(
    point=True,
    color='#FFD700'
).encode(
    x=alt.X('month:N', title='Month'),
    y=alt.Y('value:Q', title='Market Performance')
).properties(
    width=600,
    height=300,
    title='Market Performance'
)

# Save the chart as an SVG file
chart.save('chart.svg')