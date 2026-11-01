import pandas as pd
import numpy as np

# 1. Genereer de tijdreeks voor 1 week (168 uur)
timestamps = pd.date_range(start="2026-06-01 00:00", periods=168, freq="h")

# 2. Maak Opwek-dataset (Solar Generation in MWh)
# Overdag opwek, 's nachts geen zon
solar_generation = [max(0, np.sin((h % 24) * np.pi / 12) * 15 + np.random.normal(0, 2)) for h in range(168)]
df_opwek = pd.DataFrame({
    'Tijdstip': timestamps,
    'Opwek_MWh': solar_generation
})

# 3. Maak Prijs-dataset (Marktprijs in €/MWh)
# Prijzen dalen meestal overdag door veel zon (het 'duck curve' effect), steeds vaker zelfs negatief door one-day-ahead markt
market_prices = [50 - max(0, np.sin((h % 24) * np.pi / 12) * 60) + np.random.normal(0, 10) for h in range(168)]
df_prijzen = pd.DataFrame({
    'Tijdstip': timestamps,
    'Marktprijs_Euro': market_prices
})

print("Datasets succesvol gegenereerd!")
print("\nEerste regels Opwek:")
print(df_opwek.head(3))
print("\nEerste regels Prijzen:")
print(df_prijzen.head(3))

# Voeg de twee datasets samen op basis van kolom 'Tijdstip' (de 'Merge/Join')
df_compleet = pd.merge(df_opwek, df_prijzen, on='Tijdstip', how='inner')

# Bereken bruto omzet per uur (Opwek * Marktprijs)
df_compleet['Omzet_Euro'] = df_compleet['Opwek_MWh'] * df_compleet['Marktprijs_Euro']

# Conditionele logica (CASE WHEN in SQL, .loc of np.where in Pandas)
# Voeg  kolom 'Curtailment_Advies' toe. Als de prijs negatief is en er is opwek,'AFSCHAKELEN' , anders 'PRODUCEREN'.
df_compleet['Curtailment_Advies'] = np.where(
    (df_compleet['Marktprijs_Euro'] < 0) & (df_compleet['Opwek_MWh'] > 0), 
    'AFSCHAKELEN', 
    'PRODUCEREN'
)

print("Transformaties voltooid. Controleer het resultaat:")
print(df_compleet.loc[df_compleet['Marktprijs_Euro'] < 0].head(5)) # Toont rijen met negatieve prijzen

# OPDRACHT D: Maak dag-kolom aan voor groeperen
df_compleet['Datum'] = df_compleet['Tijdstip'].dt.date

# Groepeer per dag en bereken de totale opwek, gemiddelde prijs en totale omzet
df_dagrapport = df_compleet.groupby('Datum').agg({
    'Opwek_MWh': 'sum',
    'Marktprijs_Euro': 'mean',
    'Omzet_Euro': 'sum'
}).reset_index()

# Afronden voor rapportage
df_dagrapport = df_dagrapport.round(2)

print("Eindresultaat voor Finance / Business Control:")
print(df_dagrapport)
