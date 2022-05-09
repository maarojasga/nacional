import os
import pdb
import pandas as pd

ligas={
    'Argentina.PrimeraDivision':'Argentina - Liga Profesional',
    'Bolivia.LFPB':'Bolivia - LFPB',
    'Brazil.BrasileiroSerieA':'Brasil - Brasileirao Serie A',
    'Brazil.BrasileiroSerieB':'Brasil - Brasileirao Serie B',
    'Chile.PrimeraDivision':'Chile - Primera División',
    'Colombia.PrimeraA':'Colombia - Liga Betplay',
    'Colombia.PrimeraB':'Colombia - Torneo Betplay',
    'Ecuador.LigaPro':'Ecuador - Liga Pro',
    'Mexico.LigaBBVAExpansion':'México - Liga BBVA Expansión',
    'Mexico.LigaMX':'México - Liga MX',
    'Panama.LPF':'Panamá - LPF',
    'Paraguay.DivisionProfesional':'Paraguay - División Profesional',
    'Peru.PrimeraDivision':'Perú - Primera División',
    'Uruguay.PrimeraDivisionApertura':'Uruguay - Primera División',
    'Uruguay.PrimeraDivisionClausura':'Uruguay - Primera División',
    'Venezuela.PrimeraDivision':'Venezuela - Primera División',
    'UnitedStates.MLS':'Estados Unidos - MLS',
    'Argentina.CopadelaLigaProfesional':'Argentina - Copa de la Liga Profesional',
    'France.Ligue1':'Francia - Ligue 1',
    'Spain.SegundaDivision':'España - Segunda División',
    'Chile.primeraB':'Chile - Primera B',
    'LigaPortugal': 'Portugal - Liga Portugal'
}

path_jug = os.path.join('player_data/field_players_tournament_*')
path_arq = os.path.join('player_data/goalkeepers_tournament_*')

prueba = pd.read_excel('field_players_tournament_Brazil.BrasileiroSerieB.xlsx')

pdb.set_trace()
for col in prueba.columns:
    print(col)
    if '%' in col:
        prueba[col] = prueba[col].replace(to_replace='-',value=0)
        prueba[col]=float(prueba[col].str.rstrip('%').astype('float').fillna(0)/100.0)



