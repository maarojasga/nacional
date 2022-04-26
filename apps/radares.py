from os import write
from modelo import *
import streamlit as st


dict_import={
    'General':['xG (Expected goals) per 90 min','Goals per 90 min',"Opponent's xG per 90 min",'Expected points per 90 min','Challenges won, % per 90 min','Air challenges won, % per 90 min','Successful actions, % per 90 min','Accurate passes, % per 90 min','Accurate crosses, % per 90 min','Lost balls per 90 min'],
    'Ofensivo':['xG (Expected goals) per 90 min','Goals per 90 min','Chances per 90 min','Shots per 90 min','Shots on target per 90 min','xG per shot per 90 min','xG per goal per 90 min','Key passes per 90 min','Challenges in attack won, % per 90 min','Attacking challenges won per 90 min','Successful dribbles, % per 90 min','Dribbles successful per 90 min'],
    'Defensivo':["Opponent's xG per 90 min",'Challenges in defence won, % per 90 min','Defensive challenges won per 90 min','Tackles won, % per 90 min','Tackles successful per 90 min','Ball interceptions per 90 min','Free ball pick ups per 90 min','Ball recoveries per 90 min',"Ball recoveries in opponent's half per 90 min",'Team pressing successful per 90 min','Pressing efficiency, % per 90 min'],
    'Estilo de juego':['Positional attacks per 90 min','% of efficiency for positional attacks per 90 min','Counter-attacks per 90 min','% of efficiency for counterattacks per 90 min','Set pieces attacks per 90 min' ,'% of efficiency for set-piece attacks per 90 min','Building-ups per 90 min','Building-ups without pressing per 90 min','High pressing per 90 min','High pressing, % per 90 min','Ball possession, % per 90 min','Average duration of ball possession, min per 90 min'],
    'Zonas de ataque':['Attacks - center per 90 min','Efficiency for attacks through the central zone, % per 90 min','Attacks - left flank per 90 min','Efficiency for attacks through the right flank, % per 90 min','Attacks - right flank per 90 min','Efficiency for attacks through the left flank, % per 90 min',"Entrances on opponent's half per 90 min","Entrances on final third of opponent's half per 90 min","Entrances to the opponent's box per 90 min" ]
}
def search_options(n, df_in):
    df_temp = copy.deepcopy(df_in)
    with st.beta_expander(f'Buscar equipo {n}'):
        list_seasons = sorted(list(df_temp['Season'].unique()), reverse=True)
        season = st.selectbox('Escriba o seleccione la temporada', list_seasons, key=str(n))
        df_temp = df_temp[df_temp['Season'].isin([season])]
        league = st.selectbox('Liga', sorted(list(df_temp['League'].unique())), key=str(n+10))
        df_temp = df_temp[df_temp['League'].isin([league])]
        list_names = sorted(df_temp['Team'])
        list_names.insert(0, '--Buscar--')
        df_raw=copy.deepcopy(df_temp)
        percentile(df_temp)
        pl_name = st.selectbox('Escriba o seleccione el equipo', list_names, key=str(n+100))
        if '--Buscar--' not in pl_name:
            df_temp = df_temp[df_temp['Team'].isin([pl_name])]
            df_raw = df_raw[df_raw['Team'].isin([pl_name])]
            return [df_raw,df_temp]
        else:
            return pd.DataFrame(), pd.DataFrame()
def app():
    st.write("""
             # Radar Equipos 
             > Radares de equipos seleccionados.
             """)
    df = base_equipos()
    n_search = st.number_input('¿Cuantos equipos va a comparar?', min_value=1, max_value=10)
    df_radar = pd.DataFrame()
    df_raw = pd.DataFrame()
    for n in range(0,n_search):
        df_raw_s,df_selection = search_options(n+1, df)
        if len(df_selection)!=0 :
            df_radar = df_radar.append(df_selection)
            df_raw = df_raw.append(df_raw_s)
    if (len(df_radar)!=0):
        radar_type=st.selectbox('¿Que tipo de radar desea visualizar?',list(dict_import.keys()))
        radar_equipos(df_radar,df_raw,dict_import[radar_type],radar_type)
        for liga in df.League.unique():
            st.write(f"Tabla {liga}")
            df['Puntos por 90 min']=df['Puntos']/df['Partidos jugados']
            df['Puntos esperados por 90 min']=df['Expected points']/13

            st.write(df.loc[df['League']==liga,['Team','Puntos','Puntos por 90 min','Expected points','Puntos esperados por 90 min','Expected points per 90 min','Partidos jugados']].sort_values('Puntos',ascending=False).reset_index(drop=True))

            fig = plt.figure()
            ax = fig.add_subplot(1,1,1)
            ax.scatter(x=df.loc[df['League']==liga,'Puntos'],y=df.loc[df['League']==liga,'Expected points'])

            for idx, row in df.loc[df['League']==liga,['Puntos','Expected points','Team']].iterrows(): 
                plt.text(row['Puntos'], row['Expected points'], row['Team'])
            plt.title("Puntos vs puntos esperados")
            plt.xlabel("Puntos por 90 min")
            plt.ylabel("Puntos por esperados 90 min")
            ax.plot([0,df['Puntos'].max()],[0,df['Puntos'].max()],color='white')
            st.pyplot(fig)