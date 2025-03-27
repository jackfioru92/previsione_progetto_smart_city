# DOCUMENTAZIONE SISTEMA SMART CITY

## PANORAMICA GENERALE
L'algoritmo è progettato per aiutare nella pianificazione di progetti smart city, combinando dati di città esistenti, progetti già realizzati e opportunità di finanziamento EU.

### Funzionalità Principali

#### 1. Analisi Città Simili
- Raccoglie caratteristiche di una nuova città (popolazione, costi, trasporti, etc.)
- Confronta questi dati con un database di città esistenti
- Usa pesi personalizzati per dare più importanza a certi aspetti
- Trova le 5 città più simili con percentuali di corrispondenza

#### 2. Ricerca Progetti Smart City
- Cerca progetti nelle città simili identificate
- Confronta progetti per ambito (es. Smart Mobility) e durata
- Identifica:
  * Match perfetti (stesso ambito e durata)
  * Match parziali (suggerimenti alternativi)
- Fornisce dettagli completi dei progetti trovati

#### 3. Ricerca Finanziamenti
- Cerca finanziamenti EU disponibili per:
  * Provincia selezionata
  * Categoria smart city scelta
- Mostra dettagli come:
  * URL del progetto
  * Budget disponibile
  * Spese ammissibili

### Processo Utente
1. Input Richiesti:
   - Dati della nuova città
   - Ambito smart city interessato
   - Provincia di riferimento
   - Durata desiderata del progetto

2. Output Forniti:
   - Lista città simili con percentuali
   - Progetti pertinenti realizzati
   - Finanziamenti EU disponibili
   - Dettagli implementazione
   - Suggerimenti alternativi

## ASPETTI TECNICI

### 1. Librerie Utilizzate

#### Pandas (pd)
- Manipolazione e analisi dati
- Funzionalità:
  * Lettura CSV ed Excel
  * Gestione DataFrame
  * Pulizia dati
  * Operazioni di filtraggio e aggregazione

#### NumPy (np)
- Calcoli numerici
- Funzionalità:
  * Calcoli matematici efficienti
  * Array multidimensionali
  * Ordinamento risultati
  * Operazioni vettoriali

#### Scikit-learn (sklearn)
1. MinMaxScaler
   - Normalizza dati in range [0,1]
   - Formula: X_scaled = (X - X_min) / (X_max - X_min)
   - Rende comparabili features con scale diverse

2. KMeans
   - Algoritmo di clustering
   - Raggruppa città simili
   - Divide dati in k gruppi basati su distanza

3. pairwise_distances
   - Calcola distanze tra coppie di punti
   - Implementa varie metriche di distanza

### 2. Metodo di Confronto

#### Distanza Euclidea
- Metrica principale per confronto città
- Formula: sqrt(sum((x_i - y_i)^2))
- Vantaggi:
  * Intuitiva
  * Sensibile a tutte le dimensioni
  * Efficace per dati normalizzati

#### Sistema di Pesi
- Personalizzazione importanza features
- Pesi maggiori per:
  * Densità popolazione (0.15)
  * Costo della vita (0.15)
  * Trasporti pubblici (0.10)
  * Temperature (0.10 ciascuna)
  * Punti interesse (0.10)

#### Calcolo Similarità
- Conversione distanza in similarità
- Formula: similarità = 100 * (1 - (distanza / distanza_max))
- Range: 0-100%

### 3. Ottimizzazioni

#### Preprocessing
- Pulizia dati mancanti
- Normalizzazione features
- Codifica variabili categoriche

#### Performance
- Calcoli vettoriali NumPy
- Ottimizzazione memoria
- Gestione matrici sparse

#### Robustezza
- Gestione errori
- Log debugging
- Controlli consistenza

### 4. Gestione Dati

#### Dataset Input
- cities.csv: dati città esistenti
- progetti_smart.csv: progetti realizzati
- projects_2025-02-15_IT_con_codifica.xlsx: finanziamenti EU

#### Preprocessing
- Normalizzazione dati numerici
- Conversione categorie in valori numerici
- Gestione dati mancanti
- Pulizia e validazione input

#### Validazione
- Controllo completezza dati
- Verifica coerenza input
- Gestione errori e eccezioni

