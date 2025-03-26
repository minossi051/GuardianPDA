import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os
import requests
from PIL import Image
import fitz
import docx
import json
import os

#issues on 25/03/2025
# o gateway procergs não processa a solicita~]ao do client para o uso da api deep seek
# tentei com o certificado exportado .pem e não adiantou
# desativei a verificação SSL para testes de desenvolvimento; é necessário a solução deste problema para o deploy em produção

#métodos para a solução da verificação  SSL
#Usar Certificado Corporativo Global (Solução Permanente)
import certifi
print(certifi.where())
from requests.adapters import HTTPAdapter
from urllib3.poolmanager import
import ssl
class CustomHttpAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_version=ssl.PROTOCOL_TLS_CLIENT,
            ca_certs='C:\\Users\\vicenzo-minossi\\AppData\\Local\\Programs\\Python\\Python313\\Lib\\site-packages\\certifi\\cacert.pem'
        )
DEEPSEEK_API_URL = "https://api.deepseek.com"
DEEPSEEK_API_KEY = "key"
PROXY_URL_AUTENTICADED = 'http://vicenzo-minossi:Copodecoca2005!@proxy.procergs.reders'

sessao = requests.Session()
sessao.mount('https://', CustomHttpAdapter())



st.title('Painel interativo - PoPs RS📊')

#caminho excel (local) --> precisa ser implementado para alimentar o dash automatico
base_dados = 'C:\\Users\\vicenzo-minossi\\Desktop\\Guardian\\DIF-PIR Execução POPS.xlsx'

# planilha principal
sheet = "Panorama POPS RS"
df = pd.read_excel(base_dados, sheet_name=sheet, engine='openpyxl')

# colunas alvo
if sheet == 'Panorama POPS RS':
    if {'Latitude', 'Longitude', 'Endereço', 'Nome PoP', 'Observações'}.issubset(df.columns):
        st.write("📍 **Mapa de Localização dos POPs**")

        # string to float
        df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
        df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

        # coordenadas null
        df = df.dropna(subset=["Latitude", "Longitude"])

        if df.empty:
            st.warning("Nenhuma coordenada válida encontrada. Verifique os dados!")
        else:
            
            map_center = [df['Latitude'].mean(), df['Longitude'].mean()]
            mapa = folium.Map(location=map_center, zoom_start=6)

            icon_path = 'C:\\Users\\vicenzo-minossi\\Desktop\\Guardian\\alfinete.png'

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

#url onedrive
one_drive_url = "https://rsgovbr-my.sharepoint.com/:x:/g/personal/moises-brum_procergs_rs_gov_br/EehxrZIY7LFPjdulIaRlBp8BsmHlWdMJNN9V9oH1pEk0xg?e=YW15MQ"
#ainda não resolvi o problema do acesso ao one drive, talvez eu crie uma pasta local para hospedar a pasta do one drive que contém a planilha
@st.cache_data
def carregar_dados():
    """
    Lê os dados da planilha de PoPs
    """
    try:
        # Se for um arquivo local
        caminho_planilha = 'C:\\Users\\vicenzo-minossi\\Desktop\\Guardian\\DIF-PIR Execução POPS.xlsx'
        xls = pd.ExcelFile(caminho_planilha, engine='openpyxl')

        dataframes = {}
        for aba in xls.sheet_names:
            dataframes[aba] = xls.parse(aba)

        return dataframes
        
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return None
abas = carregar_dados()

#Eagle

# arquivos de treinamento
def carregar_arquivos():
    arquivos_extraidos = {}
    pasta_atual = "C:\\Users\\vicenzo-minossi\\Desktop\\Guardian\\dados"
    
    if not os.path.exists(pasta_atual):
        print(f"Erro: O diretório {pasta_atual} não existe.")
        return {}
    
    for arquivo in os.listdir(pasta_atual):
        caminho_completo = os.path.join(pasta_atual, arquivo)
        
        if arquivo.endswith(".txt"):
            with open(caminho_completo, "r", encoding="utf-8") as f:
                arquivos_extraidos[arquivo] = f.read()
        elif arquivo.endswith(".pdf"):
            texto_pdf = ""
            with fitz.open(caminho_completo) as pdf:
                for pagina in pdf:
                    texto_pdf += pagina.get_text()
            arquivos_extraidos[arquivo] = texto_pdf
        elif arquivo.endswith(".docx"):
            doc = docx.Document(caminho_completo)
            texto_docx = "\n".join([p.text for p in doc.paragraphs])
            arquivos_extraidos[arquivo] = texto_docx
        elif arquivo.endswith(".xlsx"):
            try:
                xls = pd.ExcelFile(caminho_completo, engine='openpyxl')
                arquivos_extraidos[arquivo] = {aba: xls.parse(aba).to_string() for aba in xls.sheet_names}
            except Exception as e:
                arquivos_extraidos[arquivo] = f"Erro ao carregar planilha: {e}"
    
    return arquivos_extraidos



bot_icon = "C:\\Users\\vicenzo-minossi\\Desktop\\Guardian\\guardian.png" 
st.image(Image.open(bot_icon), width=100) 
st.title("💬 Eagle, assistente DIF-PIR-PoPs")
#deepseek


raw_user = os.getlogin()
raw_user = str(raw_user)

