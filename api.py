import streamlit as st
from modelo import *
import requests
from bs4 import BeautifulSoup
from io import StringIO
from urllib.request import urlopen

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
ligas={
    'Colombia - Liga Bet Play':217,
    'Colombia - Torneo Bet Play':407,
    'Argentina - Torneo 2021':5334,
    'Argentina - Torneo 2022':5040,
    'Mexico - Liga MX':108,
    'Estados Unidos - MLS':41,
    'Internacional - Copa Libertadores':184
}
temporadas={
    '2021':27,
    '2022':29
}
season_2021=27
season_2022=29
info=['xG','xG conversion','xG per shot','Goals','Shots','Minutes played']

@st.cache(allow_output_mutation=True)
def show_match_events(match_id):
    url=f'http://service.instatfootball.com/feed.php?id=819845&key=T4bwoXqr&tpl=36&start_ms=0&match_id={match_id}&lang_id=1&lang=en&format=csv'
    try:
        response=requests.get(url,headers=headers)
        soup=BeautifulSoup(response.content,'lxml')
        s= soup.get_text()
        f = StringIO(s)
        df =pd.read_csv(f,sep=';')
        return df
    except requests.exceptions.RequestException as e:
        print(e)
        exit()
    
@st.cache
def extract_matches(tournament_id,season_id):
    url=f'http://service.instatfootball.com/feed.php?id=819845&key=T4bwoXqr&tpl=35&tournament_id={tournament_id}&season_id={season_id}&date_start=&date_end=&lang_id=1&lang=en&format=csv'
    try:
        response=requests.get(url,headers=headers)
        soup=BeautifulSoup(response.content,'lxml')
        s= soup.get_text()
        f = StringIO(s)
        df =pd.read_csv(f,sep=';')
        return df
    except requests.exceptions.RequestException as e:
        print(e)
        exit()

@st.cache
def extract_teams(tournament_id,temporada=29):
    url=f'http://service.instatfootball.com/feed.php?id=819845&key=T4bwoXqr&tpl=32&tournament_id={tournament_id}&season_id={temporada}&date_start=&date_end=&lang_id=1&lang=&format=csv'
    try:
        response=requests.get(url,headers=headers)
        soup=BeautifulSoup(response.content,'lxml')
        s= soup.get_text()
        f = StringIO(s)
        df =pd.read_csv(f,sep=';')
        return df
    except requests.exceptions.RequestException as e:
        print(e)
        exit()
@st.cache
def show_players(team_id):
    url=f'http://service.instatfootball.com/feed.php?id=819845&key=T4bwoXqr&tpl=5&team_id={team_id}&lang_id=1&lang=en&format=csv'
    try:
        response=requests.get(url,headers=headers)
        soup=BeautifulSoup(response.content,'lxml')
        s= soup.get_text()
        f = StringIO(s)
        df =pd.read_csv(f,sep=';')
        return df
    except requests.exceptions.RequestException as e:
        print(e)
        exit()
@st.cache
def players_match_match(player_id,tournament_id=217,season_id=27,fecha_inicio='2021-07-01'):
    url=f'http://service.instatfootball.com/feed.php?id=819845&key=T4bwoXqr&tpl=41&player_id={player_id}&tournament_id={tournament_id}&season_id={season_id}&date_start={fecha_inicio}&date_end=&lang_id=1&lang=en&format=xml'
    try:
        response=requests.get(url,headers=headers)
        soup=BeautifulSoup(response.content,'lxml')
        s= soup.get_text()
        f = StringIO(s)
        df =pd.read_csv(f,sep=';')
        return df
    except requests.exceptions.RequestException as e:
        print(e)
        exit()
@st.cache
def show_player_stats(player_id,tournament_id=217,season_id=27,fecha_inicio='2021-07-01'):
    url=f'http://service.instatfootball.com/feed.php?id=819845&key=T4bwoXqr&tpl=61&player_id={player_id}&tournament_id={tournament_id}&season_id={season_id}&date_start={fecha_inicio}&date_end=&lang_id=1&lang=en&format=csv'
    try:
        response=requests.get(url,headers=headers)
        soup=BeautifulSoup(response.content,'lxml')
        s= soup.get_text()
        f = StringIO(s)
        df =pd.read_csv(f,sep=';')
        return df
    except requests.exceptions.RequestException as e:
        print(e)
        exit()
