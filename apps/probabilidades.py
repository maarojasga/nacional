import streamlit as st
from modelo import *
from api import *
import statsmodels.api as sm
from scipy.stats import poisson
import matplotlib.ticker as mtick

poisson_model_int = sm.load('Data/poisson_model_fpc.pickle')
equipos_dim={
    'Independiente Medellin':'DIM',
    'America de Cali':'AME',
    'CD Popular Junior FC SA':'JUN',
    'Alianza Petrolera':'ALI',
    'Deportivo Pasto':'PAS',
    'Millonarios':'MIL',
    'Deportes Tolima':'TOL',
    'Patriotas Boyaca':'PAT',
    'Envigado':'ENV',
    'Once Caldas':'OC',
    'Cortulua':'COR',
    'Atletico Nacional':'NAL',
    'Jaguares de Cordoba':'JAG',
    'Union Magdalena':'MAG',
    'La Equidad':'EQU',
    'Independiente Santa Fe':'ISF',
    'Deportivo Cali':'CAL',
    'Atletico Bucaramanga':'BUC',
    'Aguilas Doradas':'AGU',
    'Deportivo Pereira':'PER'
}

def simulate_match(foot_model,xG_local,xG_perm_local, xG_visitante,xG_perm_visitante,casa=True, max_goals=5):
    if casa==True:
        home_goals_avg = foot_model.predict(pd.DataFrame(data={'cumxG_propio': xG_local,  'cumxG_contrario_equipo2':xG_perm_visitante,'Home':1},index=[1])).values[0]
    else:
        home_goals_avg = foot_model.predict(pd.DataFrame(data={'cumxG_propio': xG_local,  'cumxG_contrario_equipo2':xG_perm_visitante,'Home':0},index=[1])).values[0]     
    away_goals_avg = foot_model.predict(pd.DataFrame(data={'cumxG_propio': xG_visitante, 'cumxG_contrario_equipo2':xG_perm_local,'Home':0},index=[1])).values[0]
    
    team_pred = [[poisson.pmf(i, team_avg) for i in range(0, max_goals+1)] for team_avg in [home_goals_avg, away_goals_avg]]
    return(np.outer(np.array(team_pred[0]), np.array(team_pred[1])))

def probabilidades(xG_local,xG_perm_local, xG_visitante,xG_perm_visitante,casa=True, max_goals=5,foot_model=poisson_model_int):
    partido=simulate_match(foot_model,xG_local,xG_perm_local, xG_visitante,xG_perm_visitante,casa, max_goals)
    series=pd.Series([1-np.sum(np.triu(partido, 1))-np.sum(np.diag(partido)),np.sum(np.diag(partido)),np.sum(np.triu(partido, 1))],index=['Local','Empate','Visitante'])
    return series
def ganador(local,result):
    color=""
    if local==1:
        if result>0:
            color="green"
        elif result==0:
            color="orange"
        elif result < 0:
            color="red"
    elif local==0:
        if result>0:
            color="red"
        elif result==0:
            color="orange"
        elif result < 0:
            color="green"
    return color

