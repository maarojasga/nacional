from modelo import *
import pandas as pd
from api import *
from matplotlib.gridspec import GridSpec
import time 
from stqdm import stqdm
color_xpecta='#7ee1bd'

nombres_columnas={
    'xG':'xG', 
    'xG (Contrario)':'xG Contrario',
    'xG_from setpiece':'xG (Balon parado)',
    'xG_from setpiece (Contrario)':'xG Contrario (Balon parado)',
    'key_passes':'Pases claves',
    'key_passes (Contrario)':'Pases claves Contrario',
    'Net xG':'Net xG (xG favor - xG contra)',
    'xG por remate':'xG por remate',
    'xG por remate (Contrario)':'xG por remate (Contrario)',
    'xG por jugada gol':'xG por jugada gol',
    'xG por jugada gol (Contrario)':'xG por jugada gol (Contrario)'
}
def axis_op(df_f,equipo,columna,ax):
    per25=np.percentile(df_f.groupby('team_name').mean()[columna],25)
    per50=np.percentile(df_f.groupby('team_name').mean()[columna],50)
    per75=np.percentile(df_f.groupby('team_name').mean()[columna],75)
        

    ax.axvspan(per25, per50, color='yellow', alpha=0.5)
    ax.axvspan(per50, per75, color='orange', alpha=0.5)
    ax.axvspan(per75, df_f[columna].max()+1, color='red', alpha=0.5)
    ax.axvspan(df_f[columna].min()-1, per25, color='green', alpha=0.5)

    for idx,row in df_f.groupby('team_name').mean().iterrows():
        eq=idx
        xg=row[columna]
        if eq==equipo:
            ax.scatter(row[columna],1,color='white',s=400,zorder=11,label=f"Promedio Temporada {equipo}")
        elif eq=='Atletico Nacional' and equipo!='Aletico nacional':
            ax.scatter(row[columna],1,color='lime',s=200,zorder=11,label="Promedio Atletico Nacional")
        else:
            ax.scatter(row[columna],1,color='grey',s=100,zorder=10)

    ax.set_title(f"{nombres_columnas[columna]}",loc='left',fontsize=15)
    ax.tick_params(left = False, right = False , labelleft = False ,labelbottom = True, bottom = True)
    ax.axvline(x=df_f.loc[(df_f['jornada']==df_f.loc[df_f['team_name']==equipo,'jornada'].max())&(df_f['team_name']==equipo),columna].values[0],linestyle='--',color='white',zorder=10,label=f'Ultimo partido {equipo}')
    if df_f.loc[(df_f['jornada']==df_f.loc[df_f['team_name']==equipo,'jornada'].max())&(df_f['team_name']==equipo),columna].values[0] < df_f.groupby('team_name').mean()[columna].min():
        xop_min= df_f.loc[(df_f['jornada']==df_f.loc[df_f['team_name']==equipo,'jornada'].max())&(df_f['team_name']==equipo),columna].values[0] 
    else:
        xop_min=df_f.groupby('team_name').mean()[columna].min() 
    if df_f.loc[(df_f['jornada']==df_f.loc[df_f['team_name']==equipo,'jornada'].max())&(df_f['team_name']==equipo),columna].values[0] < df_f.groupby('team_name').mean()[columna].max():
        xop_max= df_f.groupby('team_name').mean()[columna].max() 
    else:
        xop_max=df_f.loc[(df_f['jornada']==df_f.loc[df_f['team_name']==equipo,'jornada'].max())&(df_f['team_name']==equipo),columna].values[0] 
    if columna in ['xG por remate (Contrario)','xG por jugada gol (Contrario)']:
        ax.set_xlim((xop_min-0.005,xop_max+0.005))
    else:
        ax.set_xlim((xop_min-0.05,xop_max+0.05))
    
    ax.set_xlim(ax.get_xlim()[::-1])

