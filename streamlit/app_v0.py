import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import numpy as np

# https://www.uefa.com/nationalassociations/uefarankings/country/#/yr/2023

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


@st.cache_data
def load_model(position):
    if position == 'Torwart':
        return pickle.load(open('../models/simple-model-xgb-tw.pkl', 'rb'))
    else:
        return pickle.load(open('../models/simple-model-xgb.pkl', 'rb'))


st.sidebar.markdown("# Fussballspieler Prognose")
st.sidebar.markdown("___")

# Füge eine Seitenauswahl hinzu
page = st.sidebar.radio("Navigiere zu:", ("Hauptseite", "Metadaten",
                                          "Einfaches Modell", 'Einfaches Modell Prediction', 'Impressum'))

st.sidebar.markdown("___")

if page == "Hauptseite":
    # Titel der Streamlit-Seite
    st.title(
        "Vorhersage der Unter- oder Überbewertung von Fussballspielern")

    # Daten laden
    df_clean = load_data()

    # Erstelle ein Dataframe für das Filtern
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
        selected_data.reset_index(drop=True, inplace=True)
        st.dataframe(selected_data, width=st.expander('use_column_width=True'))
    else:
        st.write("Keine Ligen ausgewählt.")

elif page == "Metadaten":
    st.title("Spieler Metadaten")

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

    # Creating two columns for the first row
    col1, col2 = st.columns(2)

    # 1. Verteilung der Füsse
    col1.subheader("Verteilung der Füsse")
    filtered_df['Foot'] = filtered_df['Foot'].replace('beidfüßig', 'beidfüssig')
    foot_counts = filtered_df['Foot'].value_counts()

    # Define the color palette as a list
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

    # Creating two columns for the second row
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

elif page == "Einfaches Modell":
    st.title("Einfaches Modell")

    df_simple_model = load_data()

    # Create a new DataFrame for displaying and filtering
    df_display = df_simple_model.copy()

    # Ligen mit weniger als 100 Spielern in "Andere Ligen" zusammenfassen
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
        df_simple_model = df_simple_model.loc[mask_leagues]

        # Recalculate min and max for sliders based on selected data subset
        min_value = int(df_simple_model['Value'].min())
        max_value = int(df_simple_model['Value'].max())
        min_age = int(df_simple_model['Age'].min())
        max_age = int(df_simple_model['Age'].max())

    else:
        # Default min and max for sliders based on full dataset
        min_value = int(df_simple_model['Value'].min())
        max_value = int(df_simple_model['Value'].max())
        min_age = int(df_simple_model['Age'].min())
        max_age = int(df_simple_model['Age'].max())

    # Filteroptionen
    unique_position_categories = df_simple_model['PositionCategory'].unique().tolist()
    unique_position_categories.insert(0, 'Alle Positionen')
    position_category = st.selectbox('Wähle Position', options=unique_position_categories)

    value_range = st.slider('Wähle Wert in €', min_value=min_value, max_value=max_value, value=(min_value, max_value),
                            step=10000)

    age_range = st.slider('Wähle Alter', min_value=min_age, max_value=max_age, value=(min_age, max_age))

    # Filtern des DataFrames und Auswählen des Spielers mit dem höchsten Wert in 'PercentDifferenceSimpleModelXGB'
    if position_category == 'Alle Positionen':
        mask = (df_simple_model['Value'].between(*value_range)) & (df_simple_model['Age'].between(*age_range))
    else:
        mask = (df_simple_model['PositionCategory'] == position_category) & (
            df_simple_model['Value'].between(*value_range)) & (df_simple_model['Age'].between(*age_range))
    top_player = df_simple_model.loc[
        mask, ['Name', 'Age', 'PositionCategory', 'Club', 'Value', 'PredictedValueSimpleModelXGB',
               'PercentDifferenceSimpleModelXGB', 'Image']  # Include 'Image' column
    ].nlargest(5, 'PercentDifferenceSimpleModelXGB')
    top_player.reset_index(drop=True, inplace=True)  # Reset index and remove index column

    default_image_url = "https://img.a.transfermarkt.technology/portrait/big/13775-1662993749.jpg"

    # Create 5 columns for player images
    cols = st.columns(5)

    for i in range(len(top_player)):
        player_name = top_player.loc[i, 'Name']
        player_image_url = top_player.loc[i, 'Image']

        # Check if player_image_url is not NaN
        if pd.notna(player_image_url):
            # Streamlit code to display the player's image and name in a separate column
            cols[i].image(player_image_url, caption=player_name, use_column_width=True)
        else:
            cols[i].image(default_image_url, caption=player_name, use_column_width=True)

    # Dropping the 'PercentDifferenceSimpleModelXGB' column
    top_player = top_player.drop(columns=['PercentDifferenceSimpleModelXGB', 'Image'])

    # Filtern der Spalten 'Name' und 'Club'
    top_player = top_player.rename(columns={'Age': 'Alter', 'PositionCategory': 'Position', 'Club': 'Klub',
                                            'Value': 'Wert in €',
                                            'PredictedValueSimpleModelXGB': 'Vorausgesagter Wert in €'})

    # Zeige den Spieler in einem DataFrame an
    st.dataframe(top_player)


