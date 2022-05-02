import pandas as pd

# Diccionario que pone bonito los nombres
ligas={
    'Argentina.Torneo2021':'Argentina - Liga Profesional',
    'Bolivia.LFPB':'Bolivia - LFPB',
    'Brazil.BrasileiroSerieA':'Brasil - Brasileiro Serie A',
    'Brazil.BrasileiroSerieB':'Brasil - Brasileiro Serie B',
    'Chile.PrimeraDivision':'Chile - Primera Division',
    'Colombia.PrimeraA':'Colombia - Liga Betplay',
    'Colombia.PrimeraB':'Colombia - Torneo Betplay',
    'Ecuador.LigaPro':'Ecuador - Liga Pro',
    'Mexico.LigaBBVAExpansion':'México - Liga BBVA Expansion',
    'Mexico.LigaMX':'México - Liga MX',
    'Panama.LPF':'Panamá - LPF',
    'Paraguay.DivisionProfesional':'Paraguay - Division Profesional',
    'Peru.PrimeraDivision':'Perú - Primera Division',
    'Uruguay.PrimeraDivisionApertura':'Uruguay - Primera Division',
    'Uruguay.PrimeraDivisionClausura':'Uruguay - Primera Division',
    'Venezuela.PrimeraDIvision':'Venezuela - Primera Division',
    'UnitedStates.MLS':'Estados Unidos - MLS',
    'Argentina.CopadelaLigaProfesional':'Argentina - Copa de la Liga Profesional',
    'France.Ligue1':'Francia - Ligue 1',
    'Spain.SegundaDivision':'España - Segunda División',
    'Chile.primeraB':'Chile - Primera B'
}

#Leer los archivos con las ligas pasadas
jugadores=pd.read_csv('Jugadores.csv', header=0, delimiter=';', decimal=',', na_values='-', encoding="utf-8")
arqueros = pd.read_csv('Arqueros.csv', header=0, delimiter=';', decimal=',', na_values='-', encoding="utf-8")
jugadores.drop(columns=['Unnamed: 0'],inplace=True)
arqueros.drop(columns=['Unnamed: 0'],inplace=True)


# Extensión de donde pertenecen los archivos
file_j=f'2510/25_10_2021_field_players_tournament_'
file_a=f'2510/25_10_2021_goalkeepers_tournament_'
filej=file_j+'{}.xlsx'
filea=file_a+'{}.xlsx'

jugadores_m = pd.DataFrame(columns=jugadores.columns.tolist())
arqueros_m = pd.DataFrame(columns=arqueros.columns.tolist())
for lig in ligas.keys():
    #try:
    print(filej.format(lig))
    j = pd.read_excel(filej.format(lig),na_values='-')
    j.rename(columns={'Unnamed: 0':'Number','Unnamed: 1':'Name','Сhances created':'Chances created','Penalties\n scored':'Penalties scored',"Opponent's penalties saved, %":"Penalties saved, %","Opponent's penalties conceded":"Goals conceded - Penalties","Opponent's penalties saved":"Penalties saved"},inplace=True)
    
    j['League']=ligas[lig]
    if (lig=='Uruguay.PrimeraDivisionClausura')|(lig=='Mexico.LigaBBVAExpansion'):
        j['Season']=20212
    elif (lig=='Brazil.BrasileiroSerieA')|(lig=='Brazil.BrasileiroSerieB')|(lig=='UnitedStates.MLS'):
        j['Season']=2021
    else:
        j['Season']=2022
    jugadores_m=jugadores_m.append(j,ignore_index=True)

    try:
        print(filea.format(lig))
        a = pd.read_excel(filea.format(lig),na_values='-')
        a.rename(columns={'Unnamed: 0':'Number','Unnamed: 1':'Name',"Opponent's penalties saved, %":"Penalties saved, %","Opponent's penalties conceded":"Goals conceded - Penalties","Opponent's penalties saved":"Penalties saved"},inplace=True)
        a['League']=ligas[lig]
        if lig=='Uruguay.PrimeraDivisionClausura':
            a['Season']=20212
        elif (lig=='Brazil.BrasileiroSerieA')|(lig=='Brazil.BrasileiroSerieB')|(lig=='UnitedStates.MLS'):
            a['Season']=2021
        else:
            a['Season']=2022
        arqueros_m=arqueros_m.append(a,ignore_index=True)
    except Exception as e:
        print("No existe el archivo {}".format(filea.format(lig)))
        print(str(e))

#Parte de Colombia
jugcol=pd.read_csv('colombiaJugadores.csv',na_values='-')
jugcol.rename(columns={'Сhances created':'Chances created','Penalties\n scored':'Penalties scored'},inplace=True)
jugcol['League']='Colombia - Liga Betplay'
jugcol['Season']=20212
arqcol=pd.read_csv('colombiaArqueros.csv',na_values='-')
arqcol['League']='Colombia - Liga Betplay'
arqcol['Season']=20212

#Verificar que todo tenga las mismas columnas para poder hacer el append bien
print(set(jugcol.columns.tolist())-set(jugadores_m.columns.tolist()))
print(set(jugadores_m.columns.tolist())-set(jugcol.columns.tolist()))

print(set(arqcol.columns.tolist())-set(arqueros_m.columns.tolist()))
print(set(arqueros_m.columns.tolist())-set(arqcol.columns.tolist()))

arq_arqueros=set(arqcol.columns.tolist())-set(arqueros_m.columns.tolist())
arqcol=arqcol.drop(columns=arq_arqueros)

arqueros_arq=set(arqueros_m.columns.tolist())-set(arqcol.columns.tolist())
arqueros_m=arqueros_m.drop(columns=arqueros_arq)

print(set(arqcol.columns.tolist())-set(arqueros_m.columns.tolist()))
print(set(arqueros_m.columns.tolist())-set(arqcol.columns.tolist()))

# Añado la parte de colombia 2021-1 al DataFrame nuevo
jugadores_m=jugadores_m.append(jugcol)
arqueros_m=arqueros_m.append(arqcol)

# Tratamiento de datos
jugadores_m['Team']=jugadores_m['Team'].fillna('---')
arqueros_m['Team']=arqueros_m['Team'].fillna('---')
arqueros_m['Goals conceded']=arqueros_m['Goals conceded'].astype(float).tolist()

# Borro todo lo que sea de 2021 antes de añadir los nuevos 
indicesj = jugadores[(jugadores['League'].isin(list(ligas.values()))) & (jugadores['Season']==2021)].index
indicessj= jugadores[jugadores['Season']==20212].index
jugadores.drop(indicesj,inplace=True)
jugadores.drop(indicessj,inplace=True)

indicesa=arqueros[(arqueros['League'].isin(list(ligas.values()))) & (arqueros['Season']==2021)].index
arqueros.drop(indicesa,inplace=True)
indicessa=arqueros[arqueros['Season']==20212].index
arqueros.drop(indicessa,inplace=True)

# Los uno y los exporto
jugadores=jugadores.append(jugadores_m,ignore_index=True)
arqueros=arqueros.append(arqueros_m,ignore_index=True)
jugadores.to_csv(f'../Jugadores2510.csv', sep=';', decimal=',', na_rep='-', encoding="utf-8")
arqueros.to_csv(f'../Arqueros2510.csv', sep=';', decimal=',', na_rep='-', encoding="utf-8")


