import sys
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QTabWidget, QFormLayout
from PyQt5.QtGui import QFont, QFontDatabase, QIcon, QPixmap
from PyQt5.QtCore import Qt
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min
from stile import applica_stile

# Carica il dataset delle città
df = pd.read_csv('cities.csv')

# Carica il dataset dei progetti
progetti_df = pd.read_csv('Dati_progetti.csv')

# Preprocessa la colonna "Clima (range annuale)"
def extract_temperature(clima):
    min_temp, max_temp = clima.replace('°C', '').split(' / ')
    return (float(min_temp) + float(max_temp)) / 2

df['Clima (range annuale)'] = df['Clima (range annuale)'].apply(extract_temperature)

# Mappa per la colonna "Importanza amministrativa"
importance_map = {
    'Capitale nazionale': 1,
    'Capitale regionale': 2,
    'Hub economico': 3,
    'Centro culturale': 4,
    'Centro turistico': 5,
    'Città satellite': 6
}

# Mappa per le colonne "Primario", "Secondario", "Terziario" e "Quaternario"
sector_map = {
    'Limitato': 1,
    'Moderato': 2,
    'Forte': 3,
    'Dominante': 4
}

df['Importanza amministrativa'] = df['Importanza amministrativa'].map(importance_map)
df['Primario'] = df['Primario'].map(sector_map)
df['Secondario'] = df['Secondario'].map(sector_map)
df['Terziario'] = df['Terziario'].map(sector_map)
df['Quaternario'] = df['Quaternario'].map(sector_map)

numerical_columns = ['Densità di popolazione (ab/km²)', 'Costo della vita (€/mese)', 
                     'Trasporto pubblico (unità totali)', 'Clima (range annuale)', 
                     'Punti di interesse turistici', 'Aeroporti principali', 
                     'Livello di inquinamento (PM2.5)', 'Età media (anni)', 
                     'Media eventi annuali', 'Importanza amministrativa',
                     'Primario', 'Secondario', 'Terziario', 'Quaternario']

df = df.dropna(subset=numerical_columns)

scaler = MinMaxScaler()
df[numerical_columns] = scaler.fit_transform(df[numerical_columns])

# Inizializzazione del modello KMeans con 50 cluster
kmeans = KMeans(n_clusters=50, random_state=42)
df['Cluster'] = kmeans.fit_predict(df[numerical_columns])

# Funzione per trovare la città più simile
def find_most_similar_city(new_city_features, kmeans, df):
    new_city_scaled = scaler.transform([new_city_features])
    new_city_cluster = kmeans.predict(new_city_scaled)
    cluster_data = df[df['Cluster'] == new_city_cluster[0]]
    if cluster_data.empty:
        return "Nessuna città trovata"
    distances, indices = pairwise_distances_argmin_min(new_city_scaled, cluster_data[numerical_columns], metric='euclidean')
    if indices[0] >= len(cluster_data):
        return "Nessuna città trovata"
    most_similar_city = cluster_data.iloc[int(indices[0])]['City']
    return most_similar_city

