import streamlit as st
from modelo import *
import pdb

def search_options(n, df_in):
    """
    Guarda búsqueda del usuario teniendo en cuenta la temporada, la liga, el equipo y el
    nombre del jugador.

    Retorna data frame con resultados de búsqueda.
    """
    df_temp = copy.deepcopy(df_in)
    with st.expander(f'Buscar jugador {n}'):
        list_seasons = sorted(list(df_temp['Season'].unique()), reverse=True)
        season = st.selectbox('Escriba o seleccione la temporada', list_seasons, key=str(n))
        # Se filtra data frame de entrada por temporada
        df_temp = df_temp[df_temp['Season'].isin([season])]
        league = st.selectbox('Liga', sorted(list(df_temp['League'].unique())), key=str(n+10))
        # Se filtra data frame de entrada por liga
        df_temp = df_temp[df_temp['League'].isin([league])]
        team = st.selectbox('Equipo', sorted(df_temp.index.get_level_values('Team').unique().tolist()),\
             key=str(n+10000))
        # Se filtra data frame de entrada por equipo
        df_temp = df_temp[df_temp.index.get_level_values('Team').isin([team])]
        list_names = sorted(df_temp.index.get_level_values('Name').unique().tolist())
        list_names.insert(0, '--Buscar--')
        pl_name = st.selectbox('Escriba o seleccione jugador', list_names, key=str(n+100))
        # Se filtra data frame de entrada por nombre
        if '--Buscar--' not in pl_name:
            df_temp = df_temp[df_temp.index.get_level_values('Name').isin([pl_name])]
            return df_temp
        else:
            return pd.DataFrame()
def app():
    """
    Corre la pestaña de Comparar Jugadores en X Scout
    """
    st.write("""
             # Comparar jugadores
             > Radar + tabla de estadísticas de jugadores seleccionados.
             """)
    bool_arqueros = st.checkbox('¿Va a comparar arqueros?')

    # Se carga la base de datos de los jugadores y de los arqueros
    df_ju = base_jugadores()
    df_gk = base_arqueros()

    # Condicional para modificar base de datos de arqueros
    if bool_arqueros:
        posicion = 'Arquero'
        w = weights(posiciones[posicion])
        w.rename(index = {np.NaN:"xG conceded - Goals conceded"}, inplace = True)
        df = copy.deepcopy(df_gk)
        df["xG conceded - Goals conceded"]=df['xG conceded']-df['Goals conceded']
    else:
        df = copy.deepcopy(df_ju)
    # Procesamiento de base de datos
    df = df[~df['League'].isin(['---'])]
    df = df[~df.index.get_level_values('Nationality').str.contains('0', na=False)]
    df = df[~df.index.get_level_values('Team').str.contains('0', na=False)]
    df_raw = copy.deepcopy(df)

    if bool_arqueros:
        df[w.index.tolist()]=df[w.index.tolist()].apply(pd.to_numeric,errors='coerce')
    
    # Se pregunta la cantidad de jugadores que se quieren comparar
    n_search = st.number_input('¿Cuantos jugadores va a comparar?', min_value=1, max_value=10)
    df_radar = pd.DataFrame()
    df_selec_temp = pd.DataFrame()

    for n in range(0,n_search):
        df_selection = search_options(n+1, df)

        if len(df_selection)!=0:
            # Se guarda la selección del usuario
            df_radar = df_radar.append(df_selection)
            df_selec_temp = df_selec_temp.append(copy.deepcopy(df_selection))

    # En este bloque se filtra la base de datos global para realizar las comparaciones
    if len(df_radar)==n_search:
        st.write("""## Parámetros de gráficas""")
        # Se selecciona el número de variables para realizar la comparación
        N_variables = st.slider('Número de variables en radar', 5,12)

        # Se guarda la información del filtro de mínimo de minutos jugados
        min_minutes = st.slider('Minimo de minutos jugados',\
            min_value=90,max_value=int(df_raw[(df_raw['Season'].isin(list(df_selection['Season'].unique()))) &\
            (df_raw['League'].isin(list(df_selection['League'].unique())))]['Minutes played'].max())-1)

        # Filtramos base de datos global para que únicamente incluya jugadores que tengan >= minutos que
        # la cantidad seleccionada
        df_raw = df_raw[df_raw['Minutes played'] >= min_minutes]

        # Para evitar eliminar a los jugadores que el usuario busca pero que no cumplen con el parámetro
        # de minutos jugados, los agregamos a la base de datos de nuevo.
        if df_selec_temp['Minutes played'].min()<min_minutes:
            df_raw = df_raw.append(df_selec_temp[df_selec_temp['Minutes played']<min_minutes])
        df_raw2 = copy.deepcopy(df_raw)

        # Se obtienen percentiles de la base de datos filtrada
        percentile(df_raw2)

        # Se guardan en un data frame únicamente los jugadores seleccionados
        df_radar_final = pd.DataFrame()

        df_selection_final = df_raw2[(df_raw2['Season'].isin(list(df_radar['Season'].unique()))) &\
            (df_raw2['League'].isin(list(df_radar['League'].unique()))) &\
                (df_raw2.index.get_level_values('Name').isin(df_radar.index.get_level_values('Name').unique().tolist()))]

        df_radar_final = df_radar_final.append(df_selection_final)

        # Se selecciona la posición para realizar la comparación
        if not bool_arqueros:
            lista_posiciones = sorted(list(posiciones.keys()))
            lista_posiciones.insert(0,'--Buscar--')
            lista_posiciones.remove('Lateral')
            posicion = st.selectbox('Escriba o seleccione la posición de juego', lista_posiciones)

            if '--Buscar--' not in posicion:
                w = weights(posiciones[posicion])
                w.rename(index = {'xG per shot taken':'xG per shot'}, inplace = True)
                # Finalmente se muestra el radar y/o tabla de estadísticas para los jugadores seleccionados
                radar_streamlit(df_radar_final, df_raw2, posiciones[posicion], w, N_variables)


        else:
            radar_streamlit(df_radar_final, df_raw2, posiciones[posicion], w, N_variables)