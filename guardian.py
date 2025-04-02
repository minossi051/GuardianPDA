import json
import pandas as pd
from openai import OpenAI
import os
from flask import Flask, send_file

app = Flask(__name__)

@app.route('/download')
def baixar_planilha():
    caminho_arquivo = "C:\\Users\\vicenzo-minossi\\OneDrive - Governo do Estado do Rio Grande do Sul\\POPs - Arquivos de Moises Gustavo Brum\DIF-PIR Execução POPS.xlsx"
    return send_file(caminho_arquivo, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


raw_user = os.getlogin()
nome, sobrenome = "Usuário", ""
parters = raw_user.split('-')
if len(parters) > 0:
    nome = parters[0].capitalize()
if len(parters) > 1:
    sobrenome = parters[1].capitalize()

API_KEY = "chave"
BASE_URL = "https://api.deepseek.com"
HISTORICO_JSON = "historico.json"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def carregar_historico():
    """Carrega o histórico de perguntas e respostas de um arquivo JSON."""
    try:
        with open(HISTORICO_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def salvar_historico(historico):
    """Salva o histórico atualizado no arquivo JSON."""
    with open(HISTORICO_JSON, "w", encoding="utf-8") as f:
        json.dump(historico, f, ensure_ascii=False, indent=4)

def carregar_dados_excel(arquivo_excel):
    """Lê apenas as abas desejadas da planilha do Excel."""
    abas_permitidas = ["Panorama POPS RS", "Splits", "Nobreaks","Pessoal"]
    try:
        xls = pd.ExcelFile(arquivo_excel)
        return {aba: xls.parse(aba) for aba in abas_permitidas if aba in xls.sheet_names}
    except Exception as e:
        print(f"Erro ao carregar o arquivo Excel: {e}")
        return {}

def formatar_dados_para_contexto(dados):
    """Formata os dados do Excel em uma string para a IA."""
    contexto = f"Olá, {nome}! Abaixo estão os dados disponíveis:\n"
    for aba, df in dados.items():
        contexto += f"### Aba: {aba}\n"
        contexto += df.to_string(index=False)
        contexto += "\n"
    return contexto[:5000]  # Limite de caracteres para evitar erro 400

def consultar_deepseek(pergunta, contexto):
    """Consulta a IA DeepSeek, verificando primeiro se a resposta já existe no histórico."""
    historico = carregar_historico()
    if pergunta in historico:
        return historico[pergunta]  # Retorna resposta do histórico
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": f"Você é Guardian, um assistente útil que responde com base nos dados dos PoPs. O usuário atual é {nome}. Você pode consultar o nome do pessoal que trabalha neste setor de infraestrutura, ali estará listado as funções de cada um. Eu sou o Vicenzo, seu programador e membro da equipe dos PoPs."},
                {"role": "user", "content": contexto},
                {"role": "user", "content": f"Pergunta: {pergunta}"}
            ],
            temperature=0.7,
            max_tokens=500,
            stream=False
        )
        resposta = response.choices[0].message.content
        historico[pergunta] = resposta  # Salva no histórico
        salvar_historico(historico)
        return resposta
    except Exception as e:
        return f"Erro ao consultar a IA: {e}"

def main():
    arquivo_excel = "C:\\Users\\vicenzo-minossi\\OneDrive - Governo do Estado do Rio Grande do Sul\\POPs - Arquivos de Moises Gustavo Brum\\DIF-PIR Execução POPS.xlsx"
    dados = carregar_dados_excel(arquivo_excel)
    if not dados:
        print("Erro ao carregar os dados do Excel.")
        return
    contexto = formatar_dados_para_contexto(dados)
    
    while True:
        pergunta = input("Digite sua pergunta (ou 'sair' para encerrar): ")
        if pergunta.lower() == "sair":
            print('🤖: Até logo...')
            break
        resposta = consultar_deepseek(pergunta, contexto)
        print(f"\n🤖:", resposta, "\n")

if __name__ == "__main__":
    main()

#interface no tkinter, fazer um programa executável com servidores 
