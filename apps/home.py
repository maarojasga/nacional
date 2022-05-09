import time
from PIL import Image
import streamlit as st
import os

def app():
    modificationTime = time.strftime('%d / %m / %Y', time.localtime(os.path.getmtime('Data/base_jugadores.csv')))
    st.write("""
    #
    #
    #
    """)
    image = Image.open('Imagenes/xpecta.png')
    col1, col2 = st.columns([1, 1])
    col1.image(image)
    col2.write("""
    # **X scout**
    > Scouting Engine -- ALPHA version --\n
    > Updated {}
    """.format(modificationTime))