def axis_eq(df_f,equipo,columna,ax):
    per25=np.percentile(df_f.groupby('team_name').mean()[columna],25)
    per50=np.percentile(df_f.groupby('team_name').mean()[columna],50)
    per75=np.percentile(df_f.groupby('team_name').mean()[columna],75)
        

    ax.axvspan(df_f[columna].min()-1, per25, color='red', alpha=0.5)
    ax.axvspan(per25, per50, color='orange', alpha=0.5)
    ax.axvspan(per50, per75, color='yellow', alpha=0.5)
    ax.axvspan(per75, df_f[columna].max()+1, color='green', alpha=0.5)

    for idx,row in df_f.groupby('team_name').mean().iterrows():
        eq=idx
        xg=row[columna]
        if eq==equipo:
            ax.scatter(row[columna],1,color='white',s=400,zorder=11,label=f"Promedio Temporada {equipo}")
        elif eq=='Atletico Nacional' and equipo!='Aletico nacional':
            ax.scatter(row[columna],1,color='lime',s=200,zorder=11,label="Promedio Atletico Nacional")
        else:
            ax.scatter(row[columna],1,color='grey',s=100,zorder=10)
    ax.set_title(f"{nombres_columnas[columna]}",loc='left',fontsize=15)
    ax.tick_params(left = False, right = False , labelleft = False ,labelbottom = True, bottom = True)
    ax.axvline(x=df_f.loc[(df_f['jornada']==df_f.loc[df_f['team_name']==equipo,'jornada'].max())&(df_f['team_name']==equipo),columna].values[0],linestyle='--',color='white',zorder=10,label=f"Ultimo partido {equipo}")
    
    
    if df_f.loc[(df_f['jornada']==df_f.loc[df_f['team_name']==equipo,'jornada'].max())&(df_f['team_name']==equipo),columna].values[0] < df_f.groupby('team_name').mean()[columna].min():
        xop_min2= df_f.loc[(df_f['jornada']==df_f.loc[df_f['team_name']==equipo,'jornada'].max())&(df_f['team_name']==equipo),columna].values[0] 
    else:
        xop_min2=df_f.groupby('team_name').mean()[columna].min() 
    if df_f.loc[(df_f['jornada']==df_f.loc[df_f['team_name']==equipo,'jornada'].max())&(df_f['team_name']==equipo),columna].values[0] < df_f.groupby('team_name').mean()[columna].max():
        xop_max2=df_f.groupby('team_name').mean()[columna].max() 
    else:
        xop_max2= df_f.loc[(df_f['jornada']==df_f.loc[df_f['team_name']==equipo,'jornada'].max())&(df_f['team_name']==equipo),columna].values[0] 
    if columna in ['xG por remate','xG por jugada gol']:
        ax.set_xlim((xop_min2-0.005,xop_max2+0.005))
    else:
        ax.set_xlim((xop_min2-0.05,xop_max2+0.05))
        
def barra_eq(df_f,equipo,columna):
    fig2=plt.figure(figsize=(10,2))
    per25=np.percentile(df_f.groupby('team_name').mean()[columna],25)
    per50=np.percentile(df_f.groupby('team_name').mean()[columna],50)
    per75=np.percentile(df_f.groupby('team_name').mean()[columna],75)
        

    plt.axvspan(df_f[columna].min()-1, per25, color='red', alpha=0.5)
    plt.axvspan(per25, per50, color='orange', alpha=0.5)
    plt.axvspan(per50, per75, color='yellow', alpha=0.5)
    plt.axvspan(per75, df_f[columna].max()+1, color='green', alpha=0.5)

    for idx,row in df_f.groupby('team_name').mean().iterrows():
        eq=idx
        xg=row[columna]
        if eq==equipo:
            plt.scatter(row[columna],1,color='white',s=200,zorder=11,label="Promedio Temporada")
        else:
            plt.scatter(row[columna],1,color='grey',zorder=10)
    plt.title(f"{columna}")
    plt.tick_params(left = False, right = False , labelleft = False ,labelbottom = True, bottom = True)
    plt.axvline(x=df_f.loc[(df_f['jornada']==df_f.loc[df_f['team_name']==equipo,'jornada'].max())&(df_f['team_name']==equipo),columna].values[0],linestyle='--',color='white',zorder=10,label="Ultimo partido")
    
    if df_f.loc[(df_f['jornada']==df_f.loc[df_f['team_name']==equipo,'jornada'].max())&(df_f['team_name']==equipo),columna].values[0] < df_f.groupby('team_name').mean()[columna].min():
        xop_min2= df_f.loc[(df_f['jornada']==df_f.loc[df_f['team_name']==equipo,'jornada'].max())&(df_f['team_name']==equipo),columna].values[0] - 0.05
    else:
        xop_min2=df_f.groupby('team_name').mean()[columna].min() - 0.05
    if df_f.loc[(df_f['jornada']==df_f.loc[df_f['team_name']==equipo,'jornada'].max())&(df_f['team_name']==equipo),columna].values[0] < df_f.groupby('team_name').mean()[columna].max():
        xop_max2=df_f.groupby('team_name').mean()[columna].max() + 0.05
    else:
        xop_max2= df_f.loc[(df_f['jornada']==df_f.loc[df_f['team_name']==equipo,'jornada'].max())&(df_f['team_name']==equipo),columna].values[0] + 0.05
    plt.legend()
    plt.xlim((xop_min2,xop_max2))
    plt.legend(bbox_to_anchor=(1.04,0.5), loc="center left")
    st.pyplot(fig2)

