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


@st.cache_data
def load_data():
    df = pd.read_csv('../data/df_simple_model_full_merge.csv', index_col=0)
    return df


# Add a selectbox to the sidebar:
page = st.sidebar.selectbox("Wähle eine Seite", ("Hauptseite", "Metadaten", "Einfaches Modell"))

if page == "Hauptseite":
    # Titel der Streamlit-Seite
    st.title(
        "Vorhersage der Unter- oder Uberbewertung von Fussballspielern")  # Der Titel der Streamlit-Seite ist "Vorhersage der Unter- oder Uberbewertung von Fussballspielern"

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
    plt.figure(figsize=(12, 8))
    sns.barplot(x=league_counts.values, y=league_counts.index, palette="Greens_r")
    plt.xlabel('Anzahl der Fussballspieler',
               fontsize=14)  # Die Beschriftung der X-Achse ist "Anzahl der Fussballspieler"
    plt.ylabel('Ligen', fontsize=14)  # Die Beschriftung der Y-Achse ist "Ligen"
    plt.title('Anzahl der Fussballspieler in jeder Liga',
              fontsize=16)  # Der Titel des Diagramms ist "Anzahl der Fussballspieler in jeder Liga"

    # Diagramm anzeigen
    st.pyplot(plt.gcf())

    # Ligen für den Filter auswählen
    leagues = df_display['League_Country'].unique()
    selected_leagues = st.multiselect("Ligen auswählen", options=leagues)

    # Spieler der ausgewählten Ligen anzeigen
    if selected_leagues:
        mask = df_display['League_Country'].isin(selected_leagues)
        selected_data = df_clean.loc[mask, ['Name', 'Club', 'League', 'NationalLeagueLevel', 'LeagueCountry', 'Value']]
        selected_data = selected_data.rename(columns={'Club': 'Klub', 'League': 'Liga',
                                                      'NationalLeagueLevel': 'Liga-Ebene',
                                                      'LeagueCountry': 'Liga Land', 'Value': 'Wert in €'})
        selected_data.reset_index(drop=True, inplace=True)  # Reset index and remove index column
        st.dataframe(selected_data)  # use st.dataframe() instead of st.write() to display the table
    else:
        st.write("Keine Ligen ausgewählt.")

elif page == "Metadaten":
    st.title("Spieler Metadaten")  # Der Titel der Streamlit-Seite ist "Spieler Metadaten"

    df_meta = load_data()

    unique_league_levels = sorted(df_meta['NationalLeagueLevel'].unique().tolist())
    unique_league_levels.insert(0, 'Alle')
    selected_level = st.selectbox('Wähle Liga-Ebene', options=unique_league_levels)

    # Filtern des DataFrames nach ausgewählter Liga-Ebene
    if selected_level == 'Alle':
        filtered_df = df_meta
    else:
        mask = df_meta['NationalLeagueLevel'] == selected_level
        filtered_df = df_meta.loc[mask]

    # 1. Verteilung der Füsse
    st.subheader("Verteilung der Füsse")
    foot_counts = filtered_df['Foot'].value_counts()
    fig, ax = plt.subplots()
    ax.pie(foot_counts, labels=foot_counts.index, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)

    # 2. Verteilung der Positionskategorien
    st.subheader("Verteilung der Positionskategorien")
    position_counts = filtered_df['PositionCategory'].value_counts()
    plt.figure(figsize=(12, 8))
    sns.barplot(x=position_counts.values, y=position_counts.index, palette="Greens_r")
    plt.xlabel('Anzahl der Spieler', fontsize=14)
    plt.ylabel('Positionskategorien', fontsize=14)
    plt.title('Verteilung der Positionskategorien', fontsize=16)
    st.pyplot(plt.gcf())

    # 3. Verteilung des Alters
    st.subheader("Verteilung des Alters")
    plt.figure(figsize=(12, 8))
    sns.histplot(filtered_df['Age'], bins=30, kde=True, color='green')
    plt.xlabel('Alter', fontsize=14)
    plt.ylabel('Anzahl der Spieler', fontsize=14)
    plt.title('Verteilung des Alters', fontsize=16)
    st.pyplot(plt.gcf())

    # 4. Verteilung der Werte
    st.subheader("Verteilung der Werte")
    plt.figure(figsize=(12, 8))
    sns.histplot(filtered_df['Value'], bins=30, kde=True, color='green')
    plt.xlabel('Wert in €', fontsize=14)
    plt.ylabel('Anzahl der Spieler', fontsize=14)
    plt.title('Verteilung der Werte', fontsize=16)
    st.pyplot(plt.gcf())


elif page == "Einfaches Modell":
    st.title("Einfaches Modell")

    df_simple_model = load_data()

    # Filteroptionen
    unique_position_categories = df_simple_model['PositionCategory'].unique().tolist()
    unique_position_categories.insert(0, 'Alle Positionen')
    position_category = st.selectbox('Wähle Position', options=unique_position_categories)

    min_value = int(df_simple_model['Value'].min())
    max_value = int(df_simple_model['Value'].max())
    value_range = st.slider('Wähle Wert in €', min_value=min_value, max_value=max_value, value=(min_value, max_value),
                            step=10000)

    min_age = int(df_simple_model['Age'].min())
    max_age = int(df_simple_model['Age'].max())
    age_range = st.slider('Wähle Alter', min_value=min_age, max_value=max_age, value=(min_age, max_age))

    # Filtern des DataFrames und Auswählen des Spielers mit dem höchsten Wert in 'DifferenceSimpleModelXGB'
    if position_category == 'Alle Positionen':
        mask = (df_simple_model['Value'].between(*value_range)) & (df_simple_model['Age'].between(*age_range))
    else:
        mask = (df_simple_model['PositionCategory'] == position_category) & (
            df_simple_model['Value'].between(*value_range)) & (df_simple_model['Age'].between(*age_range))
    top_player = df_simple_model.loc[
        mask, ['Name', 'Age', 'PositionCategory', 'Club', 'Value', 'PredictedValueSimpleModelXGB',
               'PercentDifferenceSimpleModelXGB']].nlargest(5, 'PercentDifferenceSimpleModelXGB')
    top_player.reset_index(drop=True, inplace=True)  # Reset index and remove index column

    # Filtern der Spalten 'Name' und 'Club'
    top_player = top_player.rename(columns={'Age': 'Alter', 'PositionCategory': 'Position', 'Club': 'Klub',
                                            'Value': 'Wert in €',
                                            'PredictedValueSimpleModelXGB': 'Vorausgesagter Wert Einfaches Modell',
                                            'PercentDifferenceSimpleModelXGB': 'Prozentuale Differenz'})

    # Zeige den Spieler in einem DataFrame an
    st.dataframe(top_player)
