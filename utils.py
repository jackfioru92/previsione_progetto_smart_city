import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances

def load_data():
    """Carica e preprocessa i dati delle città e dei progetti."""
    try:
        # Carica dataset principale città
        df = pd.read_csv('cities.csv')
        
        # Carica dataset progetti smart
        progetti_df = pd.read_csv('progetti_smart.csv')

        # Estrai temperature dal campo clima
        def extract_temperatures(clima):
            min_temp, max_temp = map(float, clima.replace('°C', '').split(' / '))
            return min_temp, max_temp

        df[['Temp_Min', 'Temp_Max']] = pd.DataFrame(
            df['Clima (range annuale)'].apply(extract_temperatures).tolist(),
            columns=['Temp_Min', 'Temp_Max']
        )
        
        # Carica dataset finanziamenti EU (solo colonne necessarie)
        finanziamenti_eu_df = pd.read_excel(
            'projects_2025-02-15_IT_con_codifica.xlsx',
            sheet_name='projects_2025-02-15_IT',
            usecols=[
                'Operation_Unique_Identifier',
                'Region3',
                'Total_Eligible_Expenditure_amount',
                'Project_EU_Budget',
                'Category_Label'
            ]
        )
        categorie_df = pd.read_excel(
            'projects_2025-02-15_IT_con_codifica.xlsx',
            sheet_name='projects_2025-02-15_IT_con codi'
        )
        
        # Pulizia e ordinamento province
        finanziamenti_eu_df['Region3'] = finanziamenti_eu_df['Region3'].fillna('Non specificata')
        # Converti tutti i valori in stringa
        finanziamenti_eu_df['Region3'] = finanziamenti_eu_df['Region3'].astype(str)
        # Rimuovi eventuali .0 dai numeri convertiti in stringa
        finanziamenti_eu_df['Region3'] = finanziamenti_eu_df['Region3'].apply(lambda x: x.replace('.0', '') if x.endswith('.0') else x)
        province = sorted(finanziamenti_eu_df['Region3'].unique())

        # Mappature per conversione dati categorici
        sector_map = {
            'Limitato': 1,
            'Moderato': 2,
            'Forte': 3,
            'Dominante': 4
        }
        
        importance_map = {
            'Capitale nazionale': 4,
            'Capitale regionale': 3,
            'Hub economico': 3,
            'Centro regionale': 2,
            'Città satellite': 1
        }

        # Converti campi categorici in numerici
        df['Importanza amministrativa'] = df['Importanza amministrativa'].map(importance_map)
        for col in ['Primario', 'Secondario', 'Terziario', 'Quaternario']:
            df[col] = df[col].map(sector_map)

        # Definizione colonne numeriche per analisi
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
            'Primario', 'Secondario',
            'Terziario', 'Quaternario'
        ]

        # Rimozione righe con dati mancanti
        df = df.dropna(subset=numerical_columns)
        
        # Normalizzazione dei dati numerici
        scaler = MinMaxScaler()
        df[numerical_columns] = scaler.fit_transform(df[numerical_columns])

        print("Dati caricati con successo:")
        print(f"- Città analizzate: {len(df)}")
        print(f"- Progetti smart: {len(progetti_df)}")
        print(f"- Finanziamenti EU: {len(finanziamenti_eu_df)}")
        print(f"- Province disponibili: {len(province)}")

        return df, progetti_df, finanziamenti_eu_df, categorie_df, scaler, numerical_columns, province

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
        
        # Trova top 5
        top_indices = np.argsort(similarities.flatten())[-5:][::-1]
        
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