def barra_op(df_f,equipo,columna):
    fig2=plt.figure(figsize=(10,2))
    per25=np.percentile(df_f.groupby('team_name').mean()[columna],25)
    per50=np.percentile(df_f.groupby('team_name').mean()[columna],50)
    per75=np.percentile(df_f.groupby('team_name').mean()[columna],75)
        

    plt.axvspan(per25, per50, color='yellow', alpha=0.5)
    plt.axvspan(per50, per75, color='orange', alpha=0.5)
    plt.axvspan(per75, df_f[columna].max()+1, color='red', alpha=0.5)

    for idx,row in df_f.groupby('team_name').mean().iterrows():
        eq=idx
        xg=row[columna]
        if eq==equipo:
            plt.scatter(row[columna],1,color='white',s=200,zorder=11,label="Promedio Temporada")
        else:
            plt.scatter(row[columna],1,color='grey',zorder=10)

    plt.title(f"{columna}")
    plt.tick_params(left = False, right = False , labelleft = False ,labelbottom = True, bottom = True)
    plt.axvline(x=df_f.loc[(df_f['jornada']==df_f.loc[df_f['team_name']==equipo,'jornada'].max())&(df_f['team_name']==equipo),columna].values[0],linestyle='--',color='white',zorder=10,label='Ultimo partido')
    plt.axvspan(0, per25, color='green', alpha=0.5)
    if df_f.loc[(df_f['jornada']==df_f.loc[df_f['team_name']==equipo,'jornada'].max())&(df_f['team_name']==equipo),columna].values[0] < df_f.groupby('team_name').mean()[columna].min():
        xop_min= df_f.loc[(df_f['jornada']==df_f.loc[df_f['team_name']==equipo,'jornada'].max())&(df_f['team_name']==equipo),columna].values[0] - 0.05
    else:
        xop_min=df_f.groupby('team_name').mean()[columna].min() - 0.05
    if df_f.loc[(df_f['jornada']==df_f.loc[df_f['team_name']==equipo,'jornada'].max())&(df_f['team_name']==equipo),columna].values[0] < df_f.groupby('team_name').mean()[columna].max():
        xop_max= df_f.groupby('team_name').mean()[columna].max() + 0.05
    else:
        xop_max=df_f.loc[(df_f['jornada']==df_f.loc[df_f['team_name']==equipo,'jornada'].max())&(df_f['team_name']==equipo),columna].values[0] + 0.05
    plt.xlim((0,xop_max))
    plt.gca().invert_xaxis()
    plt.legend(bbox_to_anchor=(1.04,0.5), loc="center left")
    st.pyplot(fig2)

