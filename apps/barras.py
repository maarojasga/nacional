from modelo import *
import pandas as pd
from api import *
color_xpecta='#7ee1bd'

def app():
    st.write(
        """
        # Estadísticas
        """
    )
    temporada = st.selectbox("Seleccione la temporada",list(temporadas.keys()))
    liga = st.selectbox("Seleccione la liga de la cual desea ver los equipos",list(ligas.keys()))
    teams= extract_teams(ligas[liga],temporadas[temporada])
    equipo = st.selectbox("Seleccione el equipo", ['Seleccionar']+teams['name'].to_list())
    if equipo!='Seleccionar':
        part = partidos_liga(teams,ligas[liga],temporadas[temporada])
        part['Goals scored - Result']=part['Goals scored - Result'].astype(float)
        part['Goals conceded']=part['Goals conceded']=part['Goals conceded'].astype(float)
        part['Net xG']=part['Goals scored - Result']-part['xG']
        plotear_xG(part,equipo)
        plotear_OpxG(part,equipo)

        st.write("""
            # Top variables de equipo
        """)

        ranking=part.groupby('Equipo').sum()[['xG','Opponent xG','Porteria 0','Goals scored - Result','Goals conceded','Net xG']]
        ranking['Top porteria 0']=ranking['Porteria 0'].rank(method='max',ascending=False).astype(int)
        ranking['Top xG']=ranking['xG'].rank(method='max',ascending=False).astype(int)
        ranking['Top xG Concedido']=ranking['Opponent xG'].rank(method='max').astype(int)
        ranking['Top Goles anotados']=ranking['Goals scored - Result'].rank(method='max').astype(int)
        ranking['Top Goles concedidos']=ranking['Goals conceded'].rank(method='max').astype(int)
        ranking['Top Net xG (Goles - xG)']=ranking['Net xG'].rank(method='max').astype(int)



        st.write(ranking.loc[equipo,['Top Goles anotados','Top Goles concedidos','Top Net xG (Goles - xG)','Top porteria 0','Top xG','Top xG Concedido']])
        

        


        
        
    
    
