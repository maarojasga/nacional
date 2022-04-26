from modelo import *
import pandas as pd
from api import *
color_xpecta='#7ee1bd'



def app():
    st.write(
        """
        # Gráficas de Goles vs Goles esperados por equipo
        """
    )
    temporada=st.selectbox("Seleccione la temporada",list(temporadas.keys()))
    liga = st.selectbox("Seleccione la liga de la cual desea ver los equipos",['Seleccionar']+list(ligas.keys()))
    if liga != "Seleccionar":
        teams= extract_teams(ligas[liga],temporadas[temporada])
        partidos = pd.DataFrame()
        for idx in teams['id'].unique():
            temp=team_match_match(idx,ligas[liga],temporadas[temporada])
            partidos=partidos.append(temp,ignore_index=True)
        partidos[['Goals scored - Result','xG']]=partidos[['Goals scored - Result','xG']].astype(float)
        for idx,row in partidos.iterrows():
            xg=row['xG']
            id_=row['Id Partido']
            equipo=row['Equipo']
            partidos.loc[(partidos['Id Partido']==id_)&(partidos['Equipo']!=equipo),'Op xG']=xg
        
        df_grafica=partidos.groupby('Equipo').sum()[['Goals scored - Result','xG','Op xG']]
        df_grafica['Net xG (Goles - xG)']=df_grafica['Goals scored - Result']-df_grafica['xG']
        df_grafica['Net xG (xG favor - xG contra)']=df_grafica['xG']-df_grafica['Op xG']
        st.write("""
            ## Graficas comparación xG con Goles
        """)
        
        fig, ax = plt.subplots()
        df_grafica['Net xG (Goles - xG)'].sort_values(ascending=True).plot.barh(color=color_xpecta,ax=ax)
        ax.set_title("Net xG (Goles anotados - xG) Equipos",loc='left')
        for i, v in enumerate(sorted(df_grafica.sort_values(by='Net xG (Goles - xG)',ascending=True)['Net xG (Goles - xG)'])):
            if v > 0:
                plt.text(v+0.01, i, str(round(v, 2)), color='white', va="center")
            else:
                plt.text(v-0.5, i, str(round(v, 2)), color='white', va="center")

        plt.xlim(df_grafica['Net xG (Goles - xG)'].min()-0.6,df_grafica['Net xG (Goles - xG)'].max()+0.5)  
        
        st.pyplot(fig)

        ordered_df=df_grafica.sort_values('Net xG (Goles - xG)',ascending=True)
        my_range=range(1,len(ordered_df.index)+1)

        fig, ax = plt.subplots()
        plt.hlines(y=my_range, xmin=ordered_df['xG'], xmax=ordered_df['Goals scored - Result'], color='white', alpha=0.4)
        plt.scatter(ordered_df['xG'], my_range, color='white', alpha=1, label='xG',s=100)
        plt.scatter(ordered_df['Goals scored - Result'], my_range, color=color_xpecta, alpha=1 , label='Goles',s=100)
        ax.legend(loc='upper left', bbox_to_anchor=(1.04, 1),)


        plt.yticks(my_range, ordered_df.index)
        plt.title("Goles vs xG", loc='left')
        plt.xlabel('Valor')
        plt.ylabel('Equipo')
        
        
        st.pyplot(fig)
        st.write("""
            ## Graficas comparación xG favor con xG contra
        """)
        fig, ax = plt.subplots()
        df_grafica['Net xG (xG favor - xG contra)'].sort_values(ascending=True).plot.barh(color=color_xpecta,ax=ax)
        ax.set_title("Net xG (xG favor - xG contra) Equipos",loc='left')
        for i, v in enumerate(sorted(df_grafica.sort_values(by='Net xG (xG favor - xG contra)',ascending=True)['Net xG (xG favor - xG contra)'])):
            if v > 0:
                plt.text(v+0.01, i, str(round(v, 2)), color='white', va="center")
            else:
                plt.text(v-0.5, i, str(round(v, 2)), color='white', va="center")

        plt.xlim(df_grafica['Net xG (xG favor - xG contra)'].min()-0.6,df_grafica['Net xG (xG favor - xG contra)'].max()+0.5)  
        st.pyplot(fig)

        ordered_df=df_grafica.sort_values('Net xG (xG favor - xG contra)',ascending=True)
        my_range=range(1,len(ordered_df.index)+1)

        fig, ax = plt.subplots()
        ax.hlines(y=my_range, xmin=ordered_df['xG'], xmax=ordered_df['Op xG'], color='white', alpha=0.4)
        ax.scatter(ordered_df['xG'], my_range, color='white', alpha=1, label='xG (A favor)',s=100)
        ax.scatter(ordered_df['Op xG'], my_range, color=color_xpecta, alpha=1 , label='xG (En contra)',s=100)
        ax.legend(loc='upper left', bbox_to_anchor=(1.04, 1),)

        plt.yticks(my_range, ordered_df.index)
        plt.title("xG Favor vs xG Contra", loc='left')
        plt.xlabel('Valor')
        plt.ylabel('Equipo')
        
        
        st.pyplot(fig)

        st.write("""
            ## Tabla con datos
        """)
        df_grafica=df_grafica.rename(columns={'Goals scored - Result':'Goles'})
        st.write(np.round(df_grafica,2).astype(str))