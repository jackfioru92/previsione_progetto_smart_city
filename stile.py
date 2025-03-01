from PyQt5.QtGui import QFont, QFontDatabase

def applica_stile(app):
    # Carica il font Montserrat
    QFontDatabase.addApplicationFont("Montserrat-Bold.ttf")
    
    # Definisci i colori
    colore_sfondo = "#ffffff"
    colore_titolo = "#dba332"
    colore_testo = "#40403e"
    colore_bottone = "#dba332"
    colore_testo_bottone = "#ffffff"
    
    # Imposta lo stile globale
    app.setStyleSheet(f"""
        QWidget {{
            background-color: {colore_sfondo};
            color: {colore_testo};
            font-family: Montserrat;
        }}
        QLabel {{
            color: {colore_testo};
        }}
        QLabel#title {{
            color: {colore_titolo};
            font-size: 16pt;
            font-weight: bold;
        }}
        QLineEdit {{
            border: 1px solid {colore_titolo};
            border-radius: 10px;
            padding: 5px;
        }}
        QPushButton {{
            background-color: {colore_bottone};
            color: {colore_testo_bottone};
            border-radius: 10px;
            padding: 10px;
            min-width: 100px;
        }}
        QTabWidget::pane {{
            border: 1px solid {colore_titolo};
        }}
        QTabBar::tab {{
            background: {colore_sfondo};
            border: 1px solid {colore_titolo};
            padding: 10px;
        }}
        QTabBar::tab:selected {{
            background: {colore_titolo};
            color: {colore_testo_bottone};
        }}
    """)