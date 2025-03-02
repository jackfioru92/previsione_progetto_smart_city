import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

def load_data():
    """Carica e preprocessa i dati usando MinMaxScaler."""
    df = pd.read_csv('cities.csv')
    progetti_df = pd.read_csv('Dati_progetti.csv')

    # Preprocessa clima
    def extract_temperature(clima):
        min_temp, max_temp = clima.replace('°C', '').split(' / ')
        return (float(min_temp) + float(max_temp)) / 2

    df['Clima (range annuale)'] = df['Clima (range annuale)'].apply(extract_temperature)

    # Mappature
    sector_map = {'Limitato': 1, 'Moderato': 2, 'Forte': 3, 'Dominante': 4}
    importance_map = {
        'Capitale nazionale': 4,
        'Capitale regionale': 3,
        'Hub economico': 3,
        'Centro regionale': 2,
        'Città satellite': 1
    }

    # Converti colonne categoriche
    df['Importanza amministrativa'] = df['Importanza amministrativa'].map(importance_map)
    for col in ['Primario', 'Secondario', 'Terziario', 'Quaternario']:
        df[col] = df[col].map(sector_map)

    numerical_columns = [
        'Densità di popolazione (ab/km²)', 'Costo della vita (€/mese)',
        'Trasporto pubblico (unità totali)', 'Clima (range annuale)',
        'Punti di interesse turistici', 'Aeroporti principali',
        'Livello di inquinamento (PM2.5)', 'Età media (anni)',
        'Media eventi annuali', 'Importanza amministrativa',
        'Primario', 'Secondario', 'Terziario', 'Quaternario'
    ]

    df = df.dropna(subset=numerical_columns)
    
    # Usa MinMaxScaler
    scaler = MinMaxScaler()
    df[numerical_columns] = scaler.fit_transform(df[numerical_columns])

    return df, progetti_df, scaler, numerical_columns

def find_most_similar_cities(new_city_features, df, scaler, numerical_columns):
    """Trova le città più simili usando MinMaxScaler."""
    # Normalizza nuovi dati
    new_city_df = pd.DataFrame([new_city_features], columns=numerical_columns)
    new_city_scaled = scaler.transform(new_city_df)
    
    # Calcola similarità
    similarities = cosine_similarity(df[numerical_columns], new_city_scaled).flatten()
    similarities = (similarities + 1) / 2 * 100  # Normalizza a percentuale [0,100]
    
    # Trova top 3
    top_indices = np.argsort(similarities)[::-1][:3]
    
    similar_cities = []
    print("\nDETTAGLI SIMILARITÀ:")
    print("\nCittà target (valori normalizzati):")
    for i, col in enumerate(numerical_columns):
        print(f"  {col}: {new_city_scaled[0][i]:.4f}")
    
    for idx in top_indices:
        city = df.iloc[idx]['City']
        similarity = similarities[idx]
        similar_cities.append((city, similarity))
        print(f"\n{city} - Similarità: {similarity:.2f}%")
        print("Valori normalizzati:")
        for col in numerical_columns:
            val = df.iloc[idx][col]
            if abs(val) > 0.01:  # Mostra solo valori significativi
                print(f"  {col}: {val:.4f}")
    
    return similar_cities

def find_best_project(city, budget, progetti_df):
    """Trova il progetto migliore dato budget e città."""
    try:
        # Verifica se la città esiste
        city_projects = progetti_df[progetti_df['Città'] == city]
        if city_projects.empty:
            return "Nessun progetto trovato", ""
        
        # Lista per contenere i progetti validi
        valid_projects = []
        
        # Controlla il primo progetto se esiste
        if 'Nome progetto 1' in progetti_df.columns and 'Costo progetto 1' in progetti_df.columns:
            nome1 = city_projects['Nome progetto 1'].iloc[0]
            ambito1 = city_projects['Ambito progetto 1'].iloc[0]
            costo1 = city_projects['Costo progetto 1'].iloc[0]
            if costo1 <= budget:
                valid_projects.append((nome1, ambito1, costo1))
        
        # Controlla il secondo progetto se esiste
        if 'Nome progetto 2' in progetti_df.columns and 'Costo progetto 2' in progetti_df.columns:
            nome2 = city_projects['Nome progetto 2'].iloc[0]
            ambito2 = city_projects['Ambito progetto 2'].iloc[0]
            costo2 = city_projects['Costo progetto 2'].iloc[0]
            if costo2 <= budget:
                valid_projects.append((nome2, ambito2, costo2))
        
        # Se non ci sono progetti validi
        if not valid_projects:
            return "Nessun progetto adatto trovato", ""
            
        # Trova il progetto con il costo minore
        best_project = min(valid_projects, key=lambda x: x[2])
        return best_project[0], best_project[1]
        
    except Exception as e:
        print(f"Errore nel trovare il progetto: {e}")
        return "Errore nella ricerca del progetto", ""
def validate_fields(entries, budget_entry):
    """Valida i campi input."""
    return all(entry.text().strip() for entry in entries.values()) and budget_entry.text().strip()