def find_best_project(similar_cities, smart_city_scope, duration, progetti_df):
    """
    Trova il progetto migliore utilizzando i nomi esatti delle colonne del CSV.
    """
    try:
        print("\nDEBUG - Parametri ricevuti:")
        print(f"Smart City Scope: {smart_city_scope}")
        print(f"Duration: {duration}")
        print(f"Città simili: {similar_cities}")
        
        found_projects = []
        suggested_projects = []
        result = []
        
        result.append("RICERCA PROGETTI SMART CITY")
        result.append(f"Ambito richiesto: {smart_city_scope}")
        result.append(f"Durata richiesta: {duration}\n")
        
        for city, similarity in similar_cities[:5]:
            print(f"\nDEBUG - Analisi città: {city}")
            result.append(f"\nANALISI {city} (Similarità: {similarity:.2f}%)")
            
            # Verifica se la città è presente
            if city not in progetti_df['Città'].values:
                print(f"DEBUG - Città {city} non trovata in progetti_df")
                result.append(f"⚠ {city} non ha progetti nel database")
                continue
            
            city_projects = progetti_df[progetti_df['Città'] == city]
            
            # Analisi progetto 1
            try:
                project1_data = {
                    'nome': city_projects['Nome progetto 1'].iloc[0],
                    'ambito': city_projects['Ambito progetto 1'].iloc[0],
                    'durata': city_projects['Tipo di investimento 1'].iloc[0],
                    'descrizione': city_projects['Descrizione Progetto 1'].iloc[0],
                    'stato': city_projects['Attivo / Non attivo progetto 1'].iloc[0]
                }
                
                ambito_match1 = project1_data['ambito'] == smart_city_scope
                durata_match1 = project1_data['durata'] == duration
                
                result.append(f"\nProgetto 1: {project1_data['nome']}")
                result.append(f"Ambito: {project1_data['ambito']} {'✓' if ambito_match1 else '✗'}")
                result.append(f"Durata: {project1_data['durata']} {'✓' if durata_match1 else '✗'}")
                result.append(f"Stato: {project1_data['stato']}")
                
                project_info1 = {
                    'Città': city,
                    'Nome progetto': project1_data['nome'],
                    'Ambito progetto': project1_data['ambito'],
                    'Tipo di investimento': project1_data['durata'],
                    'Descrizione': project1_data['descrizione'],
                    'Stato': project1_data['stato'],
                    'Similarità': similarity
                }
                
                if ambito_match1 and durata_match1:
                    result.append("→ Match perfetto!")
                    found_projects.append(project_info1)
                elif ambito_match1 or durata_match1:
                    result.append("→ Match parziale")
                    suggested_projects.append(project_info1)
                
            except Exception as e:
                print(f"DEBUG - Errore analisi progetto 1: {str(e)}")
            
            # Analisi progetto 2
            try:
                project2_data = {
                    'nome': city_projects['Nome proggetto 2'].iloc[0],
                    'ambito': city_projects['Ambito progetto 2'].iloc[0],
                    'durata': city_projects['Tipo di investimento 2'].iloc[0],
                    'descrizione': city_projects['Descrizione progetto 2'].iloc[0],
                    'stato': city_projects['Attivo / Non attivo progetto 2'].iloc[0]
                }
                
                ambito_match2 = project2_data['ambito'] == smart_city_scope
                durata_match2 = project2_data['durata'] == duration
                
                result.append(f"\nProgetto 2: {project2_data['nome']}")
                result.append(f"Ambito: {project2_data['ambito']} {'✓' if ambito_match2 else '✗'}")
                result.append(f"Durata: {project2_data['durata']} {'✓' if durata_match2 else '✗'}")
                result.append(f"Stato: {project2_data['stato']}")
                
                project_info2 = {
                    'Città': city,
                    'Nome progetto': project2_data['nome'],
                    'Ambito progetto': project2_data['ambito'],
                    'Tipo di investimento': project2_data['durata'],
                    'Descrizione': project2_data['descrizione'],
                    'Stato': project2_data['stato'],
                    'Similarità': similarity
                }
                
                if ambito_match2 and durata_match2:
                    result.append("→ Match perfetto!")
                    found_projects.append(project_info2)
                elif ambito_match2 or durata_match2:
                    result.append("→ Match parziale")
                    suggested_projects.append(project_info2)
                
            except Exception as e:
                print(f"DEBUG - Errore analisi progetto 2: {str(e)}")
        
        # Risultati finali
        result.append("\n" + "="*50 + "\n")
        result.append("RISULTATI FINALI:")
        
        if not found_projects and not suggested_projects:
            result.append("\n❌ Nessun progetto trovato con i parametri specificati")
            
        if found_projects:
            result.append("\n✅ PROGETTI CON MATCH PERFETTO:")
            for proj in found_projects:
                result.extend([
                    f"\nCittà: {proj['Città']} (Similarità: {proj['Similarità']:.2f}%)",
                    f"Nome: {proj['Nome progetto']}",
                    f"Ambito: {proj['Ambito progetto']}",
                    f"Durata: {proj['Tipo di investimento']}",
                    f"Stato: {proj['Stato']}",
                    f"Descrizione: {proj['Descrizione']}"
                ])
        
        if suggested_projects:
            result.append("\n💡 PROGETTI ALTERNATIVI CONSIGLIATI:")
            for proj in suggested_projects[:3]:
                result.extend([
                    f"\nCittà: {proj['Città']} (Similarità: {proj['Similarità']:.2f}%)",
                    f"Nome: {proj['Nome progetto']}",
                    f"Ambito: {proj['Ambito progetto']}",
                    f"Durata: {proj['Tipo di investimento']}",
                    f"Stato: {proj['Stato']}",
                    f"Descrizione: {proj['Descrizione']}"
                ])
        
        return "\n".join(result)

    except Exception as e:
        print(f"DEBUG - Errore principale: {str(e)}")
        import traceback
        print(f"DEBUG - Traceback:\n{traceback.format_exc()}")
        return "⚠ Errore durante la ricerca dei progetti"
    
