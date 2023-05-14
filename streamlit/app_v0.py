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

# Add a selectbox to the sidebar:
page = st.sidebar.selectbox("Wähle eine Seite", ("Hauptseite", "Metadaten", "Einfaches Modell"))

if page == "Hauptseite":
    # Titel der Streamlit-Seite
    st.title("Vorhersage der Unter- oder Uberbewertung von Fussballspielern")  # Der Titel der Streamlit-Seite ist "Vorhersage der Unter- oder Uberbewertung von Fussballspielern"

    # Funktion zum Laden der Daten definieren
    @st.cache_data
    def load_data():
        df = pd.read_csv('../data/df_clean.csv', index_col=0)
        return df

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
    df_display['League_Country'] = df_display['DisplayLeague'] + '/' + df_display['DisplayLeagueCountry']
    league_counts = df_display['League_Country'].value_counts()

    # Balkendiagramm erstellen basierend auf den gesamten Daten
    plt.figure(figsize=(12,8))
    sns.barplot(x=league_counts.values, y=league_counts.index, palette="Greens_r")
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
        selected_data = df_clean.loc[mask, ['Name', 'Club', 'League', 'NationalLeagueLevel', 'LeagueCountry', 'Value']]
        selected_data = selected_data.rename(columns={'Value': 'Value in €'})
        st.dataframe(selected_data)  # use st.dataframe() instead of st.write() to display the table
    else:
        st.write("Keine Ligen ausgewählt.")

elif page == "Metadaten":
    st.title("Spieler Metadaten")  # Der Titel der Streamlit-Seite ist "Spieler Metadaten"

elif page == "Einfaches Modell":
    st.title("Einfaches Modell")

    @st.cache_data
    def load_data_df():
        df = pd.read_csv('../data/simple_model_fs_merged.csv', index_col=0)
        return df

    df_simple_model = load_data_df()

    # Filteroptionen
    unique_position_categories = df_simple_model['PositionCategory'].unique().tolist()
    position_category = st.selectbox('Wähle Position Category', options=unique_position_categories)

    min_value = int(df_simple_model['Value'].min())
    max_value = int(df_simple_model['Value'].max())
    value_range = st.slider('Wähle Value', min_value=min_value, max_value=max_value, value=(min_value, max_value), step=10000)

    min_age = int(df_simple_model['Age'].min())
    max_age = int(df_simple_model['Age'].max())
    age_range = st.slider('Wähle Alter', min_value=min_age, max_value=max_age, value=(min_age, max_age))

    # Filtern des DataFrames und Auswählen des Spielers mit dem höchsten Wert in 'DifferenceSimpleModelXGB'
    mask = (df_simple_model['PositionCategory'] == position_category) & (df_simple_model['Value'].between(*value_range)) & (df_simple_model['Age'].between(*age_range))
    top_player = df_simple_model.loc[mask].nlargest(5, 'PercentDifferenceSimpleModelXGB')

    # Zeige den Spieler in einer Tabelle an
    st.table(top_player)


