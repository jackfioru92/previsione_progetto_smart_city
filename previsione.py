import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min

# Carica il dataset delle città
df = pd.read_csv('cities.csv')

# Carica il dataset dei progetti
progetti_df = pd.read_csv('Dati_progetti.csv')

# Stampa i nomi delle colonne per il debug
print(progetti_df.columns)

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

# Funzione per gestire l'inserimento dei dati tramite interfaccia grafica
def submit():
    new_city = []
    for feature in numerical_columns:
        value = float(entries[feature].get())
        new_city.append(value)
    budget = float(budget_entry.get())
    most_similar_city = find_most_similar_city(new_city, kmeans, df)
    project_name, project_scope = find_best_project(most_similar_city, budget, progetti_df)
    result_label.config(text=f"La città più simile è: {most_similar_city}\nProgetto: {project_name}\nAmbito: {project_scope}")

# Creazione dell'interfaccia grafica
root = tk.Tk()
root.title("Previsione Nuova Città")

# Aggiungi un logo e ridimensionalo
original_logo = Image.open("logo.png")
resized_logo = original_logo.resize((100, 50), Image.LANCZOS)  # Ridimensiona il logo a 100x100 pixel
logo = ImageTk.PhotoImage(resized_logo)
logo_label = ttk.Label(root, image=logo)
logo_label.pack(pady=3)

# Aggiungi un titolo
title_label = ttk.Label(root, text="Inserisci i dati della nuova città", font=("Helvetica", 16))
title_label.pack(pady=3)

# Aggiungi un sottotitolo
subtitle_label = ttk.Label(root, text="Capstone di Giacomo Fiorucci, Giada Mancini, Emiliana Orero, David Colangeli, Dario Dicensi", font=("Helvetica", 12))
subtitle_label.pack(pady=2)

# Aggiungi una legenda
legend_text = """
Legenda:
Per Primario,secondario,terziario e quaternario inserire valore numerico tra 1 e 4.
Per Importanza amministrativa. 'Capitale nazionale': 1, 'Capitale regionale': 2, 'Hub economico': 3, 'Centro culturale': 4, 'Centro turistico': 5, 'Città satellite': 6.
"""
legend_label = ttk.Label(root, text=legend_text, font=("Helvetica", 10), justify="left")
legend_label.pack(pady=3)

entries = {}
for feature in numerical_columns:
    frame = ttk.Frame(root)
    frame.pack(fill='x', pady=5)
    label = ttk.Label(frame, text=feature)
    label.pack(side='left', padx=5)
    entry = ttk.Entry(frame)
    entry.pack(side='right', fill='x', expand=True, padx=5)
    entries[feature] = entry

# Aggiungi il campo di input per il budget
budget_frame = ttk.Frame(root)
budget_frame.pack(fill='x', pady=5)
budget_label = ttk.Label(budget_frame, text="Budget a disposizione per il progetto in euro")
budget_label.pack(side='left', padx=5)
budget_entry = ttk.Entry(budget_frame)
budget_entry.pack(side='right', fill='x', expand=True, padx=5)

submit_button = ttk.Button(root, text="Invia", command=submit)
submit_button.pack(pady=3)

result_label = ttk.Label(root, text="", font=("Helvetica", 12))
result_label.pack(pady=3)

root.mainloop()