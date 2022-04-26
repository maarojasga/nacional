import pandas as pd
import streamlit as st
from modelo import *
def app():
    df_in = base_jugadores()
    df_gk_in = base_arqueros()

    st.dataframe(df_in)
    st.write(df_gk_in)