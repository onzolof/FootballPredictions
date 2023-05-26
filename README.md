# Talent Tracker
Dieses Projekt ist eine interaktive Fussball-Analyse-Applikation, die mit Streamlit erstellt wurde. Als Grundlage wurden die Daten der Webseite Transfermarkt verwendet. Die Applikation ermöglicht es den Nutzern, detaillierte Spielerdaten aus verschiedenen Ligen zu analysieren. Zudem lassen sich unter- und überbewertete Spieler identifizieren sowie Vorhersagen über den Wert neuer Spieler treffen. Dieses Projekt wurde im Rahmen des Kurses Methoden: Big Data und Data Science der Universität St.Gallen erstellt.

## Projektmitglieder
- Jonas Vogel
- Marc Sieber
- Stella Sun
- Linda Fuchs
- Eliane Elsässer

## Projektstruktur
Das Projekt ist in mehrere Hauptordner unterteilt:

- `analysis`
- `data`
- `models`
- `scraping`
- `streamlit`

### `analysis`
Enthält Notebooks und Skripte für Datenanalyse und Modellierung.

- `Descriptive Analysis_V1.ipynb`: Deskriptive Analyse der Daten.
- `data_analysis.ipynb`: Notebook mit erstem Versuch einer Datenanalyse.
- `empty_values.ipynb`: Notebook zur Behandlung von empty values.
- `extensive_model_data_preprocessing_fs.ipynb` und `extensive_model_data_preprocessing_tw.ipynb`: Daten-Vorverarbeitung für das extensive model.
- `extensive_model_fs.ipynb` und `extensive_model_tw.ipynb`: Notebooks mit den extensive models.
- `feature_engineering.ipynb`: Notebook für Feature-Engineering.
- `model_predictions_full_merge.ipynb`: Notebook, das die Modelle zusammenführt.
- `performance-extensive-model-fs.csv` und `performance-extensive-model-tw.csv`: Leistung der extensive models mit unterschiedlichen Feature-Kombinationen.
- `performance-simple-model-fs.csv` und `performance-simple-model-tw.csv`: Leistung der simple models mit unterschiedlichen Feature-Kombinationen.
- `performance_plots.ipynb`: Notebook zur Erstellung von Leistungsdiagrammen.
- `simple_model_data_preprocessing_fs.ipynb` und `simple_model_data_preprocessing_tw.ipynb`: Daten-Vorverarbeitung für die simple models.
- `simple_model_fs.ipynb` und `simple_model_tw.ipynb`: Notebooks mit simple models.
- `utils.py`: Funktionen, die im gesamten Projekt verwendet werden.

### `data`
Enthält alle relevanten Datendateien, die während des Projekts verwendet und generiert wurden.

- `df_clean.csv`: Datensatz, welcher für die Modelle vorverarbeitet wurde. Dieser beispielsweise keine Datumsformate mehr und es wurden einzelne Features hinzugefügt (PositionCategory, Cards & Trending). Gleichzeitig wurden Daten verworfen, die für das Training irrelevant sind, z.B. Link zum Instagram-Account.
- `df_extensive_model_fs.csv` & `df_extensive_model_fs_unfiltered.csv`: Vorverarbeitete Daten für das extensive FS-Modell. Dieses File enthält X und y im Endzustand. Die Variante '...unfiltered' umfasst ausserdem die für das Training ausgeschlossenen Ausreisser Mbappe & Haaland.
- `df_extensive_model_fs_results.csv`: Beinhaltet alle Predictions des extensive FS-Modells.
- `df_extensive_model_tw.csv`: Vorverarbeitete Daten für das extensive TW-Modell. Dieses File enthält X und y im Endzustand.
- `df_extensive_model_tw_results.csv`: Beinhaltet alle Predictions des extensive TW-Modells.
- `df_model_full_merge.csv`: Kombinierter Datensatz aus `df_clean.csv` als Basis mit den Predictions aller Modelle.
- `df_simple_model_fs.csv` & `df_simple_model_fs_unfiltered.csv`: Vorverarbeitete Daten für das einfache FS-Modell. Dieses File enthält X und y im Endzustand. Die Variante '...unfiltered' umfasst ausserdem die für das Training ausgeschlossenen Ausreisser Mbappe & Haaland.
- `df_simple_model_fs_results.csv`: Beinhaltet alle Predictions des einfachen FS-Modells.
- `df_simple_model_fs_streamlit.csv`: FS-Modell-Datengrundlage für die Streamlit-App für die Prediction auf dem einfachen Modell.
- `df_simple_model_tw.csv`: Vorverarbeitete Daten für das einfache TW-Modell. Dieses File enthält X und y im Endzustand.
- `df_simple_model_tw_results.csv`: Beinhaltet alle Predictions des einfachen TW-Modells.
- `df_simple_model_tw_streamlit.csv`: TW-Modell-Datengrundlage für die Streamlit-App für die Prediction auf dem einfachen Modell.

