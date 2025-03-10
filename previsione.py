import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, 
                            QPushButton, QVBoxLayout, QHBoxLayout, QWidget, 
                            QTabWidget, QFormLayout, QComboBox)  # Aggiunto QComboBox
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
        
        # Font
        QFontDatabase.addApplicationFont("Montserrat-Bold.ttf")
        font = QFont("Montserrat", 10)
        
        # Widget principale
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("logo.png").scaled(150, 100, Qt.KeepAspectRatio)
        logo_label.setPixmap(logo_pixmap)
        main_layout.addWidget(logo_label, alignment=Qt.AlignCenter)
        
        # Titolo e sottotitolo
        title_label = QLabel("Inserisci i dati della nuova città")
        title_label.setObjectName("title")
        main_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        
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
        
        # Crea pagine
        self.pages = []
        self.page_layouts = []
        for i in range(3):
            page = QWidget()
            page.setMinimumHeight(150)
            self.tab_widget.addTab(page, f"Pagina {i+1}")
            self.pages.append(page)
            page_layout = QFormLayout(page)
            self.page_layouts.append(page_layout)
        
        # Entries dictionary
        self.entries = {}

        # Campo Smart City nella prima pagina
        smart_city_label = QLabel("Ambito di intervento Smart City")
        smart_city_label.setFont(font)

        # Container per combo e input
        smart_city_container = QWidget()
        smart_city_layout = QVBoxLayout(smart_city_container)
        smart_city_layout.setSpacing(5)
        smart_city_layout.setContentsMargins(0,0,0,0)

        # ComboBox per l'ambito
        self.smart_city_combo = QComboBox()
        self.smart_city_combo.setFont(font)
        self.smart_city_combo.addItems([
            "Smart_Mobility",
            "Smart_Environment", 
            "Smart_Economy",
            "Smart_People",
            "Smart_Living"
        ])
        self.smart_city_combo.setMaximumWidth(self.width() // 2)

        # Assembla il layout
        smart_city_layout.addWidget(self.smart_city_combo)

        # Aggiungi alla prima pagina
        self.page_layouts[0].addRow(smart_city_label, smart_city_container)

        # Campo durata progetto
        duration_label = QLabel("Aspettative durata progetto")
        duration_label.setFont(font)

        # Container per combo durata
        duration_container = QWidget()
        duration_layout = QVBoxLayout(duration_container)
        duration_layout.setSpacing(5)
        duration_layout.setContentsMargins(0,0,0,0)

        # ComboBox per la durata
        self.duration_combo = QComboBox()
        self.duration_combo.setFont(font)
        self.duration_combo.addItems([
            "Breve termine (2 anni)",
            "Medio termine (5 anni)",
            "Lungo termine (10 anni)"
        ])
        self.duration_combo.setMaximumWidth(self.width() // 2)

        # Assembla il layout
        duration_layout.addWidget(self.duration_combo)

        # Aggiungi alla prima pagina dopo Smart City
        self.page_layouts[0].addRow(duration_label, duration_container)

        # Layout temperature ridotto al 50%
        temp_layout = QHBoxLayout()
        temp_layout.setSpacing(0)
        temp_label = QLabel("Temperature (°C)")
        temp_label.setFont(font)

        # Container per min e max ridotto
        temp_inputs = QHBoxLayout()
        temp_inputs.setSpacing(15)

        # Input temperatura minima
        min_container = QWidget()
        min_layout = QHBoxLayout(min_container)
        min_layout.setSpacing(0)
        min_layout.setContentsMargins(0,0,0,0)
        temp_min_label = QLabel("Min:")
        temp_min_label.setFont(font)
        temp_min_label.setContentsMargins(0,0,0,0)
        self.entries['Temp_Min'] = QLineEdit()
        self.entries['Temp_Min'].setFont(font)
        self.entries['Temp_Min'].setFixedWidth(60)
        self.entries['Temp_Min'].setContentsMargins(0,0,0,0)
        min_layout.addWidget(temp_min_label)
        min_layout.addWidget(self.entries['Temp_Min'])

        # Input temperatura massima
        max_container = QWidget()
        max_layout = QHBoxLayout(max_container)
        max_layout.setSpacing(0)
        max_layout.setContentsMargins(0,0,0,0)
        temp_max_label = QLabel("Max:")
        temp_max_label.setFont(font)
        temp_max_label.setContentsMargins(0,0,0,0)
        self.entries['Temp_Max'] = QLineEdit()
        self.entries['Temp_Max'].setFont(font)
        self.entries['Temp_Max'].setFixedWidth(60)
        self.entries['Temp_Max'].setContentsMargins(0,0,0,0)
        max_layout.addWidget(temp_max_label)
        max_layout.addWidget(self.entries['Temp_Max'])

        # Assembla il layout
        temp_inputs.addWidget(min_container)
        temp_inputs.addWidget(max_container)

        # Container finale ridotto al 50%
        temp_container = QWidget()
        temp_container.setFixedWidth(self.width() // 2)  # Imposta larghezza al 50%
        temp_container.setLayout(temp_inputs)
        self.page_layouts[0].addRow(temp_label, temp_container)
                
        # Altri campi
        remaining_features = [f for f in numerical_columns if f not in ['Temp_Min', 'Temp_Max']]
        fields_per_page = (len(remaining_features) + 2) // 3
        
        for i, feature in enumerate(remaining_features):
            page_index = i // fields_per_page
            label = QLabel(feature)
            label.setFont(font)
            entry = QLineEdit()
            entry.setFont(font)
            entry.setMaximumWidth(self.width() // 2)
            self.entries[feature] = entry
            self.page_layouts[page_index].addRow(label, entry)
        
        # Campo budget
        budget_label = QLabel("Budget a disposizione per il progetto in euro")
        budget_label.setFont(font)
        self.budget_entry = QLineEdit()
        self.budget_entry.setFont(font)
        self.budget_entry.setMaximumWidth(self.width() // 2)
        self.page_layouts[-1].addRow(budget_label, self.budget_entry)
        
        # Layout bottoni
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)
        
        # Bottoni
        self.back_button = QPushButton("Indietro")
        self.back_button.setFont(font)
        self.back_button.setFixedWidth(100)
        self.back_button.clicked.connect(self.previous_page)
        button_layout.addWidget(self.back_button)
        
        self.continue_button = QPushButton("Continua")
        self.continue_button.setFont(font)
        self.continue_button.setFixedWidth(100)
        self.continue_button.clicked.connect(self.next_page)
        button_layout.addWidget(self.continue_button)
        
        self.submit_button = QPushButton("Invia")
        self.submit_button.setFont(font)
        self.submit_button.setFixedWidth(100)
        self.submit_button.clicked.connect(self.submit)
        button_layout.addWidget(self.submit_button)
        
        # Labels risultato e errore
        self.result_label = QLabel("")
        self.result_label.setFont(font)
        main_layout.addWidget(self.result_label, alignment=Qt.AlignCenter)
        
        self.error_label = QLabel("")
        self.error_label.setFont(font)
        self.error_label.setStyleSheet("color: red;")
        main_layout.addWidget(self.error_label, alignment=Qt.AlignCenter)
        
        # Inizializza bottoni
        self.update_buttons()
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
        if not validate_fields(self.entries, self.budget_entry):
            return
            
        try:
            # Raccogli i dati della città
            new_city = []
            for feature in numerical_columns:
                value = float(self.entries[feature].text())
                new_city.append(value)
            
            # Ottieni le città simili e crea il testo iniziale
            similar_cities = find_most_similar_cities(new_city, df, scaler, numerical_columns)
            result_text = "\nCITTÀ PIÙ SIMILI:\n"
            for city, similarity in similar_cities:
                result_text += f"{city}: {similarity:.2f}%\n"
                
            # Ottieni i parametri selezionati
            smart_city_scope = self.smart_city_combo.currentText()
            duration = self.duration_combo.currentText()
            
            # Aggiungi i progetti trovati
            result_text += "\n" + find_best_project(similar_cities, smart_city_scope, duration, progetti_df)
            
            # Mostra il risultato
            self.result_label.setText(result_text)
            
        except ValueError as e:
            self.result_label.setText("Errore: Inserisci solo valori numerici validi")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    applica_stile(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())