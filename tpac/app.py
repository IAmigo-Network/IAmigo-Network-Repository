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
# Painel principal
# ---------------------------------------------------------------------------

def tela_painel():
    usuario = st.session_state.usuario

    st.title("🤖 IAmigo")
    st.markdown(f"👤 **Usuário:** {usuario}  |  🤖 IAmigo Online")
    st.subheader("Como posso te ajudar?")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Organizar minhas tarefas", use_container_width=True):
            ir_para("tarefas_diarias")
            st.rerun()
        if st.button("🤖 Conversar com o IAmigo", use_container_width=True):
            ir_para("ia_chat")
            st.rerun()
    with col2:
        if st.button("📚 Planejar meus estudos", use_container_width=True):
            ir_para("tarefas_educacionais")
            st.rerun()
        if st.button("👋 Encerrar por agora", use_container_width=True):
            st.session_state.usuario = None
            ir_para("inicio")
            st.rerun()


# ---------------------------------------------------------------------------
# Gerenciamento de tarefas (diárias ou educacionais)
# ---------------------------------------------------------------------------

def tela_tarefas(chave: str, titulo: str):
    usuario = st.session_state.usuario
    dados = st.session_state.dados
    tarefas = dados[usuario][chave]

    st.title(titulo)

    if st.button("⬅ Voltar ao painel"):
        ir_para("painel")
        st.rerun()

    st.divider()

    if not tarefas:
        st.write("[Nenhuma tarefa pendente.]")

    for idx, t in enumerate(tarefas):
        with st.container(border=True):
            col_check, col_titulo, col_ia = st.columns([1, 6, 3])

            with col_check:
                concluida = st.checkbox(
                    "Feito", value=t["concluida"], key=f"check_{chave}_{idx}",
                    label_visibility="collapsed",
                )
                if concluida != t["concluida"]:
                    core_tarefas.alternar_status_tarefa(dados, usuario, chave, idx)
                    recarregar_dados()
                    st.rerun()

            with col_titulo:
                texto = f"~~{t['titulo']}~~" if t["concluida"] else t["titulo"]
                st.markdown(texto)
                for p in t.get("passos", []):
                    st.markdown(f"&nbsp;&nbsp;&nbsp;○ {p['texto']}", unsafe_allow_html=True)

            with col_ia:
                if st.button("🤖 Desmembrar com IA", key=f"ia_{chave}_{idx}"):
                    st.session_state["ia_sugestao_idx"] = idx
                    st.session_state["ia_sugestao_chave"] = chave
                    with st.spinner("Pensando nos passos..."):
                        st.session_state["ia_sugestao_passos"] = ia_service.gerar_passos_tarefa(t["titulo"])
                    st.rerun()

            # Se essa é a tarefa com sugestão de IA pendente, mostra abaixo dela
            if (
                st.session_state.get("ia_sugestao_idx") == idx
                and st.session_state.get("ia_sugestao_chave") == chave
            ):
                st.info("🤖 Passos sugeridos pela IA:")
                for i, p in enumerate(st.session_state["ia_sugestao_passos"], 1):
                    st.write(f"{i}. {p}")

                col_aceitar, col_recusar = st.columns(2)
                with col_aceitar:
                    if st.button("✅ Aceitar sugestão", key=f"aceitar_{chave}_{idx}"):
                        core_tarefas.injetar_passos_ia(
                            dados, usuario, chave, idx, st.session_state["ia_sugestao_passos"]
                        )
                        recarregar_dados()
                        del st.session_state["ia_sugestao_idx"]
                        del st.session_state["ia_sugestao_chave"]
                        del st.session_state["ia_sugestao_passos"]
                        st.rerun()
                with col_recusar:
                    if st.button("❌ Descartar", key=f"recusar_{chave}_{idx}"):
                        del st.session_state["ia_sugestao_idx"]
                        del st.session_state["ia_sugestao_chave"]
                        del st.session_state["ia_sugestao_passos"]
                        st.rerun()

    st.divider()
    with st.form(f"form_nova_tarefa_{chave}", clear_on_submit=True):
        nova_tarefa = st.text_input("Nome da nova tarefa")
        if st.form_submit_button("➕ Criar tarefa"):
            if nova_tarefa.strip():
                core_tarefas.adicionar_tarefa(dados, usuario, chave, nova_tarefa.strip())
                recarregar_dados()
                st.rerun()


# ---------------------------------------------------------------------------
# Chat com a IA
# ---------------------------------------------------------------------------

def tela_ia_chat():
    usuario = st.session_state.usuario
    dados = st.session_state.dados
    estilo = dados[usuario]["preferencias"]["estilo_instrucao"]

    st.title("🤖 Assistente de IA para TPAC")
    st.caption("Peça ajuda para simplificar enunciados, organizar rotinas ou tirar dúvidas.")

    if st.button("⬅ Voltar ao painel"):
        ir_para("painel")
        st.rerun()

    if "chat_historico" not in st.session_state:
        st.session_state.chat_historico = []

    for pergunta, respostas in st.session_state.chat_historico:
        with st.chat_message("user"):
            st.write(pergunta)
        with st.chat_message("assistant"):
            for linha in respostas:
                st.write(f"- {linha}")

    pergunta = st.chat_input("Digite sua pergunta...")
    if pergunta:
        with st.chat_message("user"):
            st.write(pergunta)
        with st.chat_message("assistant"):
            with st.spinner(f"Processando (Modo {estilo.upper()})..."):
                respostas = ia_service.obter_resposta_ia(pergunta, estilo)
            for linha in respostas:
                st.write(f"- {linha}")
        st.session_state.chat_historico.append((pergunta, respostas))


# ---------------------------------------------------------------------------
# Roteador principal
# ---------------------------------------------------------------------------

def main():
    inicializar_estado()

    tela = st.session_state.tela

    if tela == "inicio":
        tela_inicio()
    elif tela == "painel":
        tela_painel()
    elif tela == "tarefas_diarias":
        tela_tarefas("tarefas_diarias", "📝 Rotina Diária")
    elif tela == "tarefas_educacionais":
        tela_tarefas("tarefas_educacionais", "📚 Estudos e Educação")
    elif tela == "ia_chat":
        tela_ia_chat()


if __name__ == "__main__":
    main()