def calculando_probabilidades(part_22,df,equipo):
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
    df.loc[df['action_name'].isin(tiros),'xG'] = df.loc[df['action_name'].isin(tiros),'Suma'].apply(lambda x:1/(1+np.exp(x)))
    df_xg=df.groupby(['match_date','match_id','team_name']).sum()['xG'].reset_index()
    df_xg['Op xG']=0
    for idx,row in df_xg.iterrows():
        team_name=row['team_name']
        match_id=row['match_id']
        df_xg.loc[(df_xg['match_id']==match_id)&(df_xg['team_name']!=team_name),'Op xG']=row['xG']

    df_xg=df_xg.sort_values('match_date')
    df_xg['cumxG_propio'] = df_xg.groupby(['team_name'])['xG'].apply(lambda x: x.shift().rolling(3).mean())
    df_xg['cumxG_contrario'] = df_xg.groupby(['team_name'])['Op xG'].apply(lambda x: x.shift().rolling(3).mean())
    df_xg.sort_values('match_date').groupby('team_name').tail(1)[['team_name','cumxG_propio','cumxG_contrario']].to_csv('xG.csv')
    df_retornar=df_xg.sort_values('match_date').groupby('team_name').tail(1)[['team_name','cumxG_propio','cumxG_contrario']]
    for idx, row in part_22.iterrows():
        id=row['id']
        team1=row['team1_name']
        team2=row['team2_name']
        try:
            part_22.loc[(part_22['id']==id),'team1_xG']=df_xg.loc[(df_xg['match_id']==id)&(df_xg['team_name']==team1),'cumxG_propio'].values[0]
        except:
            pass 
        try:
            part_22.loc[(part_22['id']==id),'team2_xG']=df_xg.loc[(df_xg['match_id']==id)&(df_xg['team_name']==team2),'cumxG_propio'].values[0]
        except:
            pass
        try:
            part_22.loc[(part_22['id']==id),'team1_xG_op']=df_xg.loc[(df_xg['match_id']==id)&(df_xg['team_name']==team1),'cumxG_contrario'].values[0]
        except:
            pass
        try:
            part_22.loc[(part_22['id']==id),'team2_xG_op']=df_xg.loc[(df_xg['match_id']==id)&(df_xg['team_name']==team2),'cumxG_contrario'].values[0]
        except:
            pass
    
    part_22['team1_name_abr']=part_22['team1_name'].replace(equipos_dim)
    part_22['team2_name_abr']=part_22['team2_name'].replace(equipos_dim)
    part_22[['team1_xG','team1_xG_op','team2_xG','team2_xG_op']]=part_22[['team1_xG','team1_xG_op','team2_xG','team2_xG_op']].fillna(part_22[['team1_xG','team1_xG_op','team2_xG','team2_xG_op']].quantile(.05))
    part_22[['Prob L','Prob E','Prob V']]=np.round(part_22.apply(lambda x: probabilidades(x['team1_xG'],x['team1_xG_op'],x['team2_xG'],x['team2_xG_op']),axis=1),2)
    df_probabilidades=part_22[['id','match_date','team1_name','team1_name_abr','team2_name_abr','team1_score','team2_score','team2_name','Prob L','Prob E','Prob V']]
    df_eq=df_probabilidades[(df_probabilidades['team1_name']==equipo)|(df_probabilidades['team2_name']==equipo)]
    df_eq['Probabilidad Ganar']=df_eq.apply(lambda x: x['Prob L'] if x['team1_name']==equipo else x['Prob V'],axis=1)
    df_eq['Partido']=df_eq['team1_name_abr']+' '+df_eq['team1_score'].map(str)+' \n '+df_eq['team2_name_abr']+' '+df_eq['team2_score'].map(str)
    df_eq['Local']=(df_eq['team1_name']==equipo).astype(int)
    df_eq['ganador']=df_eq['team1_score']-df_eq['team2_score']
    df_eq['color']=df_eq[['Local','ganador']].apply(lambda x : ganador(x[0],x[1]),axis=1)
    df_eq=df_eq.sort_values('match_date')
    
    fig,ax=plt.subplots()
    df_eq['match_date']=pd.to_datetime(df_eq['match_date']).dt.date.astype(str)
    df_eq=df_eq.set_index('match_date')
    plt.plot(df_eq.index,df_eq['Probabilidad Ganar'])
    plt.scatter(df_eq.index,df_eq['Probabilidad Ganar'],s=2500,zorder=30,color=df_eq['color'])
    
    plt.axhline(y = 0.5, color = 'green', linestyle = '--')
    plt.text(-1,0.51,"Should win",color='green')
    plt.text(-1,0.23,"Should lose",color='red')
    plt.axhline(y = 0.22, color = 'red', linestyle = '--')
    
    for idx,row in df_eq.iterrows():
        plt.text(idx,row['Probabilidad Ganar']+0.08,row['Partido'])
        plt.text(idx,row['Probabilidad Ganar']-0.005,str(int(row['Probabilidad Ganar']*100))+'%',zorder=1000,ha='center')
    
    plt.xticks(rotation=45,ha='right')
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    plt.ylim(0,1)
    plt.xlim(-1,len(df_eq.index)+0.005)
    plt.title("Probabilidad vs Resultado")
    plt.xlabel("Partido")
    plt.ylabel("Probabilidad de Ganar")
    
    
    st.write("""
        ## Gráfica
    """)
    st.pyplot(fig)
    st.write("""
        ## Tabla con datos
    """)
    df_eq['Probabilidad Ganar']=(np.round(df_eq['Probabilidad Ganar']*100,2)).astype(str)+'%'
    st.dataframe(df_eq[['Partido','Probabilidad Ganar']].rename(columns={'Prob L':'Probabilidad de ganar'}).astype(str))
    return df_retornar

           
