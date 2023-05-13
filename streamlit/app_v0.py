import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Die App-Eigenschaften definieren
st.set_page_config(
    page_title="Fussballspieler Bewertung",  # Der Titel der Seite ist "Fussballspieler Bewertung"
    page_icon="⚽",
    layout="wide"
)

# Titel der Streamlit-Seite
st.title("Vorhersage der Unter- oder Uberbewertung von Fussballspielern")  # Der Titel der Streamlit-Seite ist "Vorhersage der Unter- oder Uberbewertung von Fussballspielern"

# Funktion zum Laden der Daten definieren
@st.cache_data
def load_data():
    df_clean = pd.read_csv("df_clean.csv")
    return df_clean

# Daten laden
df_clean = load_data()

# Create a new DataFrame for displaying and filtering
df_display = df_clean.copy()

# Ligen mit weniger als 100 Spielern in "Andere Ligen" zusammenfassen
mask = df_display.groupby('League')['Name'].transform('count') < 100
df_display['DisplayLeague'] = df_display['League']
df_display['DisplayLeagueCountry'] = df_display['LeagueCountry']
df_display.loc[mask, 'DisplayLeague'] = 'Andere Ligen'
df_display.loc[mask, 'DisplayLeagueCountry'] = 'Andere Länder'

# Anzahl der Fussballspieler in jeder Liga zählen
df_display['League_Country'] = df_display['DisplayLeague'] + '/' + df_display['DisplayLeagueCountry']
league_counts = df_display['League_Country'].value_counts()

# Balkendiagramm erstellen
plt.figure(figsize=(12,8))
sns.barplot(x=league_counts.values, y=league_counts.index, palette="viridis")
plt.xlabel('Anzahl der Fussballspieler', fontsize=14)  # Die Beschriftung der X-Achse ist "Anzahl der Fussballspieler"
plt.ylabel('Ligen', fontsize=14)  # Die Beschriftung der Y-Achse ist "Ligen"
plt.title('Anzahl der Fussballspieler in jeder Liga', fontsize=16)  # Der Titel des Diagramms ist "Anzahl der Fussballspieler in jeder Liga"

# Diagramm anzeigen
st.pyplot(plt.gcf())

# Ligen für den Filter auswählen
leagues = df_display['League_Country'].unique()
selected_leagues = st.multiselect("Ligen auswählen", options=leagues)

# Spieler der ausgewählten Ligen anzeigen
if selected_leagues:
    mask = df_display['League_Country'].isin(selected_leagues)
    selected_data = df_clean.loc[mask, ['Name', 'Club', 'League', 'NationalLeagueLevel', 'LeagueCountry']]
    st.write(selected_data)
else:
    st.write("Keine Ligen ausgewählt.")
