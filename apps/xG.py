from modelo import *
import pandas as pd
from api import *
color_xpecta='#7ee1bd'

def app():
    st.write(
        """
        # Gráfica de Goles vs Goles esperados por jugador
        """
    )
    temporada = st.selectbox("Seleccione la temporada",list(temporadas.keys()))
    liga = st.selectbox("Seleccione la liga de la cual desea ver los equipos",list(ligas.keys()))
    teams= extract_teams(ligas[liga],temporadas[temporada])
    equipo = st.selectbox("Seleccione el equipo", ['Seleccionar']+teams['name'].to_list())
    if equipo !='Seleccionar':
        team_id=teams.loc[teams['name']==equipo,'id'].values[0]
        jugadores=show_players(team_id)
        jugadores=jugadores[['id','firstname','lastname','position1_name']]
        jugadores=jugadores[jugadores['position1_name']!='Goalkeeper']

        ordered_df=consolidar_jugadores(jugadores,liga,temporadas[temporada])
        
        my_range=range(1,len(ordered_df.index)+1)

        fig=plt.figure(figsize=(10,12))
        plt.hlines(y=my_range, xmin=ordered_df['xG'], xmax=ordered_df['Goals'], color='white', alpha=0.4)
        plt.scatter(ordered_df['xG'], my_range, color='white', alpha=1, label='xG',s=100)
        plt.scatter(ordered_df['Goals'], my_range, color=color_xpecta, alpha=1 , label='Goles',s=100)
        plt.legend(loc=4)

        plt.yticks(my_range, ordered_df['Jugador'])
        plt.title("Goles vs xG", loc='left')
        plt.xlabel('Valor')
        plt.ylabel('Jugador')
        st.write("""
            ## Gráfica
        """)
        st.pyplot(fig)
        st.write("""
            ## Tabla con datos
        """)

        disp_df=ordered_df.sort_values('Goals',ascending=False)[['Jugador','Goals','xG','xG per shot','Minutes played']].reset_index(drop=True).set_index('Jugador')
        disp_df['Goles - xG']=disp_df['Goals']-disp_df['xG']
        st.dataframe(disp_df.style.format({'Goals':'{:.0f}','xG':'{:.2f}','xG per shot':'{:.2f}','Minutes played':'{:.0f}','Goles - xG':'{:.2f}'}))