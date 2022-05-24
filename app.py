import streamlit as st
from multiapp import MultiApp
from apps import home, ranking,xG, Tiros,barras,probabilidades,barrasEstadisticas,rankingref,xgEquipos,pasesT,compjugadores, parecidos,onceideal, histjug,radares,colombia


app=MultiApp()
app.add_app("INICIO",home.app)
app.add_app("RANKING",ranking.app)
app.add_app("RANKING COLOMBIANOS",colombia.app)
app.add_app("RANKING POR REFERENTE", rankingref.app)
app.add_app("COMPARAR JUGADORES", compjugadores.app)
app.add_app("BUSCAR PARECIDOS",parecidos.app)
app.add_app("11 IDEAL",onceideal.app)
app.add_app("HISTÓRICO JUGADORES",histjug.app)
#app.add_app("RADARES DE EQUIPOS",radares.app)
app.add_app("RED PASES",pasesT.app)
app.add_app("DIFERENCIA XG - JUGADORES",xG.app)
app.add_app("DIFERENCIA XG - EQUIPOS",xgEquipos.app)
#app.add_app("ESTADÍSTICAS",barras.app)
app.add_app("MAPA DE TIROS",Tiros.app)
app.add_app("BARRAS ESTADÍSTICAS",barrasEstadisticas.app)
app.add_app("PROBABILIDADES ",probabilidades.app)


#app.add_app("PRUEBA",prueba.app)
app.run()
