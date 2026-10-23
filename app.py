import os
import io
import json
import uuid
import html as html_lib
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components

# Precisa ser o primeiro comando do Streamlit
st.set_page_config(
    page_title="OssBot - Assistente de Jiu-Jitsu",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Biblioteca de áudio
try:
    from gtts import gTTS
    tem_gtts_lib = True
except Exception:
    tem_gtts_lib = False

MODELO = "llama-3.3-70b-versatile"

# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------
def esc(texto):
    """Escapa o texto digitado pelo usuário para não quebrar o HTML."""
    return html_lib.escape(str(texto)).replace("\n", "<br>")


def mostrar_html(codigo):
    """Mostra HTML sem linhas em branco/indentação (evita virar bloco de código)."""
    limpo = " ".join(linha.strip() for linha in codigo.splitlines() if linha.strip())
    st.markdown(limpo, unsafe_allow_html=True)


def gerar_audio_local(texto):
    if not tem_gtts_lib:
        return b""
    limpo = texto.replace("*", "").replace("#", "").replace("|", " ").replace("_", " ")
    buffer = io.BytesIO()
    try:
        gTTS(text=limpo, lang="pt", slow=False).write_to_fp(buffer)
        return buffer.getvalue()
    except Exception:
        return b""


# Chave de API da Groq definitiva
GROQ_API_KEY = "Gsk_iIrY2RYUqeoOw6Hz6oO4WGdyb3FYOHQJ3BY0pvsUDUlYOZfeiFfb"


def obter_chave_groq():
    return GROQ_API_KEY


@st.cache_resource
def criar_cliente_groq(chave):
    from groq import Groq
    return Groq(api_key=chave)


# ---------------------------------------------------------------------------
# Dados por usuário
# ---------------------------------------------------------------------------
PASTA_DADOS = os.path.dirname(os.path.abspath(__file__))

CAMPOS = [
    "conversas", "historico_lutas", "dinamic_kids_custom", "flashcards_pressao",
    "alunos_graduacao", "cards_vitoria", "cursos_interativos",
    "lista_alunos_academia", "notas_kimono",
]


def dados_vazios():
    return {campo: ({} if campo == "conversas" else []) for campo in CAMPOS}


def obter_caminho_usuario(nome_usuario):
    nome_limpo = "".join(c if c.isalnum() else "_" for c in nome_usuario.lower()).strip("_")
    return os.path.join(PASTA_DADOS, f"usuario_{nome_limpo}.json")


def carregar_dados_usuario(nome_usuario):
    dados = dados_vazios()
    caminho = obter_caminho_usuario(nome_usuario)
    try:
        if os.path.exists(caminho):
            with open(caminho, "r", encoding="utf-8") as f:
                dados.update(json.load(f))
    except Exception:
        pass
    return dados


def salvar_dados_usuario(nome_usuario, dados):
    caminho = obter_caminho_usuario(nome_usuario)
    try:
        tmp = caminho + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        os.replace(tmp, caminho)
    except Exception:
        pass


def salvar_tudo():
    usuario = st.session_state.get("usuario_atual")
    if not usuario:
        return
    salvar_dados_usuario(usuario, {campo: st.session_state[campo] for campo in CAMPOS})


SAUDACAO_PADRAO = (
    "Olá, OSS! 🥋 Como posso te ajudar hoje? Posso criar um cronograma de aula, "
    "montar uma dinâmica para a turma kids, tirar uma dúvida técnica ou preparar uma "
    "estratégia para campeonato."
)


def iniciar_nova_conversa():
    st.session_state.historico = [{"role": "assistant", "content": SAUDACAO_PADRAO}]
    st.session_state.conversa_id = uuid.uuid4().hex
    st.session_state.titulo = ""
    st.session_state.titulo_ia = False


def salvar_conversa_atual():
    primeira = next((m["content"] for m in st.session_state.historico if m["role"] == "user"), None)
    if primeira is None:
        return
    if not st.session_state.titulo:
        st.session_state.titulo = primeira.strip().replace("\n", " ")[:40]
    st.session_state.conversas[st.session_state.conversa_id] = {
        "titulo": st.session_state.titulo or "Nova conversa",
        "titulo_ia": st.session_state.titulo_ia,
        "atualizada": datetime.now().isoformat(timespec="seconds"),
        "mensagens": st.session_state.historico,
    }
    salvar_tudo()


def abrir_conversa(cid):
    conv = st.session_state.conversas.get(cid)
    if conv:
        st.session_state.historico = conv["mensagens"]
        st.session_state.conversa_id = cid
        st.session_state.titulo = conv["titulo"]
        st.session_state.titulo_ia = conv.get("titulo_ia", True)


def apagar_conversa(cid):
    if cid in st.session_state.conversas:
        del st.session_state.conversas[cid]
        salvar_tudo()
    if cid == st.session_state.conversa_id:
        iniciar_nova_conversa()


def carregar_usuario(nome):
    dados = carregar_dados_usuario(nome)
    st.session_state.usuario_atual = nome
    for campo in CAMPOS:
        st.session_state[campo] = dados[campo]
    if st.session_state.conversas:
        ultimo_id = max(st.session_state.conversas,
                        key=lambda c: st.session_state.conversas[c].get("atualizada", ""))
        abrir_conversa(ultimo_id)
    else:
        iniciar_nova_conversa()


def gerar_atalhos_inteligentes(conversas):
    palavras_chave = {}
    termos_comuns = {"como", "para", "qual", "uma", "com", "que", "dos", "das", "por",
                     "sobre", "mais", "isso", "ele", "ela", "quero", "dicas"}
    for conv in conversas.values():
        for m in conv.get("mensagens", []):
            if m["role"] == "user":
                for palavra in m["content"].lower().split():
                    p_limpa = "".join(c for c in palavra if c.isalnum())
                    if len(p_limpa) > 3 and p_limpa not in termos_comuns:
                        palavras_chave[p_limpa] = palavras_chave.get(p_limpa, 0) + 1
    ordenados = sorted(palavras_chave.items(), key=lambda x: x[1], reverse=True)
    top = [item[0].capitalize() for item in ordenados[:4]]
    return top if top else ["Guarda", "Raspagem", "Campeonato", "Kids"]


def definir_atalho(atalho):
    st.session_state.atalho_clicado = f"Quero dicas sobre: {atalho}"


# ---------------------------------------------------------------------------
# Funções do Modo Luta
# ---------------------------------------------------------------------------
def somar(lado, campo, valor):
    st.session_state[f"{campo}_{lado}"] += valor


def definir_tempo():
    st.session_state.tempo_segundos = st.session_state.select_tempo * 60
    st.session_state.cronometro_rodando = False


def iniciar_cronometro():
    if st.session_state.tempo_segundos > 0:
        st.session_state.cronometro_rodando = True


def pausar_cronometro():
    st.session_state.cronometro_rodando = False


def zerar_luta():
    st.session_state.cronometro_rodando = False
    st.session_state.tempo_segundos = st.session_state.select_tempo * 60
    for lado in ("a", "b"):
        st.session_state[f"pts_{lado}"] = 0
        st.session_state[f"vant_{lado}"] = 0
        st.session_state[f"pun_{lado}"] = 0


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
CSS = """
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { background-color: #121212 !important; }
[data-testid="stSidebar"], [data-testid="stSidebar"] > div { background-color: #181818 !important; }
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp p, .stApp li, .stApp label, .stApp summary { color: #ffffff; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * { color: #aaaaaa !important; }

div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="textarea"], div[data-baseweb="select"] > div { background-color: #1e1e1e !important; border-color: #ff4d4d !important; border-radius: 8px !important; }
div[data-baseweb="input"] input, div[data-baseweb="base-input"] input, div[data-baseweb="textarea"] textarea, div[data-baseweb="base-input"] textarea, input, textarea { background-color: #1e1e1e !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; caret-color: #ffffff !important; font-weight: bold !important; }
input::placeholder, textarea::placeholder { color: #9ca3af !important; -webkit-text-fill-color: #9ca3af !important; opacity: 1 !important; }
input:-webkit-autofill { -webkit-box-shadow: 0 0 0 1000px #1e1e1e inset !important; -webkit-text-fill-color: #ffffff !important; }
div[data-baseweb="select"] * { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; }
div[data-baseweb="select"] svg { fill: #ffffff !important; }

div[data-baseweb="popover"], div[data-baseweb="popover"] > div, ul[role="listbox"], [data-baseweb="menu"] { background-color: #1e1e1e !important; }
div[data-baseweb="popover"] li, div[data-baseweb="popover"] li *, ul[role="listbox"] li { background-color: #1e1e1e !important; color: #ffffff !important; }
div[data-baseweb="popover"] li:hover, ul[role="listbox"] li:hover { background-color: #3a1f1f !important; }
div[data-baseweb="calendar"], div[data-baseweb="calendar"] * { background-color: #1e1e1e !important; color: #ffffff !important; }
div[data-baseweb="calendar"] [aria-selected="true"] { background-color: #ff4d4d !important; }

[data-testid="stNumberInput"] button { background-color: #2a2a2a !important; color: #ffffff !important; border: none !important; }

[data-testid="stFileUploaderDropzone"], [data-testid="stFileUploader"] section { background-color: #1e1e1e !important; border: 2px dashed #ff4d4d !important; border-radius: 10px !important; }
[data-testid="stFileUploader"] * { color: #ffffff !important; }
[data-testid="stFileUploader"] svg { fill: #ffffff !important; }
[data-testid="stFileUploader"] button { background-color: #ff4d4d !important; border: 2px solid #ffffff !important; }

[data-testid="stAudioInput"], [data-testid="stCameraInput"] { background-color: #1e1e1e !important; border-radius: 10px !important; padding: 15px; border: 1px solid #444444; }
[data-testid="stCameraInput"] button { background-color: #ff4d4d !important; color: #ffffff !important; }

[data-testid="stChatInput"] { background-color: #1e1e1e !important; border-radius: 10px !important; border: 2px solid #ff4d4d !important; }
[data-testid="stChatInput"] > div, [data-testid="stChatInput"] div[data-baseweb="textarea"] { background-color: #1e1e1e !important; border: none !important; }
[data-testid="stChatInput"] textarea { font-size: 16px !important; }
[data-testid="stChatInput"] button { background-color: #ff4d4d !important; color: #ffffff !important; }
[data-testid="stChatMessage"] { background-color: #1a1a1a !important; border-radius: 10px !important; }

.stButton > button, div[data-testid="stFormSubmitButton"] > button { border-radius: 10px !important; font-weight: bold !important; background-color: #ff4d4d !important; color: #ffffff !important; border: 2px solid #ffffff !important; }
.stButton > button p, div[data-testid="stFormSubmitButton"] > button p { color: #ffffff !important; }
.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover { background-color: #e60000 !important; color: #ffffff !important; }

[data-testid="stExpander"] { background-color: #1e1e1e !important; border: 1px solid #444444 !important; border-radius: 10px !important; }
[data-testid="stForm"] { border: 1px solid #444444 !important; border-radius: 12px !important; }

.placar-box, .nutri-box, .camp-box, .curso-box, .kids-box { color: #ffffff; border-radius: 15px; padding: 20px; margin-bottom: 20px; }
.placar-box { background-color: #1e1e1e; border: 2px solid #ff4d4d; text-align: center; }
.placar-numero { font-size: 50px; font-weight: bold; color: #00ffcc; }
.nutri-box { background-color: #1e293b; border: 2px solid #00ffcc; }
.camp-box { background-color: #1e1b4b; border: 2px solid #ff4d4d; }
.curso-box { background-color: #0f172a; border: 2px solid #38bdf8; }
.kids-box { background-color: #451a03; border: 2px solid #fbbf24; }
"""
css_compacto = " ".join(CSS.split())
st.markdown(f"<style>{css_compacto}</style>", unsafe_allow_html=True)

# Botões flutuantes para subir e descer a página
components.html("""
<script>
const doc = window.parent.document;
const janela = window.parent;

['botoes-rolagem', 'estilo-botoes-rolagem'].forEach(function(id) {
  const antigo = doc.getElementById(id);
  if (antigo) antigo.remove();
});

const estilo = document.createElement('style');
estilo.id = 'estilo-botoes-rolagem';
estilo.innerHTML = `
  #botoes-rolagem { position: fixed; right: 20px; bottom: 110px; display: flex; flex-direction: column; gap: 12px; z-index: 999999; }
  #botoes-rolagem button { width: 64px; height: 64px; font-size: 28px; font-weight: bold; color: #ffffff; background-color: #e60000; border: 2px solid #ffffff; border-radius: 50%; cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.6); }
  #botoes-rolagem button:hover { background-color: #ff4d4d; }
`;
doc.head.appendChild(estilo);

function rolar(direcao) {
  doc.querySelectorAll('*').forEach(function(el) {
    if (el.closest('[data-testid="stSidebar"]')) return;
    const e = janela.getComputedStyle(el);
    const rola = (e.overflowY === 'auto' || e.overflowY === 'scroll');
    if (rola && el.scrollHeight > el.clientHeight + 20) {
      el.scrollTop = (direcao === 'cima') ? 0 : el.scrollHeight;
    }
  });
  doc.documentElement.scrollTop = (direcao === 'cima') ? 0 : doc.documentElement.scrollHeight;
  doc.body.scrollTop = (direcao === 'cima') ? 0 : doc.body.scrollHeight;
}

const caixa = document.createElement('div');
caixa.id = 'botoes-rolagem';

const subir = document.createElement('button');
subir.type = 'button'; subir.title = 'Subir'; subir.textContent = '▲';
subir.addEventListener('click', function() { rolar('cima'); });

const descer = document.createElement('button');
descer.type = 'button'; descer.title = 'Descer'; descer.textContent = '▼';
descer.addEventListener('click', function() { rolar('baixo'); });

caixa.appendChild(subir);
caixa.appendChild(descer);
doc.body.appendChild(caixa);
</script>
""", height=0)

# ---------------------------------------------------------------------------
# Barra lateral
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🥋 Identificação")
    st.session_state.setdefault("input_usuario", "Henry Cesar")
    usuario_input = st.text_input(
        "Digite seu Nome e Sobrenome:",
        placeholder="Ex: Henry Cesar",
        key="input_usuario",
    ).strip() or "Visitante"

    if st.session_state.get("usuario_atual") != usuario_input:
        carregar_usuario(usuario_input)

    st.divider()
    st.markdown("## 🥋 Minhas conversas")
    st.button("➕ Nova conversa", on_click=iniciar_nova_conversa, key="btn_nova_conversa",
              use_container_width=True)

    busca = st.text_input("🔍 Pesquisar", placeholder="Ex.: guarda", key="busca_conversas").strip().lower()
    st.divider()

    conversas = st.session_state.conversas
    ids = sorted(conversas, key=lambda c: conversas[c].get("atualizada", ""), reverse=True)

    mostradas = 0
    for cid in ids:
        conv = conversas[cid]
        if busca:
            texto_total = conv["titulo"].lower() + " " + " ".join(m["content"].lower() for m in conv["mensagens"])
            if busca not in texto_total:
                continue
        mostradas += 1
        atual = cid == st.session_state.conversa_id
        col_a, col_b = st.columns([5, 1])
        with col_a:
            st.button(("▶ " if atual else "") + conv["titulo"], key=f"abrir_{cid}",
                      on_click=abrir_conversa, args=(cid,), use_container_width=True)
        with col_b:
            st.button("🗑️", key=f"apagar_{cid}", on_click=apagar_conversa, args=(cid,),
                      help="Apagar esta conversa")

    if mostradas == 0:
        st.caption("Nenhuma conversa encontrada." if busca else "Suas conversas vão aparecer aqui. 🥋")

# ---------------------------------------------------------------------------
# Estados auxiliares
# ---------------------------------------------------------------------------
for chave, valor in {
    "atalho_clicado": None,
    "pts_a": 0, "vant_a": 0, "pun_a": 0,
    "pts_b": 0, "vant_b": 0, "pun_b": 0,
    "tempo_segundos": 300, "cronometro_rodando": False,
}.items():
    st.session_state.setdefault(chave, valor)

# ---------------------------------------------------------------------------
# Cabeçalho
# ---------------------------------------------------------------------------
col_esq, col_centro, col_dir = st.columns([1.2, 2.6, 1.2])
with col_esq:
    st.image("https://images.unsplash.com/photo-1517838277536-f5f99be501cd?q=80&w=600&auto=format&fit=crop",
             caption="Técnica e Combate", use_container_width=True)
with col_centro:
    st.markdown("<h1 style='text-align: center; color: #ff4d4d;'>🥋 OssBot App</h1>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center; color: #00ffcc;'>Usuário: {esc(st.session_state.usuario_atual)}</h4>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #aaaaaa;'>O seu Assistente de Jiu-Jitsu (PWA)</h3>", unsafe_allow_html=True)
with col_dir:
    st.image("https://images.unsplash.com/photo-1555597673-b21d5c935865?q=80&w=600&auto=format&fit=crop",
             caption="Faixa Preta — Tradição", use_container_width=True)

st.divider()

(aba_chat, aba_modo_luta, aba_historico_lutas, aba_nutricao, aba_camp, aba_cursos, aba_kids,
 aba_drills, aba_pressao, aba_grad, aba_kimono, aba_card, aba_caderneta, aba_chaves) = st.tabs([
    "💬 Chat IA", "🤼 Luta", "📜 Histórico", "🥗 Nutrição", "🏆 Camp", "📚 Cursos", "👶 Kids",
    "⏱️ Drills", "🧠 Pressão", "🥇 Graduação", "🥋 Kimono", "📸 Card", "📇 Alunos", "⏱️ Chaves",
])

# ===========================================================================
# ABA 1: CHAT COM IA
# ===========================================================================
def mostrar_historico():
    for i, mensagem in enumerate(st.session_state.historico):
        with st.chat_message(mensagem["role"]):
            st.markdown(mensagem["content"])
            if mensagem["role"] == "assistant" and st.button("🔊 Ouvir", key=f"ouvir_{i}"):
                ab = gerar_audio_local(mensagem["content"])
                if ab:
                    st.audio(ab, format="audio/mp3")
                else:
                    st.caption("Áudio indisponível (instale a biblioteca gTTS e verifique a internet).")


with aba_chat:
    st.markdown("### ⚙️ Escolha o Modo de Atendimento")
    modo_selecionado = st.radio(
        "Como você quer que o OssBot responda?",
        [
            "🥋 Aluno / Competidor (Online)",
            "👶 Professor / Turma Kids (Online)",
            "📡 Modo Offline (Economizar Dados Móveis / Sem Internet)",
        ],
        index=0, key="modo_atendimento",
    )

    if "Modo Offline" in modo_selecionado:
        st.info("📡 **Modo Offline Ativado!** Nenhuma requisição externa será feita nesta aba. "
                "Você pode usar 100% das outras abas sem gastar nada da sua rede!")
        st.divider()
        mostrar_historico()
    else:
        client = None
        chave_groq = obter_chave_groq()
        if chave_groq:
            try:
                client = criar_cliente_groq(chave_groq)
            except Exception:
                client = None

        if "Kids" in modo_selecionado:
            system_prompt = ("Você é o OssBot, assistente especialista em BJJ para professores de turmas kids. "
                             "Sugira dinâmicas lúdicas, seguras e divertidas. Use termos como OSS, guarda, raspagem.")
        else:
            system_prompt = ("Você é o OssBot, assistente especialista em BJJ focado em atletas e professores. "
                             "Use termos como OSS, guarda, raspagem.")

        st.divider()
        st.markdown("### ⚡ Atalhos Inteligentes")
        atalhos_personalizados = gerar_atalhos_inteligentes(st.session_state.conversas)
        cols_atalhos = st.columns(len(atalhos_personalizados))
        for idx, atalho in enumerate(atalhos_personalizados):
            with cols_atalhos[idx]:
                st.button(f"📌 {atalho}", key=f"atalho_{idx}", use_container_width=True,
                          on_click=definir_atalho, args=(atalho,))

        st.divider()

        pergunta_texto = st.chat_input("Digite sua dúvida...")
        atalho_pendente = st.session_state.pop("atalho_clicado", None)
        texto_para_enviar = pergunta_texto or atalho_pendente

        if texto_para_enviar:
            st.session_state.historico.append({"role": "user", "content": texto_para_enviar})
            salvar_conversa_atual()

        mostrar_historico()

        if texto_para_enviar:
            if not client:
                st.warning("⚠️ Sem rede para a IA. Mude para a opção 'Modo Offline'!")
            else:
                with st.chat_message("assistant"):
                    with st.spinner("OssBot pensando... OSS! 🥋"):
                        try:
                            mensagens = [{"role": "system", "content": system_prompt}]
                            for m in st.session_state.historico[-20:]:
                                mensagens.append({"role": m["role"], "content": m["content"]})
                            
                            res = client.chat.completions.create(
                                model=MODELO, 
                                messages=mensagens, 
                                temperature=0.7
                            )
                            resp = res.choices[0].message.content
                            st.markdown(resp)
                            st.session_state.historico.append({"role": "assistant", "content": resp})
                            salvar_conversa_atual()
                        except Exception as e:
                            erro_str = str(e)
                            if "401" in erro_str or "Invalid API Key" in erro_str:
                                st.warning("⚠️ Chave da API da Groq inválida ou expirada (Erro 401). Ative o 'Modo Offline' acima para usar todas as outras funções sem travar!")
                            else:
                                st.warning(f"Erro na IA: {e}")

# ===========================================================================
# ABA 2: MODO LUTA
# ===========================================================================
def bloco_placar(lado, nome, emoji, cor):
    pts = st.session_state[f"pts_{lado}"]
    vant = st.session_state[f"vant_{lado}"]
    pun = st.session_state[f"pun_{lado}"]
    mostrar_html(f"""
    <div class='placar-box'>
        <h2 style='color: {cor};'>{emoji} {esc(nome)}</h2>
        <div class='placar-numero'>{pts} Pts</div>
        <p>Vantagens: {vant} | Punições: {pun}</p>
    </div>
    """)
    cols = st.columns(5)
    botoes = [("+2 Pts", "pts", 2), ("+3 Pts", "pts", 3), ("+4 Pts", "pts", 4),
              ("+Vant", "vant", 1), ("+Pun", "pun", 1)]
    for col, (rotulo, campo, valor) in zip(cols, botoes):
        col.button(rotulo, key=f"{lado}_{campo}_{valor}", on_click=somar,
                   args=(lado, campo, valor), use_container_width=True)


with aba_modo_luta:
    st.markdown("<h2 style='text-align: center; color: #ff4d4d;'>⏱️ PLACAR & CRONÔMETRO DE LUTA</h2>", unsafe_allow_html=True)

    col_l1, col_l2 = st.columns(2)
    with col_l1:
        nome_atleta_a = st.text_input("🔵 Atleta 1 (Azul/Preto):", value="Atleta Azul", key="nome_a")
    with col_l2:
        nome_atleta_b = st.text_input("⚪ Atleta 2 (Branco):", value="Atleta Branco", key="nome_b")
    st.divider()

    col_t1, col_t2, col_t3 = st.columns([1, 2, 1])
    with col_t2:
        st.selectbox("Tempo do Rola:", list(range(1, 11)), index=4, key="select_tempo",
                     format_func=lambda m: f"{m} min", on_change=definir_tempo)

        @st.fragment(run_every=1 if st.session_state.cronometro_rodando else None)
        def painel_cronometro():
            if st.session_state.cronometro_rodando:
                if st.session_state.tempo_segundos > 0:
                    st.session_state.tempo_segundos -= 1
                if st.session_state.tempo_segundos <= 0:
                    st.session_state.cronometro_rodando = False
                    st.rerun(scope="app")
            mins, segs = divmod(st.session_state.tempo_segundos, 60)
            st.markdown(
                f"<h1 style='text-align: center; font-size: 70px; color: #ff4d4d;'>{mins:02d}:{segs:02d}</h1>",
                unsafe_allow_html=True,
            )

        painel_cronometro()

        bc1, bc2, bc3 = st.columns(3)
        bc1.button("▶️ INICIAR", use_container_width=True, key="btn_iniciar_luta", on_click=iniciar_cronometro)
        bc2.button("⏸️ PAUSAR", use_container_width=True, key="btn_pausar_luta", on_click=pausar_cronometro)
        bc3.button("🔄 ZERAR", use_container_width=True, key="btn_zerar_luta", on_click=zerar_luta)

    st.divider()
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        bloco_placar("a", nome_atleta_a, "🔵", "#4da6ff")
    with col_p2:
        bloco_placar("b", nome_atleta_b, "⚪", "#ffffff")

    st.divider()
    if st.button("💾 SALVAR RESULTADO DA LUTA", use_container_width=True, key="btn_salvar_luta"):
        st.session_state.historico_lutas.append({
            "data": datetime.now().strftime("%d/%m/%Y - %H:%M"),
            "atleta_a": nome_atleta_a, "pts_a": st.session_state.pts_a,
            "vant_a": st.session_state.vant_a, "pun_a": st.session_state.pun_a,
            "atleta_b": nome_atleta_b, "pts_b": st.session_state.pts_b,
            "vant_b": st.session_state.vant_b, "pun_b": st.session_state.pun_b,
        })
        salvar_tudo()
        st.success("✅ Luta salva na memória!")

# ===========================================================================
# ABA 3: HISTÓRICO DE LUTAS
# ===========================================================================
with aba_historico_lutas:
    st.markdown("### 📜 Lutas Registradas")
    if not st.session_state.historico_lutas:
        st.info("Nenhuma luta registrada ainda.")
    else:
        for luta in reversed(st.session_state.historico_lutas):
            with st.expander(f"🥋 {luta['data']} - {luta['atleta_a']} vs {luta['atleta_b']}"):
                st.write(f"🔵 **{luta['atleta_a']}**: {luta['pts_a']} Pts ({luta['vant_a']}V/{luta['pun_a']}P) | "
                         f"⚪ **{luta['atleta_b']}**: {luta['pts_b']} Pts ({luta['vant_b']}V/{l
