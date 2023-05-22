import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import numpy as np

# Die App Seitenkonfiguration festlegen
st.set_page_config(
    page_title="Talent Tracker",
    page_icon="⚽",
    layout="wide"
)


# Funktion für die Erstellung von Dummyvariablen festlegen
def process_categorical(df, column, min_count=10):
    value_counts = df[column].value_counts()
    frequent_categories = value_counts[value_counts >= min_count].index
    df.loc[:, 'processed_' + column] = df[column].apply(lambda x: x if x in frequent_categories else 'other')
    dummies = pd.get_dummies(df['processed_' + column], prefix=column)
    df = df.drop(column, axis=1)
    df = df.drop('processed_' + column, axis=1)
    df = pd.concat([df, dummies], axis=1)
    return df


# Funktion für das Laden des gesamten Datensets
@st.cache_data
def load_data():
    df = pd.read_csv('data/df_model_full_merge.csv', index_col=0)
    return df


# Funktion für das Laden des FS Datensets
@st.cache_data
def load_data_fs():
    df = pd.read_csv('data/df_simple_model_fs_streamlit.csv', index_col=0)
    return df


# Funktion für das Laden des TW Datensets
@st.cache_data
def load_data_tw():
    df = pd.read_csv('data/df_simple_model_tw_streamlit.csv', index_col=0)
    return df


# Funktion für das Laden des Modells in Abhängigkeit der Position
@st.cache_data
def load_model(position):
    if position == 'Torwart':
        return pickle.load(open('models/simple-model-xgb-tw.pkl', 'rb'))
    else:
        return pickle.load(open('models/simple-model-xgb.pkl', 'rb'))


# Navigationsleiste erstellen
st.sidebar.image('https://i.postimg.cc/66PwVzmF/TT-new.png')
st.sidebar.markdown("___")

# Füge eine Seitenauswahl hinzu
page = st.sidebar.radio("Navigiere zu:", ("Datenpool", "Deskriptive Analyse",
                                          "Talentsuche", 'Prediction', 'Impressum ©'))

st.sidebar.markdown("___")

if page == "Datenpool":
    # Titel der Streamlit-Seite
    st.title(
        "Spieler Datenpool")

    # Daten laden
    df_clean = load_data()

    # Erstelle ein Dataframe für das Filtern
    df_display = df_clean.copy()

    # Ligen mit weniger als 100 Spielern in andere Ligen zusammenfassen
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
        selected_data.reset_index(drop=True, inplace=True)
        st.dataframe(selected_data, width=1000)
    else:
        st.write("Keine Ligen ausgewählt.")

