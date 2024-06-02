import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the data
@st.cache
df = pd.read_csv("dashboard_data.csv")

# Get unique pollutants and stations
pollutants = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
stations = df['station'].unique()

# Streamlit UI
st.title('Beijing Air Quality Dashboard')

# Dropdowns for day range, pollutant, and station
day_range_option = st.radio("Select Day Range Option:", ('All Dates', 'Custom Range', 'Single Day'))
if day_range_option == 'Custom Range':
    start_date = st.date_input("Start Date:")
    end_date = st.date_input("End Date:")
elif day_range_option == 'Single Day':
    selected_date = st.date_input("Select Date:")

selected_pollutant = st.selectbox("Select Pollutant:", pollutants)
selected_station = st.multiselect("Select Station(s):", stations, default=stations)

# Filter data based on selected options
filtered_df = df.copy()
if day_range_option == 'Custom Range':
    filtered_df = filtered_df[(filtered_df['date'] >= start_date) & (filtered_df['date'] <= end_date)]
elif day_range_option == 'Single Day':
    filtered_df = filtered_df[filtered_df['date'].dt.date == selected_date]

# Plotting
if st.button("Plot"):
    fig, ax = plt.subplots(figsize=(10, 6))

    for station in selected_station:
        station_data = filtered_df[filtered_df['station'] == station]
        station_hour_avg = station_data.groupby(station_data['date'].dt.hour)[selected_pollutant].mean()
        ax.plot(station_hour_avg.index, station_hour_avg, label=station)

    ax.set_title(f'{selected_pollutant} Levels per Hour by Station')
    ax.set_xlabel('Hour of the Day')
    ax.set_ylabel(selected_pollutant)
    ax.legend(title='Station')

    st.pyplot(fig)