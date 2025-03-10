import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances

def load_data():
    """Carica e preprocessa i dati delle città."""
    try:
        # Carica datasets
        df = pd.read_csv('cities.csv')
        progetti_df = pd.read_csv('progetti_smart.csv')

        # Estrai temperature
        def extract_temperatures(clima):
            min_temp, max_temp = map(float, clima.replace('°C', '').split(' / '))
            return min_temp, max_temp

        df[['Temp_Min', 'Temp_Max']] = pd.DataFrame(
            df['Clima (range annuale)'].apply(extract_temperatures).tolist(),
            columns=['Temp_Min', 'Temp_Max']
        )

        # Mappature
        sector_map = {'Limitato': 1, 'Moderato': 2, 'Forte': 3, 'Dominante': 4}
        importance_map = {
            'Capitale nazionale': 4,
            'Capitale regionale': 3,
            'Hub economico': 3,
            'Centro regionale': 2,
            'Città satellite': 1
        }

        # Converti categorie
        df['Importanza amministrativa'] = df['Importanza amministrativa'].map(importance_map)
        for col in ['Primario', 'Secondario', 'Terziario', 'Quaternario']:
            df[col] = df[col].map(sector_map)

        numerical_columns = [
            'Densità di popolazione (ab/km²)',
            'Costo della vita (€/mese)',
            'Trasporto pubblico (unità totali)',
            'Temp_Min', 'Temp_Max',
            'Punti di interesse turistici',
            'Aeroporti principali',
            'Livello di inquinamento (PM2.5)',
            'Età media (anni)',
            'Media eventi annuali',
            'Importanza amministrativa',
            'Primario', 'Secondario', 'Terziario', 'Quaternario'
        ]

        df = df.dropna(subset=numerical_columns)
        
        # Normalizza dati
        scaler = MinMaxScaler()
        df[numerical_columns] = scaler.fit_transform(df[numerical_columns])

        return df, progetti_df, scaler, numerical_columns

    except Exception as e:
        print(f"Errore durante il caricamento dei dati: {e}")
        raise

def find_most_similar_cities(new_city_features, df, scaler, numerical_columns):
    """Trova le città più simili con similarità migliorate."""
    try:
        # Pesi personalizzati per caratteristiche più importanti
        weights = {
            'Densità di popolazione (ab/km²)': 0.15,
            'Costo della vita (€/mese)': 0.15,
            'Trasporto pubblico (unità totali)': 0.10,
            'Temp_Min': 0.10,
            'Temp_Max': 0.10,
            'Punti di interesse turistici': 0.10,
            'Livello di inquinamento (PM2.5)': 0.05,
            'Età media (anni)': 0.05,
            'Media eventi annuali': 0.05,
            'Importanza amministrativa': 0.05,
            'Primario': 0.02,
            'Secondario': 0.03,
            'Terziario': 0.03,
            'Quaternario': 0.02
        }

        # Normalizza input
        new_city_df = pd.DataFrame([new_city_features], columns=numerical_columns)
        new_city_scaled = scaler.transform(new_city_df)

        # Applica pesi
        weighted_data = df[numerical_columns].copy()
        weighted_new_city = new_city_scaled.copy()
        
        for i, col in enumerate(numerical_columns):
            if col in weights:
                weighted_data[col] *= weights[col]
                weighted_new_city[0][i] *= weights[col]

        # Calcola similarità usando distanza euclidea inversa
        distances = pairwise_distances(weighted_data, weighted_new_city)
        similarities = 100 * (1 - (distances / distances.max()))
        
        # Trova top 3
        top_indices = np.argsort(similarities.flatten())[-3:][::-1]
        
        similar_cities = []
        print("\nDETTAGLI SIMILARITÀ:")
        
        for idx in top_indices:
            city = df.iloc[idx]['City']
            similarity = similarities[idx][0]
            similar_cities.append((city, similarity))
            print(f"\n{city} - Similarità: {similarity:.2f}%")
            print("Valori significativi (pesati):")
            for col in numerical_columns:
                val = weighted_data.iloc[idx][col]
                if abs(val) > 0.01:
                    print(f"  {col}: {val:.4f}")

        return similar_cities

    except Exception as e:
        print(f"Errore nel calcolo delle similarità: {e}")
        return [("Errore nell'analisi", 0)]

def find_best_project(city, budget, progetti_df):
    """Trova il progetto migliore dato budget e città."""
    try:
        city_projects = progetti_df[progetti_df['Città'] == city]
        if city_projects.empty:
            return "Nessun progetto trovato", ""
        
        projects = []
        if 'Nome progetto 1' in progetti_df.columns:
            projects.append((
                city_projects['Nome progetto 1'].iloc[0],
                city_projects['Ambito progetto 1'].iloc[0],
                city_projects['Costo progetto 1'].iloc[0]
            ))
        
        if 'Nome progetto 2' in progetti_df.columns:
            projects.append((
                city_projects['Nome progetto 2'].iloc[0],
                city_projects['Ambito progetto 2'].iloc[0],
                city_projects['Costo progetto 2'].iloc[0]
            ))

        valid_projects = [(name, scope, cost) for name, scope, cost in projects if cost <= budget]
        if not valid_projects:
            return "Nessun progetto adatto trovato", ""
            
        best_project = min(valid_projects, key=lambda x: x[2])
        return best_project[0], best_project[1]

    except Exception as e:
        print(f"Errore nella ricerca del progetto: {e}")
        return "Errore nella ricerca", ""

def validate_fields(entries, budget_entry):
    """Valida i campi input."""
    return all(entry.text().strip() for entry in entries.values()) and budget_entry.text().strip()