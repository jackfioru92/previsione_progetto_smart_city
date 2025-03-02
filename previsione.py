import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QTabWidget, QFormLayout
from PyQt5.QtGui import QFont, QFontDatabase, QPixmap
from PyQt5.QtCore import Qt
from stile import applica_stile
from animazioni import animate_transition
from utils import load_data, find_most_similar_cities, find_best_project, validate_fields

# Carica i dataset
df, progetti_df, scaler, numerical_columns = load_data()

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
        
        # Messaggio di errore
        self.error_label = QLabel("")
        self.error_label.setFont(font)
        self.error_label.setStyleSheet("color: red;")
        main_layout.addWidget(self.error_label, alignment=Qt.AlignCenter)
        
        # Aggiorna i bottoni in base alla pagina corrente
        self.update_buttons()
        
        # Connetti il segnale di cambio pagina
        self.tab_widget.currentChanged.connect(self.update_buttons)
    
    def next_page(self):
        current_index = self.tab_widget.currentIndex()
        if current_index < self.tab_widget.count() - 1:
            next_index = current_index + 1
            animate_transition(self.tab_widget, current_index, next_index)
            self.tab_widget.setCurrentIndex(next_index)
    
    def previous_page(self):
        current_index = self.tab_widget.currentIndex()
        if current_index > 0:
            next_index = current_index - 1
            animate_transition(self.tab_widget, current_index, next_index)
            self.tab_widget.setCurrentIndex(next_index)
    
    def update_buttons(self):
        current_index = self.tab_widget.currentIndex()
        self.back_button.setVisible(current_index > 0)
        self.continue_button.setVisible(current_index < self.tab_widget.count() - 1)
        self.submit_button.setVisible(current_index == self.tab_widget.count() - 1)
    
    def submit(self):
        """Gestisce la sottomissione del form."""
        if not validate_fields(self.entries, self.budget_entry):
            return
            
        try:
            # Raccogli i dati inseriti
            new_city = []
            for feature in numerical_columns:
                value = float(self.entries[feature].text())
                new_city.append(value)
            
            budget = float(self.budget_entry.text())
            
            # Trova città simili (senza weights)
            similar_cities = find_most_similar_cities(new_city, df, scaler, numerical_columns)
            
            result_text = "Le città più simili sono:\n"
            for city, similarity in similar_cities:
                result_text += f"{city}: {similarity:.2f}%\n"
            
            # Trova il progetto migliore per la città più simile
            most_similar_city = similar_cities[0][0]
            project_name, project_scope = find_best_project(most_similar_city, budget, progetti_df)
            result_text += f"\nProgetto più adatto per {most_similar_city}:\n{project_name}\nAmbito: {project_scope}"
            
            self.result_label.setText(result_text)
            
        except ValueError as e:
            self.result_label.setText("Errore: Inserisci solo valori numerici validi")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Applica lo stile
    applica_stile(app)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())