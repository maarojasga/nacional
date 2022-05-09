import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import numpy as np
from mplsoccer.pitch import Pitch
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import copy
from scipy.spatial import distance
import io
import base64
import pickle
import json
import re
import uuid
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import math
import seaborn as sns

mpl.rcParams['figure.figsize'] = 12, 8

##### Font Properties
mpl.rcParams['font.size'] = 16

##### Text
mpl.rcParams['text.color'] = 'ffffff'

##### Grid
mpl.rcParams['grid.color'] = 'a0a9ba'

##### figure
mpl.rcParams['figure.facecolor'] = '000000'
mpl.rcParams['figure.edgecolor'] = '000000'

##### Axes properties
mpl.rcParams['axes.linewidth'] = 2
mpl.rcParams['axes.labelpad'] = 10
mpl.rcParams['axes.labelcolor'] = 'e9e9e9'
mpl.rcParams['axes.edgecolor'] = 'e9e9e9'
mpl.rcParams['axes.facecolor'] = '000000'
mpl.rcParams['axes.prop_cycle'] = "cycler(color=['5074b9', '78cfe2', 'fbd37b', 'f7902b', 'ed2054'])"

##### Tick properties
# x-axis
mpl.rcParams['xtick.top'] = False
mpl.rcParams['xtick.direction'] = 'in'
mpl.rcParams['xtick.major.size'] = 7
mpl.rcParams['xtick.major.width'] = 2
mpl.rcParams['xtick.minor.size'] = 5
mpl.rcParams['xtick.minor.width'] = 2
mpl.rcParams['xtick.color'] = 'e9e9e9'

# y-axis
mpl.rcParams['ytick.right'] = False
mpl.rcParams['ytick.direction'] = 'in'
mpl.rcParams['ytick.major.size'] = 7
mpl.rcParams['ytick.major.width'] = 2
mpl.rcParams['ytick.minor.size'] = 5
mpl.rcParams['ytick.minor.width'] = 2
mpl.rcParams['ytick.color'] = 'e9e9e9'

##### Lines properties
mpl.rcParams['lines.linewidth'] = 2

##### Legend properties
mpl.rcParams['legend.framealpha'] = 1
mpl.rcParams['legend.frameon'] = False

dict_pos_players = {'interior': {'Kevin De Bruyne', 'Bruno Fernandes', 'James Maddison'},
                    'extremo': {'Sadio Mane', 'Neymar', 'R. Sterling', 'Kylian Mbappe Lottin'},
                    'lateral_derecho': {'Sergino Dest', 'Dani Carvajal', 'Trent Alexander-Arnold', 'Aaron Wan-Bissaka'},
                    'lateral_izquierdo': {'Jordi Alba', 'Andrew Robertson', 'Alphonso Davies'},
                    'mediocentro': {'Casemiro', 'Thiago Alcantara', 'Joshua Kimmich'},
                    'central': {'Virgil van Dijk', 'D. Upamecano', 'D. Alaba'},
                    'delantero': {'Karim Benzema', 'Erling Braut Haaland', 'Romelu Lukaku'},
                    'volante_creativo': {'Lionel Messi', 'Kai Havertz', 'Heung-Min Son'},
                    'volante_mixto': {'Paul Pogba', 'Toni Kroos'},
                    'arquero': {'Ederson Moraes', 'M. ter Stegen', 'Jan Oblak'}}

dict_tactics = {'1-4-2-2-2':{'line 0':['arquero'], 'line 1':['lateral_izquierdo', 'central', 'central', 'lateral_derecho'], 'line 2':['mediocentro', 'mediocentro'], 'line 3':['volante_mixto', 'volante_mixto'], 'line 4':['delantero', 'delantero']},
                '1-4-4-2':{'line 0':['arquero'], 'line 1':['lateral_izquierdo', 'central', 'central', 'lateral_derecho'], 'line 2':['extremo', 'mediocentro', 'interior', 'extremo'], 'line 3':['delantero', 'delantero']},
                '1-4-3-3':{'line 0':['arquero'], 'line 1':['lateral_izquierdo', 'central', 'central', 'lateral_derecho'], 'line 2':['interior', 'mediocentro', 'volante_mixto'], 'line 3':['extremo', 'delantero', 'extremo']},
                '1-4-2-3-1':{'line 0':['arquero'], 'line 1':['lateral_izquierdo', 'central', 'central', 'lateral_derecho'], 'line 2':['mediocentro', 'mediocentro'], 'line 3':['extremo', 'volante_creativo', 'extremo'], 'line 4':['delantero']},
                '1-5-3-2':{'line 0':['arquero'], 'line 1':['lateral_izquierdo', 'central', 'central', 'central','lateral_derecho'], 'line 2':['volante_mixto', 'mediocentro', 'interior'], 'line 3':['delantero', 'delantero']},
                '1-3-4-3':{'line 0':['arquero'], 'line 1':['central', 'central', 'central'], 'line 2':['interior', 'mediocentro', 'mediocentro', 'volante_mixto'], 'line 3':['extremo', 'delantero', 'extremo']}}

dict_fill_pos = {'interior': (148, 22, 81, 255),
                 'extremo': (255, 252, 0, 255),
                 'lateral_derecho': (4, 50, 255, 255),
                 'lateral_izquierdo': (115, 254, 255, 255),
                 'mediocentro': (170, 170, 170, 255),
                 'central': (255, 38, 0, 255),
                 'delantero': (255, 133, 255, 255),
                 'volante_creativo': (0, 250, 0, 255),
                 'volante_mixto': (255, 147, 0, 255),
                 'arquero': (148, 82, 0, 255)}
        
posiciones = {'Interior': 'interior',
 'Extremo': 'extremo',
 'Lateral': 'lateral',
 'Volante Creativo': 'volante_creativo',
 'Volante Mixto': 'volante_mixto',
 'Mediocentro': 'mediocentro',
 'Central': 'central',
 'Delantero': 'delantero',
 'Arquero': 'arquero',
 'Lateral Derecho': 'lateral_derecho',
 'Lateral Izquierdo': 'lateral_izquierdo'}

dict_pos_eq_instat = {'interior': {'CM', 'DM'},
                      'extremo': {'RM', 'LM'},
                      'lateral_izquierdo': {'LD'},
                      'lateral_derecho': {'RD'},
                      'mediocentro': {'DM'},
                      'central': {'CD'},
                      'delantero': {'F'},
                      'volante_creativo': {'CM'},
                      'volante_mixto': {'CM', 'DM'}}

dict_metrics = {'Braycurtis':distance.braycurtis,
                'Canberra':distance.canberra,
                'Chebyshev':distance.chebyshev,
                'Cityblock':distance.cityblock,
                'Correlation':distance.correlation,
                'Cosine':distance.cosine,
                'Euclidean':distance.euclidean,
                'Sqeuclidean':distance.sqeuclidean,
                'Minkowski':distance.minkowski}

dict_metrics_pos = {'interior': 'Euclidean',
                    'extremo': 'Euclidean',
                    'lateral_derecho': 'Braycurtis',
                    'lateral_izquierdo': 'Braycurtis',
                    'mediocentro': 'Braycurtis',
                    'central': 'Euclidean',
                    'delantero': 'Euclidean',
                    'volante_creativo': 'Euclidean',
                    'volante_mixto': 'Euclidean',
                    'arquero': 'Euclidean'}

descriptive_vars_lst = ['Matches played', 'Minutes played', 'Starting lineup appearances', 'Substitute out', 'Substitutes in',
                        'Number', 'InStat Index', 'Age', 'Height', 'Weight','Season'
                        'National team (last match date, mm.yy)', 'Youth national team (last match date, mm.yy)']

gk_vars_to_minimize_set = {"Opponents' xG conversion"}

vars_to_minimize_set = {'Fouls per 90 min', 'Offsides per 90 min',
                        'Yellow cards per 90 min', 'Red cards per 90 min',
                        'Shots wide per 90 min', 'Blocked shots per 90 min', 'Shots on post / bar per 90 min',
                        'Lost balls per 90 min', 'Lost balls in own half per 90 min',
                        "Opponent's xG with a player on"}

#################### Diccionarios ####################
dict_pos = {'interior': 'Interior',
            'extremo': 'Extremo',
            'lateral_derecho': 'Lateral Derecho',
            'lateral_izquierdo': 'Lateral Izquierdo',
            'mediocentro': 'Mediocentro',
            'central': 'Central',
            'delantero': 'Delantero',
            'volante_creativo': 'Volante Creativo',
            'volante_mixto': 'Volante Mixto',
            'arquero': 'Arquero'}
dict_translate_players = {
# Goles
'xG (Expected goals)':'xG (Goles esperados)',
'Goals per 90 min':'Goles por 90 min',
'xG with a player on':'xG con marca',
'Shots on target per 90 min':'Remates a puerta por 90 min',
'Shots on target, %':'Remates a puerta, %',
'Shots wide per 90 min':'Remates desviados por 90 min',
'xG per shot':'xG por remate',

# Oportunidades
'Chances successful per 90 min':'Oportunidades exitosas por 90 min',
'Chances, % of conversion':'Oportunidades, % de conversión',
'Chances created per 90 min':'Oportunidades creadas por 90 min',

# Juego aéreo
'Air challenges won, %':'Duelos aéreos ganados, %',
'Air challenges won per 90 min':'Duelos aéreos ganados por 90 min',

# Regates
'Dribbles successful per 90 min':'Regates exitosos por 90 min',
'Successful dribbles, %':'Regates exitosos, %',

# Pases
'Successful actions per 90 min':'Acciones exitosas por 90 min',
'Successful actions, %':'Acciones exitosas, %',
'Accurate passes per 90 min':'Pases acertados por 90 min',
'Accurate passes, %':'Pases acertados, %',
'Crosses accurate per 90 min':'Centros acertados por 90 min',
'Accurate crosses, %':'Centros acertados, %',
'Lost balls in own half per 90 min':'Balones perdidos en\ncampo propio por 90 min',

# Duelos defensivos
'Defensive challenges won per 90 min':'Duelos defensivos ganados por 90 min',
'Challenges in defence won, %':'Duelos defensivos ganados, %',

# Duelos ofensivos
'Attacking challenges won per 90 min':'Duelos ofensivos ganados por 90 min',
'Challenges in attack won, %':'Duelos ofensivos ganados, %',

# Recuperaciones
'Ball recoveries per 90 min':'Balones recuperados por 90 min',
"Ball recoveries in opponent's half per 90 min":'Balones recuperados en campo\ncontrario por 90 min',
'Tackles successful per 90 min':'Entradas ganadas por 90 min',
'Tackles won, %':'Entradas ganadas, %',
'Blocked shots per 90 min':'Remates bloqueados por 90 min',

# Pases clave
'Key passes accurate per 90 min':'Pases clave acertados por 90 min',
'Expected assists':'Asistencias esperadas',
'Assists per 90 min':'Asistencias por 90 min',

# Otros
'Fouls per 90 min':'Faltas por 90 min',
'Fouls suffered per 90 min':'Faltas recibidas por 90 min',
'Offsides per 90 min':'Fueras de juego por 90 min',
'Yellow cards per 90 min':'Tarjetas amarillas por 90 min',
'Red cards per 90 min':'Tarjetas rojas por 90 min',
'Penalty per 90 min':'Penaltis cobrados por 90 min',
'Penalties scored per 90 min':'Penaltis anotados por 90 min',
'Penalty kicks scored, %':'Penaltis anotados, %',
'Ball interceptions per 90 min':'Intercepciones por 90 min',
'Free ball pick ups per 90 min':'Recogidas de balón\nlibre por 90 min',
'xG per goal':'xG por gol',
'xG conversion':'Conversión de xG',
"Opponent's xG with a player on":'xG del oponente con marca',
"Net xG (xG player on - opp. team's xG)":'xG neto (xG con marca -\nxG del equipo contrincante)',
'Defensive xG (xG of shots made by guarded player)':'xG defensivo (xG de los remates\nhechos por el jugador marcado)',
'Defensive xG per shot':'xG defensivo por remate',
'Shots on post / bar per 90 min':'Remates al palo por 90 min',
'Challenges per 90 min':'Duelos por 90 min',
'Challenges won per 90 min':'Duelos aéreos por 90 min',
'Challenges won, %':'Duelos ganados, %',
'Lost balls per 90 min':'Balones perdidos por 90 min',
'Dribbles per 90 min':'Regates por 90 min',
'Total actions per 90 min':'Total de acciones por 90 minutos',
'Passes per 90 min':'Pases por 90 min',
'Crosses per 90 min':'Cruces por 90 min',
'Defensive challenges per 90 min':'Duelos defensivos por 90 min',
'Attacking challenges per 90 min':'Duelos ofensivos por 90 min',
'Air challenges per 90 min':'Duelos aéreos por 90 min',
'Chances per 90 min':'Oportunidades por 90 min',
'Shots per 90 min':'Remates por 90 min',
'Tackles per 90 min':'Entradas por 90 min',
'Key passes per 90 min':'Pases clave por 90 min'
}