def app():
    st.write("""
             # Probabilidades vs Resultados
             > Comparación de la probabilidad de ganar de un equipo contra el resultado obtenido
             """)

    liga = 'Colombia - Liga Bet Play'
    if liga!='Seleccionar':

        part_21=extract_matches(217,27)
        part_22=extract_matches(217,29)
        part_22.to_csv('calendario.csv')
        partidos_restantes=part_22.loc[(pd.to_datetime(part_22['match_date'])<pd.to_datetime('2022-5-16'))&(part_22['available_events']==False),['match_date','round_name','team1_name','team2_name']]
        part_21=part_21[part_21['available_events']==True]
        part_22=part_22[part_22['available_events']==True]
        parts=part_21.append(part_22,ignore_index=True)
        list_21=part_21.loc[part_21.round_name.isin(['Week 39','Week 38','Week 37']),'id'].tolist()
        list_22=part_22['id'].unique().tolist()
        lista_ids=list_21+list_22
        teams= extract_teams(ligas[liga],29)
        equipo = st.selectbox("Seleccione el equipo", ['Seleccionar']+teams['name'].to_list())
        if equipo!='Seleccionar':
            df=pd.DataFrame()
            for idx in lista_ids:
                try:
                    temp=pd.read_csv(f'DataApi/{idx}.csv')
                except:
                    temp=show_match_events(idx)
                    temp.to_csv(f'DataApi/{idx}.csv')
                temp['match_date']=parts.loc[parts['id']==idx,'match_date'].values[0]
                temp['match_id']=idx
                df=df.append(temp,ignore_index=True)
            
            xgs=calculando_probabilidades(part_22,df,equipo)
            st.write("""
                ## Partidos restantes
            """)
            probas_futuras=partidos_restantes.merge(xgs.rename(columns={'cumxG_propio':'team1_xG','cumxG_contrario':'team1_xG_op'}),how='left',left_on='team1_name',right_on='team_name')
            probas_futuras=probas_futuras.drop(columns=['team_name'])
            probas_futuras=probas_futuras.merge(xgs.rename(columns={'cumxG_propio':'team2_xG','cumxG_contrario':'team2_xG_op'}),how='left',left_on='team2_name',right_on='team_name')
            probas_futuras=probas_futuras.drop(columns=['team_name'])
            probas_futuras[['Prob L','Prob E','Prob V']]=np.round(probas_futuras.apply(lambda x: probabilidades(x['team1_xG'],x['team1_xG_op'],x['team2_xG'],x['team2_xG_op']),axis=1),2)
            probas_futuras[['match_date','team1_name','team2_name','Prob L','Prob E','Prob V']].to_excel('probabilidades_futuras.xlsx')
            probas_futuras['Prob L']=(np.round(probas_futuras['Prob L']*100,2)).astype(str)+'%'
            probas_futuras['Prob E']=(np.round(probas_futuras['Prob E']*100,2)).astype(str)+'%'
            probas_futuras['Prob V']=(np.round(probas_futuras['Prob V']*100,2)).astype(str)+'%'

            dic_columnas={'match_date':'Fecha Partido','team1_name':'Local','team2_name':'Visitante','Prob L':'Probabilidad Local','Prob E':'Probabilidad Empate','Prob V':'Probabilidad Visitante','round_name':'Fecha'}
            probas_futuras=probas_futuras.loc[((probas_futuras['team1_name']==equipo)|(probas_futuras['team2_name']==equipo)),['match_date','round_name','team1_name','team2_name','Prob L','Prob E','Prob V']].rename(columns=dic_columnas)
            st.write(probas_futuras.sort_values('Fecha Partido').astype(str))
