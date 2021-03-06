import csv
from collections import defaultdict
from functools import reduce

import pandas as reader

# Read data source.
file_path = 'covid-data/200511COVID19MEXICO.csv'
data = reader.read_csv(file_path, encoding='unicode_escape')
inputDict = data.to_dict(orient='rows')

# Constants
SONORA = ('Sonora', 26)
CHIHUAHUA = ('Chihuahua', 8)
NUEVO_LEON = ('Nuevo Leon', 19)
PUEBLA = ('Puebla', 21)
NAME = 0
ID = 1
# Data keys
ENTIDAD_KEY = 'ENTIDAD_UM'

# Result accumulators
sonoraResults = []
aggregateStateResults = {
    SONORA[NAME]: 0,
    CHIHUAHUA[NAME]: 0,
    NUEVO_LEON[NAME]: 0,
    PUEBLA[NAME]: 0,
}


# Utility function for requirement for "tabla1"
def isEntryForSonoraResults(entry):
    isFromSonora = entry[ENTIDAD_KEY] == SONORA[1]
    isCovidPositive = entry['RESULTADO'] == 1
    return isFromSonora and isCovidPositive


# Aggregate utility function to create "tabla2"
def aggregateEntryIfFromFilterStates(entry):
    if entry['TIPO_PACIENTE'] == 2:  # If hospitalized
        if entry[ENTIDAD_KEY] == SONORA[ID]:
            aggregateStateResults[SONORA[NAME]] += 1
        if entry[ENTIDAD_KEY] == CHIHUAHUA[ID]:
            aggregateStateResults[CHIHUAHUA[NAME]] += 1
        if entry[ENTIDAD_KEY] == NUEVO_LEON[ID]:
            aggregateStateResults[NUEVO_LEON[NAME]] += 1
        if entry[ENTIDAD_KEY] == PUEBLA[ID]:
            aggregateStateResults[PUEBLA[NAME]] += 1


# Process each entry. Populate all data required to go through the data just once.
for entry in inputDict:
    if isEntryForSonoraResults(entry):
        sonoraResults.append(entry)

    aggregateEntryIfFromFilterStates(entry)

# Process Sonora Results
curatedSonoraResults = []
sortedSonoraResults = sorted(sonoraResults, key=lambda r: (r['FECHA_SINTOMAS'], r['FECHA_DEF']))
for entry in sortedSonoraResults:
    curatedSonoraResults.append(
        {'Fecha': entry["FECHA_SINTOMAS"], 'Confirmado': 1 if entry['RESULTADO'] == 1 else 0,
         'Deceso': 1 if entry['FECHA_DEF'] != '9999-99-99' else 0, })

df = reader.DataFrame(curatedSonoraResults)

groupedResults = df.groupby(['Fecha']).agg(sum)

# Write "tabla1.csv"
with open('tabla1.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['Fecha', 'Confirmados', 'Decesos'])
    for entry in groupedResults.reset_index().to_dict('records'):
        row = [entry['Fecha'],
               entry['Confirmado'],
               entry['Deceso']
               ]
        writer.writerow(row)

# Write "tabla2.csv"
with open('tabla2.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['State', 'Value'])
    for key, value in aggregateStateResults.items():
        writer.writerow([key, value])
