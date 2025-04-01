import pandas as pd

def clean_excel_file():
    try:
        print("Lettura del file Excel...")
        excel_file = 'projects_2025-02-15_IT_con_codifica.xlsx'
        
        # Leggi il primo foglio
        df1 = pd.read_excel(excel_file, sheet_name='projects_2025-02-15_IT')
        print("\nColonne nel primo foglio:")
        print(df1.columns.tolist())
        
        # Mantieni solo le colonne necessarie nel primo foglio
        columns_to_keep = [
            'Operation_Unique_Identifier',
            'Region3',
            'Total_Eligible_Expenditure_amount',
            'Project_EU_Budget',
            'Category_Label'
        ]
        df1 = df1[columns_to_keep]
        
        # Leggi il secondo foglio
        df2 = pd.read_excel(excel_file, sheet_name='projects_2025-02-15_IT_con codi')
        print("\nColonne nel secondo foglio:")
        print(df2.columns.tolist())
        print("\nPrime righe del secondo foglio:")
        print(df2.head())
        
        # Aspetta input utente per verificare le colonne
        input("\nPremi Enter dopo aver verificato i nomi delle colonne...")
        
        # Crea un nuovo DataFrame con le colonne corrette
        new_df2 = pd.DataFrame(columns=['Category_Of_Intervention', 'Category_Label', 'Category_Smart'])
        
        # Mappatura colonne (da aggiornare dopo aver visto l'output)
        column_mapping = {
            'Unnamed: 0': 'Category_Of_Intervention',
            'Unnamed: 1': 'Category_Label',
            'Unnamed: 12': 'Category_Smart'
        }
        
        # Rinomina le colonne
        df2 = df2.rename(columns=column_mapping)
        
        # Copia i dati
        for new_col, old_col in column_mapping.items():
            new_df2[new_col] = df2[old_col].dropna()
        
        # Pulisci gli spazi e rimuovi righe duplicate
        new_df2 = new_df2.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        new_df2 = new_df2.drop_duplicates()
        
        print("\nStruttura finale del secondo foglio:")
        print(new_df2.head())
        
        # Salva entrambi i fogli nel file Excel
        print("\nSalvataggio del file pulito...")
        with pd.ExcelWriter(excel_file) as writer:
            df1.to_excel(writer, sheet_name='projects_2025-02-15_IT', index=False)
            new_df2.to_excel(writer, sheet_name='projects_2025-02-15_IT_con codi', index=False)
        
        print("File Excel aggiornato con successo!")
        
    except Exception as e:
        print(f"Errore durante l'elaborazione del file: {e}")
        import traceback
        print(f"Traceback completo:\n{traceback.format_exc()}")

if __name__ == "__main__":
    clean_excel_file()