### `models`
Speichert trainierte Maschinenlernmodelle für Vorhersagen.

- `extensive-model-xgb-fs.pkl` und `extensive-model-xgb-tw.pkl`: Gespeicherte extensive models.
- `simple-model-xgb-tw.pkl` und `simple-model-xgb.pkl`: Gespeicherte simple models.

### `scraping`
Enthält Dateien im Zusammenhang mit Daten-Scraping, -Bereinigung und -Verwaltung.

- `cleansed_data`: Verzeichnis mit bereinigten Daten aus dem Scraping.
- `scraped_data`: Verzeichnis mit roh gescrapten Daten.
- `chromedriver_mac`: Chrome-Treiber für Mac OS.
- `config.yaml`: Konfigurationsdatei für den Scraping-Prozess.
- `data_cleansing.ipynb`: Notebook zur Datenbereinigung.
- `manager.py` und `worker.py`: Python-Skripte zum Scrapen der Daten von Transfermarkt. Durch Starten des manager.py werden die Scraping-Links auf mehrere Worker-Instanzen aufgeteilt.

### `streamlit`
Enthält Dateien im Zusammenhang mit der mit Streamlit erstellten Web-App.

- `app_v0.py`: Haupt-Streamlit-App-Datei.
- `requirements.txt`: Liste der Python-Pakete, die für das Deployment der Streamlit-App benötigt werden.

Link zur deployed Streamlit Web-App: https://onzolof-footballpredictions-streamlitapp-v0-3hmugi.streamlit.app/

## Datenverarbeitungs-Prozess

1. Daten werden gescraped und im Verzeichnis `scraping` abgelegt. Pro Scraping-Worker existiert ein Daten-File.
2. Anschliessend werden die Datensätze im Notebook `data_cleansing.ipynb` zusammengefasst und um Text-Noise vom Scraping bereinigt. Das Resultat ist ein File im Verzeichnis `cleansed_data`.
3. Mit dem Notebook `empty_values.ipynb` werden die Daten für den ML-Anwendungsfall vorverarbeitet und es resultiert das `df_clean.csv`.
4. Im Anschluss wird pro Modell das jeweilige Preprocessing-Notebook ausgeführt. Entsprechend entstehen die Input-Daten für die Modelle im Verzeichnis `data`.
5. In den jeweiligen Modell-Notebooks werden die einzelnen Modelle evaluiert und optimiert. Zum Schluss werden, in denselben Notebooks, die optimierten Modelle auf den Input-Datensatz angewandt und die Predictions der einzelnen Modelle werden in den Results-Files im Verzeichnis `data` abgelegt.
6. Die einzelnen Resultate werden mit dem Notebook `model_prediction_full_merge.ipynb` zusammengefasst. Der Output wird ebenfalls ins Verzeichnis `data` exportiert.
7. Die Performance der einzelnen Modelle kann nun im Notebook `performance_plots.ipynb` eingesehen werden.

## Hilfsmittel
- OpenAI's ChatGPT für die Bereitstellung von Codierungshilfe, Dokumentation und Problemlösungsstrategien.
