import streamlit as st
from modelo import *

def app():
    st.write("""
             # Buscar parecidos a jugador
             > Jugadores similares a referente seleccionado.
             """)
    st.write("""## Jugador modelo""")
    df_reference = pd.DataFrame()
    df = pd.DataFrame()
    df_in = base_jugadores()
    df_gk_in = base_arqueros()
    with st.expander('Filtros'):
        lista_posiciones = sorted(list(posiciones.keys()))
        lista_posiciones.remove('Lateral')
        lista_posiciones.insert(0,'--Buscar--')
        posicion = st.selectbox('Escriba o seleccione la posicion de juego',lista_posiciones)
        if'--Buscar--' not in posicion:
            w=weights(posiciones[posicion])
            if 'Arquero' not in posicion:
                w.rename(index = {'xG per shot taken':'xG per shot'}, inplace = True)
                df = copy.deepcopy(df_in)
                df_pos = pd.DataFrame()
                for p in dict_pos_eq_instat[posiciones[posicion]]:
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

            df_reference = copy.deepcopy(df)

            list_seasons = sorted(list(df_reference['Season'].unique()), reverse=True)
            season = st.selectbox('Escriba o seleccione la temporada', list_seasons)
            df_reference = df_reference[df_reference['Season'].isin([season])]

            league = st.selectbox('Liga', sorted(list(df_reference['League'].unique())))
            df_reference = df_reference[df_reference['League'].isin([league])]
            
            team = st.selectbox('Equipo', sorted(df_reference.index.get_level_values('Team').unique().tolist()))
            df_reference = df_reference[df_reference.index.get_level_values('Team').isin([team])]
            
            list_names = sorted(df_reference.index.get_level_values('Name').unique().tolist())
            list_names.insert(0, '--Buscar--')
            reference_name = st.selectbox('Escriba o seleccione jugador', list_names)
            
            if '--Buscar--' not in reference_name:
                df_reference = df_reference[df_reference.index.get_level_values('Name').isin([reference_name])]
                df = df[~df.index.get_level_values('Name').isin([reference_name])]
    
    st.write("""## Jugadores a incluir en la búsqueda""")
    with st.expander('Filtros'):
        if '--Buscar--' not in posicion:
            season = st.selectbox('Escriba o seleccione la temporada', ('2020', '2021','20212','202122'), key=str(2))
            df = df[df['Season'].isin([season])]
            list_leagues = sorted(list(df['League'].unique()))
            list_leagues.insert(0, '--All--')
            leagues = st.multiselect('Escriba o seleccione la(s) liga(s) objetivo', list_leagues, '--All--')
            if '--All--' not in leagues:
                df = df[df['League'].isin(leagues)]
            list_teams = sorted(list(df.index.get_level_values('Team').unique()))
            list_teams.insert(0, '--All--')
            teams = st.multiselect('Escriba o seleccione el(los) equipo(s) objetivo', list_teams, '--All--')
            if '--All--' not in teams:
                df = df[df.index.get_level_values('Team').isin(teams)]
            if (len(leagues) != 0) and (len(df) != 0):
                min_minutes = st.number_input('Minimo de minutos jugados', min_value=90, max_value=int(df['Minutes played'].max())-1)
                df = df[df['Minutes played'] >= min_minutes]
                lst_nationalities = sorted(list({name for a in df.index.get_level_values('Nationality').unique().tolist() for name in a.split(', ')}))
                if len(lst_nationalities) > 1:
                    bool_nationality = st.checkbox('¿Filtrar por nacionalidad?')
                    if bool_nationality:
                        nationality = st.selectbox('Nacionalidad',lst_nationalities)
                        if '--All--' not in nationality:
                            df = df[df.index.get_level_values('Nationality').str.contains(nationality, na=False)]
                if int(df['Age'].min())<int(df['Age'].max()):
                    bool_age = st.checkbox('¿Filtrar por edad?')
                    if bool_age:
                        age = st.slider('Rango de edad', int(df['Age'].min()),int(df['Age'].max()), value=(int(df['Age'].min()), int(df['Age'].max())))
                        df['Age']=df['Age'].fillna(0).astype(int)
                        df = df[(df['Age'].astype(int) >= int(age[0])) & (df['Age'] <= int(age[-1]))]
        else:
            st.write("""Seleccione la posición del jugador modelo para habilitar opciones""")

    if ('--Buscar--' not in posicion) and ('--Buscar--' not in reference_name) and (len(df) != 0):
        st.write("""
             ***
             ***
             ***
             """)
        df = Xp_ranking(df, best_df=df_reference, weight=w, d_metric=dict_metrics[dict_metrics_pos[posiciones[posicion]]])
        table_streamlit(df, posiciones[posicion])
        st.write("""
             ***
             """)
        df_radar = pd.DataFrame()
        with st.expander('Comparar con Radar'):
            bool_reference = st.checkbox(f'¿Añadir a {reference_name} al radar?')
            if bool_reference:
                df_reference['Xp Score'] = np.NaN
                df_reference['Xp Ranking'] = 0
                df_reference['Percentil'] = np.NaN
                df_radar = df_radar.append(df_reference)
            if 'Atl. Nacional' in df.index.get_level_values('Team').unique().tolist():
                st.write("""## Selección de jugadores de Atlético Nacional""")
                df_radar_team = copy.deepcopy(df[df.index.get_level_values('Team').isin(['Atl. Nacional'])].sort_values('Xp Ranking'))
                if len(df_radar_team.index.get_level_values('Name').tolist()) != len(set(df_radar_team.index.get_level_values('Name').tolist())):
                    names_team = st.multiselect('Escriba o seleccione jugador(es)', sorted([f"{n} ({l})" for n, l in zip(df_radar_team.index.get_level_values('Name').tolist(), df_radar_team['League'].values.tolist())]))
                    df_radar_team = df_radar_team[df_radar_team['League'].isin([n.split(' (')[1].split(')')[0] for n in names_team])]
                    names_team = [n.split(' (')[0] for n in names_team]
                else:
                    names_team = st.multiselect('Escriba o seleccione jugador(es)', sorted(df_radar_team.index.get_level_values('Name').tolist()))
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
            # names_other = st.multiselect('Escriba o seleccione jugador(es)', df_radar_other.index.get_level_values('Name').tolist())
            if len(df_radar_other.index.get_level_values('Name').tolist()) != len(set(df_radar_other.index.get_level_values('Name').tolist())):
                names_other = st.multiselect('Escriba o seleccione jugador(es)', sorted([f"{n} ({l})" for n, l in zip(df_radar_other.index.get_level_values('Name').tolist(), df_radar_other['League'].values.tolist())]))
                df_radar_other = df_radar_other[df_radar_other['League'].isin([n.split(' (')[1].split(')')[0] for n in names_other])]
                names_other = [n.split(' (')[0] for n in names_other]
            else:
                names_other = st.multiselect('Escriba o seleccione jugador(es)', sorted(df_radar_other.index.get_level_values('Name').tolist()))
            df_radar_other = df_radar_other[df_radar_other.index.get_level_values('Name').isin(names_other)]
            df_radar = df_radar.append(df_radar_other)
            st.write("""## Parámetros de gráficas""")
            N_variables = st.slider('Número de variables en radar', 5,12)

        if len(df_radar)!=0:
            radar_streamlit(df_radar, df_raw, posiciones[posicion], w, N_variables)