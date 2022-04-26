from modelo import *

def app():
    df_in = base_jugadores()
    df_gk_in = base_arqueros()

    st.write("""
             # Selección Colombia
             > Ranking de jugadores a partir del perfil de juego seleccionado con ligas europeas y asiáticas incluidas.
             """)
    st.write("""## Perfil""")
    lista_posiciones = sorted(list(posiciones.keys()))
    lista_posiciones.insert(0,'--Buscar--')
    lista_posiciones.remove('Lateral')
    posicion = st.selectbox('Escriba o seleccione la posicion de juego',lista_posiciones)
    if '--Buscar--' not in posicion:
        position = posiciones[posicion]
        w = weights(position)
        if 'arquero' not in position:
            w.rename(index = {'xG per shot taken':'xG per shot'}, inplace = True)
            df = copy.deepcopy(df_in)
            df_pos = pd.DataFrame()
            for p in dict_pos_eq_instat[position]:
                df_pos = df_pos.append(df[df.Position.str.contains(p, na=True)])
            df = df_pos
        else:
            w.rename(index = {np.NaN:"xG conceded - Goals conceded"}, inplace = True) ##Quitar
            df = copy.deepcopy(df_gk_in)
            df["xG conceded - Goals conceded"]=df['xG conceded']-df['Goals conceded']
        df = df[~df['League'].isin(['---'])]
        df = df[~df.index.get_level_values('Nationality').str.contains('0', na=False)]
        df = df[~df.index.get_level_values('Team').str.contains('0', na=False)]
        df = df[df['Minutes played'] >= 90]
        df_raw = copy.deepcopy(df)
        percentile(df)
        st.write("""## Jugadores a incluir en el ranking""")
        list_seasons = sorted(list(df['Season'].unique()), reverse=True)
        season = st.selectbox('Escriba o seleccione la temporada', list_seasons)
        df = df[df['Season'].isin([season])]
        list_leagues = sorted(list(df['League'].unique()))
        list_leagues.insert(0, '--All--')
        leagues = st.multiselect('Escriba o seleccione la(s) liga(s) objetivo', list_leagues)
        if '--All--' not in leagues:
            df = df[df['League'].isin(leagues)]
        if ('--Buscar--' not in position) and (len(leagues) != 0) and (len(df) != 0):
            min_minutes = st.number_input('Minimo de minutos jugados', min_value=90, max_value=int(df['Minutes played'].max())-1)
            df = df[df['Minutes played'] >= min_minutes]
            lst_nationalities = sorted(list({name for a in df.index.get_level_values('Nationality').unique().tolist() for name in a.split(', ')}))
            if len(lst_nationalities) > 1:
                bool_nationality = st.checkbox('¿Filtrar por nacionalidad?')
                if bool_nationality:
                    nationality = st.selectbox('Nacionalidad',lst_nationalities)
                    if '--All--' not in nationality:
                        df = df[df.index.get_level_values('Nationality').str.contains(nationality, na=False)]
            if int(df.query('Age >= 10')['Age'].min())<int(df['Age'].max()):
                bool_age = st.checkbox('¿Filtrar por edad?')
                if bool_age:
                    age = st.slider('Rango de edad', int(df.query('Age >= 10')['Age'].min()),int(df['Age'].max()), value=(int(df.query('Age >= 10')['Age'].min()), int(df['Age'].max())))
                    df = df[(df['Age'] >= int(age[0])) & (df['Age'] <= int(age[-1]))]

            st.write("""
                 ***
                 ***
                 ***
                 """)
            df = Xp_ranking(df, weight=w, d_metric=dict_metrics[dict_metrics_pos[position]])
            table_streamlit(df, position)

            st.write("""
                 ***
                 """)
            df_radar = pd.DataFrame()
            with st.beta_expander('Comparar con Radar'):
                if 'Atl. Nacional' in df.index.get_level_values('Team').unique().tolist():
                    st.write("""## Selección de jugadores de Atlético Nacional""")
                    df_radar_team = copy.deepcopy(df[df.index.get_level_values('Team').isin(['Atl. Nacional'])].sort_values('Xp Ranking'))
                    names_team = st.multiselect('Escriba o seleccione jugador(es)', df_radar_team.index.get_level_values('Name').tolist())
                    df_radar_team = df_radar_team[df_radar_team.index.get_level_values('Name').isin(names_team)]
                    df_radar = df_radar.append(df_radar_team)
                st.write("""## Selección de jugadores""")
                df_radar_other = copy.deepcopy(df[~df.index.get_level_values('Team').isin(['Atl. Nacional'])].sort_values('Xp Ranking'))
                if ('--All--' in leagues) or (len(leagues)>1):
                    list_leagues = sorted(df_radar_other['League'].unique().tolist())
                    list_leagues.insert(0, '--All--')
                    leagues = st.multiselect('Escriba o seleccione la(s) ligas(s)', list_leagues, '--All--')
                    if '--All--' not in leagues:
                        df_radar_other = df_radar_other[df_radar_other['League'].isin(leagues)]
                list_teams = sorted(df_radar_other.index.get_level_values('Team').unique().tolist())
                list_teams.insert(0, '--All--')
                teams = st.multiselect('Escriba o seleccione el (los) equipo(s)', list_teams, '--All--')
                if '--All--' not in teams:
                    df_radar_other = df_radar_other[df_radar_other.index.get_level_values('Team').isin(teams)]
                names_other = st.multiselect('Escriba o seleccione jugador(es)', df_radar_other.index.get_level_values('Name').tolist())
                df_radar_other = df_radar_other[df_radar_other.index.get_level_values('Name').isin(names_other)]
                df_radar = df_radar.append(df_radar_other)
                st.write("""## Parámetros de gráficas""")
                number_var = len(dict_var_rad[position])
                N_variables = st.slider('Número de variables en radar', 5,number_var)

            if len(df_radar)!=0:
                radar_streamlit(df_radar, df_raw, position, w, N_variables)