@st.cache
def players_match_match(player_id,tournament_id=217,season_id=29):
    url=f'http://service.instatfootball.com/feed.php?id=819845&key=T4bwoXqr&tpl=41&player_id={player_id}&tournament_id={tournament_id}&season_id={season_id}&date_start=&date_end=&lang_id=1&lang=en&format=json'
    try:
        response = urlopen(url)
        data = json.loads(response.read())
    except:
        print(f'No se encontró {player_id}')
        return pd.DataFrame()
    output = pd.DataFrame()
    for i in data['data']['match']:
        dict_temp={'Partido': i['title'],'Id Jugador':i['team'][0]['player'][0]['id'],'Jugador':i['team'][0]['player'][0]['name']}
        for j in i['team'][0]['player'][0]['param']:
            dict_temp[j['name']]= j['value']
        output = output.append(dict_temp, ignore_index=True)
    output.fillna(0,inplace=True)
    return output

@st.cache(suppress_st_warning=True)
def consolidar_jugadores(jugadores,liga,temporada):
    jugadores_consolidado=pd.DataFrame()
    for idx in jugadores['id']:
        try:
            temp=players_match_match(idx,ligas[liga],temporada)
            jugadores_consolidado=pd.concat([jugadores_consolidado,temp])
        except:
            jugadores_consolidado=jugadores_consolidado
    jugadores_consolidado[['Goals','xG','xG per shot','Minutes played','Shots','xG conversion']]=jugadores_consolidado[['Goals','xG','xG per shot','Minutes played','Shots','xG conversion']].astype(float)
    df=jugadores_consolidado.groupby('Jugador').sum()[info].reset_index()
    ordered_df = df.sort_values(by='Goals')
    return ordered_df

@st.cache(suppress_st_warning=True)
def team_match_match(team_id,tournament_id=217,season_id=27):
    url=f'http://service.instatfootball.com/feed.php?id=819845&key=T4bwoXqr&tpl=43&team_id={team_id}&tournament_id={tournament_id}&season_id={season_id}&date_start=&date_end=&lang_id=1&lang=en&format=json'
    try:
        response = urlopen(url)
        data = json.loads(response.read())
    except:
        return pd.DataFrame()
    output = pd.DataFrame()
    for i in data['data']['match']:
        dict_temp={'Partido': i['title'],'Id Partido':i['id'],'Equipo':i['team'][0]['name'],'Jornada':int(data['data']['match'].index(i)+1)}
        for j in i['team'][0]['param']:
            dict_temp[j['name']]= j['value']
        output = output.append(dict_temp, ignore_index=True)
    output.fillna(0,inplace=True)
    return output


@st.cache(suppress_st_warning=True)
def partidos_liga(equipos,tournament_id=217,season_id=27):
    part=pd.DataFrame()
    for idx in equipos['id'].unique():
        print(idx)
        tmm=team_match_match(idx,tournament_id,season_id)
        part=pd.concat([part,tmm])
    part['Opponent xG']=np.nan
    part.reset_index(drop=True,inplace=True)
    for idx,row in part.iterrows():
        id_partido=row['Id Partido']
        equipo=row['Equipo']
        part.loc[idx,'Opponent xG']=part.loc[(part['Id Partido']==id_partido)&(part['Equipo']!=equipo),'xG'].values[0]
        part[['xG','Opponent xG']]=part[['xG','Opponent xG']].astype(float)
        part['Porteria 0']=part['Goals conceded'].apply(lambda x: 1 if x==0 else 0)
    return part

