import random
import streamlit as st

from data.data_manager import carregar_dados, salvar_dados
import core.tarefas as core_tarefas
import core.ia_service as ia_service

st.set_page_config(page_title="IAmigo - TPAC", page_icon="🤖", layout="centered")

FRASES = [
    "😊 Que bom te ver por aqui!",
    "🚀 Vamos organizar o dia juntos?",
    "📚 Um passo de cada vez.",
    "✨ Pequenos avanços também são conquistas.",
    "🎯 Vamos focar no que importa hoje.",
    "🌟 Você está indo muito bem!",
    "🤖 Estou pronto para ajudar.",
    "💡 Toda tarefa começa com um primeiro passo.",
    "📝 Vamos colocar as ideias em ordem?",
    "😄 Pronto para mais um dia produtivo?",
]


# ---------------------------------------------------------------------------
# Estado da sessão
# ---------------------------------------------------------------------------

def inicializar_estado():
    if "dados" not in st.session_state:
        st.session_state.dados = carregar_dados()
    if "tela" not in st.session_state:
        st.session_state.tela = "inicio"
    if "usuario" not in st.session_state:
        st.session_state.usuario = None
    if "frase" not in st.session_state:
        st.session_state.frase = random.choice(FRASES)


def recarregar_dados():
    st.session_state.dados = carregar_dados()


def ir_para(tela: str):
    st.session_state.tela = tela


# ---------------------------------------------------------------------------
# Tela inicial (escolher ou criar perfil)
# ---------------------------------------------------------------------------

def tela_inicio():
    st.title("🤖 IAmigo")
    st.caption("Seu amigo para organizar tarefas e estudos")
    st.info(st.session_state.frase)

    dados = st.session_state.dados

    st.subheader("Continuar com meu perfil")
    if not dados:
        st.write("Nenhum perfil salvo ainda. Crie o primeiro abaixo! 👇")
    else:
        nomes = list(dados.keys())
        escolhido = st.selectbox("Qual perfil deseja acessar?", nomes)
        if st.button("Entrar", type="primary"):
            st.session_state.usuario = escolhido
            ir_para("painel")
            st.rerun()

    st.divider()
    st.subheader("Criar um novo perfil")
    with st.form("form_novo_perfil"):
        nome = st.text_input("Como você gostaria de ser chamado(a)?").strip()
        estilo_opcao = st.radio(
            "Quando você precisa fazer algo, o que funciona melhor pra você?",
            ["Instruções curtas e sem enrolação", "Um guia mais detalhado, explicando cada etapa"],
        )
        criar = st.form_submit_button("Criar perfil")

        if criar:
            if not nome:
                st.error("Não consegui identificar seu nome. Tente novamente.")
            elif nome in dados:
                st.error(f"Já encontrei um cadastro com o nome '{nome}'. Escolha outro nome.")
            else:
                estilo = "direto" if estilo_opcao.startswith("Instruções curtas") else "detalhado"
                dados[nome] = {
                    "preferencias": {"estilo_instrucao": estilo},
                    "tarefas_diarias": [],
                    "tarefas_educacionais": [],
                }
                salvar_dados(dados)
                recarregar_dados()
                st.success(f"Tudo certo, {nome}! Seu perfil foi criado.")
                st.session_state.usuario = nome
                ir_para("painel")
                st.rerun()


# ---------------------------------------------------------------------------
# Roteador principal
# ---------------------------------------------------------------------------

def main():
    inicializar_estado()

    if st.session_state.tela == "inicio":
        tela_inicio()
    else:
        st.write("As próximas telas (painel, tarefas e IA) chegam na próxima etapa.")
        if st.button("⬅ Voltar ao início"):
            st.session_state.usuario = None
            ir_para("inicio")
            st.rerun()


if __name__ == "__main__":
    main()