dict_translate_gk = {
"xG conceded - Goals conceded":'Diferencia xG rival vs goles encajados',
"Opponent's shots":'Remates del oponente',
"Opponents' shots  on target":'Remates a puerta del oponente',
'Goals conceded':'Goles encajados',
'Shots saved':'Remates parados',
'Shots saved, %':'Remates parados, %',
'Supersaves':'Súper paradas',
'Passes':'Pases',
'Accurate passes':'Pases acertados',
'Accurate passes, %':'Pases acertados, %',
'Key passes':'Pases clave',
'Key passes accurate':'Pases clave acertados',
'Fouls':'Faltas',
'Matches played':'Partidos jugados',
'Minutes played':'Minutos jugados',
'Clean sheets':'Valla invicta',
'Penalties saved':'Penaltis atajados',
'Goals conceded - Penalties':'Goles encajados - Penaltis',
'Penalties saved, %':'Penaltis atajados, %',
"Goalkeeper's interception":'Intercepciones',
'Good interception of goalkeeper':'Intercepciones acertadas',
'Goalkeeper interceptions, %':'Intercepciones, %',
'Foot passes from open play':'Pases con el pie\ndesde pelota en movimiento',
'Accurate foot passes from open play':'Pases acertados con el pie\ndesde pelota en movimiento',
'Accurate foot passes from open play, %':'Pases acertados con el pie\ndesde pelota en movimiento, %',
'Hand passes':'Pases con la mano',
'Hand passes, accurate':'Pases acertados con la mano',
'Hand passes, accurate, %':'Pases acertados con la mano, %',
'Passes from set pieces':'Pases desde jugada a pelota detenida',
'Accurate passes from set pieces':'Pases acertados desde\njugada a pelota detenida',
'Set piece passes, accurate, %':'Pases acertados desde\njugada a pelota detenida, %',
'Short passes':'Pases cortos',
'Short passes accurate':'Pases cortos acertados',
'Short passes, accurate, %':'Pases cortos acertados, %',
'Medium passes':'Pases de media distancia',
'Medium passes - accurate':'Pases de media distancia acertados',
'Mid range passes, accurate, %':'Pases de media distancia acertados, %',
'Long passes':'Pases largos',
'Accurate long passes':'Pases largos acertados',
'Accurate long passes, %':'Pases largos acertados, %',
'Close range shots':'Remates de corta distancia',
'Close range shots on target':'Remates a puerta\nde corta distancia',
'Close range shots saved':'Remates de corta\ndistancia parados',
'Сlose range shots saved, %':'Remates de corta\ndistancia parados, %',
'Mid range shots':'Remates de media distancia',
'Mid range shots on target':'Remates a puerta\nde media distancia',
'Mid range shots saved':'Remates de media\ndistancia parados',
'Mid range shots saved, %':'Remates de media\ndistancia parados, %',
'Long range shots':'Remates de larga distancia',
'Long range shots on target':'Remates a puerta\nde larga distancia',
'Long range shots saved':'Remates de larga\ndistancia parados',
'% of long range shots saved':'Remates de larga\ndistancia detenidos, %',
'Jumping saves':'Paradas con salto',
'Saves without jumping':'Paradas sin salto',
'Stopped shots':'Remates detenidos',
'Stopped shots, %':'Remates detenidos, %',
'Shots saved with successful bouncing':'Remates detenidos con\nrebote efectivo',
'Shots saved with successful bouncing, %':'Remates detenidos con\nrebote efectivo, %',
'Shots saved with unsuccessful bouncing':'Remates detenidos con\nrebote no efectivo',
'Shots saved with unsuccessful bouncing, %':'Remates detenidos con\nrebote no efectivo, %',
'xG conceded':'xG concedido',
'xG per shot taken':'xG por remate',
'xG per goal conceded':'xG por gol concedido',
'xG per shot saved':'xG por remate rechazado',
"Opponents' xG conversion":'Conversión de xG del oponente'
}

per90_var_lst = ['Goals', 'Assists', 'Chances', 'Chances successful', 'Chances created',
                 'Fouls', 'Fouls suffered', 'Offsides', 'Yellow cards', 'Red cards',
                 'Total actions', 'Successful actions',
                 'Shots', 'Shots on target', 'Shots wide', 'Blocked shots', 'Shots on post / bar',
                 'Penalty', 'Penalties scored',
                 'Passes', 'Accurate passes', 'Key passes', 'Key passes accurate',
                 'Crosses', 'Crosses accurate',
                 'Lost balls', 'Lost balls in own half',
                 'Ball recoveries', "Ball recoveries in opponent's half",
                 'Challenges', 'Challenges won', 'Defensive challenges', 'Defensive challenges won', 'Attacking challenges', 'Attacking challenges won', 'Air challenges', 'Air challenges won',
                 'Dribbles', 'Dribbles successful',
                 'Tackles', 'Tackles successful',
                 'Ball interceptions', 'Free ball pick ups','Expected points']

dict_var_rad_esp ={'arquero': {'Diferencia xG rival vs goles encajados', 'Intercepciones, %', 'Pases acertados, %', 'Pases acertados con el pie\ndesde pelota en movimiento, %', 'Pases acertados con el pie\ndesde pelota en movimiento', 'Intercepciones acertadas', 'Pases cortos acertados, %', 'Pases de media distancia acertados, %', 'Pases largos acertados, %', 'Remates de corta\ndistancia parados, %', 'Remates de media\ndistancia parados, %', 'Remates de larga\ndistancia detenidos, %'},
                   'lateral_izquierdo': {'Duelos defensivos ganados, %', 'Entradas ganadas, %', 'Regates exitosos, %', 'Duelos ofensivos ganados, %', 'Asistencias esperadas', 'Pases acertados, %', 'Centros acertados, %', 'Duelos aéreos ganados, %', 'Duelos defensivos ganados por 90 min', 'Balones recuperados por 90 min', 'Regates exitosos por 90 min', 'Duelos ofensivos ganados por 90 min'},
                   'lateral_derecho': {'Duelos defensivos ganados, %', 'Entradas ganadas, %', 'Regates exitosos, %', 'Duelos ofensivos ganados, %', 'Asistencias esperadas', 'Pases acertados, %', 'Centros acertados, %', 'Duelos aéreos ganados, %', 'Duelos defensivos ganados por 90 min', 'Balones recuperados por 90 min', 'Regates exitosos por 90 min', 'Duelos ofensivos ganados por 90 min'},
                   'volante_mixto': {'Duelos defensivos ganados, %', 'Duelos ofensivos ganados, %', 'Asistencias esperadas', 'Regates exitosos, %', 'Entradas ganadas, %', 'Pases acertados, %', 'Centros acertados, %', 'Acciones exitosas, %', 'Pases clave acertados por 90 min', 'xG (Goles esperados)', 'Balones recuperados por 90 min', 'Intercepciones por 90 min'},
                   'volante_creativo': {'Asistencias esperadas', 'Duelos ofensivos ganados, %', 'Regates exitosos, %', 'xG (Goles esperados)', 'Pases acertados, %', 'Centros acertados, %', 'Entradas ganadas, %', 'Asistencias por 90 min', 'Balones recuperados en campo\ncontrario por 90 min', 'Intercepciones por 90 min', 'Duelos ofensivos ganados por 90 min', 'Regates exitosos por 90 min'},
                   'delantero': {'xG (Goles esperados)', 'xG por remate', 'Goles por 90 min', 'Duelos ofensivos ganados, %', 'Duelos aéreos ganados, %', 'Regates exitosos, %', 'Asistencias esperadas', 'Duelos ofensivos ganados por 90 min', 'Pases acertados, %', 'Centros acertados, %', 'Acciones exitosas, %', 'Regates exitosos por 90 min'},
                   'central': {'Duelos defensivos ganados, %', 'Entradas ganadas, %', 'Duelos aéreos ganados, %', 'xG (Goles esperados)', 'Pases acertados, %', 'Acciones exitosas, %', 'Duelos defensivos ganados por 90 min', 'Balones recuperados por 90 min', 'Intercepciones por 90 min', 'Acciones exitosas por 90 min', 'Balones perdidos en\ncampo propio por 90 min', 'Pases acertados por 90 min'},
                   'mediocentro': {'Duelos defensivos ganados, %', 'Entradas ganadas, %', 'Duelos ofensivos ganados, %', 'Balones recuperados por 90 min', 'Intercepciones por 90 min', 'Pases acertados, %', 'Acciones exitosas, %', 'Pases clave acertados por 90 min', 'xG (Goles esperados)', 'Asistencias esperadas', 'Regates exitosos, %', 'Duelos aéreos ganados, %'},
                   'interior': {'Regates exitosos, %', 'Asistencias esperadas', 'xG (Goles esperados)', 'Duelos defensivos ganados, %', 'Duelos ofensivos ganados, %', 'Pases acertados, %', 'Centros acertados, %', 'Acciones exitosas, %', 'Entradas ganadas, %', 'Pases clave acertados por 90 min', 'Duelos aéreos ganados, %', 'Intercepciones por 90 min'},
                   'extremo': {'Duelos ofensivos ganados, %', 'Regates exitosos, %', 'Asistencias esperadas', 'Centros acertados, %', 'xG (Goles esperados)', 'Entradas ganadas, %', 'Faltas recibidas por 90 min', 'Balones recuperados en campo\ncontrario por 90 min', 'Intercepciones por 90 min', 'Duelos ofensivos ganados por 90 min', 'Asistencias por 90 min', 'Oportunidades creadas por 90 min'}}