elif page == "Deskriptive Analyse":
    st.title("Deskriptive Analyse")

    # Daten laden
    df_meta = load_data()

    # Liga-Ebene für den Filter auswählen
    unique_league_levels = sorted(df_meta['NationalLeagueLevel'].unique().tolist())
    unique_league_levels.insert(0, 'Alle')
    selected_level = st.selectbox('Wähle Liga-Ebene', options=unique_league_levels)

    # Filtern des DataFrames nach ausgewählter Liga-Ebene
    if selected_level == 'Alle':
        filtered_df = df_meta
    else:
        mask = df_meta['NationalLeagueLevel'] == selected_level
        filtered_df = df_meta.loc[mask]

    # Erstelle zwei Spalten für die erste Zeile
    col1, col2 = st.columns(2)

    # 1. Verteilung der Füsse
    col1.subheader("Verteilung der Füsse")
    filtered_df['Foot'] = filtered_df['Foot'].replace('beidfüßig', 'beidfüssig')
    foot_counts = filtered_df['Foot'].value_counts()

    # Lege eine grüne Farbpalette als Liste fest
    colors = plt.cm.Greens(np.linspace(0, 1, len(foot_counts)))
    fig, ax = plt.subplots()
    ax.pie(foot_counts, labels=foot_counts.index, autopct='%1.1f%%', startangle=90, colors=colors)
    ax.axis('equal')
    col1.pyplot(fig)

    # 2. Verteilung der Positionskategorien
    col2.subheader("Verteilung der Positionskategorien")
    position_counts = filtered_df['PositionCategory'].value_counts()
    plt.figure(figsize=(12, 8))
    sns.barplot(x=position_counts.values, y=position_counts.index, palette="Greens_r")
    plt.xlabel('Anzahl der Spieler', fontsize=14)
    plt.ylabel('Positionskategorien', fontsize=14)
    plt.title('Verteilung der Positionskategorien', fontsize=16)
    col2.pyplot(plt.gcf())

    # Erstelle zwei Spalten für die zweite Zeile
    col3, col4 = st.columns(2)

    # 3. Verteilung des Alters
    col3.subheader("Verteilung des Alters")
    plt.figure(figsize=(12, 8))
    sns.histplot(filtered_df['Age'], bins=30, kde=True, color='green')
    plt.xlabel('Alter', fontsize=14)
    plt.ylabel('Anzahl der Spieler', fontsize=14)
    plt.title('Verteilung des Alters', fontsize=16)
    col3.pyplot(plt.gcf())

    # 4. Verteilung der Werte
    col4.subheader("Verteilung der Werte")
    plt.figure(figsize=(12, 8))
    sns.histplot(filtered_df['Value'], bins=30, kde=True, color='green')
    plt.xlabel('Wert in €', fontsize=14)
    plt.ylabel('Anzahl der Spieler', fontsize=14)
    plt.title('Verteilung der Werte', fontsize=16)
    col4.pyplot(plt.gcf())

elif page == "Talentsuche":
    st.title("Talentsuche")

    # Daten laden
    df_model = load_data()

    # Erstelle ein Dataframe für das Filtern
    df_display = df_model.copy()

    # Ligen mit weniger als 100 Spielern in andere Ligen zusammenfassen
    mask = df_display.groupby('League')['Name'].transform('count') < 100
    df_display['DisplayLeague'] = df_display['League']
    df_display['DisplayLeagueCountry'] = df_display['LeagueCountry']
    df_display.loc[mask, 'DisplayLeague'] = 'Andere Ligen'
    df_display.loc[mask, 'DisplayLeagueCountry'] = 'Andere Länder'
    df_display['League_Country'] = df_display['DisplayLeague'] + '/' + df_display['DisplayLeagueCountry']

    # Ligen für den Filter auswählen
    leagues = df_display['League_Country'].unique()
    selected_leagues = st.multiselect("Ligen auswählen", options=leagues)

    # Spieler der ausgewählten Ligen anzeigen
    if selected_leagues:
        mask_leagues = df_display['League_Country'].isin(selected_leagues)
        df_model = df_model.loc[mask_leagues]

    # Filteroptionen
    unique_position_categories = df_model['PositionCategory'].unique().tolist()
    unique_position_categories.insert(0, 'Alle Positionen')
    position_category = st.selectbox('Wähle Position', options=unique_position_categories)

    # Anpassung der Schieberegler basierend auf den ausgewählten Ligen und der Positionskategorie
    if position_category != 'Alle Positionen':
        df_model = df_model[df_model['PositionCategory'] == position_category]

    # Minimal- und Maximalwerte für Schieberegler auf der Grundlage der ausgewählten Daten neu festlegen
    min_value = int(df_model['Value'].min())
    max_value = int(df_model['Value'].max())
    min_age = int(df_model['Age'].min())
    max_age = int(df_model['Age'].max())

    value_range = st.slider('Wähle Wert in €', min_value=min_value, max_value=max_value, value=(min_value, max_value),
                            step=10000)

    age_range = st.slider('Wähle Alter', min_value=min_age, max_value=max_age, value=(min_age, max_age))

    # Filtern des DataFrames und Auswählen des Spielers mit dem höchsten Wert in PercentDifferenceConsistent
    if position_category == 'Alle Positionen':
        mask = (df_model['Value'].between(*value_range)) & (df_model['Age'].between(*age_range))
    else:
        mask = (df_model['PositionCategory'] == position_category) & (
            df_model['Value'].between(*value_range)) & (df_model['Age'].between(*age_range))
    top_player = df_model.loc[
        mask, ['Name', 'Age', 'PositionCategory', 'Club', 'Value', 'PredictedValueConsistent',
               'PercentDifferenceConsistent', 'Image']
    ].nlargest(5, 'PercentDifferenceConsistent')
    top_player.reset_index(drop=True, inplace=True)

    # Lege Rudi Völler als Bild fest für alle Spieler ohne ein Bild
    default_image_url = "https://img.a.transfermarkt.technology/portrait/big/13775-1662993749.jpg"

    # 5 Spalten für Player-Bilder erstellen
    cols = st.columns(5)

    for i in range(len(top_player)):
        player_name = top_player.loc[i, 'Name']
        player_image_url = top_player.loc[i, 'Image']

        # Prüfen ob Bild vorhanden
        if pd.notna(player_image_url):
            cols[i].image(player_image_url, caption=player_name, use_column_width=True)
        else:
            cols[i].image(default_image_url, caption=player_name, use_column_width=True)

    # PercentDifferenceConsistent und Image entfernen
    top_player = top_player.drop(columns=['PercentDifferenceConsistent', 'Image'])

    # Spalten umbenennen
    top_player = top_player.rename(columns={'Age': 'Alter', 'PositionCategory': 'Position', 'Club': 'Klub',
                                            'Value': 'Wert in €',
                                            'PredictedValueConsistent': 'Vorausgesagter Wert in €'})

    # Zeige die Spieler in einem DataFrame an
    st.dataframe(top_player, width=1000)

