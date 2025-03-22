import pandas as pd

def clean_excel_file():
    try:
        # Leggi il file Excel
        print("Lettura del file Excel...")
        excel_file = 'projects_2025-02-15_IT_con_codifica.xlsx'
        
        # Leggi entrambi i fogli
        df1 = pd.read_excel(excel_file, sheet_name='projects_2025-02-15_IT')
        df2 = pd.read_excel(excel_file, sheet_name='projects_2025-02-15_IT_con codi')
        
        # Mantieni solo le colonne specificate nel primo foglio
        columns_to_keep = [
            'Operation_Unique_Identifier',
            'Region3',
            'Total_Eligible_Expenditure_amount',
            'Project_EU_Budget',
            'Category_Label'
        ]
        
        df1 = df1[columns_to_keep]
        
        # Pulisci la colonna Region3
        print("Pulizia della colonna Region3...")
        df1['Region3'] = df1['Region3'].fillna('Non specificata')
        df1['Region3'] = df1['Region3'].astype(str)
        df1['Region3'] = df1['Region3'].apply(lambda x: x.split('|')[0].strip())
        
        # Salva il file con entrambi i fogli
        print("Salvataggio del file...")
        with pd.ExcelWriter(excel_file) as writer:
            df1.to_excel(writer, sheet_name='projects_2025-02-15_IT', index=False)
            df2.to_excel(writer, sheet_name='projects_2025-02-15_IT_con codi', index=False)
            
        print("File Excel aggiornato con successo!")
        print(f"Colonne mantenute nel primo foglio: {', '.join(columns_to_keep)}")
        
    except Exception as e:
        print(f"Errore durante l'elaborazione del file: {e}")

if __name__ == "__main__":
    clean_excel_file()