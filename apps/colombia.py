import streamlit as st
from modelo import *
import copy



def app():
    
    st.write("""
             # Rankings Colombianos
             > Ranking de jugadores Colombianos en las ligas objetivo
             """)
    st.write("""## Perfil""")

    df_ju = base_jugadores()
    df_gk = base_arqueros()

    lista_posiciones = sorted(list(posiciones.keys()))
    lista_posiciones.insert(0,'--Buscar--')
    lista_posiciones.remove('Lateral')
    posicion = st.selectbox('Escriba o seleccione la posicion de juego',lista_posiciones)
    
    if '--Buscar--' not in posicion:
        w = weights(posiciones[posicion])
        if 'Arquero' not in posicion:
            w.rename(index = {'xG per shot taken':'xG per shot'}, inplace = True)
            df_pos=pd.DataFrame()
            for p in dict_pos_eq_instat[posiciones[posicion]]:
                df_pos =df_pos.append(df_ju[df_ju.Position.str.contains(p,na=True)])
            df =copy.deepcopy(df_pos)
        else: 
            df =copy.deepcopy(df_gk)
            df["xG conceded - Goals conceded"]=df['xG conceded']-df['Goals conceded']
            w.rename(index={np.NaN:"xG conceded - Goals conceded"},inplace=True)

        df = df[~df['League'].isin(['---'])]
        df = df[~df.index.get_level_values('Nationality').str.contains('0', na=False)]
        df = df[~df.index.get_level_values('Team').str.contains('0', na=False)]
        df = df[df.index.get_level_values('Nationality').str.contains('Colombia', na=False)]
        st.write("""## Jugadores a incluir en el ranking""")
        list_seasons = sorted(list(df['Season'].unique()), reverse=True)
        season = st.selectbox('Escriba o seleccione la temporada', list_seasons)

        list_leagues = sorted(list(df.loc[df['Season'].isin([season]),'League'].unique()))
        list_leagues.insert(0, '--All--')
        leagues = st.multiselect('Escriba o seleccione la(s) liga(s) objetivo', list_leagues)


        if '--All--' not in leagues:
            df = df[(df['League'].isin(leagues)) & (df['Season'].isin([season]))]
        else:
            df = df[(df['Season'].isin([season]))]

        if ('--Buscar--' not in posicion) and (len(leagues) != 0) and (len(df)!=0):

            min_minutes = st.number_input('Minimo de minutos jugados', min_value=90, max_value=int(df['Minutes played'].max())-1)
            df = df[df['Minutes played'] >= min_minutes]
            #lst_nationalities = sorted(list({name for a in df.index.get_level_values('Nationality').unique().tolist() for name in a.split(', ')}))
            #bool_nationality = st.checkbox('¿Filtrar por nacionalidad?')

            #if len(lst_nationalities) > 1:
                #if bool_nationality:
                    #nationality = st.selectbox('Nacionalidad',lst_nationalities)
                    #df = df[df.index.get_level_values('Nationality').str.contains(nationality, na=False)]

            if int(df['Age'].min())<int(df['Age'].max()):
                bool_age = st.checkbox('¿Filtrar por edad?')
                if bool_age:
                    df['Age']=df['Age'].astype(int)
                    age = st.slider('Rango de edad', int(df.query('Age >= 10')['Age'].min()),int(df['Age'].max()), value=(int(df.query('Age >= 10')['Age'].min()), int(df['Age'].max())))
                    df = df[(df['Age'] >= int(age[0])) & (df['Age'] <= int(age[-1]))]

            st.write("""
                 ***
                 ***
                 ***
                 """)
            
            df_raw = copy.deepcopy(df)
            percentile(df)

            df = Xp_ranking(df,weight=w,d_metric=dict_metrics[dict_metrics_pos[posiciones[posicion]]])
            table_streamlit(df,posiciones[posicion])

            st.write("""
                 ***
                 """)
            df_radar = pd.DataFrame()
            with st.expander('Comparar con Radar'):
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
                
                list_teams = df_radar_other.index.get_level_values('Team').unique().tolist()
                clean_list_teams = [x for x in list_teams if str(x)!='nan']
                list_teams = sorted(clean_list_teams)
                list_teams.insert(0, '--All--')
                teams = st.multiselect('Escriba o seleccione el (los) equipo(s)', list_teams, '--All--')
                if '--All--' not in teams:
                    df_radar_other = df_radar_other[df_radar_other.index.get_level_values('Team').isin(teams)]
                if len(df_radar_other.index.get_level_values('Name').tolist()) != len(set(df_radar_other.index.get_level_values('Name').tolist())):
                    names_other = st.multiselect('Escriba o seleccione jugador(es)', sorted([f"{n} ({l})" for n, l in zip(df_radar_other.index.get_level_values('Name').tolist(), df_radar_other['League'].values.tolist())]))
                    df_radar_other = df_radar_other[df_radar_other['League'].isin([n.split(' (')[1].split(')')[0] for n in names_other])]
                    names_other = [n.split(' (')[0] for n in names_other]
                else:
                    names_other = st.multiselect('Escriba o seleccione jugador(es)', sorted(df_radar_other.index.get_level_values('Name').tolist()))
                df_radar_other = df_radar_other[df_radar_other.index.get_level_values('Name').isin(names_other)]
                df_radar = df_radar.append(df_radar_other)
                st.write("""## Parámetros de gráficas""")
                number_var = len(dict_var_rad[posiciones[posicion]])
                N_variables = st.slider('Número de variables en radar', 5,number_var)
            
            if len(df_radar)!=0:
                radar_streamlit(df_radar, df_raw, posiciones[posicion], w, N_variables)