esp_eng = {**{val:key for key, val in dict_translate_players.items()}, **{val:key for key, val in dict_translate_gk.items()}}
dict_var_rad = dict()
for key, value in dict_var_rad_esp.items():
    dict_var_rad[key] = {esp_eng[var] for var in dict_var_rad_esp[key]}
    if (key != 'arquero') and ('xG per shot taken' in dict_var_rad[key]):
        s = set(dict_var_rad[key])
        s.remove('xG per shot taken')
        s.add('xG per shot')
        dict_var_rad[key] = s
@st.cache
def base_jugadores():

    df = pd.read_csv('Data/base_jugadores.csv',header=0,delimiter=',',decimal='.',na_values='-',encoding="utf-8",low_memory=False)
    if 'Unnamed: 0' in df.columns:
        df.drop(columns=['Unnamed: 0'],inplace=True)
    #df.drop(columns=['Nationality'], inplace=True)
    df = df.loc[~df.Name.str.contains('H. Palacios',na=True)]
    df['Nationality']=df['Nationality'].fillna('---')
    df.set_index(['Name','Nationality','Team'],inplace=True)
    #df.set_index(['Name','Team'],inplace=True)
    df = df.replace([np.inf, -np.inf], np.nan) 
    df = df.fillna(0)
    df['Season'] = df['Season'].astype(int).astype(str)
    min_played = df['Minutes played'].astype(float)

    df['Age']=df['Age'].astype(float).astype(int)
    df=df[df['Age']>0]

    for col in df.columns:
        if col.find('%') !=-1:
            if isinstance(df[col], str):
                df[col]=float(df[col].str.rstrip('%').astype('float').fillna(0)/100.0)
        if col in per90_var_lst:
            try:
                df[col] = (df[col]/min_played)*90
            except:
                print('Division por 0')
            df.rename(columns={col: str(col)+' per 90 min'}, inplace=True)

    return df

@st.cache
def base_arqueros():

    posicion='Arquero'
    w = weights(posiciones[posicion])
    df = pd.read_csv('Data/base_arqueros.csv',header=0,delimiter=',',decimal='.',na_values='-',encoding="utf-8")
    df.drop(columns=['Unnamed: 0'],inplace=True)
    df = df.loc[~df.Name.str.contains('H. Palacios',na=True)]
    df['Nationality']=df['Nationality'].fillna('---')
    df.set_index(['Name','Nationality','Team'],inplace=True)
    df = df.replace([np.inf, -np.inf], np.nan) 
    df = df.fillna(0)
    df['Season'] = df['Season'].astype(int).astype(str)
    
    for col in df.columns:
        if col.find('%') != -1:
            if isinstance(df[col], str):
                df[col]=float(df[col].str.rstrip('%').astype('float').fillna(0)/100.0)
    
    df['Age']=df['Age'].astype(float).astype(int)
    df=df[df['Age']>0]
    df["xG conceded - Goals conceded"]=df['xG conceded'].astype(float)-df['Goals conceded'].astype(float)
    w.rename(index={np.NaN:"xG conceded - Goals conceded"},inplace=True)
    df[w.index.tolist()]=df[w.index.tolist()].apply(pd.to_numeric,errors='coerce')
   
    return df


def weights(pos, print_checks=False):
    
    dict_pos = {'interior': 'Interior', 'extremo': 'Extremo', 'lateral': 'Lateral',
    'volante_creativo': 'Volante Creativo', 'volante_mixto': 'Volante Mixto', 'mediocentro': 'Mediocentro', 'central': 'Central',
     'delantero': 'Delantero', 'arquero':'Arquero', 'lateral_derecho':'Lateral Derecho',
     'lateral_izquierdo':'Lateral Izquierdo', 'extremo':'Extremo'}

    dict_pos = {val:key for key, val in dict_pos.items()}
    players_esp_eng = {val:key for key, val in dict_translate_players.items()}
    gk_esp_eng = {val:key for key, val in dict_translate_gk.items()}
    esp_eng = {**players_esp_eng, **gk_esp_eng}

    df = pd.read_csv('pesos.csv',sep=';')
    if 'Unnamed: 0' in df.columns:
        df.drop(columns=['Unnamed: 0'],inplace=True)

    df['Posicion python'] = df['Posicion'].map(dict_pos)
    df['Translated variables'] = df['Variable'].map(esp_eng)
    df['Peso% Final (PG*PV)'] = df['Peso% Grupo (PG)']*df['Peso% Variable (PV)']

    if pos in dict_pos.values():

        if 'lateral_' in pos:
            for lat in ['lateral_izquierdo', 'lateral_derecho']:
                mini_df = df[df['Posicion python'] == 'lateral']
                mini_df['Posicion python'] = lat
                df = df.append(mini_df)

        dict_out = {var:weight for var, weight in zip(df.loc[df['Posicion python'] == pos, 'Translated variables'], df.loc[df['Posicion python'] == pos,'Peso% Final (PG*PV)'])}
        
        if pos != 'arquero':
            dict_out['xG per shot'] = dict_out.pop('xG per shot taken')
        return pd.Series(dict_out)

def percentile(df, bool_gk = False): 
    for col in df.columns.values:
        if (df[col].dtype != 'object') and ((col not in descriptive_vars_lst) == True) and (col!='Season'):
            if bool_gk:
                vars_set=gk_vars_to_minimize_set
            else:
                vars_set=vars_to_minimize_set
            if col not in vars_set:
                df[col] = df[col].rank(pct=True)
            else:
                df[col] = df[col].rank(pct=True, ascending=False)

def Xp_ranking(df,best_df=pd.Series(), weight=pd.Series(),d_metric=dict_metrics['Euclidean']):
    df_copy = copy.deepcopy(df[list(weight.keys())])
    df_copy.fillna(0, inplace=True)
    
    if len(best_df) != 0:
        best = best_df[list(weight.keys())]
        best.fillna(0,inplace=True)
        best = best.squeeze()
        
    else:
        best = pd.Series(dtype='float64')
        for col in df_copy.columns.values:
            df_copy[col] = df_copy[col].astype(float)
            best[col] = df_copy[col].max()
    Xp_score=[]
    for _, row in df_copy.iterrows():
        if best.shape[0]==2:
            best=best.iloc[0,:]

        df_xpr = pd.concat({'Weight':weight, 'Best':best, 'Row':row}, axis = 1)
        if len(best_df) != 0:
            df_xpr['Row']=df_xpr['Row'].astype(float)
            df_xpr['Best']=df_xpr['Best'].astype(float)
            Xp_score.append(d_metric(np.array(df_xpr['Row'].values.tolist()), np.array(df_xpr['Best'].values.tolist())))
        else:
            Xp_score.append(d_metric(np.array(df_xpr['Row'].values.tolist()), np.array(df_xpr['Best'].values.tolist()), np.array(df_xpr['Weight'].values.tolist())))
    
    df_out = pd.DataFrame(data={'Xp Score': Xp_score}, index=df_copy.index)
    df_out['Xp Ranking'] = df_out['Xp Score'].rank(method='max').astype(int)
    df_out['Percentil'] = df_out['Xp Score'].rank(pct=True, ascending=False)*100
    max_score = df_out['Xp Score'].max()
    df_out['Xp Score'] = (1-(df_out['Xp Score']/max_score))*100
    df_out = pd.concat([df, df_out], axis=1)
    return df_out

def team_color(s, column):
        is_team = pd.Series(data=False, index=s.index)
        is_team[column] = s[column].str.contains('Atl. Nacional', na=False)
        return ['background-color: green' if is_team.any() else '' for v in is_team]


def download_button(object_to_download, download_filename, button_text, pickle_it=False):
    if pickle_it:
        try:
            object_to_download = pickle.dumps(object_to_download)
        except pickle.PicklingError as e:
            st.write(e)
            return None

    else:
        if isinstance(object_to_download, bytes):
            pass

        elif isinstance(object_to_download, pd.DataFrame):
            #object_to_download = object_to_download.to_csv(index=False)
            towrite = io.BytesIO()
            object_to_download = object_to_download.to_excel(towrite, encoding='utf-8', index=True, header=True)
            towrite.seek(0)

        else:
            object_to_download = json.dumps(object_to_download)

    try:
        b64 = base64.b64encode(object_to_download.encode()).decode()

    except AttributeError as e:
        b64 = base64.b64encode(towrite.read()).decode()

    button_uuid = str(uuid.uuid4()).replace('-', '')
    button_id = re.sub('\d+', '', button_uuid)

    custom_css = f"""
        <style>
            #{button_id} {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                background-color: rgb(2, 143, 66);
                color: rgb(0, 0, 0);
                padding: .25rem .75rem;
                position: relative;
                text-decoration: none;
                border-radius: 4px;
                border-width: 1px;
                border-style: solid;
                border-color: rgb(0, 0, 0);
                border-image: initial;
            }}
            #{button_id}:hover {{
                border-color: rgb(255, 255, 255);
                color: rgb(255, 255, 255);
            }}
            #{button_id}:active {{
                box-shadow: none;
                background-color: rgb(0, 0, 0);
                color: white;
                }}
        </style> """

    dl_link = custom_css + f'<a download="{download_filename}" id="{button_id}" href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}">{button_text}</a><br></br>'

    st.markdown(dl_link, unsafe_allow_html=True)


def table_streamlit(df, position):
    list_vars_table = ['Age','Xp Ranking','Xp Score','Percentil','Minutes played']
    if 'arquero' not in position:
        list_vars_table = list_vars_table + ['Position']
    if len(df['League'].unique())>=2:
        list_vars_table = list_vars_table + ['League']
    df_table = df[list_vars_table].sort_values('Xp Ranking')
    df_table.reset_index(inplace=True)
    df_table.rename(columns={'Name':'Nombre','Nationality':'Nacionalidad','Team':'Equipo','Age':'Edad','Minutes played':'Minutos jugados','Position':'Posición InStat', 'League':'Liga/Torneo'}, inplace=True)
    st.write("""
        # Xp Ranking
        ## {}
        ###
        """.format(dict_pos[position]))
    try:
        df_table.set_index(['Nombre'], inplace=True)
        st.dataframe(df_table.style.apply(team_color, column=['Equipo'], axis=1))
        download_button(df_table, f'ranking_{position}.xlsx', f'Descargar tabla', pickle_it=False)
    except:
        df_table.reset_index(inplace=True)
        try:
            df_table.set_index(['Xp Ranking'], inplace=True)
            st.dataframe(df_table.style.apply(team_color, column=['Equipo'], axis=1))
            download_button(df_table, f'ranking_{position}.xlsx', f'Descargar tabla', pickle_it=False)
        except:
            df_table.reset_index(inplace=True)
            df_table.set_index(['Nombre'], inplace=True)
            st.dataframe(df_table)
            download_button(df_table, f'ranking_{position}.xlsx', f'Descargar tabla', pickle_it=False)