parters = raw_user.split('-')
nome = parters[0].capitalize() if len(parters) > 0 else ''
sobrenome = parters[1].capitalize() if len(parters) > 1 else ''


# Chamada da função e verificação
arquivos_extraidos = carregar_arquivos()
if arquivos_extraidos is None:
    arquivos_extraidos = {}
    
#concatenar dados para agregar ao contexto
# Criar o contexto do chatbot (sem duplicidade)
contexto_completo = f'Usuário: {nome} {sobrenome}\n\n'
if abas:
    for nome_aba, df in abas.items():
        contexto_completo += f"\n\n### Dados da aba: {nome_aba}\n"
        contexto_completo += df.to_string()
else:
    contexto_completo += "Alguns dados não foram carregados."

for nome_arquivo, conteudo in arquivos_extraidos.items():
    contexto_completo += f"\n\n### Arquivo: {nome_arquivo}\n{conteudo}"


def processar_pergunta_com_deepseek(pergunta, contexto):
    """
    Envia a pergunta e o contexto para a API DeepSeek.
    """
    headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "Ei, olá! Você é Guardian, assistente especializado na manutenção de PoPs. Você tem acesso a todos os dados "
            "reunidos sobre a operação de PoPs ao redor do estado do Rio Grande do Sul, na PROCERGS (Companhia pública responsável). Eis um resumo de como as coisas acontecem por aqui: "
            "Você trabalhá ajudando o pessoal do setor de Projeto e Instalação de Rede. Todos do setor vão ter acesso a sua interface, "
            "mas apenas uma equipe é responsável pela manutenção dos PoPs, estão eles: Vicenzo (Seu programador e quem está lhe dizendo isso :) ), Moises, Dario e Gabriel, são eles que podem ser consultados para"
            "eventuais confirmações de informações ou para assuntos operacionais. A chefia do setor, (nosso chefe), é o Carlos, então acatamos às ordens dele."
            "Nosso setor é composto, em suma maioria, por projetistas de rede e engenheriros elétricos. Nós dos PoPs, comos meros técnicos de T.I mortais, podemos sugerir infraestruturas nos PoPs,"
            "projetar circuitos e supervisionar terceirizadas. Nos seus dados, está incluso as planilhas de orçamento da terceirizada CDS, "
            "que executa as obras, em caso precisemos de uma visão mais analítica de um projeto a respeito das metragens e dos materiais utilizados."
            "Sobre os dados DIF-PIR Execução PoPs: A aba 'Panorama PoPs RS' aglutina informações gerais sobre os PoPs, as quais você pode observar. As outras abas correspondem a assuntos mais direcionados,"
            "como os splits e os nobreaks, por exemplo. Há também as abas que representam um mapeamento dos racks nos PoPs, com cada equipamento sinalizado. Adicionei ao seu contexo o nome do usuário do Windows"
            "ao qual você está falando no momento, então saberás se sou eu, Carlos, ou outro colega do setor. Dê sempre respostas claras e objetivas, com uma entonação um pouco mais despojada"
            ", descontraída, mas sem fugir muito do profissionalismo. Em caso de informações faltando ou caso não chegue a uma conclusão sobre algo, por favor informe a nós! Suas respostas, se convirem à, podem incluir"
            "interfaces gráficas em Python (pergunte ao usuário sempre) e análise de dados mais aprofundada. Estarei disponibilizando algumas instruções operacionais nos seus arquivos de treinamento, que contém"
            "informações sobre a política e postura que a comapnhia adota diante de incidentes registrados. "},
            {"role": "user", "content": f"{contexto}\n\nPergunta: {pergunta}"}
        ],
        "max_tokens": 300
    }

    #response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, verify=True)  ##################################### Ativar verificação SSl para ambiente de produção
    #return response.json().get("choices", [{}])[0].get("message", {}).get("content", "Erro na resposta")

    response = sessao.get(
        DEEPSEEK_API_URL, proxies={'http': PROXY_URL_AUTENTICADED, 'https': PROXY_URL_AUTENTICADED},
        verify=True
    )

# Controle de histórico de conversas
if "conversas" not in st.session_state:
    st.session_state["conversas"] = []

# Entrada do usuário
pergunta = st.text_input("Digite sua pergunta sobre os PoPs:")
if pergunta:
    resposta = processar_pergunta_com_deepseek(pergunta, contexto_completo)
    st.session_state["conversas"].append({"user": pergunta, "bot": resposta})


st.write("O bot acessará todas as abas para responder suas perguntas.")
st.success(f"⚠️ Informações geradas por IA podem estar incorretas, considere verificar.")

# Exibir histórico da conversa
st.subheader("📜 Histórico da Conversa")
for conv in st.session_state["conversas"]:
    st.write(f"🧑‍💻 Você: {conv['user']}")
    st.write(f"🤖 Eagle: {conv['bot']}")


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


    #informações sobre as preventivas   
    aba_preventivas = list(abas.keys())[9]
    if{'POP','1° DATA','2° DATA'}.issubset(abas[aba_preventivas].columns):
        df_preventivas = abas[aba_preventivas][['POP','1° DATA','2° DATA']]
        st.write(f'📄 ** Tabela de manutenções preventivas **')
        st.dataframe(df_preventivas)
    else:
        st.warning('Não foi possível carregar os dados das preventivas')
    