# Funzione per trovare il progetto più adatto
def find_best_project(city, budget, progetti_df):
    city_projects = progetti_df[progetti_df['Città'] == city]
    if city_projects.empty:
        return "Nessun progetto trovato", ""
    
    project1_cost = city_projects['Costo progetto 1'].values[0]
    project2_cost = city_projects['Costo progetto 2'].values[0]
    
    if project1_cost <= budget and (project1_cost <= project2_cost or project2_cost > budget):
        project_name = city_projects['Nome progetto 1'].values[0]
        project_scope = city_projects['Ambito progetto 1'].values[0]
    elif project2_cost <= budget:
        project_name = city_projects['Nome progetto 2'].values[0]
        project_scope = city_projects['Ambito progetto 2'].values[0]
    else:
        return "Nessun progetto adatto trovato", ""
    
    return project_name, project_scope

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Previsione Nuova Città")
        self.setGeometry(100, 100, 800, 600)
        
        # Carica il font Montserrat
        QFontDatabase.addApplicationFont("Montserrat-Bold.ttf")
        font = QFont("Montserrat", 10)
        
        # Widget principale
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Layout principale
        main_layout = QVBoxLayout(main_widget)
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("logo.png").scaled(150, 100, Qt.KeepAspectRatio)
        logo_label.setPixmap(logo_pixmap)
        main_layout.addWidget(logo_label, alignment=Qt.AlignCenter)
        
        # Titolo
        title_label = QLabel("Inserisci i dati della nuova città")
        title_label.setObjectName("title")
        main_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        
        # Sottotitolo
        subtitle_label = QLabel("Capstone di Giacomo Fiorucci, Giada Mancini, Emiliana Orero, David Colangeli, Dario Dicensi")
        subtitle_label.setFont(font)
        main_layout.addWidget(subtitle_label, alignment=Qt.AlignCenter)
        
        # Legenda
        legend_text = """
        Legenda:
        Per Primario,secondario,terziario e quaternario inserire valore numerico tra 1 e 4.
        Per Importanza amministrativa. 'Capitale nazionale': 1, 'Capitale regionale': 2, 'Hub economico': 3, 'Centro culturale': 4, 'Centro turistico': 5, 'Città satellite': 6.
        """
        legend_label = QLabel(legend_text)
        legend_label.setFont(font)
        main_layout.addWidget(legend_label, alignment=Qt.AlignLeft)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Pagine
        self.pages = []
        self.page_layouts = []
        for i in range(3):
            page = QWidget()
            page.setMinimumHeight(150)  # Imposta un'altezza minima per le pagine
            self.tab_widget.addTab(page, f"Pagina {i+1}")
            self.pages.append(page)
            page_layout = QFormLayout(page)
            self.page_layouts.append(page_layout)
        
        # Layout delle pagine
        self.entries = {}
        fields_per_page = (len(numerical_columns) + 2) // 3  # Distribuisci i campi tra le pagine
        for i, feature in enumerate(numerical_columns):
            page_index = i // fields_per_page
            label = QLabel(feature)
            label.setFont(font)
            entry = QLineEdit()
            entry.setFont(font)
            entry.setMaximumWidth(self.width() // 2)  # Imposta la larghezza al 50% dello spazio disponibile
            self.entries[feature] = entry
            self.page_layouts[page_index].addRow(label, entry)
        
        # Campo di input per il budget
        budget_label = QLabel("Budget a disposizione per il progetto in euro")
        budget_label.setFont(font)
        self.budget_entry = QLineEdit()
        self.budget_entry.setFont(font)
        self.budget_entry.setMaximumWidth(self.width() // 2)  # Imposta la larghezza al 50% dello spazio disponibile
        self.page_layouts[-1].addRow(budget_label, self.budget_entry)
        
        # Layout per i bottoni "Indietro", "Continua" e "Invia"
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)
        
        # Bottone "Indietro"
        self.back_button = QPushButton("Indietro")
        self.back_button.setFont(font)
        self.back_button.setFixedWidth(100)  # Imposta una larghezza fissa per i bottoni
        self.back_button.clicked.connect(self.previous_page)
        button_layout.addWidget(self.back_button)
        
        # Bottone "Continua"
        self.continue_button = QPushButton("Continua")
        self.continue_button.setFont(font)
        self.continue_button.setFixedWidth(100)  # Imposta una larghezza fissa per i bottoni
        self.continue_button.clicked.connect(self.next_page)
        button_layout.addWidget(self.continue_button)
        
        # Bottone "Invia"
        self.submit_button = QPushButton("Invia")
        self.submit_button.setFont(font)
        self.submit_button.setFixedWidth(100)  # Imposta una larghezza fissa per i bottoni
        self.submit_button.clicked.connect(self.submit)
        button_layout.addWidget(self.submit_button)
        
        # Risultato
        self.result_label = QLabel("")
        self.result_label.setFont(font)
        main_layout.addWidget(self.result_label, alignment=Qt.AlignCenter)
        
        # Aggiorna i bottoni in base alla pagina corrente
        self.update_buttons()
        
        # Connetti il segnale di cambio pagina
        self.tab_widget.currentChanged.connect(self.update_buttons)
    
    def next_page(self):
        current_index = self.tab_widget.currentIndex()
        if current_index < self.tab_widget.count() - 1:
            self.tab_widget.setCurrentIndex(current_index + 1)
    
    def previous_page(self):
        current_index = self.tab_widget.currentIndex()
        if current_index > 0:
            self.tab_widget.setCurrentIndex(current_index - 1)
    
    def update_buttons(self):
        current_index = self.tab_widget.currentIndex()
        self.back_button.setVisible(current_index > 0)
        self.continue_button.setVisible(current_index < self.tab_widget.count() - 1)
        self.submit_button.setVisible(current_index == self.tab_widget.count() - 1)
    
    def submit(self):
        new_city = []
        for feature in numerical_columns:
            value = float(self.entries[feature].text())
            new_city.append(value)
        budget = float(self.budget_entry.text())
        most_similar_city = find_most_similar_city(new_city, kmeans, df)
        project_name, project_scope = find_best_project(most_similar_city, budget, progetti_df)
        self.result_label.setText(f"La città più simile è: {most_similar_city}\nProgetto: {project_name}\nAmbito: {project_scope}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Applica lo stile
    applica_stile(app)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())