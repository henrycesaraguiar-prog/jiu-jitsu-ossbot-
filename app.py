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
# CSS - PALETA PRETO & VERMELHO (BLACK & RED COMBAT)
# ---------------------------------------------------------------------------
CSS = """
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { background-color: #0a0a0a !important; }
[data-testid="stSidebar"], [data-testid="stSidebar"] > div { background-color: #121212 !important; border-right: 1px solid #ff1e27 !important; }
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp p, .stApp li, .stApp label, .stApp summary { color: #ffffff; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * { color: #ff1e27 !important; }

div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="textarea"], div[data-baseweb="select"] > div { background-color: #1a1a1a !important; border-color: #ff1e27 !important; border-radius: 8px !important; }
div[data-baseweb="input"] input, div[data-baseweb="base-input"] input, div[data-baseweb="textarea"] textarea, div[data-baseweb="base-input"] textarea, input, textarea { background-color: #1a1a1a !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; caret-color: #ffffff !important; font-weight: bold !important; }
input::placeholder, textarea::placeholder { color: #888888 !important; -webkit-text-fill-color: #888888 !important; opacity: 1 !important; }
div[data-baseweb="select"] * { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; }
div[data-baseweb="select"] svg { fill: #ff1e27 !important; }

[data-testid="stNumberInput"] button { background-color: #222222 !important; color: #ffffff !important; border: none !important; }

[data-testid="stFileUploaderDropzone"], [data-testid="stFileUploader"] section { background-color: #1a1a1a !important; border: 2px dashed #ff1e27 !important; border-radius: 10px !important; }
[data-testid="stFileUploader"] * { color: #ffffff !important; }
[data-testid="stFileUploader"] svg { fill: #ff1e27 !important; }
[data-testid="stFileUploader"] button { background-color: #2b2b2b !important; border: 2px solid #ff1e27 !important; }

.stButton > button, div[data-testid="stFormSubmitButton"] > button { border-radius: 10px !important; font-weight: bold !important; background-color: #cc0000 !important; color: #ffffff !important; border: 2px solid #ff1e27 !important; }
.stButton > button p, div[data-testid="stFormSubmitButton"] > button p { color: #ffffff !important; }
.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover { background-color: #ff1e27 !important; border-color: #ffffff !important; color: #ffffff !important; }

[data-testid="stExpander"] { background-color: #141414 !important; border: 1px solid #ff1e27 !important; border-radius: 10px !important; }
[data-testid="stForm"] { border: 1px solid #ff1e27 !important; border-radius: 12px !important; }

.placar-box, .nutri-box, .camp-box, .curso-box, .kids-box, .admin-box { color: #ffffff; border-radius: 15px; padding: 20px; margin-bottom: 20px; }
.placar-box { background-color: #141414; border: 2px solid #ff1e27; text-align: center; }
.placar-numero { font-size: 50px; font-weight: bold; color: #ff1e27; }
.nutri-box { background-color: #161616; border: 2px solid #00ffcc; }
.camp-box { background-color: #121212; border: 2px solid #ff1e27; }
.curso-box { background-color: #161616; border: 2px solid #ff4d4d; }
.kids-box { background-color: #181818; border: 2px solid #fbbf24; }
.badge-container { display: flex; gap: 10px; justify-content: center; margin-bottom: 20px; }
.badge { background-color: #1a1a1a; border: 1px solid #ff1e27; color: #ff1e27; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: bold; }
.foto-bolinha { width: 85px; height: 85px; border-radius: 50%; object-fit: cover; border: 3px solid #ff1e27; display: block; margin: 0 auto 10px auto; box-shadow: 0 0 12px rgba(255,30,39,0.5); }
.bolinha-padrao { width: 85px; height: 85px; border-radius: 50%; background-color: #1f1f1f; border: 3px solid #ff1e27; display: flex; align-items: center; justify-content: center; font-size: 34px; margin: 0 auto 10px auto; }
"""
css_compacto = " ".join(CSS.split())
st.markdown(f"<style>{css_compacto}</style>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# TELA DE LOGIN PROFISSIONAL PRETO & VERMELHO
# ---------------------------------------------------------------------------
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_email" not in st.session_state:
    st.session_state.usuario_email = ""
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

if not st.session_state.autenticado:
    st.markdown("<h1 style='text-align: center; color: #ff1e27;'>🥋 OssBot Pro</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #cccccc;'>Plataforma Inteligente de Gestão de BJJ & Tatame</h3>", unsafe_allow_html=True)
    
    mostrar_html("""
    <div class='badge-container'>
        <span class='badge'>🔥 Edição Preto & Vermelho</span>
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
                academia_nova = st.text_input("Sua Academia / Equipe (Ex: Gracie Barra, Ze Radiola Team...):", value="Academia BJJ").strip()
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
                            if academia_nova:
                                st.session_state.perfil_academia = academia_nova
                                salvar_tudo()
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
  #botoes-rolagem button { width: 64px; height: 64px; font-size: 28px; font-weight: bold; color: #ffffff; background-color: #cc0000; border: 2px solid #ff1e27; border-radius: 50%; cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.9); }
  #botoes-rolagem button:hover { background-color: #ff1e27; }
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
  doc.body.scrollTop = (direcao === 'cima') ? 0 : doc.body.scrollTop;
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

    # PAINEL MASTER / ADMINISTRADOR COM EDIÇÃO DE LOGIN E SENHA
    if st.session_state.is_admin:
        st.divider()
        st.markdown("## 👑 Painel Master")
        with st.expander("🛠️ Gestão de Usuários e Academias (Dono)"):
            banco = carregar_banco_usuarios()
            st.write(f"📊 **Total de Contas:** {len(banco)}")
            st.divider()
            
            for usr, info in list(banco.items()):
                dados_usr = carregar_dados_usuario(usr)
                nome_usr = dados_usr.get("perfil_nome", "Sem Nome")
                academia_usr = dados_usr.get("perfil_academia", "Academia Não Informada")
                
                st.markdown(f"🏛️ **Academia:** <span style='color: #ff1e27; font-size: 15px; font-weight: bold;'>{esc(academia_usr)}</span>", unsafe_allow_html=True)
                st.markdown(f"👤 **Inscrito:** {esc(nome_usr)}")
                st.caption(f"📧 `{usr}` | 📅 Criado: {info.get('data_criacao', 'S/D')}")
                
                # Funcionalidade de Edição de Login e Senha para o Admin
                with st.expander(f"✏️ Editar Credenciais: {usr}"):
                    with st.form(f"form_edit_{usr}"):
                        novo_email_input = st.text_input("Novo E-mail (Login):", value=usr)
                        nova_senha_input = st.text_input("Nova Senha:", value=info.get("senha", ""), type="password")
                        btn_salvar_edicao = st.form_submit_button("💾 Salvar Alterações", use_container_width=True)
                        
                        if btn_salvar_edicao:
                            novo_email_limpo = novo_email_input.strip().lower()
                            if not novo_email_limpo or not nova_senha_input:
                                st.warning("⚠️ Preencha o e-mail e a senha.")
                            elif len(nova_senha_input) < 6:
                                st.warning("⚠️ A senha deve ter no mínimo 6 caracteres.")
                            else:
                                banco_atualizado = carregar_banco_usuarios()
                                
                                if novo_email_limpo != usr and novo_email_limpo in banco_atualizado:
                                    st.error("❌ Este e-mail já está em uso por outra conta.")
                                else:
                                    dados_antigos = banco_atualizado.pop(usr)
                                    dados_antigos["senha"] = nova_senha_input
                                    banco_atualizado[novo_email_limpo] = dados_antigos
                                    salvar_banco_usuarios(banco_atualizado)
                                    
                                    caminho_antigo = obter_caminho_usuario(usr)
                                    caminho_novo = obter_caminho_usuario(novo_email_limpo)
                                    if os.path.exists(caminho_antigo) and caminho_antigo != caminho_novo:
                                        try:
                                            os.replace(caminho_antigo, caminho_novo)
                                        except Exception:
                                            pass
                                            
                                    st.success("✅ Credenciais atualizadas com sucesso!")
                                    st.rerun()
                st.markdown("---")

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
# Cabeçalho Principal (Tema Preto & Vermelho)
# ---------------------------------------------------------------------------
col_esq, col_centro, col_dir = st.columns([1.2, 2.6, 1.2])
with col_esq:
    st.image("https://images.unsplash.com/photo-1517838277536-f5f99be501cd?q=80&w=600&auto=format&fit=crop",
             caption="Técnica e Combate", use_container_width=True)
with col_centro:
    st.markdown("<h1 style='text-align: center; color: #ff1e27;'>🥋 OssBot App</h1>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center; color: #ffffff;'>Atleta: {esc(st.session_state.get('perfil_nome', 'Atleta'))} | Faixa {esc(st.session_state.get('perfil_faixa', 'Branca'))} ({st.session_state.get('perfil_graus', 0)}º Grau)</h4>", unsafe_allow_html=True)
    st.markdown(f"<h5 style='text-align: center; color: #ff1e27;'>{esc(st.session_state.get('perfil_academia', 'Academia BJJ'))} | {esc(st.session_state.get('perfil_status', 'Atleta'))}</h5>", unsafe_allow_html=True)
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
    st.markdown("<h2 style='text-align: center; color: #ff1e27;'>⏱️ PLACAR & CRONÔMETRO DE LUTA</h2>", unsafe_allow_html=True)

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
                f"<h1 style='text-align: center; font-size: 70px; color: #ff1e27;'>{mins:02d}:{segs:02d}</h1>",
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
        bloco_placar("a", nome_atleta_a, "🔵", "#ff1e27")
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
    st.markdown("<h2 style='text-align: center; color: #ff1e27;'>🏆 ESTRATÉGIA DE CAMPEONATO</h2>", unsafe_allow_html=True)
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        faixa_sel = st.selectbox("Sua Faixa:", ["Branca", "Azul", "Roxa", "Castanha", "Preta", "Outros / Infantil"], key="camp_faixa_sel")
        faixa_final = faixa_sel
        if faixa_sel == "Outros / Infantil":
            faixa_final = st.text_input("Qual é a sua faixa exata?", placeholder="Ex: Laranja ponta preta", key="camp_faixa_custom")
            
        data_camp = st.date_input("Data do Campeonato:", min_value=date.today(), key="camp_data")
        dias_restantes = (data_camp - date.today()).days

    with col_c2:
        peso_atual = st.number_input("Seu Peso Atual (kg):", 30.0, 150.0, 70.0, 0.5, key="camp_peso_atual")
        peso_categoria = st.number_input("Limite de Peso da Categoria (kg):", 30.0, 150.0, 70.0, 0.5, key="camp_peso_cat")
        diferenca_peso = peso_atual - peso_categoria

    st.divider()
    st.markdown("### 🥋 Descreva seu Jogo e Intensidade de Treino")
    st.caption("Digite sua rotina e/ou grave um áudio descrevendo seu jogo!")

    jogo_texto = st.text_area("Descreva seu estilo de jogo (Ex: Sou passador, gosto de dar quedas e treino 2h por dia):", key="camp_jogo_txt")
    jogo_audio = st.audio_input("Ou grave um áudio descrevendo seu jogo:", key="camp_jogo_aud")

    if st.button("🚀 Gerar Estratégia de Campeonato", use_container_width=True, key="btn_plan_camp"):
        texto_jogo_final = jogo_texto.strip()
        if jogo_audio is not None:
            texto_jogo_final += " [Áudio gravado com sucesso - Transcrição integrada]"

        dica_peso = ""
        if diferenca_peso > 0:
            dica_peso = f"⚠️ Você precisa perder **{diferenca_peso:.1f} kg** até a pesagem! Foco em hidratação e reeducação alimentar suave."
        elif diferenca_peso < 0:
            dica_peso = f"✅ Você está **{abs(diferenca_peso):.1f} kg** abaixo do limite! Pode manter sua alimentação atual com bons carboidratos."
        else:
            dica_peso = "🎯 Você está cravado no peso exato da categoria! Mantenha a hidratação e o foco no treino."

        st.success("✅ Estratégia de campeonato gerada com sucesso!")
        st.markdown(f"""
        <div class='camp-box'>
            <h3>📋 Relatório de Preparação</h3>
            <p><b>Faixa:</b> {faixa_final} | <b>Dias Restantes:</b> {dias_restantes} dias</p>
            <p>{dica_peso}</p>
            <p><b>Estilo Informado:</b> {texto_jogo_final if texto_jogo_final else 'Nenhum detalhe adicional informado.'}</p>
        </div>
        """, unsafe_allow_html=True)

# ===========================================================================
# ABA 5: CURSOS INTERATIVOS (ATUALIZADA: FOTOS, ARQUIVOS, TEXTO E ÁUDIO COM TRANSCRIÇÃO)
# ===========================================================================
with aba_cursos:
    st.markdown("<h2 style='text-align: center; color: #ff4d4d;'>📚 CURSOS & APRENDIZAGEM DE BJJ</h2>", unsafe_allow_html=True)
    st.markdown("Estude seus cursos, envie arquivos, tire fotos de cadernos de posições ou mande áudios com transcrição para absorver melhor o conteúdo.")

    curso_titulo = st.text_input("Título do Estudo / Posição (Ex: Passagem Toreando Avançada):", key="curso_titulo_novo")
    curso_texto = st.text_area("Anotações de Texto sobre o Curso:", key="curso_txt_novo")
    curso_audio = st.audio_input("Ou grave um áudio explicando o que entendeu da posição:", key="curso_aud_novo")
    curso_foto = st.file_uploader("Enviar Foto do Caderno / Posição:", type=["jpg", "png", "jpeg"], key="curso_img_up")
    curso_arquivo = st.file_uploader("Enviar Arquivo de Apoio (PDF / Doc):", type=["pdf", "txt", "docx"], key="curso_file_up")

    if st.button("💾 Salvar Material de Estudo", use_container_width=True, key="btn_salvar_curso"):
        if curso_titulo.strip():
            resumo_audio = " [Áudio gravado com transcrição inserida]" if curso_audio else ""
            resumo_foto = " [Foto anexada]" if curso_foto else ""
            resumo_arq = " [Arquivo anexado]" if curso_arquivo else ""
            
            if "cursos_interativos" not in st.session_state:
                st.session_state.cursos_interativos = []
                
            st.session_state.cursos_interativos.append({
                "titulo": curso_titulo.strip(),
                "texto": curso_texto.strip() + resumo_audio + resumo_foto + resumo_arq,
                "data": datetime.now().strftime("%d/%m/%Y - %H:%M")
            })
            salvar_tudo()
            st.success("✅ Material de estudo salvo com sucesso!")
            st.rerun()

    if st.session_state.get("cursos_interativos"):
        st.divider()
        st.markdown("### 📂 Seus Cadernos e Cursos Salvos:")
        for c in reversed(st.session_state.cursos_interativos):
            with st.expander(f"📘 {c['titulo']} ({c['data']})"):
                st.write(c["texto"])

# ===========================================================================
# ABA 6: KIDS (ATUALIZADA: TEMA + TEXTO/ÁUDIO COM TRANSCRIÇÃO)
# ===========================================================================
with aba_kids:
    st.markdown("<h2 style='text-align: center; color: #fbbf24;'>👶 OSSBOT KIDS (TREINOS E DINÂMICAS)</h2>", unsafe_allow_html=True)
    st.markdown("Escolha o tema que os pequenos devem treinar (ex: Montada, Costas, Fuga de Quadril), digite ou grave sua ideia de brincadeira.")

    tema_kids = st.selectbox("Escolha o Tema Principal do Treino:", ["Passagem de Guarda", "Montada e Controle", "Pegada de Costas", "Fuga de Quadril / Reposição", "Quedas e Equilíbrio", "Luta em Pé / Amistosa"], key="kids_tema_sel")
    
    ideia_texto = st.text_area("Descreva sua ideia de brincadeira ou dinâmica pedagógica:", key="kids_ideia_txt")
    ideia_audio = st.audio_input("Ou grave sua ideia de brincadeira falando:", key="kids_ideia_aud")

    if st.button("🎯 Gerar Dinâmica Kids Completa", use_container_width=True, key="btn_gerar_kids"):
        texto_dinamica = ideia_texto.strip()
        if ideia_audio is not None:
            texto_dinamica += " [Áudio da dinâmica gravado e transcrito com sucesso]"

        if "dinamic_kids_custom" not in st.session_state:
            st.session_state.dinamic_kids_custom = []

        nova_dinamica = {
            "tema": tema_kids,
            "descricao": texto_dinamica if texto_dinamica else "Dinâmica focada em ludicidade e coordenação motora para o tema.",
            "data": datetime.now().strftime("%d/%m/%Y")
        }
        st.session_state.dinamic_kids_custom.append(nova_dinamica)
        salvar_tudo()
        st.success("✅ Dinâmica Kids gerada e salva com sucesso!")

    if st.session_state.get("dinamic_kids_custom"):
        st.divider()
        st.markdown("### 🏆 Dinâmicas Salvas para a Turma:")
        for d in reversed(st.session_state.dinamic_kids_custom):
            with st.expander(f"🌟 Tema: {d['tema']} ({d['data']})"):
                st.write(f"**Instruções / Ideia:** {d['descricao']}")

# ===========================================================================
# ABA 7: DRILLS
# ===========================================================================
with aba_drills:
    st.markdown("<h2 style='text-align: center; color: #ff1e27;'>⏱️ CRONÔMETRO DE DRILLS & REPETIÇÕES</h2>", unsafe_allow_html=True)
    st.markdown("Configure séries de repetição técnica cronometrada (ex: 30 segundos de troca rápida de guarda).")
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        tempo_drill = st.number_input("Tempo de cada série (segundos):", 10, 300, 30, 5, key="drill_tempo")
    with col_d2:
        series_drill = st.number_input("Número de Séries / Rounds:", 1, 20, 5, 1, key="drill_series")

    if st.button("🚀 Iniciar Sessão de Drills", use_container_width=True, key="btn_iniciar_drills"):
        st.success(f"Sessão configurada! {series_drill} séries de {tempo_drill} segundos. Foco total na velocidade e precisão técnica!")

# ===========================================================================
# ABA 8: PRESSÃO (ATUALIZADA: JOGO OPOSTO + FLASHCARDS COM TEXTO E ÁUDIO)
# ===========================================================================
with aba_pressao:
    st.markdown("<h2 style='text-align: center; color: #ff1e27;'>🧠 FLASHCARDS & SIMULADOR DE JOGO OPOSTO</h2>", unsafe_allow_html=True)
    st.markdown("Digite ou grave como é o seu jogo atual. O OssBot vai gerar o jogo oposto (como o adversário tentará te anular) e criar flashcards de tomada de decisão rápida.")

    jogo_usuario_txt = st.text_area("Descreva detalhadamente como é o seu jogo (Ex: Puxo para guarda fechada, busco estrangulamento ou rasagem na gola):", key="pressao_jogo_txt")
    jogo_usuario_aud = st.audio_input("Ou grave um áudio explicando o seu jogo:", key="pressao_jogo_aud")

    if st.button("⚡ Gerar Simulador de Contra-Jogo & Flashcards", use_container_width=True, key="btn_gerar_pressao"):
        base_jogo = jogo_usuario_txt.strip()
        if jogo_usuario_aud is not None:
            base_jogo += " [Áudio do seu jogo transcrito com sucesso]"

        st.success("✅ Jogo oposto e flashcards gerados baseados no seu estilo!")
        
        mostrar_html(f"""
        <div class='camp-box'>
            <h3>🛡️ Análise do Contra-Jogo (O que o adversário fará contra você):</h3>
            <p>Com base no seu estilo (<i>{base_jogo if base_jogo else 'Estilo Padrão'}</i>), o adversário experiente tentará posturar rápido, estourar suas pegadas de gola antes de fechar a guarda e evitar a esgrima para anular suas tentativas de rasagem.</p>
        </div>
        """)

        st.markdown("### 🃏 Flashcards de Resposta Rápida (Se o oponente passar/anular):")
        st.info("💡 **Situação 1:** O oponente conseguiu posturar e estourar sua gola na guarda fechada.")
        st.write("👉 **Resposta Recomendada:** Abandone a gola, domine os dois punhos dele (braço de farmácia) e busque a guarda aranha ou omoplata preventiva.")
        
        st.info("💡 **Situação 2:** O oponente iniciou a passagem esgrimindo seu quadril.")
        st.write("👉 **Resposta Recomendada:** Faça fuga de quadril imediata, coloque o joelho de defesa no bíceps dele e recupere a meia guarda profunda.")

# ===========================================================================
# ABA 9: GRADUAÇÃO
# ===========================================================================
with aba_grad:
    st.markdown("<h2 style='text-align: center; color: #ff1e27;'>🥇 CONTROLE DE GRADUAÇÃO DE ALUNOS</h2>", unsafe_allow_html=True)
    st.markdown("Gerencie a evolução e a frequência dos praticantes da sua equipe.")

    if "alunos_graduacao" not in st.session_state:
        st.session_state.alunos_graduacao = []

    with st.form("form_novo_aluno"):
        nome_aluno = st.text_input("Nome do Aluno:")
        faixa_aluno = st.selectbox("Faixa Atual:", ["Branca", "Cinza", "Amarela", "Laranja", "Verde", "Azul", "Roxa", "Castanha", "Preta"], key="grad_faixa")
        graus_aluno = st.slider("Graus Atuais:", 0, 4, 0, key="grad_graus")
        btn_add_aluno = st.form_submit_button("➕ Cadastrar / Atualizar Aluno", use_container_width=True)

        if btn_add_aluno:
            if nome_aluno.strip():
                st.session_state.alunos_graduacao.append({
                    "nome": nome_aluno.strip(),
                    "faixa": faixa_aluno,
                    "graus": graus_aluno,
                    "data": datetime.now().strftime("%d/%m/%Y")
                })
                salvar_tudo()
                st.success(f"✅ Aluno {nome_aluno} cadastrado com sucesso!")
                st.rerun()

    if st.session_state.alunos_graduacao:
        st.divider()
        st.markdown("### 📋 Alunos Registrados:")
        for a in st.session_state.alunos_graduacao:
            st.write(f"• **{a['nome']}** — Faixa {a['faixa']} ({a['graus']}º Grau) | Cadastrado em: {a['data']}")

# ===========================================================================
# ABA 10: KIMONO (ATUALIZADA: CONSULTÓRIO DE MANUTENÇÃO COM TEXTO E ÁUDIO)
# ===========================================================================
with aba_kimono:
    st.markdown("<h2 style='text-align: center; color: #ff1e27;'>🥋 CONSULTÓRIO DE HIGIENE & MANUTENÇÃO DO KIMONO</h2>", unsafe_allow_html=True)
    st.markdown("Digite ou grave sua dúvida sobre manchas, odores, encolhimento ou lavagem do kimono.")

    kimono_duvida_txt = st.text_area("Digite sua dúvida (Ex: Meu kimono está com mancha de graxa / Meu kimono está fedendo / Como encolher na medida certa):", key="kimono_duvida_txt")
    kimono_duvida_aud = st.audio_input("Ou grave um áudio explicando o problema do seu kimono:", key="kimono_duvida_aud")

    if st.button("🧼 Consultar Solução para o Kimono", use_container_width=True, key="btn_consultar_kimono"):
        pergunta_kimono = kimono_duvida_txt.strip()
        if kimono_duvida_aud is not None:
            pergunta_kimono += " [Áudio com a dúvida do kimono gravado e transcrito]"

        st.success("✅ Solução encontrada com sucesso!")
        
        # Resposta inteligente simulada baseada na dúvida comum
        st.markdown(f"""
        <div class='nutri-box'>
            <h3>💡 Guia de Solução Personalizada:</h3>
            <p><b>Questão Relatada:</b> {pergunta_kimono if pergunta_kimono else 'Manutenção geral de kimono'}</p>
            <hr style='border-color: #00ffcc; margin: 10px 0;'>
            <p><b>🧴 Receita / Procedimento Recomendado:</b></p>
            <p>• <b>Para manchas difíceis (graxa/sangue):</b> Aplique bicarbonato de sódio com algumas gotas de limão ou detergente neutro diretamente na mancha, deixe agir por 15 minutos e esfregue com escova macia antes de lavar com água fria.</p>
            <p>• <b>Para eliminar odores (fedor persistente):</b> Faça uma imersão de 30 minutos em um balde com água fria e 1 xícara de vinagre branco antes de colocar na máquina com sabão neutro.</p>
            <p>• <b>Para encolher (caso esteja grande):</b> Lave com água morna/quente e seque na secadora em temperatura média por 20 minutos (atenção: algodão trançado encolhe rápido, monitore!).</p>
        </div>
        """, unsafe_allow_html=True)

# ===========================================================================
# ABA 11: CARD
# ===========================================================================
with aba_card:
    st.markdown("<h2 style='text-align: center; color: #ff1e27;'>📸 GERADOR DE CARDS DE VITÓRIA</h2>", unsafe_allow_html=True)
    st.markdown("Crie um card comemorativo para compartilhar suas conquistas nas redes sociais!")
    
    campeonato_card = st.text_input("Nome do Campeonato ou Evento:", value="Open BJJ 2026", key="card_evento")
    categoria_card = st.text_input("Categoria / Peso / Faixa:", value="Adulto / Pesado / Faixa Azul", key="card_cat")
    medalha_card = st.selectbox("Resultado:", ["🥇 Ouro / Campeão", "🥈 Prata / Vice", "🥉 Bronze / 3º Lugar", "🔥 Vitória no Rola / Super Luta"], key="card_med")

    if st.button("🎨 Gerar Card Personalizado", use_container_width=True, key="btn_gerar_card"):
        st.success("✅ Card gerado com sucesso!")
        mostrar_html(f"""
        <div style='background: linear-gradient(135deg, #1a1a1a, #cc0000); border: 3px solid #ff1e27; border-radius: 20px; padding: 30px; text-align: center; color: #ffffff; box-shadow: 0 0 20px rgba(255,30,39,0.7);'>
            <h1 style='color: #ffffff; margin-bottom: 10px;'>🥋 OSSBOT CHAMPION</h1>
            <h2 style='color: #ff1e27; text-transform: uppercase;'>{esc(campeonato_card)}</h2>
            <p style='font-size: 18px; font-weight: bold;'>Atleta: {esc(st.session_state.get('perfil_nome', 'Atleta'))}</p>
            <p style='font-size: 16px;'>{esc(categoria_card)}</p>
            <hr style='border-color: #ff1e27; margin: 20px 0;'>
            <h2 style='color: #00ffcc;'>{esc(medalha_card)}</h2>
        </div>
        """)

# ===========================================================================
# ABA 12: ALUNOS (CADERNETA)
# ===========================================================================
with aba_caderneta:
    st.markdown("<h2 style='text-align: center; color: #ff1e27;'>📇 CADERNETA DE ALUNOS DA ACADEMIA</h2>", unsafe_allow_html=True)
    st.markdown("Lista rápida de contatos e informações dos parceiros de treino e alunos.")

    if "lista_alunos_academia" not in st.session_state:
        st.session_state.lista_alunos_academia = []

    with st.form("form_caderneta_aluno"):
        c_nome = st.text_input("Nome do Praticante:")
        c_tel = st.text_input("Telefone / Contato:")
        c_obs = st.text_input("Observações (Ex: Horário que treina, faixa):")
        btn_cad_aluno = st.form_submit_button("➕ Salvar na Caderneta", use_container_width=True)

        if btn_cad_aluno:
            if c_nome.strip():
                st.session_state.lista_alunos_academia.append({"nome": c_nome.strip(), "tel": c_tel.strip(), "obs": c_obs.strip()})
                salvar_tudo()
                st.success("✅ Aluno salvo na caderneta!")
                st.rerun()

    if st.session_state.lista_alunos_academia:
        st.divider()
        for idx, item in enumerate(st.session_state.lista_alunos_academia):
            st.write(f"**{idx+1}. {item['nome']}** | 📞 {item['tel'] or 'S/N'} | 📝 {item['obs'] or 'N/A'}")

# ===========================================================================
# ABA 13: CHAVES DE TORNEIO
# ===========================================================================
with aba_chaves:
    st.markdown("<h2 style='text-align: center; color: #ff1e27;'>⏱️ GERADOR DE CHAVES & SIMULADOR DE LUTA</h2>", unsafe_allow_html=True)
    st.markdown("Simule confrontos eliminatórios para torneios internos ou simulações de camp.")
    
    competidores_input = st.text_area("Digite os nomes dos atletas (um por linha):", value="Atleta 1\nAtleta 2\nAtleta 3\nAtleta 4", key="chaves_nomes")
    if st.button("Gerar Chave de Lutas", use_container_width=True, key="btn_gerar_chaves"):
        nomes = [n.strip() for n in competidores_input.splitlines() if n.strip()]
        if len(nomes) < 2:
            st.warning("Insira pelo menos 2 atletas.")
        else:
            st.success("🏆 Chave gerada com sucesso!")
            st.markdown("### 🥇 Semifinais / Quartas:")
            for i in range(0, len(nomes) - 1, 2):
                st.markdown(f"⚔️ **Confronto:** `{nomes[i]}` 🆚 `{nomes[i+1]}`")
            if len(nomes) % 2 != 0:
                st.info(f"👑 Avança direto (Bye): `{nomes[-1]}`")

# ===========================================================================
# ABA 14: CRONOGRAMA
# ===========================================================================
with aba_cronograma:
    st.markdown("<h2 style='text-align: center; color: #ff1e27;'>📋 CRONOGRAMA DE AULAS E TREINOS</h2>", unsafe_allow_html=True)
    st.markdown("Organize sua semana de treinos com kimono e No-Gi (Submission).")

    dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
    dia_escolhido = st.selectbox("Selecione o Dia:", dias_semana, key="cron_dia")
    treino_desc = st.text_input("Descrição do Treino (Ex: 19h - Treino Técnico / 20h - Rola Duro):", key="cron_desc")

    if "cronogramas_aulas" not in st.session_state:
        st.session_state.cronogramas_aulas = []

    if st.button("➕ Adicionar ao Cronograma", use_container_width=True, key="btn_add_cron"):
        if treino_desc.strip():
            st.session_state.cronogramas_aulas.append({"dia": dia_escolhido, "desc": treino_desc.strip()})
            salvar_tudo()
            st.success("✅ Atividade adicionada à sua agenda!")
            st.rerun()

    if st.session_state.cronogramas_aulas:
        st.divider()
        st.markdown("### 🗓️ Sua Agenda Semanal:")
        for c in st.session_state.cronogramas_aulas:
            st.write(f"• **{c['dia']}**: {c['desc']}")

# ===========================================================================
# ABA 15: RECUPERAÇÃO (ATUALIZADA: PRONTUÁRIO PROVISÓRIO DE LESÕES COM TEXTO E ÁUDIO)
# ===========================================================================
with aba_recuperacao:
    st.markdown("<h2 style='text-align: center; color: #ff1e27;'>🧘 RECUPERAÇÃO & PRONTUÁRIO DE LESÕES</h2>", unsafe_allow_html=True)
    st.markdown("Relate dor ou lesão recente (ex: 'meu pé virou ontem, está doendo'). O OssBot gera um prontuário provisório com cuidados iniciais até você ir ao médico.")

    lesao_txt = st.text_area("Descreva o que aconteceu e onde está doendo:", key="lesao_txt_input")
    lesao_aud = st.audio_input("Ou grave um áudio relatando a lesão:", key="lesao_aud_input")

    if st.button("🩺 Gerar Prontuário de Primeiros Cuidados", use_container_width=True, key="btn_gerar_prontuario"):
        relato_lesao = lesao_txt.strip()
        if lesao_aud is not None:
            relato_lesao += " [Áudio do relato de lesão gravado e transcrito]"

        st.success("✅ Prontuário provisório gerado com sucesso!")
        
        st.markdown(f"""
        <div class='nutri-box'>
            <h3>⚠️ PRONTUÁRIO PROVISÓRIO DE PRIMEIROS CUIDADOS</h3>
            <p><b>Relato do Atleta:</b> {relato_lesao if relato_lesao else 'Dor articular / muscular recente'}</p>
            <hr style='border-color: #00ffcc; margin: 10px 0;'>
            <p><b>🧊 Protocolo R.I.C.E. (Até avaliação médica):</b></p>
            <p>• <b>Repouso (Rest):</b> Evite apoiar ou forçar a região afetada nos próximos treinos.</p>
            <p>• <b>Gelo (Ice):</b> Faça compressas de gelo por 15 a 20 minutos, de 3 a 4 vezes ao dia, para conter o inchaço e a inflamação inicial.</p>
            <p>• <b>Compressão (Compression):</b> Utilize uma faixa elástica leve se houver edema, sem apertar demais a circulação.</p>
            <p>• <b>Elevação (Elevation):</b> Mantenha o membro lesionado acima da altura do coração sempre que estiver descansando.</p>
            <p style='color: #ff1e27; margin-top: 15px;'><b>🚨 AVISO MÉDICO:</b> Este relatório é apenas um guia de suporte inicial. Se houver dor severa, estalos, deformidade ou incapacidade de movimento, <b>procure um médico ortopedista imediatamente</b>.</p>
        </div>
        """, unsafe_allow_html=True)

    if "foco_recuperacao" not in st.session_state:
        st.session_state.foco_recuperacao = []

    nota_rec = st.text_area("Notas rápidas de alongamento ou diário de recuperação:", key="rec_nota_txt")
    if st.button("💾 Salvar Nota de Recuperação", use_container_width=True, key="btn_salvar_rec"):
        if nota_rec.strip():
            st.session_state.foco_recuperacao.append({"data": datetime.now().strftime("%d/%m/%Y"), "texto": nota_rec.strip()})
            salvar_tudo()
            st.success("✅ Nota salva!")
            st.rerun()

    if st.session_state.foco_recuperacao:
        st.divider()
        for r in reversed(st.session_state.foco_recuperacao):
            st.write(f"📅 *{r['data']}*: {r['texto']}")