def radar_streamlit(df_radar, df_raw, position, w, N_variables):
    try:
        df_raw = df_raw[(df_raw['Season'].isin(list(df_radar['Season'].unique()))) &\
             (df_raw['League'].isin(list(df_radar['League'].unique()))) &\
                  (df_raw.index.get_level_values('Name').isin(df_radar.index.get_level_values('Name').unique().tolist()))]
        df_radar.set_index('League', append=True, inplace=True)
        df_raw.set_index('League', append=True, inplace=True)
        df_radar.set_index('Season', append=True, inplace=True)
        df_raw.set_index('Season', append=True, inplace=True)
    except:
        pass
    fig_radar = plt.figure()
    ax = fig_radar.add_subplot(111, polar=True)
    v=w[list(dict_var_rad[position])].sort_values(ascending = False).index.tolist()
    variables = v[:N_variables]
    all_variables = w.sort_values(ascending = False).index.tolist()
    try:
        df_radar_all = df_radar.loc[:,all_variables+['Xp Ranking', 'Xp Score']]
        df_radar = df_radar.loc[:, variables+['Xp Ranking']]
    except:
        df_radar_all = df_radar.loc[:,all_variables]
        df_radar = df_radar.loc[:,variables]
    ax.fill_between(np.linspace(0, 2*np.pi, 100), 0.495, 0.505, color='#ed2054', zorder=10)
    pct50_legend = plt.legend(handles=[Line2D([0], [0], marker='o', color='#000000', label='Percentil 50',\
     markeredgewidth=1.5, markeredgecolor='#ed2054', markersize=14)], bbox_to_anchor=(1.35, 0.05),\
      loc='lower right', fontsize=12)
    plt.gca().add_artist(pct50_legend)
    N = len(variables)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    if 'arquero' not in position:
        variables_spn = [dict_translate_players[v] for v in variables]
    else:
        variables_spn = [dict_translate_gk[v] for v in variables]
    plt.xticks(angles[:-1], variables_spn, size=10)
    labels = [item.get_text() for item in ax.get_yticklabels()]
    ax.set_yticklabels(['']*len(labels))
    color_nacional = ['#00bc2f', '#b7e000', '#d6820d', '#c1c1c1', '#4a6b48', '#d6820d']
    cl = 0
    for index, row in df_radar.iterrows():
        values=row[variables].tolist()
        values += values[:1]
        if len(df_radar.index.get_level_values('Name').tolist()) != len(set(df_radar.index.get_level_values('Name').tolist())):
            try:
                name_label = '#{} - {} ({})\n{} ({})'.format(int(row['Xp Ranking']), index[0], index[2], index[-2], index[-1])
            except:
                name_label = '{} ({})\n{} ({})'.format(index[0], index[2], index[-2], index[-1])
        else:
            try:
                name_label = '#{} - {} ({})'.format(int(row['Xp Ranking']), index[0], index[2])
            except:
                try:
                    name_label = '{} ({})'.format(index[0], index[2])
                except:
                    name_label = '{} ({})'.format(index[0], index[1])
        if 'Atl. Nacional' in name_label:
            ax.plot(angles, values, linewidth=1, linestyle='solid', label=name_label, color=color_nacional[cl])
            ax.fill(angles, values, alpha=0.6, color=color_nacional[cl])
            cl = cl+1
        else:
            ax.plot(angles, values, linewidth=1, linestyle='solid', label=name_label)
            ax.fill(angles, values, alpha=0.6)
    plt.legend(bbox_to_anchor=(1.08, 1), loc='upper left', fontsize=12)
    st.write("""
        # Radar Xp Ranking
        ## {}
        ###
        """.format(dict_pos[position]))
    st.pyplot(fig_radar)

    df_raw = df_raw.loc[df_radar.index,variables]
    if 'arquero' not in position:
        df_od = pd.read_excel('variables_ad.xlsx', engine='openpyxl')
        attack_variables = df_od[(df_od['A/D o B'] == 'A') | (df_od['A/D o B'] == 'B')]['Variable'].to_list()
        defense_variables = df_od[(df_od['A/D o B'] == 'D') | (df_od['A/D o B'] == 'B')]['Variable'].to_list()
        pct_ad_weighted = True
        if pct_ad_weighted:
            for i, row in df_radar_all.iterrows():
                str_p = " ponderado (segun el peso por posición de las variables)"
                df_radar_all.loc[i,'PCT promedio ofensivo'] = (w[attack_variables].astype(float).multiply(row[attack_variables].astype(float)).sum()/w[attack_variables].sum())*100
                df_radar_all.loc[i,'PCT promedio defensivo'] = (w[defense_variables].astype(float).multiply(row[defense_variables].astype(float)).sum()/w[defense_variables].sum())*100
        else:
            for i, row in df_radar_all.iterrows():
                str_p = " "
                df_radar_all.loc[i,'PCT promedio ofensivo'] = (row[attack_variables].sum()/len(row[attack_variables]))*100
                df_radar_all.loc[i,'PCT promedio defensivo'] = (row[defense_variables].sum()/len(row[attack_variables]))*100
        df_raw.rename(columns={v: dict_translate_players[v] for v in variables}, inplace=True)
        df_radar.rename(columns={v: dict_translate_players[v] for v in variables}, inplace=True)
        df_radar_all.rename(columns={v: dict_translate_players[v] for v in all_variables}, inplace=True)
    else:
        df_raw.rename(columns={v: dict_translate_gk[v] for v in variables}, inplace=True)
        df_radar.rename(columns={v: dict_translate_gk[v] for v in variables}, inplace=True)
        df_radar_all.rename(columns={v: dict_translate_gk[v] for v in all_variables}, inplace=True)
    if len(df_radar) == 1:
        st.write("""
                ***
                """)
        cmap_colors = mpl.cm.get_cmap('winter')
        list_pct_value = values[:-1]#[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.88345, 0.9, 0.910, 0.911, 0.912]
        list_pct_name = variables_spn#['Vancune nsdiufb enfuwef\ngfghghg', 'BUI NIUBBBB', 'bdcuwevf bwefwe fbwey\nvnde ndeiwu', 'nxuisn ewnweic', 'wcnenuciwn wecnecnce ecnwecn', 'suiwdh ediuh', 'asuid duie', 'wdehi wdiu', 'xnxwh denu nd ndd', "JAbde BSAA", 'ncid cni', 'ncwe']

        fig_pctl, ax = plt.subplots(math.ceil(N_variables/2), 2, figsize=(18,9))
        for n, pct_value in enumerate(list_pct_value[:N_variables]):
            row = math.floor((n)/2)
            if (n+1)%2 == 0:
                col = 1
            else:
                col = 0

            c_code = cmap_colors(0.4+0.6*float(pct_value))

            h_line = ax[row,col].hlines(0, 0, 1, color='#545454', linewidth=8, zorder=1)

            circle_0 = plt.Circle((0, 0), radius=.04, color='#545454', zorder=1)
            circle_50 = plt.Circle((0.5, 0), radius=.04, color='#545454', zorder=1)
            circle_100 = plt.Circle((1, 0), radius=.04, color='#545454', zorder=1)

            ax[row,col].add_patch(circle_0)
            ax[row,col].add_patch(circle_50)
            ax[row,col].add_patch(circle_100)

            circle = plt.Circle((float(pct_value), 0), radius=.1, color=c_code, linewidth=2, zorder=100, alpha=0.7)
            ax[row,col].add_patch(circle)
            number = ax[row,col].annotate(round(float(pct_value)*100,1), xy=(float(pct_value), 0), color='black', fontsize=20, weight='bold', ha="center", va="center", zorder=1000)
            label = ax[row,col].annotate(list_pct_name[n], xy=(0, 0.11), color='white', fontsize=20, ha="left", va="center", zorder=10000)

            ax[row,col].axis('off')
            ax[row,col].set_aspect('equal')
            ax[row,col].autoscale_view()

        if N_variables%2 != 0:
            ax[row,1].axis('off')
            ax[row,1].set_aspect('equal')
            ax[row,1].autoscale_view()

        plt.subplots_adjust(top=0.964,bottom=0.015,left=0.008,right=0.992,hspace=0.6,wspace=0.0)
        st.pyplot(fig_pctl)
    else:
        st.write("""
            ### Tabla de percentiles
            > Percentiles de acuerdo a la base de **todas** las ligas objetivo de Atl. Nacional.
            """)
        st.dataframe(df_radar)
        download_button(df_radar, f'percentiles.xlsx', f'Descargar tabla', pickle_it=False)
        
    if 'arquero' not in position:
        try:
            df_radar_all = df_radar_all[['Xp Score', 'PCT promedio defensivo', 'PCT promedio ofensivo']]
        except:
            df_radar_all = df_radar_all[['PCT promedio defensivo', 'PCT promedio ofensivo']]
        st.write("""
            ### Tabla de percentiles ofensivo y defensivo
            > Promedio{} de los percentiles de las variables defensivas y ofensivas.
            """.format(str_p))
        st.dataframe(df_radar_all)
        download_button(df_radar_all, f'percentiles_of_def.xlsx', f'Descargar tabla', pickle_it=False)
    st.write("""
        ### Tabla de valores
        > Totales acumulados por 90 minutos.
        """)
    st.dataframe(df_raw)
    download_button(df_raw, f'valores.xlsx', f'Descargar tabla', pickle_it=False)