elif page == "Prediction":
    st.title("Prediction")

    # Daten laden
    df_model = load_data()

    # Eindeutige Positionskategorien festlegen
    position_categories = df_model['PositionCategory'].unique()
    # Dropdown für Positionskategorie
    position_category = st.selectbox('Position Kategorie', position_categories)

    # Lade entsprechend der Positionskategorie die Daten
    if position_category == "Torwart":
        df_model_load = load_data_tw()
    else:
        df_model_load = load_data_fs()

    # Eingabefelder
    unique_clubs = df_model_load['Club'].unique()
    selected_club = st.selectbox('Klub', unique_clubs)

    # Automatisches Ausfüllen anderer Felder basierend auf dem Klub
    selected_club_data = df_model_load[df_model_load['Club'] == selected_club].iloc[0]
    league_country = selected_club_data['LeagueCountry']
    league = selected_club_data['League']
    national_league_level = selected_club_data['NationalLeagueLevel']
    st.text(league + ' (' +  league_country + ' - ' + national_league_level + ')')

    # Eingabefelder
    age = st.number_input('Alter', min_value=15, max_value=50)
    former_international = st.checkbox('Ehemaliger Internationaler Spieler')
    active_international = st.checkbox('Aktiver Internationaler Spieler')
    club_since = st.number_input('Vertrag seit (in Tagen)', min_value=0, value=0)

    # Eindeutige internationale Teams festlegen
    unique_international_teams = df_model_load['InternationalTeam'].unique()
    # Dropdown für internationale Teams
    selected_international_team = st.selectbox('Internationales Team', unique_international_teams, index=0)

    # Eingabefelder
    international_games = st.number_input('Anzahl Internationale Spiele', min_value=0)

    # Zusätzliche Eingabefelder für Feldspieler
    if position_category != "Torwart":
        st.subheader("Eingabefelder für Feldspieler")
        # Eindeutige Nationalität festlegen
        unique_nationalities = df_model_load['Nationality'].dropna().unique()

        # Position in Abhängigkeit der ausgewählten Positionskategorie
        unique_positions = df_model_load[df_model_load['PositionCategory'] == position_category]['Position'].unique()

        # Dropdown für Nationalität
        nationality = st.selectbox('Nationalität', unique_nationalities)

        # Dropdown für Position
        position = st.selectbox('Position', unique_positions)

        # Eingabefelder
        international_goals = st.number_input('Anzahl Internationale Tore', min_value=0)

        # Eindeutige Sponsoren festlegen
        unique_suppliers = df_model_load['Supplier'].unique()

        # Dropdown für Sponsoren
        supplier = st.selectbox('Sponsor', unique_suppliers)
    else:
        st.write()

    if st.button('Predict'):
        if position_category == "Torwart":
            # Eingabe in Wörterbuch
            # Zweimal festlegen da sonst kein Dataframe mit pd.Dataframe erstellt wird
            input_data = {
                'LeagueCountry': [league_country, league_country],
                'NationalLeagueLevel': [national_league_level, national_league_level],
                'InternationalTeam': [selected_international_team, selected_international_team],
                'League': [league, league],
                'Club': [selected_club, league],
                'Age': [age, age],
                'ClubSince': [club_since, club_since],
                'ActiveInternational': [int(active_international), int(active_international)],
                'FormerInternational': [int(former_international), int(active_international)],
                'InternationalGames': [international_games, international_games],
                'Trending': [1, 1],
            }

            # Eingabedaten in DataFrame umwandeln
            input_data_df = pd.DataFrame(input_data)

        else:
            # Eingabe in Wörterbuch
            # Zweimal festlegen da sonst kein Dataframe mit pd.Dataframe erstellt wird
            input_data = {
                'LeagueCountry': [league_country, league_country],
                'League': [league, league],
                'NationalLeagueLevel': [national_league_level, national_league_level],
                'Club': [selected_club, selected_club],
                'Age': [age, age],
                'ClubSince': [club_since, club_since],
                'Nationality': [nationality, nationality],
                'Position': [position, position],
                'PositionCategory': [position_category, position_category],
                'Supplier': [supplier, supplier],
                'InternationalTeam': [selected_international_team, selected_international_team],
                'ActiveInternational': [int(active_international), int(active_international)],
                'FormerInternational': [int(former_international), int(former_international)],
                'InternationalGames': [international_games, international_games],
                'InternationalGoals': [international_goals, international_goals],
                'Trending': [1, 1],
            }

            # Eingabedaten in DataFrame umwandeln
            input_data_df = pd.DataFrame(input_data)

        # Dummyvariablen erstellen
        if position_category == "Torwart":
            df_model_tw = load_data_tw()
            full_data_df = pd.concat([df_model_tw, input_data_df], ignore_index=True, sort=False)
            full_data_df = process_categorical(full_data_df, 'InternationalTeam', 5)
            full_data_df = process_categorical(full_data_df, 'League')
            full_data_df = process_categorical(full_data_df, 'Club')
            full_data_df = process_categorical(full_data_df, 'LeagueCountry', 5)
            full_data_df = process_categorical(full_data_df, 'NationalLeagueLevel', 5)
        else:
            df_model_fs = load_data_fs()
            full_data_df = pd.concat([df_model_fs, input_data_df], ignore_index=True, sort=False)
            full_data_df = process_categorical(full_data_df, 'Supplier')
            full_data_df = process_categorical(full_data_df, 'InternationalTeam', 5)
            full_data_df = process_categorical(full_data_df, 'League')
            full_data_df = process_categorical(full_data_df, 'Club')
            full_data_df = process_categorical(full_data_df, 'LeagueCountry', 5)
            full_data_df = process_categorical(full_data_df, 'NationalLeagueLevel', 5)
            full_data_df = process_categorical(full_data_df, 'Nationality')
            full_data_df = process_categorical(full_data_df, 'Position', 5)
            full_data_df = process_categorical(full_data_df, 'PositionCategory', 5)

        # Eingabefelder wieder aus dem Dataframe holen und verarbeiten
        input_row = full_data_df.iloc[-2:, :]
        input_row_df = pd.DataFrame(input_row)
        input_row_df = input_row_df.drop('Value', axis=1)
        input_row_df.reset_index(drop=True, inplace=True)

        # Laden des Modells in Abhängigkeit der Positionskategorie
        model = load_model(position_category)

        # Übergabe an das Modell zur Vorhersage
        prediction = model.predict(input_row_df)
        rounded_prediction = round(max(prediction[0], 10000))

        # Vorhersage darstellen
        prediction_str = "{:,}".format(rounded_prediction).replace(",", "'")
        prediction_text = 'Prediction: ' + prediction_str + ' €'
        st.markdown(f'<p style="font-size: 18px;">{prediction_text}</p>', unsafe_allow_html=True)

