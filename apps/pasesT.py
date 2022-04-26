from modelo import *
import pandas as pd
from api import *


def app():
    st.write(
        """
        # Mapa de pases totales
        """
    )
    temporada=st.selectbox("Seleccione la temporada",list(temporadas.keys()))
    liga = st.selectbox("Seleccione la liga de la cual desea ver los equipos",list(ligas.keys()))
    teams= extract_teams(ligas[liga],temporadas[temporada])
    equipo = st.selectbox("Seleccione el equipo", ['Seleccionar']+teams['name'].to_list())
    if equipo != 'Seleccionar':
        team_id=teams.loc[teams['name']==equipo,'id'].values[0]
        df = extract_matches(ligas[liga],temporadas[temporada])
        df = df[df['available_events']==True]
        partidos_id = df.loc[(df['team1_id']==team_id)|(df['team2_id']==team_id),'id'].values.tolist()

        partidos = pd.DataFrame()
        for id in partidos_id:
            try:
                t=pd.read_csv(f'DataApi/{id}.csv')
                partidos = partidos.append(t,ignore_index=True)
            except:
                t=show_match_events(id)
                try:
                    t.to_csv(f'DataApi/{id}.csv')
                    partidos=partidos.append(t,ignore_index=True)
                except:
                    partidos=partidos.append(t,ignore_index=True)
        matriz_de_pases(partidos,equipo)