def radar_streamlit_escoger(df_radar, df_raw, position, w):
    try:
        df_raw = df_raw[(df_raw['Season'].isin(list(df_radar['Season'].unique()))) &\
             (df_raw['League'].isin(list(df_radar['League'].unique()))) &\
                  (df_raw.index.get_level_values('Name').isin(df_radar.index.get_level_values('Name').unique().tolist()))]
        df_radar.set_index('League', append=True, inplace=True)
        df_raw.set_index('League', append=True, inplace=True)
        df_radar.set_index('Season', append=True, inplace=True)
        df_raw.set_index('Season', append=True, inplace=True)
    except:
        pass
    fig_radar = plt.figure()
    ax = fig_radar.add_subplot(111, polar=True)
    v = w[list(dict_var_rad[position])].sort_values(ascending = False).index.tolist()
    variables = st.multiselect('Seleccione las variables que quiere observar',options=v)

    all_variables = w.sort_values(ascending = False).index.tolist()
    try:
        df_radar_all = df_radar.loc[:,all_variables+['Xp Ranking', 'Xp Score']]
        df_radar = df_radar.loc[:, variables+['Xp Ranking']]
    except:
        df_radar_all = df_radar.loc[:,all_variables]
        df_radar = df_radar.loc[:,variables]
    ax.fill_between(np.linspace(0, 2*np.pi, 100), 0.495, 0.505, color='#ed2054', zorder=10)
    pct50_legend = plt.legend(handles=[Line2D([0], [0], marker='o', color='#000000', label='Percentil 50',\
     markeredgewidth=1.5, markeredgecolor='#ed2054', markersize=14)], bbox_to_anchor=(1.35, 0.05),\
      loc='lower right', fontsize=12)
    plt.gca().add_artist(pct50_legend)
    N = len(variables)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    if 'arquero' not in position:
        variables_spn = [dict_translate_players[v] for v in variables]
    else:
        variables_spn = [dict_translate_gk[v] for v in variables]
    plt.xticks(angles[:-1], variables_spn, size=10)
    labels = [item.get_text() for item in ax.get_yticklabels()]
    ax.set_yticklabels(['']*len(labels))
    color_nacional = ['#00bc2f', '#b7e000', '#d6820d', '#c1c1c1', '#4a6b48', '#d6820d']
    cl = 0
    for index, row in df_radar.iterrows():
        values=row[variables].tolist()
        values += values[:1]
        if len(df_radar.index.get_level_values('Name').tolist()) != len(set(df_radar.index.get_level_values('Name').tolist())):
            try:
                name_label = '#{} - {} ({})\n{} ({})'.format(int(row['Xp Ranking']), index[0], index[2], index[-2], index[-1])
            except:
                name_label = '{} ({})\n{} ({})'.format(index[0], index[2], index[-2], index[-1])
        else:
            try:
                name_label = '#{} - {} ({})'.format(int(row['Xp Ranking']), index[0], index[2])
            except:
                try:
                    name_label = '{} ({})'.format(index[0], index[2])
                except:
                    name_label = '{} ({})'.format(index[0], index[1])
        if 'Atl. Nacional' in name_label:
            ax.plot(angles, values, linewidth=1, linestyle='solid', label=name_label, color=color_nacional[cl])
            ax.fill(angles, values, alpha=0.6, color=color_nacional[cl])
            cl = cl+1
        else:
            ax.plot(angles, values, linewidth=1, linestyle='solid', label=name_label)
            ax.fill(angles, values, alpha=0.6)
    plt.legend(bbox_to_anchor=(1.08, 1), loc='upper left', fontsize=12)
    st.write("""
        # Radar Xp Ranking
        ## {}
        ###
        """.format(dict_pos[position]))
    st.pyplot(fig_radar)

    df_raw = df_raw.loc[df_radar.index,variables]
    if 'arquero' not in position:
        df_od = pd.read_excel('variables_ad.xlsx', engine='openpyxl')
        attack_variables = df_od[(df_od['A/D o B'] == 'A') | (df_od['A/D o B'] == 'B')]['Variable'].to_list()
        defense_variables = df_od[(df_od['A/D o B'] == 'D') | (df_od['A/D o B'] == 'B')]['Variable'].to_list()
        pct_ad_weighted = True
        if pct_ad_weighted:
            for i, row in df_radar_all.iterrows():
                str_p = " ponderado (segun el peso por posición de las variables)"
                df_radar_all.loc[i,'PCT promedio ofensivo'] = (w[attack_variables].astype(float).multiply(row[attack_variables].astype(float)).sum()/w[attack_variables].sum())*100
                df_radar_all.loc[i,'PCT promedio defensivo'] = (w[defense_variables].astype(float).multiply(row[defense_variables].astype(float)).sum()/w[defense_variables].sum())*100
        else:
            for i, row in df_radar_all.iterrows():
                str_p = " "
                df_radar_all.loc[i,'PCT promedio ofensivo'] = (row[attack_variables].sum()/len(row[attack_variables]))*100
                df_radar_all.loc[i,'PCT promedio defensivo'] = (row[defense_variables].sum()/len(row[attack_variables]))*100
        df_raw.rename(columns={v: dict_translate_players[v] for v in variables}, inplace=True)
        df_radar.rename(columns={v: dict_translate_players[v] for v in variables}, inplace=True)
        df_radar_all.rename(columns={v: dict_translate_players[v] for v in all_variables}, inplace=True)
    else:
        df_raw.rename(columns={v: dict_translate_gk[v] for v in variables}, inplace=True)
        df_radar.rename(columns={v: dict_translate_gk[v] for v in variables}, inplace=True)
        df_radar_all.rename(columns={v: dict_translate_gk[v] for v in all_variables}, inplace=True)
    if len(df_radar) == 1:
        st.write("""
                ***
                """)
        cmap_colors = mpl.cm.get_cmap('winter')
        list_pct_value = values[:-1]#[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.88345, 0.9, 0.910, 0.911, 0.912]
        list_pct_name = variables_spn#['Vancune nsdiufb enfuwef\ngfghghg', 'BUI NIUBBBB', 'bdcuwevf bwefwe fbwey\nvnde ndeiwu', 'nxuisn ewnweic', 'wcnenuciwn wecnecnce ecnwecn', 'suiwdh ediuh', 'asuid duie', 'wdehi wdiu', 'xnxwh denu nd ndd', "JAbde BSAA", 'ncid cni', 'ncwe']

        fig_pctl, ax = plt.subplots(math.ceil(len(variables)/2), 2, figsize=(18,9))
        for n, pct_value in enumerate(list_pct_value[:N_variables]):
            row = math.floor((n)/2)
            if (n+1)%2 == 0:
                col = 1
            else:
                col = 0

            c_code = cmap_colors(0.4+0.6*float(pct_value))

            h_line = ax[row,col].hlines(0, 0, 1, color='#545454', linewidth=8, zorder=1)

            circle_0 = plt.Circle((0, 0), radius=.04, color='#545454', zorder=1)
            circle_50 = plt.Circle((0.5, 0), radius=.04, color='#545454', zorder=1)
            circle_100 = plt.Circle((1, 0), radius=.04, color='#545454', zorder=1)

            ax[row,col].add_patch(circle_0)
            ax[row,col].add_patch(circle_50)
            ax[row,col].add_patch(circle_100)

            circle = plt.Circle((float(pct_value), 0), radius=.1, color=c_code, linewidth=2, zorder=100, alpha=0.7)
            ax[row,col].add_patch(circle)
            number = ax[row,col].annotate(round(float(pct_value)*100,1), xy=(pct_value, 0), color='black', fontsize=20, weight='bold', ha="center", va="center", zorder=1000)
            label = ax[row,col].annotate(list_pct_name[n], xy=(0, 0.11), color='white', fontsize=20, ha="left", va="center", zorder=10000)

            ax[row,col].axis('off')
            ax[row,col].set_aspect('equal')
            ax[row,col].autoscale_view()

        if N_variables%2 != 0:
            ax[row,1].axis('off')
            ax[row,1].set_aspect('equal')
            ax[row,1].autoscale_view()

        plt.subplots_adjust(top=0.964,bottom=0.015,left=0.008,right=0.992,hspace=0.6,wspace=0.0)
        st.pyplot(fig_pctl)
    else:
        st.write("""
            ### Tabla de percentiles
            > Percentiles de acuerdo a la base de **todas** las ligas objetivo de Atl. Nacional.
            """)
        st.dataframe(df_radar)
        download_button(df_radar, f'percentiles.xlsx', f'Descargar tabla', pickle_it=False)
        
    if 'arquero' not in position:
        try:
            df_radar_all = df_radar_all[['Xp Score', 'PCT promedio defensivo', 'PCT promedio ofensivo']]
        except:
            df_radar_all = df_radar_all[['PCT promedio defensivo', 'PCT promedio ofensivo']]
        st.write("""
            ### Tabla de percentiles ofensivo y defensivo
            > Promedio{} de los percentiles de las variables defensivas y ofensivas.
            """.format(str_p))
        st.dataframe(df_radar_all)
        download_button(df_radar_all, f'percentiles_of_def.xlsx', f'Descargar tabla', pickle_it=False)
    st.write("""
        ### Tabla de valores
        > Totales acumulados por 90 minutos.
        """)
    st.dataframe(df_raw)
    download_button(df_raw, f'valores.xlsx', f'Descargar tabla', pickle_it=False)

def imscatter(x, y, image, ax=None, zoom=0.1):
            if ax is None:
                ax = plt.gca()
            im = OffsetImage(image, zoom=zoom)
            x, y = np.atleast_1d(x, y)
            artists = []
            for x0, y0 in zip(x, y):
                ab = AnnotationBbox(im, (x0, y0), xycoords='data', frameon=False)
                artists.append(ax.add_artist(ab))
            ax.update_datalim(np.column_stack([x, y]))
            ax.autoscale()
            return artists

