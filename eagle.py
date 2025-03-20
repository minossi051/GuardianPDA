import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

st.title('Painel interativo - PoPs RS📊')

# Caminho do arquivo Excel
base_dados = 'C:\\Users\\vicenzo-minossi\\Desktop\\EaglePDA\\DIF-PIR Execução POPS.xlsx'

# Nome da aba a ser carregada
sheet = "Panorama POPS RS"

# Lê o Excel e carrega a aba específica
df = pd.read_excel(base_dados, sheet_name=sheet, engine='openpyxl')
colunas_existentes = []

# Verifica se a aba contém todas as colunas necessárias
if sheet == 'Panorama POPS RS':
    if {'Latitude', 'Longitude', 'Endereço', 'Nome PoP', 'Observações'}.issubset(df.columns):
        st.write("📍 **Mapa de Localização dos POPs**")

        # Converte Latitude e Longitude para float
        df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
        df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

        # Remove linhas sem coordenadas válidas
        df = df.dropna(subset=["Latitude", "Longitude"])

        if df.empty:
            st.warning("Nenhuma coordenada válida encontrada. Verifique os dados!")
        else:
            # Centraliza o mapa na média das coordenadas (sem 'Nome PoP' e 'Observações')
            map_center = [df['Latitude'].mean(), df['Longitude'].mean()]
            mapa = folium.Map(location=map_center, zoom_start=6)

            # Caminho do ícone personalizado
            icon_path = 'C:\\Users\\vicenzo-minossi\\Desktop\\EaglePDA\\alfinete.png'

            for _, row in df.iterrows():
                alfinete_png = folium.CustomIcon(
                    icon_path,
                    icon_size=(30, 30)
                )

                folium.Marker(
                    location=[row['Latitude'], row['Longitude']],
                    popup=f"<b>Nome PoP:</b> {row['Nome PoP']}<br><b>Endereço:</b> {row['Endereço']}<br><b>Observações:</b> {row['Observações']}",
                    tooltip=row['Nome PoP'],
                    icon=alfinete_png
                ).add_to(mapa)

            # Exibe o mapa no Streamlit
            st_folium(mapa, width=700, height=500)
    else:
        st.warning('A aba não contém as informações necessárias.')

    # Exibe estatísticas dos PoPs: Quantidades de PoPs sem nobreak
    st.write("📊 **Resumo Estatístico:**")
    st.write(df.describe())

