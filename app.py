import os
import io
import json
import base64
import html as html_lib
from datetime import datetime, date

import streamlit as st
import streamlit.components.v1 as components

# Configuração da página
st.set_page_config(
    page_title="OssBot Pro - Assistente de Jiu-Jitsu",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# E-mail Master (Comando Fodão / Administrador Supremo)
EMAIL_ADMIN_MASTER = "henry.cesaraguiar@gmail.com"

# Biblioteca de áudio
try:
    from gtts import gTTS
    tem_gtts_lib = True
except Exception:
    tem_gtts_lib = False

# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------
def esc(texto):
    return html_lib.escape(str(texto)).replace("\n", "<br>")


def mostrar_html(codigo):
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


# ---------------------------------------------------------------------------
# Sistema de Autenticação e Perfis por Usuário
# ---------------------------------------------------------------------------
PASTA_DADOS = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_BANCO_USUARIOS = os.path.join(PASTA_DADOS, "banco_usuarios.json")

CAMPOS = [
    "historico_lutas", "dinamic_kids_custom", "flashcards_pressao",
    "alunos_graduacao", "cards_vitoria", "cursos_interativos",
    "lista_alunos_academia", "notas_kimono", "cronogramas_aulas", "foco_recuperacao",
    "perfil_nome", "perfil_faixa", "perfil_graus", "perfil_academia", 
    "perfil_peso", "perfil_estilo", "perfil_status", "perfil_foto_b64"
]


def carregar_banco_usuarios():
    if os.path.exists(ARQUIVO_BANCO_USUARIOS):
        try:
            with open(ARQUIVO_BANCO_USUARIOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def salvar_banco_usuarios(usuarios):
    try:
        tmp = ARQUIVO_BANCO_USUARIOS + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(usuarios, f, ensure_ascii=False, indent=2)
        os.replace(tmp, ARQUIVO_BANCO_USUARIOS)
    except Exception:
        pass


def dados_vazios(email=""):
    nome_padrao = email.split("@")[0].title() if email else "Atleta"
    return {
        "historico_lutas": [],
        "dinamic_kids_custom": [],
        "flashcards_pressao": [],
        "alunos_graduacao": [],
        "cards_vitoria": [],
        "cursos_interativos": [],
        "lista_alunos_academia": [],
        "notas_kimono": [],
        "cronogramas_aulas": [],
        "foco_recuperacao": [],
        "perfil_nome": nome_padrao,
        "perfil_faixa": "Branca",
        "perfil_graus": 0,
        "perfil_academia": "Academia BJJ",
        "perfil_peso": "Médio",
        "perfil_estilo": "Versátil / Equilibrado",
        "perfil_status": "Atleta Competidor 🏆",
        "perfil_foto_b64": ""
    }


def obter_caminho_usuario(email_usuario):
    nome_limpo = "".join(c if c.isalnum() else "_" for c in email_usuario.lower()).strip("_")
    return os.path.join(PASTA_DADOS, f"usuario_{nome_limpo}.json")


def carregar_dados_usuario(email_usuario):
    dados = dados_vazios(email_usuario)
    caminho = obter_caminho_usuario(email_usuario)
    try:
        if os.path.exists(caminho):
            with open(caminho, "r", encoding="utf-8") as f:
                dados.update(json.load(f))
    except Exception:
        pass
    return dados


def salvar_dados_usuario(email_usuario, dados):
    caminho = obter_caminho_usuario(email_usuario)
    try:
        tmp = caminho + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        os.replace(tmp, caminho)
    except Exception:
        pass


def salvar_tudo():
    usuario = st.session_state.get("usuario_email")
    if not usuario:
        return
    dados = {}
    for campo in CAMPOS:
        dados[campo] = st.session_state.get(campo, dados_vazios(usuario)[campo])
    salvar_dados_usuario(usuario, dados)


def carregar_usuario(email):
    dados = carregar_dados_usuario(email)
    st.session_state.usuario_email = email
    st.session_state.usuario_atual = email.split("@")[0]
    st.session_state.is_admin = (email.lower() == EMAIL_ADMIN_MASTER.lower())
    for campo in CAMPOS:
        st.session_state[campo] = dados.get(campo, dados_vazios(email)[campo])


def fazer_logout():
    st.session_state.autenticado = False
    st.session_state.usuario_email = ""
    st.session_state.usuario_atual = ""
    st.session_state.is_admin = False
    st.rerun()


# ---------------------------------------------------------------------------
# CSS - PALETA PRETO & PRATA METÁLICO (DARK PREMIUM)
# ---------------------------------------------------------------------------
CSS = """
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { background-color: #0d0d0d !important; }
[data-testid="stSidebar"], [data-testid="stSidebar"] > div { background-color: #141414 !important; border-right: 1px solid #333333 !important; }
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp p, .stApp li, .stApp label, .stApp summary { color: #ffffff; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * { color: #aaaaaa !important; }

div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="textarea"], div[data-baseweb="select"] > div { background-color: #1f1f1f !important; border-color: #a0a0a0 !important; border-radius: 8px !important; }
div[data-baseweb="input"] input, div[data-baseweb="base-input"] input, div[data-baseweb="textarea"] textarea, div[data-baseweb="base-input"] textarea, input, textarea { background-color: #1f1f1f !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; caret-color: #ffffff !important; font-weight: bold !important; }
input::placeholder, textarea::placeholder { color: #888888 !important; -webkit-text-fill-color: #888888 !important; opacity: 1 !important; }
div[data-baseweb="select"] * { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; }
div[data-baseweb="select"] svg { fill: #ffffff !important; }

[data-testid="stNumberInput"] button { background-color: #2b2b2b !important; color: #ffffff !important; border: none !important; }

[data-testid="stFileUploaderDropzone"], [data-testid="stFileUploader"] section { background-color: #1f1f1f !important; border: 2px dashed #c0c0c0 !important; border-radius: 10px !important; }
[data-testid="stFileUploader"] * { color: #ffffff !important; }
[data-testid="stFileUploader"] svg { fill: #ffffff !important; }
[data-testid="stFileUploader"] button { background-color: #333333 !important; border: 2px solid #c0c0c0 !important; }

.stButton > button, div[data-testid="stFormSubmitButton"] > button { border-radius: 10px !important; font-weight: bold !important; background-color: #262626 !important; color: #ffffff !important; border: 2px solid #c0c0c0 !important; }
.stButton > button p, div[data-testid="stFormSubmitButton"] > button p { color: #ffffff !important; }
.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover { background-color: #404040 !important; border-color: #ffffff !important; color: #ffffff !important; }

[data-testid="stExpander"] { background-color: #181818 !important; border: 1px solid #444444 !important; border-radius: 10px !important; }
[data-testid="stForm"] { border: 1px solid #444444 !important; border-radius: 12px !important; }

.placar-box, .nutri-box, .camp-box, .curso-box, .kids-box, .admin-box { color: #ffffff; border-radius: 15px; padding: 20px; margin-bottom: 20px; }
.placar-box { background-color: #161616; border: 2px solid #c0c0c0; text-align: center; }
.placar-numero { font-size: 50px; font-weight: bold; color: #00ffcc; }
.nutri-box { background-color: #1a1a1a; border: 2px solid #00ffcc; }
.camp-box { background-color: #161616; border: 2px solid #c0c0c0; }
.curso-box { background-color: #181818; border: 2px solid #888888; }
.kids-box { background-color: #1c1c1c; border: 2px solid #fbbf24; }
.badge-container { display: flex; gap: 10px; justify-content: center; margin-bottom: 20px; }
.badge { background-color: #1f1f1f; border: 1px solid #c0c0c0; color: #e0e0e0; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: bold; }
.foto-bolinha { width: 85px; height: 85px; border-radius: 50%; object-fit: cover; border: 3px solid #c0c0c0; display: block; margin: 0 auto 10px auto; box-shadow: 0 0 12px rgba(192,192,192,0.3); }
.bolinha-padrao { width: 85px; height: 85px; border-radius: 50%; background-color: #222222; border: 3px solid #c0c0c0; display: flex; align-items: center; justify-content: center; font-size: 34px; margin: 0 auto 10px auto; }
"""
css_compacto = " ".join(CSS.split())
st.markdown(f"<style>{css_compacto}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TELA DE LOGIN PROFISSIONAL PRETO & PRATA
# ---------------------------------------------------------------------------
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_email" not in st.session_state:
    st.session_state.usuario_email = ""
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center; color: #e0e0e0;'>🥋 OssBot Pro</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #aaaaaa;'>Plataforma Inteligente de Gestão de BJJ & Tatame</h3>", unsafe_allow_html=True)
    
    mostrar_html("""
    <div class='badge-container'>
        <span class='badge'>⚙️ Edição Preto & Prata</span>
        <span class='badge'>🛡️ Acesso Seguro & Multi-Usuário</span>
        <span class='badge'>⏱️ 15 Abas Especializadas</span>
    </div>
    """)
    st.divider()

    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        aba_entrar, aba_cadastrar, aba_recuperar = st.tabs(["🔑 Entrar", "📝 Criar Conta", "🔄 Recuperar Senha"])

        with aba_entrar:
            with st.form("form_login"):
                email_log = st.text_input("Seu E-mail:").strip().lower()
                senha_log = st.text_input("Sua Senha:", type="password")
                btn_envia_login = st.form_submit_button("🚀 Entrar no OssBot", use_container_width=True)
                
                if btn_envia_login:
                    banco = carregar_banco_usuarios()
                    if email_log in banco and banco[email_log]["senha"] == senha_log:
                        st.session_state.autenticado = True
                        carregar_usuario(email_log)
                        st.success("✅ Login realizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ E-mail ou senha incorretos.")

        with aba_cadastrar:
            with st.form("form_cadastro"):
                email_novo = st.text_input("Digite seu E-mail:").strip().lower()
                senha_nova = st.text_input("Crie uma Senha (mín. 6 caracteres):", type="password")
                btn_envia_cad = st.form_submit_button("➕ Criar Minha Conta", use_container_width=True)
                
                if btn_envia_cad:
                    if not email_novo or not senha_nova:
                        st.warning("Preencha o e-mail e a senha!")
                    elif len(senha_nova) < 6:
                        st.warning("⚠️ A senha precisa ter no mínimo 6 caracteres para sua segurança.")
                    elif "@" not in email_novo or "." not in email_novo:
                        st.warning("Digite um e-mail válido!")
                    else:
                        banco = carregar_banco_usuarios()
                        if email_novo in banco:
                            st.warning("⚠️ Este e-mail já possui cadastro. Use a aba 'Entrar'.")
                        else:
                            banco[email_novo] = {
                                "senha": senha_nova,
                                "plano": "ativo" if email_novo == EMAIL_ADMIN_MASTER.lower() else "pro",
                                "data_criacao": datetime.now().strftime("%d/%m/%Y - %H:%M")
                            }
                            salvar_banco_usuarios(banco)
                            st.session_state.autenticado = True
                            carregar_usuario(email_novo)
                            st.success("🎉 Conta criada com sucesso! Acessando...")
                            st.rerun()

        with aba_recuperar:
            with st.form("form_recuperacao"):
                email_rec = st.text_input("E-mail Cadastrado:").strip().lower()
                nova_senha_rec = st.text_input("Nova Senha:", type="password")
                btn_envia_rec = st.form_submit_button("🔄 Redefinir Senha", use_container_width=True)
                
                if btn_envia_rec:
                    banco = carregar_banco_usuarios()
                    if email_rec in banco:
                        if len(nova_senha_rec) < 6:
                            st.warning("⚠️ A nova senha precisa ter no mínimo 6 caracteres.")
                        else:
                            banco[email_rec]["senha"] = nova_senha_rec
                            salvar_banco_usuarios(banco)
                            st.success("✅ Senha redefinida com sucesso! Vá em 'Entrar'.")
                    else:
                        st.error("❌ E-mail não encontrado no sistema.")

    st.stop()

# ---------------------------------------------------------------------------
# Botões flutuantes para subir e descer a página
# ---------------------------------------------------------------------------
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
  #botoes-rolagem button { width: 64px; height: 64px; font-size: 28px; font-weight: bold; color: #ffffff; background-color: #262626; border: 2px solid #c0c0c0; border-radius: 50%; cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.8); }
  #botoes-rolagem button:hover { background-color: #404040; border-color: #ffffff; }
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
# Barra lateral (Bolinha de Perfil, Carteirinha, Graus 0-11, Painel Master)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🥋 Meu Perfil Pro")
    
    if st.session_state.get("perfil_foto_b64"):
        try:
            mostrar_html(f"<img src='data:image/png;base64,{st.session_state.perfil_foto_b64}' class='foto-bolinha' />")
        except Exception:
            mostrar_html("<div class='bolinha-padrao'>🥋</div>")
    else:
        mostrar_html("<div class='bolinha-padrao'>🥋</div>")

    with st.expander(f"👤 Carteirinha: {st.session_state.get('perfil_nome', 'Atleta')}"):
        st.caption(f"📧 **{st.session_state.get('usuario_email')}**")
        if st.session_state.is_admin:
            st.success("👑 **Master Admin / Dono** (Acesso Total)")

        foto_perfil_up = st.file_uploader("Enviar Foto de Perfil:", type=["jpg", "png", "jpeg"], key="up_foto_atleta")
        if foto_perfil_up is not None:
            try:
                b64_img = base64.b64encode(foto_perfil_up.getvalue()).decode("utf-8")
                st.session_state.perfil_foto_b64 = b64_img
                salvar_tudo()
                st.rerun()
            except Exception:
                pass

        st.session_state.perfil_nome = st.text_input("Nome Completo:", value=st.session_state.get("perfil_nome", "Atleta"), key="input_perfil_nome")
        st.session_state.perfil_faixa = st.selectbox(
            "Faixa:", 
            ["Branca", "Cinza", "Amarela", "Laranja", "Verde", "Azul", "Roxa", "Castanha", "Preta", "Vermelha e Preta", "Vermelha e Branca", "Vermelha"],
            index=["Branca", "Cinza", "Amarela", "Laranja", "Verde", "Azul", "Roxa", "Castanha", "Preta", "Vermelha e Preta", "Vermelha e Branca", "Vermelha"].index(st.session_state.get("perfil_faixa", "Branca")),
            key="select_perfil_faixa"
        )
        
        st.session_state.perfil_graus = st.slider("Graus (0 a 11):", 0, 11, int(st.session_state.get("perfil_graus", 0)), key="slider_perfil_graus")
        st.session_state.perfil_academia = st.text_input("Academia / Equipe:", value=st.session_state.get("perfil_academia", "Academia BJJ"), key="input_perfil_academia")
        st.session_state.perfil_peso = st.text_input("Categoria de Peso:", value=st.session_state.get("perfil_peso", "Médio"), key="input_perfil_peso")
        st.session_state.perfil_status = st.selectbox(
            "Status:",
            ["Atleta Competidor 🏆", "Praticante / Hobby 🥋", "Monitor / Instrutor 🥇", "Faixa Preta / Mestre 👑"],
            index=0,
            key="select_perfil_status"
        )

        if st.button("💾 Salvar Carteirinha", use_container_width=True, key="btn_salvar_perfil"):
            salvar_tudo()
            st.success("✅ Perfil e carteirinha salvos com sucesso!")
            st.rerun()

    # PAINEL MASTER / ADMINISTRADOR
    if st.session_state.is_admin:
        st.divider()
        st.markdown("## 👑 Painel Master")
        with st.expander("🛠️ Gestão de Usuários (Dono)"):
            banco = carregar_banco_usuarios()
            st.write(f"📊 **Total de Contas:** {len(banco)}")
            for usr, info in banco.items():
                st.caption(f"• **E-mail:** `{usr}` | **Criado:** {info.get('data_criacao', 'S/D')}")

    st.divider()

    dados_usuario_atual = {}
    for c in CAMPOS:
        dados_usuario_atual[c] = st.session_state.get(c, {})
    
    st.download_button(
        "📥 Baixar Backup dos Dados",
        data=json.dumps(dados_usuario_atual, ensure_ascii=False, indent=2),
        file_name=f"ossbot_backup_{st.session_state.get('usuario_email', 'atleta')}.json",
        mime="application/json",
        use_container_width=True,
        help="Baixe um arquivo com todas as suas anotações e históricos salvos."
    )

    if st.button("🚪 Sair da Conta (Logout)", use_container_width=True, key="btn_logout"):
        fazer_logout()

    st.divider()
    st.markdown("## 📡 Conexão")
    st.checkbox("📡 Modo Offline Ativado", value=False, key="modo_offline", 
                help="Ative para operar sem gastar dados móveis")

    if st.session_state.get("modo_offline"):
        st.success("Modo Offline ligado com sucesso!")

# ---------------------------------------------------------------------------
# Estados auxiliares
# ---------------------------------------------------------------------------
for chave, valor in {
    "pts_a": 0, "vant_a": 0, "pun_a": 0,
    "pts_b": 0, "vant_b": 0, "pun_b": 0,
    "tempo_segundos": 300, "cronometro_rodando": False,
}.items():
    st.session_state.setdefault(chave, valor)

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
# Cabeçalho Principal (Tema Preto & Prata)
# ---------------------------------------------------------------------------
col_esq, col_centro, col_dir = st.columns([1.2, 2.6, 1.2])
with col_esq:
    st.image("https://images.unsplash.com/photo-1517838277536-f5f99be501cd?q=80&w=600&auto=format&fit=crop",
             caption="Técnica e Combate", use_container_width=True)
with col_centro:
    st.markdown("<h1 style='text-align: center; color: #e0e0e0;'>🥋 OssBot App</h1>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center; color: #00ffcc;'>Atleta: {esc(st.session_state.get('perfil_nome', 'Atleta'))} | Faixa {esc(st.session_state.get('perfil_faixa', 'Branca'))} ({st.session_state.get('perfil_graus', 0)}º Grau)</h4>", unsafe_allow_html=True)
    st.markdown(f"<h5 style='text-align: center; color: #aaaaaa;'>{esc(st.session_state.get('perfil_academia', 'Academia BJJ'))} | {esc(st.session_state.get('perfil_status', 'Atleta'))}</h5>", unsafe_allow_html=True)
with col_dir:
    st.image("https://images.unsplash.com/photo-1555597673-b21d5c935865?q=80&w=600&auto=format&fit=crop",
             caption="Faixa Preta — Tradição", use_container_width=True)

st.divider()

# DEFINIÇÃO DAS 15 ABAS
(
    aba_modo_luta, aba_historico_lutas, aba_nutricao, aba_camp, 
    aba_cursos, aba_kids, aba_drills, aba_pressao, aba_grad, 
    aba_kimono, aba_card, aba_caderneta, aba_chaves, aba_cronograma, 
    aba_recuperacao
) = st.tabs([
    "🤼 Luta", "📜 Histórico", "🥗 Nutrição", "🏆 Camp", 
    "📚 Cursos", "👶 Kids", "⏱️ Drills", "🧠 Pressão", "🥇 Graduação", 
    "🥋 Kimono", "📸 Card", "📇 Alunos", "⏱️ Chaves", "📋 Cronograma", 
    "🧘 Recuperação"
])

# ===========================================================================
# ABA 1: MODO LUTA
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
    st.markdown("<h2 style='text-align: center; color: #e0e0e0;'>⏱️ PLACAR & CRONÔMETRO DE LUTA</h2>", unsafe_allow_html=True)

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
                f"<h1 style='text-align: center; font-size: 70px; color: #e0e0e0;'>{mins:02d}:{segs:02d}</h1>",
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
        bloco_placar("a", nome_atleta_a, "🔵", "#c0c0c0")
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
# ABA 2: HISTÓRICO DE LUTAS
# ===========================================================================
with aba_historico_lutas:
    st.markdown("### 📜 Lutas Registradas")
    if not st.session_state.historico_lutas:
        st.info("Nenhuma luta registrada ainda.")
    else:
        for luta in reversed(st.session_state.historico_lutas):
            txt_a = f"🔵 **{luta['atleta_a']}**: {luta['pts_a']} Pts ({luta['vant_a']}V/{luta['pun_a']}P)"
            txt_b = f"⚪ **{luta['atleta_b']}**: {luta['pts_b']} Pts ({luta['vant_b']}V/{luta['pun_b']}P)"
            with st.expander(f"🥋 {luta['data']} - {luta['atleta_a']} vs {luta['atleta_b']}"):
                st.write(f"{txt_a} | {txt_b}")

# ===========================================================================
# ABA 3: NUTRIÇÃO & HIDRATAÇÃO
# ===========================================================================
with aba_nutricao:
    st.markdown("<h2 style='text-align: center; color: #00ffcc;'>🥗 NUTRIÇÃO & HIDRATAÇÃO</h2>", unsafe_allow_html=True)
    peso_input = st.number_input("Digite seu Peso atual (kg):", 30.0, 150.0, 65.0, 0.5, key="nutri_peso")
    horas_input = st.slider("Horas de treino por dia:", 0.5, 4.0, 1.5, 0.5, key="nutri_horas")
    agua_calc = ((peso_input * 35) / 1000) + (horas_input * 0.75)
    mostrar_html(f"""
    <div class='nutri-box'>
        <h3>🥤 Meta Diária de Água Recomendada:</h3>
        <h2>{agua_calc:.2f} Litros</h2>
        <p>• Dica: Beba 500ml de água 1h antes do treino.</p>
    </div>
    """)

# ===========================================================================
# ABA 4: ESTRATÉGIA DE CAMPEONATO
# ===========================================================================
with aba_camp:
    st.markdown("<h2 style='text-align: center; color: #e0e0e0;'>🏆 ESTRATÉGIA DE CAMPEONATO</h2>", unsafe_allow_html=True)
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        faixa_sel = st.selectbox("Sua Faixa:", ["Branca", "Azul", "Roxa", "Castanha", "Preta", "Outros / Infantil"], key="camp_faixa_sel")
        faixa_final = faixa_sel
        if faixa_sel == "Outros / Infantil":
            faixa_final = st.text_input("Qual é a sua faixa exata?", placeholder="Ex: Laranja ponta preta", key="camp_faixa_custom")
            
        data_camp = st.date_input("Data do Campeonato