def pitch_streamlit(tactic, df, df_gk):
    total_lines = len(tactic.split('-'))
    df['x'] = 0.0
    df['y'] = 0.0
    df_gk['x'] = 0.0
    df_gk['y'] = 0.0
    new_dict = dict()
    for i, item in enumerate(tactic.split('-')):
        level = int(int(item)/2) + int(int(item)%2)
        last = 1
        if total_lines-1 == i:
            last = -1
        y_top = 10 + (110*i)/total_lines + last*((5*(level-1))/2)
        lst_og = [(y_top - last*5*n) for n in range(0,int(int(item)/2))]
        lst_mirror = copy.deepcopy(lst_og)
        lst_mirror.reverse()
        if int(int(item)%2) != 0:
            if int(item) == 1:
                list_y = [y_top - last*5*(level-1)]
            else:
                list_y = lst_og + [y_top - last*5*(level-1)] + lst_mirror
        else:
            list_y = lst_og + lst_mirror
        x_left = 80/(int(item)+1)
        list_x = [x_left*n for n in range(1,int(item)+1)]

        for i, pos in enumerate(dict_tactics[tactic][f'line {i}']):
            if pos not in new_dict.keys():
                new_dict[pos] = [(list_x[i], list_y[i])]
            else:
                new_dict[pos] = new_dict[pos] + [(list_x[i], list_y[i])]

    for pos in new_dict.keys():
        if 'arquero' not in pos:
            df.loc[df['Tactic position'] == pos, 'x'] = [x for x, y in new_dict[pos]]
            df.loc[df['Tactic position'] == pos, 'y'] = [y for x, y in new_dict[pos]]
        else:
            df_gk.loc[df_gk['Tactic position'] == pos, 'x'] = [x for x, y in new_dict[pos]]
            df_gk.loc[df_gk['Tactic position'] == pos, 'y'] = [y for x, y in new_dict[pos]]


    formation = {(pos, name, number):(x, y) for pos, name, number, x, y in zip(df['Tactic position'], df.index.get_level_values('Name'), df['Number'], df['x'], df['y'])}
    formation[(df_gk['Tactic position'].values[0], df_gk.index.get_level_values('Name')[0], df_gk['Number'].values[0])] = (df_gk['x'].values[0], df_gk['y'].values[0])

    x = [coord[1] for coord in formation.values()]
    y = [coord[0] for coord in formation.values()]

    pitch = Pitch(figsize=(8, 12), pitch_color='#aabb97', line_color='white',
                  stripe_color='#c2d59d', stripe=True, orientation='vertical',
                  tight_layout=True)
    fig, ax = pitch.draw()
    pitch.scatter(x, y, ax=ax, s=200, color='red')
    for pos in formation.keys():
        if (len(pos[1]) >= 15) & (pos[1].count(" ")>1):
            groups = pos[1].split(" ")
            name_display = f"{' '.join(groups[:2])}\n{' '.join(groups[2:])}"
        else:
            name_display = pos[1]
        pitch.annotate(name_display, xy=(formation[pos][1]-5, formation[pos][0]),
        ax=ax, fontsize=10, va='top', ha='center', weight='bold', zorder=1000, c='black')
        try:
            imscatter(formation[pos][0], formation[pos][1], ax=ax, image=draw_tshirt(position = pos[0] , n = int(pos[2])))
        except:
            imscatter(formation[pos][0], formation[pos][1], ax=ax, image=draw_tshirt())

    st.pyplot(fig)

    fig2 = plt.figure(figsize=(3,2))
    ax = fig2.add_subplot(111)

    pos_list = []
    label_list = []
    for pos in new_dict.keys():
        pos_list.append(ax.scatter(1, 1, marker='s', c=[(dict_fill_pos[pos][0]/255, dict_fill_pos[pos][1]/255, dict_fill_pos[pos][2]/255)]))
        label_list.append(pos.capitalize().replace('_', ' '))

    ax.scatter(1, 1, marker='s', c='black')

    fig2.legend(pos_list, tuple(label_list), 'upper center',
    ncol=3)
    plt.axis('off')
    st.pyplot(fig2)

    return fig2

def draw_tshirt(position='volante_mixto', n=1):
    if 'arquero' not in position:
        im = Image.new('RGBA', (512, 512), (250, 250, 250, 255))
        draw = ImageDraw.Draw(im)
        draw.line((256,10,256,490), fill=dict_fill_pos[position], width=25)
        draw.line((220,10,220,490), fill=dict_fill_pos[position], width=25)
        draw.line((292,10,292,490), fill=dict_fill_pos[position], width=25)
    else:
        im = Image.new('RGBA', (512, 512), dict_fill_pos[position])
        draw = ImageDraw.Draw(im)
    font = ImageFont.truetype("Freshman-POdx.ttf", 150)
    draw.text((260,256), f'{n}', font = font, anchor='mm', fill=(0,0,0,255))

    im2 = Image.new('RGBA', (512, 512), (0, 200, 200, 0))

    mask = Image.open('black.png').convert('L').resize(im.size)

    final = Image.composite(im2, im, mask)
    return final

def imscatter(x, y, image, ax=None, zoom=0.1):
            if ax is None:
                ax = plt.gca()
            im = OffsetImage(image, zoom=zoom)
            x, y = np.atleast_1d(x, y)
            artists = []
            for x0, y0 in zip(x, y):
                ab = AnnotationBbox(im, (x0, y0), xycoords='data', frameon=False)
                artists.append(ax.add_artist(ab))
            ax.update_datalim(np.column_stack([x, y]))
            ax.autoscale()
            return artists

def dream_team(tactic, df, df_gk, season, leagues, min_minutes, nationality, age):
    df_team = pd.DataFrame()
    for line in dict_tactics[tactic].keys():
        for position in set(dict_tactics[tactic][line]):
            w = weights(position)
            if 'arquero' not in position:
                w.rename(index = {'xG per shot taken':'xG per shot'}, inplace = True)
                df_pos = pd.DataFrame()
                for p in dict_pos_eq_instat[position]:
                    df_pos = df_pos.append(df[df.Position.str.contains(p, na=True)])
                percentile(df_pos)
                df_pos =df_pos[df_pos['Season'].isin([season])]
                if ('--All--' not in leagues) and (len(leagues)!=0):
                    df_pos =df_pos[df_pos['League'].isin(leagues)]
                df_pos =df_pos[df_pos['Minutes played'] >= min_minutes]
                if '--All--' not in nationality:
                    df_pos =df_pos[df_pos.index.get_level_values('Nationality').str.contains(nationality, na=False)]
                df_pos =df_pos[(df_pos['Age'] >= int(age[0])) & (df_pos['Age'] <= int(age[-1]))]
                #st.write(Xp_ranking(df_pos, weight=w, d_metric=dict_metrics[dict_metrics_pos[position]]).sort_values('Xp Ranking').astype(str))
                df_pos = Xp_ranking(df_pos, weight=w, d_metric=dict_metrics[dict_metrics_pos[position]]).sort_values('Xp Ranking')[:dict_tactics[tactic][line].count(position)]
                df_pos['Tactic position'] = position
                df_team = df_team.append(df_pos)
            else:
                w.rename(index = {np.NaN:"xG conceded - Goals conceded"}, inplace = True)
                df_pos = df_gk
                df_team_gk = Xp_ranking(df_pos, weight=w, d_metric=dict_metrics[dict_metrics_pos[position]]).sort_values('Xp Ranking')[:dict_tactics[tactic][line].count(position)]
                df_team_gk['Tactic position'] = position
    if len(df_team[df_team.drop(['Tactic position', 'Xp Score', 'Xp Ranking', 'Percentil'], axis=1)[['Number', 'InStat Index', 'Matches played', 'Minutes played']].duplicated()]) != 0:
        df_dup = df_team.loc[df_team[df_team.drop(['Tactic position', 'Xp Score', 'Xp Ranking', 'Percentil'], axis=1)[['Number', 'InStat Index', 'Matches played', 'Minutes played']].duplicated()].index.unique(), :]
        for i in df_dup.index.unique():
            df_i = df_dup.loc[i,:]
            while len(df_i) > 0:
                df_keep = df_i[df_i['Xp Score'] == df_i['Xp Score'].max()]
                if len(df_keep)>1:
                    df_team = df_team[~((df_team.drop(['Tactic position', 'Xp Score', 'Xp Ranking', 'Percentil'], axis=1).duplicated()) & (df_team.index.get_level_values('Name').isin([i[0]])))]
                    df_res = df_team[((df_team.drop(['Tactic position', 'Xp Score', 'Xp Ranking', 'Percentil'], axis=1).duplicated()) & (df_team.index.get_level_values('Name').isin([i[0]])))]
                else:
                    df_team = df_team[~df_team.index.get_level_values('Name').isin([i[0]])]
                    df_team = df_team.append(df_keep)
                    df_res = df_i[~(df_i['Xp Score'] == df_i['Xp Score'].max())]
                for position in df_res['Tactic position']:
                    w = weights(position)
                    w.rename(index = {'xG per shot taken':'xG per shot'}, inplace = True)
                    df_pos = pd.DataFrame()
                    for p in dict_pos_eq_instat[position]:
                        df_pos = df_pos.append(df[df.Position.str.contains(p, na=True)])
                    percentile(df_pos)
                    df_pos =df_pos[df_pos['Season'].isin([season])]
                    if ('--All--' not in leagues) and (len(leagues)!=0):
                        df_pos =df_pos[df_pos['League'].isin(leagues)]
                    df_pos =df_pos[df_pos['Minutes played'] >= min_minutes]
                    if '--All--' not in nationality:
                        df_pos =df_pos[df_pos.index.get_level_values('Nationality').str.contains(nationality, na=False)]
                    df_pos =df_pos[(df_pos['Age'] >= int(age[0])) & (df_pos['Age'] <= int(age[-1]))]
                    df_pos = Xp_ranking(df_pos, weight=w, d_metric=dict_metrics[dict_metrics_pos[position]]).sort_values('Xp Ranking')
                    df_pos = df_pos[~df_pos.index.isin(df_team.index)]
                    df_pos = df_pos.iloc[0, :]
                    df_pos['Tactic position'] = position
                    df_team = df_team.append(df_pos)

                df_i = df_team.loc[df_team[df_team.drop(['Tactic position', 'Xp Score', 'Xp Ranking', 'Percentil'], axis=1).duplicated()].index, :]
                try:
                    df_i = df_i.loc[i,:]
                except:
                    pass

    if (len(df_team) == 10) & (len(df_team_gk) == 1):
        pitch_streamlit(tactic, df_team, df_team_gk)
    else:
        st.warning(f'No se encontraron jugadores para todas las posiciones de la táctica {tactic}.')
    df_team_table = copy.deepcopy(df_team)
    df_team_gk_table = copy.deepcopy(df_team_gk)
    st.write("""
            ***
            # Tabla de percentiles""")
    if len(df_team_gk_table)!=0:
        df_team_gk_table.rename(columns={'Tactic position':'Posición'}, inplace=True)
        st.dataframe(df_team_gk_table)
        download_button(df_team_gk_table, f'percentiles_equipo_arqueros.xlsx', f'Descargar tabla', pickle_it=False)
    else:
        st.info('No se encontraron arqueros para los filtros seleccionados')
    if len(df_team_table)!=0:
        df_team_table.rename(columns={'Tactic position':'Posición'}, inplace=True)
        st.dataframe(df_team_table)
        download_button(df_team_table, f'percentiles_equipo.xlsx', f'Descargar tabla', pickle_it=False)
    else:
        st.info('No se encontraron jugadores en ninguna posición para los filtros seleccionados')