def plotear_xG(part,equipo):
    fig2=plt.figure(figsize=(10,2))
    per25=np.percentile(part.groupby('Equipo').mean()['xG'],25)
    per50=np.percentile(part.groupby('Equipo').mean()['xG'],50)
    per75=np.percentile(part.groupby('Equipo').mean()['xG'],75)

    plt.axvspan(per25, per50, color='orange', alpha=0.5)
    plt.axvspan(per50, per75, color='yellow', alpha=0.5)
    plt.axvspan(per75, 3.2, color='green', alpha=0.5)

    for idx,row in part.groupby('Equipo').mean().iterrows():
        eq=idx
        xg=row['xG']
        if eq==equipo:
            plt.scatter(row['xG'],1,color='white',s=200,zorder=11,label="Promedio Temporada")
        else:
            plt.scatter(row['xG'],1,color='grey',zorder=10)
    plt.title("xG")
    plt.tick_params(left = False, right = False , labelleft = False ,labelbottom = True, bottom = True)
    plt.axvline(x=part.loc[(part['Jornada']==part.loc[part['Equipo']==equipo,'Jornada'].max())&(part['Equipo']==equipo),'xG'].values[0],linestyle='--',color='white',zorder=10,label="Ultimo partido")
    plt.axvspan(0, per25, color='red', alpha=0.5)

    if part.loc[(part['Jornada']==part.loc[part['Equipo']==equipo,'Jornada'].max())&(part['Equipo']==equipo),'xG'].values[0] < part.groupby('Equipo').mean()['xG'].min():
        xop_min2= part.loc[(part['Jornada']==part.loc[part['Equipo']==equipo,'Jornada'].max())&(part['Equipo']==equipo),'xG'].values[0] - 0.05
    else:
        xop_min2=part.groupby('Equipo').mean()['xG'].min() - 0.05
    if part.loc[(part['Jornada']==part.loc[part['Equipo']==equipo,'Jornada'].max())&(part['Equipo']==equipo),'xG'].values[0] < part.groupby('Equipo').mean()['xG'].max():
        xop_max2=part.groupby('Equipo').mean()['xG'].max() + 0.05
    else:
        xop_max2= part.loc[(part['Jornada']==part.loc[part['Equipo']==equipo,'Jornada'].max())&(part['Equipo']==equipo),'xG'].values[0] + 0.05
    plt.legend()
    plt.xlim((xop_min2,xop_max2))
    plt.legend(bbox_to_anchor=(1.04,0.5), loc="center left")
    st.pyplot(fig2)

def plotear_OpxG(part,equipo):
    fig=plt.figure(figsize=(10,2))
    per25=np.percentile(part.groupby('Equipo').mean()['Opponent xG'],25)
    per50=np.percentile(part.groupby('Equipo').mean()['Opponent xG'],50)
    per75=np.percentile(part.groupby('Equipo').mean()['Opponent xG'],75)

    plt.axvspan(per25, per50, color='yellow', alpha=0.5)
    plt.axvspan(per50, per75, color='orange', alpha=0.5)
    plt.axvspan(per75, 3.2, color='red', alpha=0.5)

    for idx,row in part.groupby('Equipo').mean().iterrows():
        eq=idx
        xg=row['Opponent xG']
        if eq==equipo:
            plt.scatter(xg,1,color='white',s=200,zorder=11,label='Promedio Temporada')
        else:
            plt.scatter(xg,1,color='grey',zorder=10)
    plt.title("Opponent xG")
    plt.tick_params(left = False, right = False , labelleft = False ,labelbottom = True, bottom = True)
    plt.axvline(x=part.loc[(part['Jornada']==part.loc[part['Equipo']==equipo,'Jornada'].max())&(part['Equipo']==equipo),'Opponent xG'].values[0],linestyle='--',color='white',zorder=10,label='Ultimo partido')
    plt.axvspan(0, per25, color='green', alpha=0.5)
    if part.loc[(part['Jornada']==part.loc[part['Equipo']==equipo,'Jornada'].max())&(part['Equipo']==equipo),'Opponent xG'].values[0] < part.groupby('Equipo').mean()['Opponent xG'].min():
        xop_min= part.loc[(part['Jornada']==part.loc[part['Equipo']==equipo,'Jornada'].max())&(part['Equipo']==equipo),'Opponent xG'].values[0] - 0.05
    else:
        xop_min=part.groupby('Equipo').mean()['Opponent xG'].min() - 0.05
    if part.loc[(part['Jornada']==part.loc[part['Equipo']==equipo,'Jornada'].max())&(part['Equipo']==equipo),'Opponent xG'].values[0] < part.groupby('Equipo').mean()['Opponent xG'].max():
        xop_max= part.groupby('Equipo').mean()['Opponent xG'].max() + 0.05
    else:
        xop_max=part.loc[(part['Jornada']==part.loc[part['Equipo']==equipo,'Jornada'].max())&(part['Equipo']==equipo),'Opponent xG'].values[0] + 0.05
    plt.xlim((xop_min,xop_max))
    plt.gca().invert_xaxis()
    plt.legend(bbox_to_anchor=(1.04,0.5), loc="center left")
    st.pyplot(fig)
