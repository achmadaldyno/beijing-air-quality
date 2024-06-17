import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

@st.cache_data
def load_data():
    # Load the data
    df = pd.read_csv('main_data.csv')

    # Drop the unnecessary columns
    df = df.drop(columns=['No', 'year', 'month', 'day', 'hour', 'wd', 'Unnamed: 0'], errors='ignore')

    # Convert 'datetime' to datetime type
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    return df

data = load_data()

# Title and description
st.title("Air Quality Analysis Dashboard")
st.write("""This dashboard provides an analysis of air quality data (12 parameters: 6 pollutants and 6 weather params) from Beijing, using data from 2013-2017 from 12 stations.""")

# About Me section
st.title("About Me")
st.markdown("""
- **Name:** Achmad Farhan Aldyno
- **Email Address:** achmad.f.a [at] mail.ugm.ac.id
- **Dicoding ID:** achmadaldyno
""")

# Sidebar for user input
st.sidebar.header("Select Data")
selected_station = st.sidebar.selectbox('Select Station', data['station'].unique())

# Date range selection using date_input
start_date = st.sidebar.date_input("Start Date", value=data['datetime'].min().date(), min_value=data['datetime'].min().date(), max_value=data['datetime'].max().date())
end_date = st.sidebar.date_input("End Date", value=data['datetime'].max().date(), min_value=data['datetime'].min().date(), max_value=data['datetime'].max().date())

# Filter data based on user input and selected date range
filtered_data = data[(data['station'] == selected_station) & (data['datetime'] >= pd.to_datetime(start_date)) & (data['datetime'] <= pd.to_datetime(end_date))]

# Display filtered data
st.header(f"Data preview and statistics summary for {selected_station} Station from selected period")
st.write(filtered_data)
st.write(filtered_data.describe())

# Time series plot
st.subheader("Time Series Plot")
pollutant = st.sidebar.radio('Select Pollutant', ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3'])

# Define China AQS Class 2 (GB3095-2012) and WHO AQG 2021 annual standards for various pollutants
china_aqs = {
    'PM2.5': 35,
    'PM10': 70,
    'O3': 160,  # 8h average
    'NO2': 40,  # Annual average
    'SO2': 60,  # Annual average
    'CO': 4,   # 24-hour average
}

who_aqg = {
    'PM2.5': 5,
    'PM10': 15,
    'O3': 60,  # 8-hour average
    'NO2': 10,  # Annual average
    'SO2': 40,  # 24-hour average
    'CO': 4,   # 24-hour average
}

# Manually calculate monthly averages
filtered_data['year'] = filtered_data['datetime'].dt.year
filtered_data['month'] = filtered_data['datetime'].dt.month
monthly_data = filtered_data.groupby(['year', 'month']).agg({pollutant: 'mean'}).reset_index()
monthly_data['datetime'] = pd.to_datetime(monthly_data[['year', 'month']].assign(day=1))

# Plot using Matplotlib
fig, ax = plt.subplots(figsize=(10, 6))

# Plot monthly average pollutant concentrations
ax.plot(monthly_data['datetime'], monthly_data[pollutant], marker='o', linestyle='-', color='b', label=f"{pollutant} Monthly Average")

# Plot China AQS Class 2 (GB3095-2012) annual standard
ax.axhline(y=china_aqs[pollutant], color='g', linestyle='--', label=f"China AQS Class 2 ({pollutant})")

# Plot WHO AQG 2021 annual standard
ax.axhline(y=who_aqg[pollutant], color='r', linestyle='--', label=f"WHO AQG 2021 ({pollutant})")

ax.set_title(f"Monthly Average {pollutant} with Annual Standards Comparison")
ax.set_xlabel('Date')
ax.set_ylabel(pollutant)
ax.legend()
ax.grid(True)

# Display plot in Streamlit
st.pyplot(fig)

# Format x-axis to display month and year
ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m'))
plt.xticks(rotation=45)

# Show plot
st.pyplot(fig)

# Display the citation and link to WHO AQG 2021
st.markdown("Standards are from the following publication:")
st.markdown("Kan H. (2022). World Health Organization air quality guidelines 2021: implication for air pollution control and climate goal in China. Chinese medical journal, 135(5), 513–515. [Link to article](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8920460/)")

# Pollutant average per hour for each station
st.subheader(f"{pollutant} Average per Hour for {selected_station} Station")

# Group by station and hour to calculate average for the selected pollutant
station_hourly_avg = filtered_data.groupby(['station', filtered_data['datetime'].dt.hour])[pollutant].mean().reset_index()

# Plotting pollutant average per hour for each station
fig, ax = plt.subplots(figsize=(10, 6))

ax.set_title(f"{pollutant} Average per Hour for {selected_station} Station")
sns.lineplot(data=station_hourly_avg, x='datetime', y=pollutant, hue='station', marker='o', markersize=8, ax=ax)
ax.set_xlabel('Hour of the Day')
ax.grid(True)
ax.legend()

# Display all hour labels
plt.xticks(station_hourly_avg['datetime'].unique())

plt.tight_layout()
st.pyplot(fig)

# Correlation heatmap
st.subheader("Correlation Heatmap")

# Drop categorical columns before computing correlation
correlation_data = filtered_data.drop(columns=['station', 'year', 'month', 'datetime']).corr()

plt.figure(figsize=(10, 8))
sns.heatmap(correlation_data, annot=True, cmap='coolwarm', annot_kws={"size": 6}, vmin=-1, vmax=1, center=0)
plt.title("Correlation Heatmap")

# Display the plot using st.pyplot() with the figure object
fig, ax = plt.subplots()
ax = sns.heatmap(correlation_data, annot=True, cmap='coolwarm', annot_kws={"size": 6}, vmin=-1, vmax=1, center=0)
ax.set_title("Correlation Heatmap")
st.pyplot(fig)
