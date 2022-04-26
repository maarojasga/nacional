from modelo import *
from api import *
import matplotlib.pyplot as plt
from matplotlib.patches import Arc

def app():
    st.write('# Mapa de Tiros por Equipo')
    plt.style.use('dark_background')
    @st.cache
    def descargar_partidos(id_equipo):
        local = partidos['team1_id'] ==  id_equipo
        visitante = partidos['team2_id'] ==  id_equipo
        partidos_equipo = partidos[local | visitante ]
        eventos = pd.DataFrame()
        for i in partidos_equipo.id :
            temporal = show_match_events(str(i))
            eventos = pd.concat([eventos, temporal], ignore_index=True)
        eventos = eventos[eventos['player_id'].notna()]
        eventos['player_id'] = eventos['player_id'].astype(int)
        return eventos

    
    @st.cache
    def filtrar_eventos(eventos, id_team):
        filtrados = eventos[eventos['team_id']==id_team]
        return filtrados
    @st.cache
    def filtrar_eventos_contra(eventos, id_team):
        filtrados = eventos[eventos['team_id']!=id_team]
        return filtrados




    
    def calculate_xG(df):
        x_tot=105
        y_der=24.85
        y_izq=43.15
        y_centro=34

        b=[ -1.2111 , 0.6653, -0.1039 ]

        df['numerador']=(x_tot-df['pos_x'])*(x_tot-df['pos_x'])+(y_izq-df['pos_y'])*(y_der-df['pos_y'])
        df['denominador']=np.sqrt((x_tot-df['pos_x'])**2 + (y_der-df['pos_y'])**2 ) * np.sqrt((x_tot-df['pos_x'])**2 + (y_izq-df['pos_y'])**2)
        df['angulo']=np.arccos(df['numerador']/df['denominador'])
        df['distancia']=np.sqrt((x_tot-df['pos_x'])**2+(y_centro-df['pos_y'])**2)
        df['Suma'] = -b[0]-b[1]*df['angulo']-b[2]*df['distancia']
        df['xG'] = 1/(1+np.exp(df['Suma']))

        return df

    def tiros_jugador(data):

        col1, col2 = st.columns(2)
        tiros=['Shot on target', 'Shot into the bar/post', 'Shot blocked', 'Shot blocked by field player', 'Goal', 'Wide shot']
        tirosygoles = data[data['action_name'].isin(tiros)]
        tirosygoles = calculate_xG(tirosygoles)
        tiros = tirosygoles[tirosygoles['action_name']!='Goal']
        goles = tirosygoles[tirosygoles['action_name']=='Goal']
        #Create figure
        fig=plt.figure()
        fig.set_size_inches(5.25, 6.8)
        ax=fig.add_subplot(1,1,1)
        #Pitch Outline & Centre Line
        plt.plot([0,0],[0,68], color="grey")
        plt.plot([0,105],[68,68], color="grey")
        plt.plot([105,105],[68,0], color="grey")
        plt.plot([105,0],[0,0], color="grey")
        plt.plot([52.5,52.5],[0,68], color="grey")
        #Left Penalty Area
        plt.plot([16.5,16.5],[54.15,13.85],color="grey")
        plt.plot([0,16.5],[54.15,54.15],color="grey")
        plt.plot([16.5,0],[13.85,13.85],color="grey")
        #Right Penalty Area
        plt.plot([105,88.5],[54.15,54.15],color="grey")
        plt.plot([88.5,88.5],[54.15,13.85],color="grey")
        plt.plot([88.5,105],[13.85,13.85],color="grey")
        #Left 6-yard Box
        plt.plot([0,5.5],[43.15,43.15],color="grey")
        plt.plot([5.5,5.5],[24.85,43.15],color="grey")
        plt.plot([5.5,0],[24.85,24.85],color="grey")
        #Right 6-yard Box
        #plt.plot([99.5,105],[24.85,24.85],color="grey")​
        plt.plot([105,99.5],[43.15,43.15],color="grey")
        plt.plot([99.5, 99.5],[43.15,24.85],color="grey")
        plt.plot([99.5, 105], [24.85, 24.85], color = 'grey')
        #Prepare Circles
        centreCircle = plt.Circle((52.5,34),9.15,color="grey",fill=False)
        centreSpot = plt.Circle((52.5,34),0.8,color="grey")
        #Draw Circles
        ax.add_patch(centreCircle)
        ax.add_patch(centreSpot)

        #Prepare Arcs
        rightArc = Arc((94,34),height=18.3,width=18.3,angle=0,theta1=127,theta2=234,color="grey")
        #Draw Arcs
        ax.add_patch(rightArc)
        plt.ylim(0, 68)
        plt.xlim(52.5, 105)
        #Tidy Axes
        plt.axis('off')
        for i in tiros.index:
            plt.plot(tiros['pos_x'][i],tiros['pos_y'][i],'o',  markeredgecolor = 'red',  markersize = 80*tiros['xG'][i], color='red', alpha=0.5)
        for i in goles.index:
            plt.plot(goles['pos_x'][i],goles['pos_y'][i],  'o', markeredgecolor = 'cyan', markersize = 80*goles['xG'][i],  color='cyan', alpha=0.5)

        plt.plot(1,1,'o', markersize =7, markeredgecolor = 'red', color='red', alpha=0.5, label = 'Tiros')
        plt.plot(1,1,'o', markersize =7, markeredgecolor = 'cyan', color='cyan', alpha=0.5, label = 'Goles')
        plt.plot(1,1,'o', markersize =7, markeredgecolor = 'black', color=  'black' ,label = '   ')

        plt.plot(1,1,'o', markersize =9, markeredgecolor = 'white', color=  'black' ,label = ' ')
        plt.plot(1,1,'o', markersize =11, markeredgecolor = 'white', color=  'black' ,label = 'xG')
        plt.plot(1,1,'o', markersize =13, markeredgecolor = 'white', color=  'black' ,label = '  ')
        #plt.plot(1,1,'o', markersize =15, markeredgecolor = 'white', color=  'black' ,label = '    ')


        plt.legend(loc = 'upper left', ncol=2)
        col1.pyplot(fig)
        #Create figure
        fig2=plt.figure()
        #fig.set_size_inches(16, 8)
        ax=fig2.add_subplot(1,1,1)

        plt.plot([-9,9],[0,0], color="grey")
        plt.plot([-5,-5],[0,3.5], color="grey")
        plt.plot([5,5],[0,3.5], color="grey")
        plt.plot([-5,5],[3.5,3.5], color="grey")

        plt.plot([-4.5,4.5],[3.7,3.7], color="grey")
        plt.plot([-5,-4.5],[3.5,3.7], color="grey")
        plt.plot([4.5,5],[3.7,3.5], color="grey")

        plt.plot([-4.5,-4.5],[1,3.7], color="grey")
        plt.plot([-5,-4.5],[0,1], color="grey")
        plt.plot([4.5,5],[1,0], color="grey")
        plt.plot([-4.5,4.5],[1,1], color="grey")
        plt.plot([4.5,4.5],[1,3.7], color="grey")

        plt.ylim(-1, 8)
        plt.xlim(-9, 9)
        plt.axis('off')
        for i in tiros.index:
            plt.plot(tiros['gate_x'][i],tiros['gate_y'][i],'o', markersize =  80*tiros['xG'][i], markeredgecolor = 'red', color='red', alpha=0.5)
        for i in goles.index:
            plt.plot(goles['gate_x'][i],goles['gate_y'][i],  'o', markersize =80*goles['xG'][i], markeredgecolor = 'cyan', color='cyan', alpha=0.5)

        plt.plot(1,-11,'o', markersize =7, markeredgecolor = 'red', color='red', alpha=0.5, label = 'Tiros')
        plt.plot(1,-11,'o', markersize =7, markeredgecolor = 'cyan', color='cyan', alpha=0.5, label = 'Goles')
        plt.plot(1,-11,'o', markersize =7, markeredgecolor = 'black', color=  'black' ,label = '   ')

        p1 = ax.plot(1, -11, 'o', markersize = 7, markeredgecolor = 'white', color='black', label = ' ')
        p2 = ax.plot(1, -11, 'o', markersize = 9, markeredgecolor = 'white', color='black', label = 'xG')
        p3 = plt.plot(1, -11, 'o', markersize = 11, markeredgecolor = 'white', color='black', label = '  ')

        plt.legend(loc = 'upper left', ncol = 2)

        col2.pyplot(fig2)




    temporada=st.selectbox("Seleccione la temporada",list(temporadas.keys()))
    lista_ligas=list(ligas.keys())
    lista_ligas.insert(0,'Seleccionar')
    liga=st.selectbox('Seleccionar liga',lista_ligas,0)

    if liga!='Seleccionar':
        equipos = extract_teams(ligas[liga],temporadas[temporada])
        escoger_partidos = st.checkbox('Escoger partidos')

        partidos=extract_matches(ligas[liga],temporadas[temporada])
        partidos=partidos[partidos['available_events']==True]
        
        equipo = st.selectbox('Seleccionar equipo', ['Seleccionar']+list(equipos['name']),0 )

        if equipo != 'Seleccionar':
            id_equipo = equipos.set_index('name').loc[equipo]['id']

            if escoger_partidos:
                local = partidos['team1_id'] ==  id_equipo
                visitante = partidos['team2_id'] ==  id_equipo
                partidos_equipo = partidos[local | visitante ]
                lista_partidos=partidos_equipo['match_date'].str.replace('-','/').str.split(' ').str[0]+' - '+partidos_equipo['match_name']
                partidos_escogidos = st.multiselect('Seleccionar partidos',list(lista_partidos) )
                eventos = pd.DataFrame()
                for partido in partidos_escogidos:
                    partido_split = partido.split(' - ',1)[1] 
                    id_partido = partidos.loc[partidos['match_name']==partido_split,'id'].values[0]
                    temporal = show_match_events(id_partido)
                    eventos = pd.concat([eventos,temporal],ignore_index=True)

            else:

                with st.spinner('Descargando eventos ...'):
                    eventos = descargar_partidos(id_equipo)

            eventos_filtrados = filtrar_eventos(eventos,id_equipo)
            eventos_filtrados_contra = filtrar_eventos_contra(eventos,id_equipo)
            st.write("""
            **Tiros a favor**
            """)
            tiros_jugador(eventos_filtrados)
            st.write("""
            **Tiros en contra**
            """)
            tiros_jugador(eventos_filtrados_contra)