elif page == "Einfaches Modell Prediction":
    st.title("Einfaches Modell Prediction")

    df_simple_model = load_data()

    # Eingabefelder
    league_country = st.text_input('LeagueCountry')
    league = st.text_input('League')
    national_league_level = st.number_input('NationalLeagueLevel', min_value=1)
    club = st.text_input('Club')
    age = st.number_input('Age', min_value=15, max_value=50)
    nationality = st.text_input('Nationality')
    # Get unique values from the "position_category" column
    position_categories = df_simple_model['PositionCategory'].unique()

    # Dropdown for position_category
    position_category = st.selectbox('Position Category', position_categories)

    # Eingabe zu Dataframe
    if st.button('Predict'):
        model = load_model(position_category)
        input_data = pd.DataFrame({
            'LeagueCountry': [league_country],
            'League': [league],
            'NationalLeagueLevel': [national_league_level],
            'Club': [club],
            'Age': [age],
            'Nationality': [nationality]
        })

elif page == "Impressum":
    st.title("Impressum")

    # Description of the project
    st.subheader("Projektbeschreibung")
    st.write("""
    Dieses Projekt ist eine interaktive Fussball-Analyse-Web-App, die mit Streamlit erstellt wurde. Sie ermöglicht es den Nutzern, detaillierte Spielerdaten aus verschiedenen Ligen zu analysieren. 
    Sie können auch spezifische Spielerprofile anzeigen und detaillierte Statistiken über Spielerleistungen einsehen. 
    Dieses Projekt ist eine Initiative der Universität St. Gallen.
    """)

    # Displaying the team members
    st.subheader("Teammitglieder")

    # List of team members and their picture URLs
    team_members = [
        {"name": "Jonas Vogel", "image": "https://media.licdn.com/dms/image/C4D03AQGB-L6UZNlipg/profile-displayphoto-shrink_400_400/0/1605261553367?e=1689811200&v=beta&t=qBV4LqPDDk1Y69xKhSX-5AXnuz9f9Sgrj1BFFxpSrBE"},
        {"name": "Marc Sieber", "image": "https://media.licdn.com/dms/image/D4E03AQHRC4BZfbzuKA/profile-displayphoto-shrink_400_400/0/1673692455616?e=1689811200&v=beta&t=tATRPN49y9-cSxJ6kw74YYhDTIb2jUmyJBMDnvzk0Kg"},
        {"name": "Stella Sun", "image": "https://media.licdn.com/dms/image/C4D03AQEHwqW5NOHI4w/profile-displayphoto-shrink_400_400/0/1635084696283?e=1689811200&v=beta&t=jb0s9JrNN5rfVvxUa7c6Kzs1J3-Jmsl-YGsN2pYn0KE"},
        {"name": "Linda Fuchs", "image": "https://media.licdn.com/dms/image/C4E03AQHrNegmSDQcrg/profile-displayphoto-shrink_400_400/0/1663147757767?e=1689811200&v=beta&t=4Q6nBQiJjz_o2zY-3PG2zsjoxs0lLJUJau-VNklrv00"},
        {"name": "Eliane Elsässer", "image": "https://media.licdn.com/dms/image/C5603AQH3rBcv0YC-eg/profile-displayphoto-shrink_400_400/0/1639067508762?e=1689811200&v=beta&t=k0n7L3ypUEiHJITiHRweRXHalVpbhhu80HjCEqBPN38"}
    ]

    # Display the team members in a single row
    cols = st.columns(5)
    for i, member in enumerate(team_members):
        cols[i].image(member["image"], use_column_width=True)
        cols[i].write(member["name"])