def app():
    st.write(
        """
        # Estadísticas
        """
    )
    
    liga = st.selectbox("Seleccione la liga de la cual desea ver los equipos",list(ligas.keys()))
    if liga!='Seleccionar':
        
        partidos=extract_matches(ligas[liga],29)
        
        partidos=partidos[partidos['available_events']==True]
        df=pd.DataFrame()

        for idx in stqdm(partidos['id'].unique()):
            try:
                temp=pd.read_csv(f'DataApi/{idx}.csv')
            except:
                temp=show_match_events(idx)
                temp.to_csv(f'DataApi/{idx}.csv')
            temp['match_id']=str(idx)
            try:
                temp['jornada']=int(partidos.loc[partidos['id']==idx,'round_id'].values[0])
            except:
                temp['jornada']=int(partidos['round_id'].max())
            df=df.append(temp,ignore_index=True)

        tiros=['Shot on target', 'Shot into the bar/post', 'Shot blocked', 'Shot blocked by field player', 'Goal', 'Wide shot']
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
        df['xG']=0
        df['Goles']=df['action_name'].apply(lambda x: 1 if x=='Goal' else 0)
        df.loc[df['action_name'].isin(tiros),'xG'] = df.loc[df['action_name'].isin(tiros),'Suma'].apply(lambda x:1/(1+np.exp(x)))
        set_pieces=['Accurate crossing from set piece with a goal','Set piece cross with goal','Accurate crossing from set piece with a shot','Misplaced crossing from set piece with a shot','Misplaced crossing from set piece with a goal']
        df['prev_action']=df['action_name'].shift()
        df['prevprev_action']=df['action_name'].shift(2)
        df['prevprevprev_action']=df['action_name'].shift(3)
        mask=(df['action_name'].isin(tiros))&((df['prev_action'].isin(set_pieces))|(df['prevprev_action'].isin(set_pieces))|(df['prevprevprev_action'].isin(set_pieces)))
        mask1=(df['action_name'].isin(tiros))&((df['prev_action']=='Accurate key pass')|(df['prevprev_action']=='Accurate key pass')|(df['prevprevprev_action']=='Accurate key pass'))
        df['xG_from setpiece']=0
        df['Remates']=(df['action_name'].isin(tiros)).astype(int)
        df.loc[mask,'xG_from setpiece']=df.loc[mask,'xG']
        df['key_passes']=df['action_name'].apply(lambda x: 1 if x in tiros else 0)
        df['jugada_gol']=df['action_name'].apply(lambda x: 1 if x=='Chances created' else 0)

        df['xG_from_keypass']=0
        df.loc[mask,'xG_from_keypass']=df.loc[mask1,'xG']
        df_f=df.groupby(['jornada','match_id','team_name']).sum()[['jugada_gol','xG','xG_from setpiece','key_passes','xG_from_keypass','Goles','Remates']].reset_index()
        df_f['xG por remate']=df_f['xG']/df_f['Remates']
        df_f['xG por jugada gol']=(df_f['xG']/df_f['jugada_gol']).fillna(0)
        df_f['xG por jugada gol']=df_f['xG por jugada gol'].replace([-np.inf,np.inf],0)
        df_f['xG (Contrario)']=0
        df_f['xG_from setpiece (Contrario)']=0
        df_f['key_passes (Contrario)']=0
        df_f['Goles en contra']=0
        for idx,row in df_f.iterrows():
            equipo=row['team_name']
            match_id=row['match_id']
            df_f.loc[(df_f['match_id']==match_id)&(df_f['team_name']!=equipo),'xG (Contrario)']=row['xG']
            df_f.loc[(df_f['match_id']==match_id)&(df_f['team_name']!=equipo),'xG_from setpiece (Contrario)']=row['xG_from setpiece']
            df_f.loc[(df_f['match_id']==match_id)&(df_f['team_name']!=equipo),'key_passes (Contrario)']=row['key_passes']
            df_f.loc[(df_f['match_id']==match_id)&(df_f['team_name']!=equipo),'Goles en contra']=row['Goles']
            df_f.loc[(df_f['match_id']==match_id)&(df_f['team_name']!=equipo),'xG por remate (Contrario)']=row['xG por remate']
            df_f.loc[(df_f['match_id']==match_id)&(df_f['team_name']!=equipo),'xG por jugada gol (Contrario)']=row['xG por jugada gol']

        df_f['Net xG']=df_f['xG']-df_f['xG (Contrario)']
        df_f['Porteria a 0']=df_f['Goles en contra'].apply(lambda x: 1 if x==0 else 0)
        df_f['Net xG (Goles - xG)']=df_f['Goles']-df_f['xG']
        ranking=df_f.groupby('team_name').sum()[['xG','xG (Contrario)','Porteria a 0','Goles','Goles en contra','Net xG (Goles - xG)']]
        ranking['Top porteria 0']=ranking['Porteria a 0'].rank(method='max',ascending=False).astype(int)
        ranking['Top xG']=ranking['xG'].rank(method='max',ascending=False).astype(int)
        ranking['Top xG Concedido']=ranking['xG (Contrario)'].rank(method='min').astype(int)
        ranking['Top Goles anotados']=ranking['Goles'].rank(method='max').astype(int)
        ranking['Top Goles concedidos']=ranking['Goles en contra'].rank(method='min').astype(int)
        ranking['Top Net xG (Goles - xG)']=ranking['Net xG (Goles - xG)'].rank(method='max').astype(int)

        teams= extract_teams(ligas[liga],season_2022)
        equipo = st.selectbox("Seleccione el equipo", ['Seleccionar']+teams['name'].to_list())
        if equipo!='Seleccionar':
            df_equipo=partidos[(partidos['team1_name']==equipo)|(partidos['team2_name']==equipo)]
            team1=df_equipo.loc[df_equipo['round_id']==df_equipo['round_id'].max(),'team1_name'].values[0]
            team1_sc=df_equipo.loc[df_equipo['round_id']==df_equipo['round_id'].max(),'team1_score'].values[0]
            team2=df_equipo.loc[df_equipo['round_id']==df_equipo['round_id'].max(),'team2_name'].values[0]
            team2_sc=df_equipo.loc[df_equipo['round_id']==df_equipo['round_id'].max(),'team2_score'].values[0]

            st.write(f"**Ultimo Partido Jugado:** {team1} {team1_sc} - {team2_sc} {team2}")
            fig = plt.figure(figsize=(10, 18))
            gs = GridSpec(nrows=11, ncols=5)
            #width_ratios=[1, 1], height_ratios=[1, 1, 1]

            ax0 = fig.add_subplot(gs[0, 0:2])
            ax1 = fig.add_subplot(gs[0, 3:])
            ax2 = fig.add_subplot(gs[2, 0:2])
            ax3 = fig.add_subplot(gs[2, 3:])
            ax4 = fig.add_subplot(gs[4, 0:2])
            ax5 = fig.add_subplot(gs[4, 3:])
            ax6 = fig.add_subplot(gs[6, 0:2])
            ax7 = fig.add_subplot(gs[6, 3:])
            ax8 = fig.add_subplot(gs[8, 0:2])
            ax9 = fig.add_subplot(gs[8, 3:])
            ax10 = fig.add_subplot(gs[10, 0:2])
            
            axis_eq(df_f,equipo,'xG',ax0)
            axis_op(df_f,equipo,'xG (Contrario)',ax1)
            axis_eq(df_f,equipo,'xG_from setpiece',ax2)
            axis_op(df_f,equipo,'xG_from setpiece (Contrario)',ax3)
            axis_eq(df_f,equipo,'key_passes',ax4)
            axis_op(df_f,equipo,'key_passes (Contrario)',ax5)
            axis_eq(df_f,equipo,'xG por remate',ax8)
            axis_op(df_f,equipo,'xG por remate (Contrario)',ax9)
            axis_eq(df_f,equipo,'xG por jugada gol',ax6)
            axis_op(df_f,equipo,'xG por jugada gol (Contrario)',ax7)
            
            axis_eq(df_f,equipo,'Net xG',ax10)
            plt.suptitle(f'Variables de juego {equipo}')
            ax1.legend(bbox_to_anchor=(1.04,0.5), loc="center left")

            st.pyplot(fig)

            disp_df=ranking.loc[equipo,['Top Goles anotados','Top Goles concedidos','Top Net xG (Goles - xG)','Top porteria 0','Top xG','Top xG Concedido']]
            st.dataframe(disp_df.astype(int))