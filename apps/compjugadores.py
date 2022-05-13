import pdb
from modelo import *
import streamlit as st
##comparar jugadores
dict_positions = {'Central':'CD',
                  'Lateral Derecho':'RD',
                  'Lateral Izquierdo':'LD',
                  'Volante Derecho':'RM',
                  'Volante Izquierdo':'LM',
                  'Volante Defensivo':'DM',
                  'Volante Central':'CM',
                  'Delantero':'F'}


def search_options(n, df_in):
    """
    Guarda búsqueda del usuario teniendo en cuenta la temporada, la liga, el equipo y el
    nombre del jugador.

    Retorna data frame con resultados de búsqueda.
    """
    df_temp = copy.deepcopy(df_in)
    df_temp2 = copy.deepcopy(df_in)

    with st.expander(f'Buscar jugador {n}'):
        # Se filtra data frame de entrada por temporada
        list_seasons = sorted(list(df_temp['Season'].unique()), reverse=True)
        list_seasons.insert(0,'--Buscar--')
        season = st.selectbox('Escriba o seleccione la temporada', list_seasons, key=str(n))
        if '--Buscar--' not in season:
            df_temp = df_temp[df_temp['Season']==season]
            df_temp2 = df_temp2[df_temp2['Season']==season]

        # Se filtra data frame de entrada por liga
        list_leagues = sorted(list(df_temp['League'].unique()), reverse=False)
        list_leagues.insert(0,'--Buscar--')
        league = st.selectbox('Escriba o seleccione la Liga', list_leagues, key=str(n+10))
        df_temp = df_temp[df_temp['League']==league]
        df_temp2 = df_temp2[df_temp2['League']==league]
        
        # Se filtra data frame de entrada por equipo
        list_teams = sorted(list(df_temp.index.unique(level='Team')), reverse=False)
        list_teams.insert(0,'--Buscar--')
        team = st.selectbox('Equipo', list_teams,key=str(n+10000))
        df_temp = df_temp[df_temp.index.get_level_values('Team').isin([team])]
        list_names = sorted(df_temp.index.get_level_values('Name').unique().tolist())
        list_names.insert(0, '--Buscar--')
        pl_name = st.selectbox('Escriba o seleccione jugador', list_names, key=str(n+100))
        # Se filtra data frame de entrada por nombre
        if '--Buscar--' not in pl_name:
            df_temp = df_temp[df_temp.index.get_level_values('Name').isin([pl_name])]
            return df_temp, df_temp2
        else:
            return pd.DataFrame(), pd.DataFrame()

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
    df_raw_sl = copy.deepcopy(df_raw)

    if bool_arqueros:
        df[w.index.tolist()]=df[w.index.tolist()].apply(pd.to_numeric,errors='coerce')
    
    # Se pregunta la cantidad de jugadores que se quieren comparar
    n_search = st.number_input('¿Cuantos jugadores va a comparar?', min_value=1, max_value=10)
    df_radar = pd.DataFrame()
    df_selec_temp = pd.DataFrame()

    for n in range(0,n_search):
        df_selection, _ = search_options(n+1, df_raw)
        #df_raw = df_raw[(df_raw['Season']==sea)&(df_raw['League'].isin(lea))]
        if len(df_selection)!=0:
            # Se guarda la selección del usuario
            df_radar = df_radar.append(df_selection)
            df_selec_temp = df_selec_temp.append(copy.deepcopy(df_selection))

    # En este bloque se filtra la base de datos global para realizar las comparaciones
    if len(df_radar)==n_search:
        st.write("""## Parámetros de gráficas""")
        df_raw_sl = df_raw_sl[df_raw_sl['Season'].isin(df_radar['Season'].unique().tolist())&df_raw_sl['League'].isin(df_radar['League'].unique().tolist())]
        print(df_raw_sl['League'].unique())
        if not bool_arqueros:
            list_pos = list(dict_positions.keys())
            list_pos.insert(0,'--Buscar--')
            filt_posicion = st.selectbox('Escriba o seleccione la posición de juego por la que desea filtrar',\
                list_pos)
            if '--Buscar--' not in filt_posicion:
                df_raw_sl = df_raw_sl[df_raw_sl['Position']==dict_positions[filt_posicion]]

        # Se guarda la información del filtro de mínimo de minutos jugados
        min_minutes = st.slider('Minimo de minutos jugados',\
            min_value=90,max_value=int(df_raw_sl['Minutes played'].max())-1)

        # Se selecciona el número de variables para realizar la comparación
        N_variables = st.slider('Número de variables en radar', 5,12)

        # Filtramos base de datos global para que únicamente incluya jugadores que tengan >= minutos que
        # la cantidad seleccionada
        df_raw_sl = df_raw_sl[df_raw_sl['Minutes played'] >= min_minutes]

        # Para evitar eliminar a los jugadores que el usuario busca pero que no cumplen con el parámetro
        # de minutos jugados, los agregamos a la base de datos de nuevo.
        if df_selec_temp['Minutes played'].min()<min_minutes:
            df_raw_sl= df_raw_sl.append(df_selec_temp[df_selec_temp['Minutes played']<min_minutes])

        if not (df_selec_temp.index.get_level_values('Name').unique().isin(df_raw_sl.index.get_level_values('Name').unique().to_list())[0]):
            df_raw_sl = df_raw_sl.append(df_selec_temp)

        df_raw_sl = df_raw_sl.drop_duplicates()
        df_raw_final = copy.deepcopy(df_raw_sl)

        # Se obtienen percentiles de la base de datos filtrada
        percentile(df_raw_final)

        # Se guardan en un data frame únicamente los jugadores seleccionados
        df_radar_final = pd.DataFrame()
        df_selection_final = df_raw_final[(df_raw_final.index.get_level_values('Name').isin(df_radar.index.get_level_values('Name').unique().tolist()))&(df_raw_final.index.get_level_values('Team').isin(df_radar.index.get_level_values('Team').unique().tolist()))]
        df_radar_final = df_radar_final.append(df_selection_final)

        # Se selecciona la posición para obtener pesos
        if not bool_arqueros:
            lista_posiciones = sorted(list(posiciones.keys()))
            lista_posiciones.insert(0,'--Buscar--')
            lista_posiciones.remove('Lateral')
            posicion = st.selectbox('Escriba o seleccione la posición de juego', lista_posiciones)

            if '--Buscar--' not in posicion:
                # Se obtienen los pesos
                w = weights(posiciones[posicion])
                w.rename(index = {'xG per shot taken':'xG per shot'}, inplace = True)

                # Finalmente se muestra el radar y/o tabla de estadísticas para los jugadores seleccionados
                radar_streamlit(df_radar_final, df_raw_final, df_raw_sl, posiciones[posicion], w, N_variables)

                #v = w[list(dict_var_rad[posiciones[posicion]])].sort_values(ascending = False).index.tolist()
                v = w.sort_values(ascending = False).index.tolist()
                if 'arquero' not in posiciones[posicion]:
                    v_esp = [dict_translate_players[var] for var in v]
                else:
                    v_esp = [dict_translate_gk[var] for var in v]
                
                variables = st.multiselect('Seleccione por lo menos 3 variables que quiere observar',options=v_esp)
                
                if 'arquero' not in posiciones[posicion]:
                    variables = [dict_translate_players_reverse[v] for v in variables]
                else:
                    variables = [dict_translate_gk_reverse[v] for v in variables]
                if len(variables)>=3:
                    radar_streamlit_escoger(df_radar_final, df_raw_final,df_raw_sl, posiciones[posicion], w, variables)
                else:
                    st.write("""
                    > Seleccione las variables que quiere observar.
                    """)
        else:
            radar_streamlit(df_radar_final, df_raw_final, df_raw_sl, posiciones[posicion], w, N_variables)
            
            #v = w[list(dict_var_rad[posiciones[posicion]])].sort_values(ascending = False).index.tolist()
            v = w.sort_values(ascending = False).index.tolist()
            if 'arquero' not in posiciones[posicion]:
                v_esp = [dict_translate_players[var] for var in v]
            else:
                v_esp = [dict_translate_gk[var] for var in v]
            variables = st.multiselect('Seleccione por lo menos 3 variables que quiere observar',options=v_esp)
            if 'arquero' not in posiciones[posicion]:
                variables = [dict_translate_players_reverse[v] for v in variables]
            else:
                variables = [dict_translate_gk_reverse[v] for v in variables]
            if len(variables)>=3:
                radar_streamlit_escoger(df_radar_final, df_raw_final,df_raw_sl, posiciones[posicion], w, variables)
            else:
                st.write("""
                > Seleccione las variables que quiere observar.
                """)

                