def history_streamlit(df_radar, df_raw, w, position):
    st.write("""
        ***
        ***
        ***
        """)
    st.write("""
        # Rendimiento por temporada para {}
        > Ranking historico de jugadores + radares de estadisticas globales por temporada.
        """.format(dict_pos[position]))
    with st.beta_expander('Filtros adicionales'):
        list_nationality = sorted(list({name for a in df_radar.index.get_level_values('Nationality').unique().tolist() for name in a.split(', ')}))
        list_nationality.insert(0, '--All--')
        nationality = st.multiselect('Escriba o seleccione la(s) nacionalidad(es)', list_nationality, '--All--',key='hola')
        if (len(nationality) != 0) and ('--All--' not in nationality):
            df_raw = df_raw[df_raw.index.get_level_values('Nationality').isin(nationality)]

    df_radar.reset_index(inplace = True)
    df_radar.set_index(['Name', 'Nationality', 'Height', 'Weight'], inplace = True)
    df_radar = df_radar[~df_radar.index.duplicated(keep='first')]

    df_raw.reset_index(inplace = True)
    df_raw[w.index.tolist()]=df_raw[w.index.tolist()].apply(pd.to_numeric,errors='coerce')
    df_sum = df_raw[w.index.tolist()+['Name', 'Nationality', 'Height', 'Weight', 'Season']].groupby(['Name', 'Nationality', 'Height', 'Weight', 'Season']).sum()
    df_size = df_raw[w.index.tolist()+['Name', 'Nationality', 'Height', 'Weight', 'Season']].groupby(['Name', 'Nationality', 'Height', 'Weight', 'Season']).size()  
    if 'arquero' not in position:
        df_position = df_raw[['Name', 'Nationality', 'Height', 'Weight', 'Season', 'Position']].groupby(['Name', 'Nationality', 'Height', 'Weight', 'Season']).sum()
    df_age = df_raw[['Name', 'Nationality', 'Height', 'Weight', 'Season', 'Age']].groupby(['Name', 'Nationality', 'Height', 'Weight', 'Season']).max()
    for col in df_sum.columns:
        if ('per 90 min' in col) or ('%' in col):
            df_sum[col] = df_sum[col].div(df_size)
    df_sum = pd.concat([df_age, df_sum], axis=1)
    df_raw = copy.deepcopy(df_sum)
    df = pd.DataFrame()
    for s in df_sum.index.get_level_values('Season').unique():
        df_sum_s = df_sum[df_sum.index.get_level_values('Season').isin([s])]
        percentile(df_sum_s)
        if 'arquero' not in position:
            df_position_s = df_position[df_position.index.get_level_values('Season').isin([s])]
            df_sum_s = pd.concat([df_position_s, df_sum_s], axis=1)
            df_sum_t = copy.deepcopy(df_sum_s)
            df_p = pd.DataFrame()
            for p in dict_pos_eq_instat[position]:
                df_p = df_p.append(df_sum_t[(df_sum_t.Position.str.contains(p, na=True)) | ((df_sum_t.index.get_level_values('Name').isin(df_radar.index.get_level_values('Name').unique())) & (df_sum_t.index.get_level_values('Nationality').isin(df_radar.index.get_level_values('Nationality').unique())) & (df_sum_t.index.get_level_values('Height').isin(df_radar.index.get_level_values('Height').unique())))])
            df_p.drop_duplicates(inplace=True)
        else:
            df_p = df_sum_s
        df_p = Xp_ranking(df_p, weight=w, d_metric=dict_metrics[dict_metrics_pos[position]])
        df = df.append(df_p)

    # print(df)

    idx = [2017, 2018, 2019, 2020, 2021]
    df_hist = pd.DataFrame()
    df_rad = pd.DataFrame()
    df_rad_raw = pd.DataFrame()
    for i, row in df_radar.iterrows():
        df_temp = df[(df.index.get_level_values('Name')==i[0]) & (df.index.get_level_values('Nationality')==i[1]) & (df.index.get_level_values('Height')==i[2]) & (df.index.get_level_values('Weight')==i[3])]
        df_temp_raw = df_raw[(df_raw.index.get_level_values('Name')==i[0]) & (df_raw.index.get_level_values('Nationality')==i[1]) & (df_raw.index.get_level_values('Height')==i[2]) & (df_raw.index.get_level_values('Weight')==i[3])]
        dict_scr = {s : scr for s, scr in zip(df_temp.index.get_level_values('Season').tolist(), df_temp['Xp Score'].tolist())}
        s_temp = pd.Series(data = dict_scr)
        s_temp.rename(i[0], inplace=True)
        df_hist = df_hist.append(s_temp)
        df_rad = df_rad.append(df_temp)
        df_rad_raw = df_rad.append(df_temp_raw)

    fig_ln = plt.figure()
    ax_ln = fig_ln.add_subplot(111)
    for i, row in df_hist.iterrows():
        row.index.astype(int, copy=False)
        row.sort_index(ascending=True, inplace=True)
        yrs = [str(y) for y in row.index.tolist()]
        val = row.values.tolist()
        ax_ln.plot(yrs, val, 'o-', label=i)
        plt.xticks(yrs)
    ax_ln.legend()
    plt.ylabel('Xp Score')
    plt.xlabel('Temporada')
    plt.ylim(0,100)
    plt.grid(color='#333333')
    st.pyplot(fig_ln)

    df_hist.columns.astype(int, copy=False)
    df_hist.sort_index(axis=1, ascending=False, inplace=True)
    st.dataframe(df_hist)

    st.write("""
            ***
            """)
    st.write("""## Parámetros de gráficas""")
    list_seasons = sorted(list(df_rad.index.get_level_values('Season').unique()), reverse=True)
    season = st.selectbox('Escriba o seleccione la temporada', list_seasons)
    df_rad = df_rad[df_rad.index.get_level_values('Season').isin([season])]
    df_rad_raw = df_rad_raw[df_rad_raw.index.get_level_values('Season').isin([season])]
    df_rad_raw.dropna(inplace=True)
    df_rad.reset_index(inplace = True)
    df_rad_raw.reset_index(inplace = True)
    df_rad.set_index(['Name', 'Nationality'], inplace = True)
    df_rad_raw.set_index(['Name', 'Nationality'], inplace = True)
    N_variables = st.slider('Número de variables en radar', 5,12, key=str(100000))
    st.write("""
            ***
            """)
    if season == list_seasons[0]:
        df = df[df.index.get_level_values('Season').isin([season])]
        df = df[['Age', 'Xp Score']]
        fig_age = plt.figure()
        ax_age = fig_age.add_subplot(111)
        ax_age.scatter(df['Age'].values.tolist(), df['Xp Score'].values.tolist())
        for i, row in df_radar.iterrows():
            df_temp = df[(df.index.get_level_values('Name')==i[0]) & (df.index.get_level_values('Nationality')==i[1]) & (df.index.get_level_values('Height')==i[2]) & (df.index.get_level_values('Weight')==i[3])]
            ax_age.scatter(df_temp['Age'].values.tolist(), df_temp['Xp Score'].values.tolist(), marker='*', s=200, label = i[0])
        plt.legend()
        plt.ylabel('Xp Score')
        plt.xlabel('Edad')
        plt.ylim(0,100)
        plt.xlim(15,40)
        st.pyplot(fig_age)
    # print(df_rad)
    # print(df_rad_raw)
    radar_streamlit(df_rad, df_rad_raw, position, w, N_variables)

equipo_per90=['xG (Expected goals)','Goals',"Opponent's xG",'Expected points','Challenges won','Air challenges won','Successful actions','Accurate passes','Crosses accurate','Lost balls','xG (Expected goals)','Goals','Chances','Shots','Shots on target','xG per shot','xG per goal','Key passes','Attacking challenges won','Dribbles successful',
"Opponent's xG",'Defensive challenges won','Tackles successful','Ball interceptions','Free ball pick ups','Ball recoveries',"Ball recoveries in opponent's half",'Team pressing successful',
'Positional attacks','Counter-attacks','Set pieces attacks' ,'Building-ups','Building-ups without pressing','High pressing','Average duration of ball possession, min',
'Attacks - center','Chances','Air challenges','Positional attacks','Positional attacks with shots','Attacking challenges','Attacks with shots - Set pieces attacks','Attacks with shots - Set pieces attacks','Attacks with shots - center','Attacks with shots - left flank','Attacks with shots - right flank','Total actions','Tackles','Team pressing','Passes','Challenges','High pressing successful','Free-kick attacks with shots','Free-kick attacks','Corner attacks','Counter-attacks with a shot','Corner attacks with shots','Counter-attacks','Crosses','Chances successful','','Defensive challenges','Dribbles','Attacks - left flank','Attacks - right flank',"Entrances on opponent's half","Entrances on final third of opponent's half","Entrances to the opponent's box" ]
equipo_per90=list(set(equipo_per90))
equipo_per=['Efficiency for attacks through the right flank, %','Efficiency for attacks through the left flank, %','Efficiency for attacks through the central zone, %','% of efficiency for set-piece attacks','% of efficiency for counterattacks','% of efficiency for positional attacks','Ball possession, %','High pressing, %','Challenges in defence won, %','Tackles won, %','Challenges won, %','Successful dribbles, %','Air challenges won, %','Successful dribbles, %','Successful actions, %','Pressing efficiency, %','Accurate passes, %','Accurate crosses, %','Challenges in attack won, %']
def base_equipos():
    df=pd.read_excel('Data/sumaequipos.xlsx',engine='openpyxl')
    df1=pd.read_excel('Data/sumaequiposb.xlsx',engine='openpyxl')
    df['Season']=20212
    df['League']='Liga Betplay'
    df1['Season']=20212
    df1['League']='Torneo Betplay'
    df=df.append(df1)

    for col in df.columns:
        if col in equipo_per90:
            try:
                df[str(col)+' per 90 min'] = (df[col]/df['Partidos jugados'])
            except:
                print('Division por 0')
    df['Ball possession, % per 90 min']=df['Ball possession, %']
    df['Chances, % of conversion per 90 min']=df['Chances successful per 90 min']/df['Chances per 90 min']*100
    df['Air challenges won, % per 90 min']=df['Air challenges won per 90 min']/df['Air challenges per 90 min']*100
    df['Challenges in attack won, % per 90 min']=df['Attacking challenges won per 90 min']/df['Attacking challenges per 90 min']*100
    df['Challenges won, % per 90 min']=df['Challenges won per 90 min']/df['Challenges per 90 min']*100
    df['% of efficiency for corner attacks per 90 min']=df['Corner attacks with shots per 90 min']/df['Corner attacks per 90 min']*100
    df['% of efficiency for counterattacks per 90 min']=df['Counter-attacks with a shot per 90 min']/df['Counter-attacks per 90 min']*100
    df['Accurate crosses, % per 90 min']=df['Crosses accurate per 90 min']/df['Crosses per 90 min']*100
    df['Challenges in defence won, % per 90 min']=df['Defensive challenges won per 90 min']/df['Defensive challenges per 90 min']*100
    df['Successful dribbles, % per 90 min']=df['Dribbles successful per 90 min']/df['Dribbles per 90 min']*100
    df['% of efficiency for free-kick attacks per 90 min']=df['Free-kick attacks with shots per 90 min']/df['Free-kick attacks per 90 min']*100
    #df['% scored free kick shots per 90 min']=df['Goals - Free-kick attack per 90 min']/df['Free-kick shots per 90 min']*100
    df['High pressing, % per 90 min']=df['High pressing successful per 90 min']/df['High pressing per 90 min']*100
    #df['Low pressing, % per 90 min']=df['Low pressing successful per 90 min']/df['Low pressing per 90 min']*100
    df['Accurate passes, % per 90 min']=df['Accurate passes per 90 min']/df['Passes per 90 min']*100
    #df['Penalties scored, % per 90 min']=df['Penalties\n scored per 90 min']/df['Penalties per 90 min']*100
    df['% of efficiency for positional attacks per 90 min']=df['Positional attacks with shots per 90 min']/df['Positional attacks per 90 min']*100
    df['Shots on target, % per 90 min']=df['Shots on target per 90 min']/df['Shots per 90 min']*100
    df['Successful actions, % per 90 min']=df['Successful actions per 90 min']/df['Total actions per 90 min']*100
    df['Tackles won, % per 90 min']=df['Tackles successful per 90 min']/df['Tackles per 90 min']*100
    df['Pressing efficiency, % per 90 min']=df['Team pressing successful per 90 min']/df['Team pressing per 90 min']*100
    #df['% of efficiency for throw-in attacks per 90 min']=df['Throw-in attacks with shots per 90 min']/df['Throw-in attacks per 90 min']*100
    df['% of efficiency for set-piece attacks per 90 min']=df['Attacks with shots - Set pieces attacks per 90 min']/df['Set pieces attacks per 90 min']*100
    df['Efficiency for attacks through the central zone, % per 90 min']=df['Attacks with shots - center per 90 min']/df['Attacks - center per 90 min']*100
    df['Efficiency for attacks through the left flank, % per 90 min']=df['Attacks with shots - left flank per 90 min']/df['Attacks - left flank per 90 min']*100
    df['Efficiency for attacks through the right flank, % per 90 min']=df['Attacks with shots - right flank per 90 min']/df['Attacks - right flank per 90 min']*100

    return df

