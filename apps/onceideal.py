import streamlit
from modelo import *

def app():
    df_in = base_jugadores()
    df_gk_in = base_arqueros()

    df = copy.deepcopy(df_in)
    df = df[~df['League'].isin(['---'])]
    df = df[~df.index.get_level_values('Nationality').str.contains('0', na=False)]
    df = df[~df.index.get_level_values('Team').str.contains('0', na=False)]
    df = df[df['Minutes played'] >= 90]
    df_gk = copy.deepcopy(df_gk_in)
    df_gk["xG conceded - Goals conceded"]=df_gk['xG conceded']-df_gk['Goals conceded']
    df_gk = df_gk[~df_gk['League'].isin(['---'])]
    df_gk = df_gk[~df_gk.index.get_level_values('Nationality').str.contains('0', na=False)]
    df_gk = df_gk[~df_gk.index.get_level_values('Team').str.contains('0', na=False)]
    df_gk = df_gk[df_gk['Minutes played'] >= 90]
    percentile(df_gk)
    df_copy = copy.deepcopy(df)
    st.write("""
             # 11 ideal
             > Mejores jugadores por táctica.
             """)
    st.write("""## Jugadores a incluir""")
    list_seasons = sorted(list(df['Season'].unique()), reverse=True)
    season = st.selectbox('Escriba o seleccione la temporada', list_seasons)
    df_copy =df_copy[df_copy['Season'].isin([season])]
    df_gk = df_gk[df_gk['Season'].isin([season])]
    list_leagues = sorted(list(df_copy['League'].unique()))
    list_leagues.insert(0, '--All--')
    leagues = st.multiselect('Escriba o seleccione la(s) liga(s) objetivo', list_leagues, '--All--')
    if ('--All--' not in leagues) and (len(leagues)!=0):
        df_copy =df_copy[df_copy['League'].isin(leagues)]
        df_gk = df_gk[df_gk['League'].isin(leagues)]
    with st.expander('Filtros adicionales'):
        min_minutes = st.number_input('Minimo de minutos jugados', min_value=90, max_value=int(max([df_copy['Minutes played'].max(), df_gk['Minutes played'].max()]))-1)
        df_copy =df_copy[df_copy['Minutes played'] >= min_minutes]
        df_gk = df_gk[df_gk['Minutes played'] >= min_minutes]
        lst_nationalities = sorted(list(set(list({name for a in df_copy.index.get_level_values('Nationality').unique().tolist() for name in a.split(', ')})+list({name for a in df_gk.index.get_level_values('Nationality').unique().tolist() for name in a.split(', ')}))))
        if len(lst_nationalities) > 1:
            lst_nationalities.insert(0, '--All--')
            nationality = st.selectbox('Nacionalidad',lst_nationalities)
            if '--All--' not in nationality:
                df_copy =df_copy[df_copy.index.get_level_values('Nationality').str.contains(nationality, na=False)]
                df_gk = df_gk[df_gk.index.get_level_values('Nationality').str.contains(nationality, na=False)]
        else:
            nationality='--All--'
        if int(min([df_copy.query('Age >= 10')['Age'].min(), df_gk.query('Age >= 10')['Age'].min()]))<int(max([df_copy['Age'].max(), df_gk['Age'].max()])):
            age = st.slider('Rango de edad', int(min([df_copy.query('Age >= 10')['Age'].min(), df_gk.query('Age >= 10')['Age'].min()])), int(max([df_copy['Age'].max(), df_gk['Age'].max()])), value=(int(min([df_copy.query('Age >= 10')['Age'].min(), df_gk.query('Age >= 10')['Age'].min()])), int(max([df_copy['Age'].max(), df_gk['Age'].max()]))))
            df_copy =df_copy[(df_copy['Age'] >= int(age[0])) & (df_copy['Age'] <= int(age[-1]))]
            df_gk = df_gk[(df_gk['Age'] >= int(age[0])) & (df_gk['Age'] <= int(age[-1]))]
    st.write("""## Táctica""")
    list_tactics = list(dict_tactics.keys())
    list_tactics.insert(0, '--Buscar--')
    tactic = st.selectbox('Escriba o seleccione la táctica de juego', list_tactics)
    if ('--Buscar--' not in tactic) and (len(leagues)!=0):
        dream_team(tactic, df, df_gk, season, leagues, min_minutes, nationality, age)