def get_available_funding(provincia, smart_city_scope, finanziamenti_eu_df, categorie_df):
    """Trova i finanziamenti disponibili per provincia e categoria smart city."""
    try:
        print("\nDEBUG - Analisi finanziamenti:")
        print(f"Provincia richiesta: {provincia}")
        print(f"Categoria Smart City originale: {smart_city_scope}")
        
        # Converti da Smart_Governance a Smart Governance per il confronto
        smart_city_scope_excel = smart_city_scope.replace('_', ' ')
        print(f"Categoria Smart City convertita per confronto: {smart_city_scope_excel}")
        
        # Verifica presenza categoria in categorie_df
        print(f"\nDEBUG - Categorie disponibili: {categorie_df['Category_Smart'].unique()}")
        if smart_city_scope_excel not in categorie_df['Category_Smart'].values:
            print(f"DEBUG - Categoria {smart_city_scope_excel} non trovata in categorie_df")
            return f"\nNessuna corrispondenza trovata per la categoria {smart_city_scope}"
        
        # Join tra i dataframe per ottenere la corrispondenza categoria
        categoria_corrispondente = categorie_df[
            categorie_df['Category_Smart'].str.strip() == smart_city_scope_excel
        ]['Category_Label'].values
        
        
        print(f"\nDEBUG - Categorie corrispondenti trovate: {categoria_corrispondente}")
        
        # Verifica presenza provincia
        print(f"\nDEBUG - Province disponibili: {finanziamenti_eu_df['Region3'].unique()}")
        if provincia not in finanziamenti_eu_df['Region3'].values:
            print(f"DEBUG - Provincia {provincia} non trovata in finanziamenti_eu_df")
            return f"\nNessun finanziamento trovato per la provincia {provincia}"
        
        # Filtra i finanziamenti per provincia e categoria
        finanziamenti_disponibili = finanziamenti_eu_df[
            (finanziamenti_eu_df['Region3'] == provincia) & 
            (finanziamenti_eu_df['Category_Label'].isin(categoria_corrispondente))
        ]
        
        print(f"\nDEBUG - Finanziamenti trovati: {len(finanziamenti_disponibili)}")
        
        if finanziamenti_disponibili.empty:
            print("DEBUG - Nessun finanziamento trovato con i criteri specificati")
            return "\nNessun finanziamento disponibile per questa combinazione di provincia e categoria."
        
        # Prepara il testo dei risultati
        result = f"\nFINANZIAMENTI DISPONIBILI PER LA PROVINCIA {provincia}\n"
        result += f"CATEGORIA SMART CITY: {smart_city_scope}\n\n"
        
        for idx, finanziamento in finanziamenti_disponibili.iterrows():
            print(f"\nDEBUG - Elaborazione finanziamento {idx}")
            try:
                result += "=" * 50 + "\n"
                result += f"URL Progetto: {finanziamento['Operation_Unique_Identifier']}\n"
                result += f"Spesa Totale Ammissibile: {finanziamento['Total_Eligible_Expenditure_amount']:,.2f} €\n"
                result += f"Budget EU Stanziato: {finanziamento['Project_EU_Budget']:,.2f} €\n"
            except Exception as e:
                print(f"DEBUG - Errore nell'elaborazione del finanziamento {idx}: {e}")
                continue
            
        return result
        
    except Exception as e:
        print(f"DEBUG - Errore nell'analisi dei finanziamenti: {e}")
        import traceback
        print(f"DEBUG - Traceback completo:\n{traceback.format_exc()}")
        return "Errore nell'analisi dei finanziamenti disponibili"
    
def validate_fields(entries, budget_entry):
    """Valida i campi input."""
    return all(entry.text().strip() for entry in entries.values()) and budget_entry.text().strip()