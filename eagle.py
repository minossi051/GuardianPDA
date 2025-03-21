import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
import requests
st.title('Painel interativo - PoPs RS📊')

base_dados = 'C:\\Users\\vicenzo-minossi\\Desktop\\EaglePDA\\DIF-PIR Execução POPS.xlsx'

sheet = "Panorama POPS RS"

df = pd.read_excel(base_dados, sheet_name=sheet, engine='openpyxl')

if sheet == 'Panorama POPS RS':
    if {'Latitude', 'Longitude', 'Endereço', 'Nome PoP', 'Observações'}.issubset(df.columns):
        st.write("📍 **Mapa de Localização dos POPs**")

        df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
        df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

        df = df.dropna(subset=["Latitude", "Longitude"])

        if df.empty:
            st.warning("Nenhuma coordenada válida encontrada. Verifique os dados!")
        else:
            map_center = [df['Latitude'].mean(), df['Longitude'].mean()]
            mapa = folium.Map(location=map_center, zoom_start=6)

    
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

        
            st_folium(mapa, width=700, height=500)
    else:
        st.warning('A aba não contém as informações necessárias.')



    #CHATBOT assistente da manutenção


#Configuração da API DeepSeek
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = "sk-09a644fe699f439cb16ab3e4ed751887" 

# url onedrive
one_drive_url = "SUA_URL_DA_PLANILHA_ONEDRIVE"

@st.cache_data
def carregar_dados():
    """
    Lê os dados da planilha de PoPs
    """
    try:
    
        caminho_planilha = 'C:\\Users\\vicenzo-minossi\\Desktop\\EaglePDA\\DIF-PIR Execução POPS.xlsx'
        xls = pd.ExcelFile(caminho_planilha, engine='openpyxl')

        dataframes = {}
        for aba in xls.sheet_names:
            dataframes[aba] = xls.parse(aba)

        return dataframes
        
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return None

abas = carregar_dados()

def processar_pergunta_com_deepseek(pergunta, contexto):
    """
    Envia a pergunta e o contexto para a API da DeepSeek, que retorna a resposta.
    """
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Você é um assistente especializado na manutenção de PoPs. Seu objetivo é fornecer informações detalhadas sobre os PoPs, auxiliar no gerenciamento da infraestrutura e sugerir ações preventivas e corretivas com base nos dados disponíveis."},
            {"role": "user", "content": f"{contexto}\n\nPergunta: {pergunta}"}
        ],
        "max_tokens": 200
    }

    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"Erro ao processar a pergunta: {response.status_code}"

# streamlit
st.title("Chatbot Assistente de Manutenção de PoPs")

# chat
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# histórico
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# entrada da pergunta
pergunta = st.text_input("Consulta de dados:")

if pergunta:
    # contexto
    contexto = df.to_string()

    # Obtém resposta do DeepSeek
    resposta = processar_pergunta_com_deepseek(pergunta, contexto)

    # histórico
    st.session_state["messages"].append({"role": "user", "content": pergunta})
    st.session_state["messages"].append({"role": "assistant", "content": resposta})

   #resposta
    with st.chat_message("assistant"):
        st.markdown(resposta)

#estátisticas gerais


#situações iminentes nos pops
if abas is not None:
    aba_principal = list(abas.keys())[7]

    if {'Observações','Nome PoP'}.issubset(abas[aba_principal].columns):
        df_filtrado = abas[aba_principal][['Nome PoP','Observações']]
        df_filtrado = df_filtrado[df_filtrado['Observações'] != 'Sem observações'] 
        st.write(f"📄 **Tabela filtrada da aba principal ({aba_principal})**")
        st.dataframe(df_filtrado)
    else:
        st.warning('Não foi possível carregar as colunas desejadas')
        
