from modelo import *

def app():
    st.write("""
             # Histórico de jugadores
             > Ranking histórico de jugadores + radares de estadísticas globales por temporada.
             """)
    bool_arqueros = st.checkbox('¿Va a comparar arqueros?')
    df_in = base_jugadores()
    df_gk_in = base_arqueros()
    if bool_arqueros:
        position = 'arquero'
        w = weights(position)
        w.rename(index = {np.NaN:"xG conceded - Goals conceded"}, inplace = True)
        df = copy.deepcopy(df_gk_in)
        df["xG conceded - Goals conceded"]=df['xG conceded']-df['Goals conceded']
        df[w.index.tolist()]=df[w.index.tolist()].apply(pd.to_numeric,errors='coerce')
    else:
        df = copy.deepcopy(df_in)
    df = df[~df['League'].isin(['---'])]
    df = df[~df.index.get_level_values('Nationality').str.contains('0', na=False)]
    df = df[~df.index.get_level_values('Team').str.contains('0', na=False)]
    df_raw = copy.deepcopy(df)
    percentile(df)
    
    def search_options(n, df_in):
        df_temp = copy.deepcopy(df_in)
        with st.beta_expander(f'Buscar jugador {n}'):
            list_seasons = sorted(list(df_temp['Season'].unique()), reverse=True)
            season = st.selectbox('Escriba o seleccione la temporada', list_seasons, key=str(n))
            df_temp = df_temp[df_temp['Season'].isin([season])]
            league = st.selectbox('Liga', sorted(list(df_temp['League'].unique())), key=str(n+10))
            df_temp = df_temp[df_temp['League'].isin([league])]
            team = st.selectbox('Equipo', sorted(df_temp.index.get_level_values('Team').unique().tolist()), key=str(n+100))
            df_temp = df_temp[df_temp.index.get_level_values('Team').isin([team])]
            list_names = sorted(df_temp.index.get_level_values('Name').unique().tolist())
            list_names.insert(0, '--Buscar--')
            pl_name = st.selectbox('Escriba o seleccione jugador', list_names, key=str(n+1000))
            if '--Buscar--' not in pl_name:
                df_temp = df_temp[df_temp.index.get_level_values('Name').isin([pl_name])]
                return df_temp
            else:
                return pd.DataFrame()
    
    n_search = st.number_input('¿Cuantos jugadores va a comparar?', min_value=1, max_value=10)
    df_radar = pd.DataFrame()
    for n in range(0,n_search):
        df_selection = search_options(n+1, df)
        if len(df_selection)!=0:
            df_radar = df_radar.append(df_selection)
    
    if len(df_radar)!=0:
        # st.write("""## Parámetros de gráficas""")
        # N_variables = st.slider('Número de variables en radar', 5,12)
        st.write("""## Parámetros del ranking""")
        if not bool_arqueros:
            list_weights=sorted(list(dict_pos.values()))[1:]
            list_weights_keys=sorted(list(dict_pos.keys()))[1:]
            position = st.selectbox('Escriba o seleccione la posición de juego', list_weights)
            if '--Buscar--' not in position:
                position = list_weights_keys[list_weights.index(position)]
                w = weights(position)
                w.rename(index = {'xG per shot taken':'xG per shot'}, inplace = True)
        with st.beta_expander('Filtros adicionales'):
            list_nationality = sorted(list({name for a in df_radar.index.get_level_values('Nationality').unique().tolist() for name in a.split(', ')}))
            list_nationality.insert(0, '--All--')
            nationality = st.multiselect('Escriba o seleccione la(s) nacionalidad(es)', list_nationality, '--All--')
            if (len(nationality) != 0) and ('--All--' not in nationality):
                df_raw = df_raw[df_raw.index.get_level_values('Nationality').isin(nationality)]
        history_streamlit(df_radar, df_raw, w, position)
