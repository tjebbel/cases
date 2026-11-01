
# Zonne-energie: opwek, marktprijs en omzetanalyse

Een Python-project dat met **pandas** en **NumPy** laat zien hoe je energiedata van een zonnepark combineert met marktprijzen om omzet te berekenen, afschakeladvies te geven en een dagrapport voor Finance / Business Control te maken.

De data is **gesimuleerd** en bedoeld als oefening in data-analyse en datatransformatie.

## Wat doet het script?

1. **Tijdreeks genereren:** één week aan uurdata (168 uur), vanaf 1 juni 2026.
2. **Opwekdataset maken:** gesimuleerde zonne-opwek in MWh per uur, met een dagritme en willekeurige ruis. Opwek is nooit negatief.
3. **Prijsdataset maken:** gesimuleerde marktprijzen in €/MWh. Op zonnige uren dalen de prijzen, soms tot onder nul. Dit bootst het  *duck curve* -effect na dat op de day-ahead-markt steeds vaker voorkomt.
4. **Datasets samenvoegen:** opwek en prijzen worden gekoppeld op de kolom `Tijdstip` (een inner join).
5. **Omzet berekenen:** per uur `Opwek_MWh × Marktprijs_Euro`.
6. **Curtailment-advies:** is de prijs negatief terwijl er wordt opgewekt, dan luidt het advies `AFSCHAKELEN`, anders `PRODUCEREN`. Bij een negatieve prijs kost produceren namelijk geld.
7. **Dagrapport:** de uurdata wordt per dag gegroepeerd tot totale opwek, gemiddelde prijs en totale omzet, afgerond op twee decimalen.

## Uitvoer

Het script print achtereenvolgens:

* de eerste regels van de opwek- en prijsdataset;
* uren met een negatieve marktprijs, inclusief het afschakeladvies;
* het dagrapport met per dag:

| Kolom               | Betekenis                     |
| ------------------- | ----------------------------- |
| `Datum`           | De dag                        |
| `Opwek_MWh`       | Totale opwek die dag          |
| `Marktprijs_Euro` | Gemiddelde marktprijs die dag |
| `Omzet_Euro`      | Totale bruto omzet die dag    |

## Gebruikte technieken

* Tijdreeksen genereren met `pd.date_range`
* DataFrames samenvoegen met `pd.merge`
* Berekende kolommen
* Conditionele logica met `np.where` (vergelijkbaar met `CASE WHEN` in SQL)
* Filteren met `.loc`
* Groeperen en aggregeren met `groupby` en `agg`

## Installatie en gebruik

Vereisten: Python 3.9 of hoger.

bash

```bash
pip install pandas numpy
python main.py
```

Vervang `main.py` door de bestandsnaam van het script.

## Opmerkingen

* Alle data is willekeurig gegenereerd, dus de uitkomsten verschillen per run. Voor reproduceerbare resultaten kun je bovenaan `np.random.seed(42)` toevoegen.
* De omzet is  **bruto** : kosten, subsidies (zoals SDE++) en onbalans zijn niet meegenomen.
