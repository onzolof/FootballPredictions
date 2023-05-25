# Talent Tracker

## Projektstruktur
Das Projekt ist in mehrere Hauptordner unterteilt:

- `analysis`
- `data`
- `models`
- `scraping`
- `streamlit`

### `analysis`
Enthält Notebooks und Skripte für Datenanalyse und Modellierung.

- `Descriptive Analysis_V1.ipynb`: Erste deskriptive Analyse der Daten.
- `analysis_todo.md`: To-do-Liste für Analyseaufgaben.
- `data_analysis.ipynb`: Notebook mit weiterer Datenanalyse.
- `empty_values.ipynb`: Notebook zur Behandlung von empty values.
- `extensive_model_data_preprocessing_fs.ipynb` und `extensive_model_data_preprocessing_tw.ipynb`: Daten-Vorverarbeitung für das extensive model.
- `extensive_model_fs.ipynb` und `extensive_model_tw.ipynb`: Notebooks mit den extensive models.
- `feature_engineering.ipynb`: Notebook für Feature-Engineering.
- `model_predictions_full_merge.ipynb`: Notebook, das die Modelle zusammenführt.
- `performance-extensive-model-fs.csv` und `performance-extensive-model-tw.csv`: Leistung der extensive models.
- `performance-simple-model-fs.csv` und `performance-simple-model-tw.csv`: Leistung der simple models.
- `performance_plots.ipynb`: Notebook zur Erstellung von Leistungsdiagrammen.
- `simple_model_data_preprocessing_fs.ipynb` und `simple_model_data_preprocessing_tw.ipynb`: Daten-Vorverarbeitung für die simple models.
- `simple_model_fs.ipynb` und `simple_model_tw.ipynb`: Notebooks mit simple models.
- `utils.py`: Funktionen, die im gesamten Projekt verwendet werden.

### `data`
Enthält alle relevanten Datendateien, die während des Projekts verwendet und generiert wurden.

- Verschiedene CSV-Dateien, die bereinigte Daten, Modellergebnisse und Daten für die Modellierung enthalten.
- @Jonas hier noch Daten beschreiben welche wo benutzt...

### `models`
Speichert trainierte Maschinenlernmodelle für Vorhersagen.

- `extensive-model-xgb-fs.pkl` und `extensive-model-xgb-tw.pkl`: Gespeicherte extensive models.
- `simple-model-xgb-tw.pkl` und `simple-model-xgb.pkl`: Gespeicherte simple models.

### `scraping`
Enthält Dateien im Zusammenhang mit Daten-Scraping, -Bereinigung und -Verwaltung.

- `cleansed_data`: Verzeichnis mit bereinigten Daten aus dem Scraping.
- `scraped_data`: Verzeichnis mit roh gescrapten Daten.
- `Cheatsheet_Scrapy_Selenium-1.pdf`: Hilfsblatt für Scrapy und Selenium.
- `chromedriver_mac`: Chrome-Treiber für Mac OS.
- `config.yaml`: Konfigurationsdatei für den Scraping-Prozess.
- `data_cleansing.ipynb`: Notebook zur Datenbereinigung.
- `manager.py` und `worker.py`: Python-Skripte zur Verwaltung des Scraping-Prozesses.

### `streamlit`
Enthält Dateien im Zusammenhang mit der mit Streamlit erstellten Web-App.

- `app_v0.py`: Haupt-Streamlit-App-Datei.
- `requirements.txt`: Liste der Python-Pakete, die für das Deployment der Streamlit-App benötigt werden.

Link zur deployed Streamlit Web-App: https://onzolof-footballpredictions-streamlitapp-v0-3hmugi.streamlit.app/

## Hilfsmittel
- OpenAI's ChatGPT für die Bereitstellung von Codierungshilfe, Dokumentation und Problemlösungsstrategien.