elif page == "Impressum ©":
    st.title("Impressum ©")

    # Beschreibung des Projekts
    st.subheader("Projektbeschreibung")
    st.write("""Dieses Projekt ist eine interaktive Fussball-Analyse-Applikation, die mit Streamlit erstellt 
    wurde. Als Grundlage wurden die Daten der Webseite Transfermarkt verwendet. Die Applikation ermöglicht es 
    den Nutzern, detaillierte Spielerdaten aus verschiedenen Ligen zu analysieren. Zudem lassen sich
    unter- und überbewertete Spieler identifizieren sowie Vorhersagen über den Wert neuer Spieler treffen. 
    Dieses Projekt wurde im Rahmen des Kurses Methoden: 
    Big Data und Data Science der Universität St.Gallen erstellt.
    
    ©2023 Universität St.Gallen""")

    # Anzeige der Teammitglieder
    st.subheader("Teammitglieder")

    # Liste der Teammitglieder und ihre Bild-URLs
    team_members = [
        {"name": "Jonas Vogel", "image": "https://media.licdn.com/dms/image/C4D03AQGB-L6UZNlipg/profile-displayphoto-shrink_400_400/0/1605261553367?e=1689811200&v=beta&t=qBV4LqPDDk1Y69xKhSX-5AXnuz9f9Sgrj1BFFxpSrBE"},
        {"name": "Marc Sieber", "image": "https://media.licdn.com/dms/image/D4E03AQHRC4BZfbzuKA/profile-displayphoto-shrink_400_400/0/1673692455616?e=1689811200&v=beta&t=tATRPN49y9-cSxJ6kw74YYhDTIb2jUmyJBMDnvzk0Kg"},
        {"name": "Stella Sun", "image": "https://media.licdn.com/dms/image/C4D03AQEHwqW5NOHI4w/profile-displayphoto-shrink_400_400/0/1635084696283?e=1689811200&v=beta&t=jb0s9JrNN5rfVvxUa7c6Kzs1J3-Jmsl-YGsN2pYn0KE"},
        {"name": "Linda Fuchs", "image": "https://media.licdn.com/dms/image/C4E03AQHrNegmSDQcrg/profile-displayphoto-shrink_400_400/0/1663147757767?e=1689811200&v=beta&t=4Q6nBQiJjz_o2zY-3PG2zsjoxs0lLJUJau-VNklrv00"},
        {"name": "Eliane Elsässer", "image": "https://media.licdn.com/dms/image/C5603AQH3rBcv0YC-eg/profile-displayphoto-shrink_400_400/0/1639067508762?e=1689811200&v=beta&t=k0n7L3ypUEiHJITiHRweRXHalVpbhhu80HjCEqBPN38"}
    ]

    # Anzeige der Teammitglieder in einer einzigen Zeile
    cols = st.columns(5)
    for i, member in enumerate(team_members):
        cols[i].image(member["image"], use_column_width=True)
        cols[i].write(member["name"])