def radar_equipos(df_radar,df_raw,variables,radar_type):
    try:   
        df_radar.set_index('League', drop=True, inplace=True)
        df_radar.set_index('Season', append=True, inplace=True)
        df_radar.set_index('Team',append=True,inplace=True)

        df_raw.set_index('League', drop=True, inplace=True)
        df_raw.set_index('Season', append=True, inplace=True)
        df_raw.set_index('Team',append=True,inplace=True)
    except:
        pass
    fig_radar = plt.figure()
    ax = fig_radar.add_subplot(111, polar=True)
   
    try:
        df_radar = df_radar.loc[:, variables]
        ax.fill_between(np.linspace(0, 2*np.pi, 100), 0.495, 0.505, color='#ed2054', zorder=10)
        pct50_legend = plt.legend(handles=[Line2D([0], [0], marker='o', color='#000000', label='Percentil 50', markeredgewidth=1.5, markeredgecolor='#ed2054', markersize=14)], bbox_to_anchor=(1.35, 0.05), loc='lower right', fontsize=12)
        plt.gca().add_artist(pct50_legend)
    except:
        df_radar = df_radar.loc[:,variables]
    N_variables = len(variables)
    angles = [n / float(N_variables) * 2 * np.pi for n in range(N_variables)]
    angles += angles[:1]

    plt.xticks(angles[:-1], variables, size=10)
    labels = [item.get_text() for item in ax.get_yticklabels()]
    ax.set_yticklabels(['']*len(labels))

    cl = 0
    if "Opponent's xG" in df_radar.columns:
        df_radar["Opponent's xG"]=1-df_radar["Opponent's xG"]
    if "Opponent's xG per 90 min" in df_radar.columns:
        df_radar["Opponent's xG per 90 min"]=1-df_radar["Opponent's xG per 90 min"]
    for index, row in df_radar.iterrows():
        values=row[variables].tolist()
        values += values[:1]
        if len(df_radar.index.get_level_values('Team').tolist()) != len(set(df_radar.index.get_level_values('Team').tolist())):
            try:
                name_label = '#{} - {} ({})\n{} ({})'.format(index[-1], index[-2], index[-3])
            except:
                name_label = '{} ({})\n{} ({})'.format(index[-1], index[-2], index[-3])
        else:
            try:
                name_label = '{} - {} ({})'.format(index[-1], index[-3],index[-2])
            except:
                    name_label = '{} ({})'.format(index[-1], index[-2])
                
        ax.plot(angles, values, linewidth=1, linestyle='solid', label=name_label)
        ax.fill(angles, values, alpha=0.6)
    plt.legend(bbox_to_anchor=(1.08, 1), loc='upper left', fontsize=12)
    st.write("""
        # Radar {}
        ## 
        ###
        """.format(radar_type))
    st.pyplot(fig_radar)

    if len(df_radar) == 1:
        st.write("""
                ***
                """)
        cmap_colors = mpl.cm.get_cmap('winter')
        list_pct_value = values[:-1]#[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.88345, 0.9, 0.910, 0.911, 0.912]
        list_pct_name = variables#['Vancune nsdiufb enfuwef\ngfghghg', 'BUI NIUBBBB', 'bdcuwevf bwefwe fbwey\nvnde ndeiwu', 'nxuisn ewnweic', 'wcnenuciwn wecnecnce ecnwecn', 'suiwdh ediuh', 'asuid duie', 'wdehi wdiu', 'xnxwh denu nd ndd', "JAbde BSAA", 'ncid cni', 'ncwe']

        fig_pctl, ax = plt.subplots(math.ceil(N_variables/2), 2, figsize=(18,9))
        for n, pct_value in enumerate(list_pct_value[:N_variables]):
            row = math.floor((n)/2)
            if (n+1)%2 == 0:
                col = 1
            else:
                col = 0

            c_code = cmap_colors(0.4+0.6*pct_value)

            h_line = ax[row,col].hlines(0, 0, 1, color='#545454', linewidth=8, zorder=1)

            circle_0 = plt.Circle((0, 0), radius=.04, color='#545454', zorder=1)
            circle_50 = plt.Circle((0.5, 0), radius=.04, color='#545454', zorder=1)
            circle_100 = plt.Circle((1, 0), radius=.04, color='#545454', zorder=1)

            ax[row,col].add_patch(circle_0)
            ax[row,col].add_patch(circle_50)
            ax[row,col].add_patch(circle_100)

            circle = plt.Circle((pct_value, 0), radius=.1, color=c_code, linewidth=2, zorder=100, alpha=0.7)
            ax[row,col].add_patch(circle)
            number = ax[row,col].annotate(round(pct_value*100,1), xy=(pct_value, 0), color='black', fontsize=20, weight='bold', ha="center", va="center", zorder=1000)
            label = ax[row,col].annotate(list_pct_name[n], xy=(0, 0.11), color='white', fontsize=20, ha="left", va="center", zorder=10000)

            ax[row,col].axis('off')
            ax[row,col].set_aspect('equal')
            ax[row,col].autoscale_view()

        if N_variables%2 != 0:
            ax[row,1].axis('off')
            ax[row,1].set_aspect('equal')
            ax[row,1].autoscale_view()

        plt.subplots_adjust(top=0.964,bottom=0.015,left=0.008,right=0.992,hspace=0.6,wspace=0.0)
        st.pyplot(fig_pctl)
    else:
        st.write("""
            ### Tabla de percentiles
            > Percentiles de acuerdo a cada una de las ligas respectivas de los equipos
            """)
        st.dataframe(df_radar[variables])
        download_button(df_radar[variables], f'percentiles.xlsx', f'Descargar tabla', pickle_it=False)
    
    st.write("""
        ### Tabla de valores
        > Totales acumulados por 90 minutos.
        """)
    
    if df_raw.index.get_level_values('League').nunique() == 1:
        n_partidos=df_raw['Partidos jugados'].values[0]
        for col in df_raw[variables]:
            if (col.count('%')<1) and (col !='Expected points'):
                df_raw[col]=df_raw[col]/n_partidos
    else:
        for idx,lig in enumerate(df_raw.index.get_level_values('League').unique()):
            n_partidos=st.number_input(f"Seleccione el número de partidos jugados en {lig}",min_value=1,key=str(idx))
            for col in df_raw.loc[df_raw.index.get_level_values('League').isin([lig]),variables]:
                if (col.count('%')<1) and (col !='Expected points'):
                    df_raw.loc[df_raw.index.get_level_values('League').isin([lig]),col]=df_raw.loc[df_raw.index.get_level_values('League').isin([lig]),col]/n_partidos
    st.dataframe(df_raw[variables])
    download_button(df_raw[variables], f'valores.xlsx', f'Descargar tabla', pickle_it=False)

def borrar_apellido(nombre):
    etiqueta=''
    nombres=str(nombre).split(' ')
    try:
        if len(nombres)==2:
            etiqueta= nombres[0][0]+'. '+ nombres[1]
        else:
            etiqueta = nombres[0][0] +'. '+ nombres[-2]
        return etiqueta
    except:
        v=1
        
def matriz_de_pases(eventos,equipo):
    
    eventos = eventos[eventos['team_name']==equipo]
    acciones = ['Attacking pass accurate', 'Accurate key pass']
    posiciones = ['LD', 'LDM', 'LM', 'LAM', 'LF', 'LCD', 'LCDM', 'LCM', 'LCAM', 'LCF', 'GK', 'CD', 'CDM', 'CM', 'CAM', 'CF', 'RCD', 'RCDM', 'RCM', 'RCAM', 'RCF', 'RD', 'RDM', 'RM', 'RAM', 'RF']

    pases = eventos[eventos[ 'action_name'].isin(acciones)]
    
    jugadores_totales = eventos[eventos['action_name']=='Average position Full match'][['player_name','pos_x', 'pos_y']]
    jugadores_iniciales = eventos[(eventos['action_name'].isin(posiciones))&(eventos['half']==1)&(eventos['second']==0)][['player_name']]
    jugadores = pd.merge(jugadores_iniciales, jugadores_totales, on='player_name', how= 'left'  )
    pases_entre=pases.groupby([ 'player_name', 'opponent_name']).id.count().reset_index()
    pases_entre=pd.merge(pases_entre, jugadores, on ='player_name', how = 'left' )
    
    pases_entre=pd.merge(pases_entre, jugadores, left_on ='opponent_name', right_on='player_name', how = 'left' ,suffixes=('','_final') ).dropna().reset_index().drop(columns=['index', 'player_name_final'])
    
    pases['player_name']=pases['player_name'].apply(borrar_apellido)
    pases['opponent_name']=pases['opponent_name'].apply(borrar_apellido)
    
    pases_entre=pases_entre[pases_entre['id']>1]
    tabla= pd.crosstab(pases['player_name'], pases['opponent_name'])
    tablalabels=tabla.replace(to_replace=0, value='')
    fig2=plt.figure()
    fig2.set_size_inches(20, 14)


    color_map = sns.cubehelix_palette(start=.0, rot=-.7, as_cmap=True)
    
    sns.heatmap(tabla, annot=tablalabels,fmt='',  cbar=False,cmap=color_map.reversed())
    plt.tick_params(axis='both', which='major', labelsize=10, labelbottom = False, bottom=False, top = False, labeltop=True)
    plt.xticks(rotation=45,ha='left')
    plt.tight_layout()
    plt.ylabel('')
    plt.xlabel('')
    
    st.pyplot(fig2)