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
# CSS - PALETA PRETO & VERMELHO PROFISSIONAL (GLOW UI)
# ---------------------------------------------------------------------------
CSS = """
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { background-color: #080808 !important; }
[data-testid="stSidebar"], [data-testid="stSidebar"] > div { background-color: #111111 !important; border-right: 1px solid #ff1e27 !important; }
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp p, .stApp li, .stApp label, .stApp summary { color: #ffffff; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * { color: #ff1e27 !important; }

div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="textarea"], div[data-baseweb="select"] > div { background-color: #161616 !important; border-color: #ff1e27 !important; border-radius: 10px !important; }
div[data-baseweb="input"] input, div[data-baseweb="base-input"] input, div[data-baseweb="textarea"] textarea, div[data-baseweb="base-input"] textarea, input, textarea { background-color: #161616 !important; color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; caret-color: #ffffff !important; font-weight: bold !important; }
input::placeholder, textarea::placeholder { color: #777777 !important; -webkit-text-fill-color: #777777 !important; opacity: 1 !important; }
div[data-baseweb="select"] * { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; }
div[data-baseweb="select"] svg { fill: #ff1e27 !important; }

[data-testid="stNumberInput"] button { background-color: #222222 !important; color: #ffffff !important; border: none !important; }

[data-testid="stFileUploaderDropzone"], [data-testid="stFileUploader"] section { background-color: #161616 !important; border: 2px dashed #ff1e27 !important; border-radius: 12px !important; }
[data-testid="stFileUploader"] * { color: #ffffff !important; }
[data-testid="stFileUploader"] svg { fill: #ff1e27 !important; }
[data-testid="stFileUploader"] button { background-color: #242424 !important; border: 2px solid #ff1e27 !important; }

.stButton > button, div[data-testid="stFormSubmitButton"] > button { border-radius: 12px !important; font-weight: bold !important; background-color: #cc0000 !important; color: #ffffff !important; border: 2px solid #ff1e27 !important; box-shadow: 0 4px 14px rgba(204,0,0,0.4) !important; transition: all 0.3s ease; }
.stButton > button p, div[data-testid="stFormSubmitButton"] > button p { color: #ffffff !important; }
.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover { background-color: #ff1e27 !important; border-color: #ffffff !important; color: #ffffff !important; box-shadow: 0 6px 20px rgba(255,30,39,0.7) !important; }

[data-testid="stExpander"] { background-color: #121212 !important; border: 1px solid #ff1e27 !important; border-radius: 12px !important; box-shadow: 0 4px 16px rgba(0,0,0,0.6); }
[data-testid="stForm"] { border: 1px solid #ff1e27 !important; border-radius: 14px !important; background-color: #121212 !important; padding: 15px; }

.placar-box, .nutri-box, .camp-box, .curso-box, .kids-box, .admin-box { color: #ffffff; border-radius: 16px; padding: 22px; margin-bottom: 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.8); }
.placar-box { background-color: #121212; border: 2px solid #ff1e27; text-align: center; }
.placar-numero { font-size: 52px; font-weight: bold; color: #ff1e27; text-shadow: 0 0 15px rgba(255,30,39,0.5); }
.nutri-box { background-color: #141414; border: 2px solid #00ffcc; }
.camp-box { background-color: #121212; border: 2px solid #ff1e27; }
.curso-box { background-color: #141414; border: 2px solid #ff4d4d; }
.kids-box { background-color: #141414; border: 2px solid #fbbf24; }
.badge-container { display: flex; gap: 10px; justify-content: center; margin-bottom: 20px; }
.badge { background-color: #161616; border: 1px solid #ff1e27; color: #ff1e27; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: bold; box-shadow: 0 0 10px rgba(255,30,39,0.3); }
.foto-bolinha { width: 90px; height: 90px; border-radius: 50%; object-fit: cover; border: 3px solid #ff1e27; display: block; margin: 0 auto 10px auto; box-shadow: 0 0 16px rgba(255,30,39,0.7); }
.bolinha-padrao { width: 90px; height: 90px; border-radius: 50%; background-color: #1a1a1a; border: 3px solid #ff1e27; display: flex; align-items: center; justify-content: center; font-size: 36px; margin: 0 auto 10px auto; box-shadow: 0 0 16px rgba(255,30,39,0.5); }
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
        <span class='badge'>🔥 Edição Preto & Vermelho Elite</span>
        <span class='badge'>🛡️ Acesso Seguro & Multi-Usuário</span>
        <span class='badge'>⚡ 15 Módulos Especializados</span>
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
                        st.toast("✅ Login realizado com sucesso!", icon="🥋")
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
                            st.toast("🎉 Conta criada com sucesso!", icon="🚀")
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
                            st.toast("✅ Senha redefinida com sucesso!", icon="🔑")
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
  #botoes-rolagem button { width: 64px; height: 64px; font-size: 28px; font-weight: bold; color: #ffffff; background-color: #cc0000; border: 2px solid #ff1e27; border-radius: 50%; cursor: pointer; box-shadow: 0 4px 16px rgba(255,30,39,0.6); }
  #botoes-rolagem button:hover { background-color: #ff1e27; box-shadow: 0 6px 20px rgba(255,30,39,0.9); }
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
# Barra lateral (Sidebar por Módulos Profissionais & Painel Master)
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
                st.toast("✅ Foto de perfil atualizada com sucesso!", icon="📸")
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
            st.toast("✅ Carteirinha salva com sucesso!", icon="💾")
            st.rerun()

    # PAINEL MASTER INTERATIVO - GESTÃO TOTAL DOS ALUNOS
    if st.session_state.is_admin:
        st.divider()
        st.markdown("## 👑 Painel Master")
        with st.expander("🛠️ Gestão de Alunos e Academias"):
            banco = carregar_banco_usuarios()
            st.write(f"📊 **Total de Contas:** {len(banco)}")
            st.divider()
            
            for usr, info in list(banco.items()):
                dados_usr = carregar_dados_usuario(usr)
                nome_usr = dados_usr.get("perfil_nome", "Sem Nome")
                academia_usr = dados_usr.get("perfil_academia", "Academia Não Informada")
                faixa_usr = dados_usr.get("perfil_faixa", "Branca")
                graus_usr = dados_usr.get("perfil_graus", 0)
                
                st.markdown(f"🏛️ **Academia:** <span style='color: #ff1e27; font-size: 15px; font-weight: bold;'>{esc(academia_usr)}</span>", unsafe_allow_html=True)
                st.markdown(f"👤 **Aluno:** {esc(nome_usr)} | Faixa {faixa_usr} ({graus_usr}º Grau)")
                st.caption(f"📧 `{usr}` | 📅 Criado: {info.get('data_criacao', 'S/D')}")
                
                # PAINEL DE GESTÃO DO ALUNO AO CLICAR
                with st.expander(f"⚙️ Gerenciar Aluno: {nome_usr}"):
                    with st.form(f"form_gestao_aluno_{usr}"):
                        st.markdown("### ✏️ Editar Credenciais")
                        novo_email_input = st.text_input("Novo E-mail (Login):", value=usr)
                        nova_senha_input = st.text_input("Nova Senha:", value=info.get("senha", ""), type="password")
                        
                        st.markdown("### 🥋 Graduação e Perfil")
                        novo_nome_input = st.text_input("Nome do Aluno:", value=nome_usr)
                        nova_faixa_input = st.selectbox(
                            "Nova Faixa:",
                            ["Branca", "Cinza", "Amarela", "Laranja", "Verde", "Azul", "Roxa", "Castanha", "Preta", "Vermelha e Preta", "Vermelha e Branca", "Vermelha"],
                            index=["Branca", "Cinza", "Amarela", "Laranja", "Verde", "Azul", "Roxa", "Castanha", "Preta", "Vermelha e Preta", "Vermelha e Branca", "Vermelha"].index(faixa_usr) if faixa_usr in ["Branca", "Cinza", "Amarela", "Laranja", "Verde", "Azul", "Roxa", "Castanha", "Preta", "Vermelha e Preta", "Vermelha e Branca", "Vermelha"] else 0
                        )
                        novos_graus_input = st.slider("Novos Graus:", 0, 11, int(graus_usr), key=f"slider_master_graus_{usr}")
                        
                        btn_salvar_gestao = st.form_submit_button("💾 Salvar Alterações do Aluno", use_container_width=True)
                        
                        if btn_salvar_gestao:
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
                                    # Atualiza credenciais no banco geral
                                    dados_antigos = banco_atualizado.pop(usr)
                                    dados_antigos["senha"] = nova_senha_input
                                    banco_atualizado[novo_email_limpo] = dados_antigos
                                    salvar_banco_usuarios(banco_atualizado)
                                    
                                    # Atualiza os dados do perfil do aluno no arquivo JSON dele
                                    dados_aluno_atual = carregar_dados_usuario(novo_email_limpo)
                                    dados_aluno_atual["perfil_nome"] = novo_nome_input
                                    dados_aluno_atual["perfil_faixa"] = nova_faixa_input
                                    dados_aluno_atual["perfil_graus"] = novos_graus_input
                                    salvar_dados_usuario(novo_email_limpo, dados_aluno_atual)
                                    
                                    # Renomeia o arquivo do usuário se o e-mail mudou
                                    caminho_antigo = obter_caminho_usuario(usr)
                                    caminho_novo = obter_caminho_usuario(novo_email_limpo)
                                    if os.path.exists(caminho_antigo) and caminho_antigo != caminho_novo:
                                        try:
                                            os.replace(caminho_antigo, caminho_novo)
                                        except Exception:
                                            pass
                                            
                                    st.toast("✅ Aluno atualizado com sucesso pelo Mestre!", icon="👑")
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
# Cabeçalho Principal (Header Bar de Elite)
# ---------------------------------------------------------------------------
col_esq, col_centro, col_dir = st.columns([1.2, 2.6, 1.2])
with col_esq:
    st.image("https://images.unsplash.com/photo-1517838277536-f5f99be501cd?q=80&w=600&auto=format&fit=crop",
             caption="Técnica e Combate", use_container_width=True)
with col_centro:
    st.markdown("<h1 style='text-align: center; color: #ff1e27;'>🥋 OssBot App Pro</h1>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center; color: #ffffff;'>Atleta: {esc(st.session_state.get('perfil_nome', 'Atleta'))} | Faixa {esc(st.session_state.get('perfil_faixa', 'Branca'))} ({st.session_state.get('perfil_graus', 0)}º Grau)</h4>", unsafe_allow_html=True)
    st.markdown(f"<h5 style='text-align: center; color: #ff1e27;'>{esc(st.session_state.get('perfil_academia', 'Academia BJJ'))} | {esc(st.session_state.get('perfil_status', 'Atleta'))}</h5>", unsafe_allow_html=True)
with col_dir:
    st.image("https://images.unsplash.com/photo-1555597673-b21d5c935865?q=80&w=600&auto=format&fit=crop",
             caption="Faixa Preta — Tradição", use_container_width=True)

st.divider()

# DEFINIÇÃO DAS 15 ABAS DIVIDIDAS POR MÓDULOS PROFISSIONAIS
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
        st.toast("✅ Luta salva na memória!", icon="🤼")

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
    st.caption("Você pode digitar no campo de texto e/ou gravar um áudio descrevendo sua rotina!")

    jogo_texto = st.text_area("Descreva seu estilo de jogo (Ex: Sou passador, gosto de dar quedas e treino 2h por dia):", key="camp_jogo_txt")
    jogo_audio = st.audio_input("Ou grave um áudio descrevendo seu jogo:", key="camp_jogo_aud")

    if st.button("🚀 Gerar Estratégia de Campeonato", use_container_width=True, key="btn_plan_camp"):
        texto_jogo_final = jogo_texto.strip()
        if jogo_audio is not None:
            texto_jogo_final += " [Áudio do jogo gravado com sucesso]"

        dica_peso = ""
        if diferenca_peso > 0:
            dica_peso = f"⚠️ Você precisa perder **{diferenca_peso:.1f} kg** até a pesagem! Foco em hidratação e reeducação alimentar suave."
        elif diferenca_peso < 0:
            dica_peso = f"✅ Você está **{abs(diferenca_peso):.1f} kg** abaixo do limite! Pode manter sua alimentação atual com bons carboidratos."
        else:
            dica_peso = "🎯 Você está cravado no peso exato da categoria! Mantenha a estabilidade."

        mostrar_html(f"""
        <div class='camp-box'>
            <h3 style='color: #ff1e27;'>🥇 GUIA TÁTICO PERSONALIZADO</h3>
            <p><b>Faixa:</b> {esc(faixa_final or "Não informada")}</p>
            <p><b>Tempo Restante:</b> {dias_restantes} dia(s) até a competição.</p>
            <p><b>Estratégia de Peso:</b> {dica_peso}</p>
            <p><b>Análise do Seu Jogo:</b> {esc(texto_jogo_final if texto_jogo_final else "Jogo padrão de combate")}</p>
            <hr>
            <p><b>Recomendação Tática:</b> Mantenha a intensidade alta nas próximas semanas e inicie a desaceleração (tapering) a 3 dias do campeonato. Oss!</p>
        </div>
        """)

# ===========================================================================
# ABA 5: CURSOS
# ===========================================================================
with aba_cursos:
    st.markdown("<h2 style='text-align: center; color: #ff4d4d;'>📚 MANUAL DE REGRAS & CURSOS BJJ</h2>", unsafe_allow_html=True)

    with st.form(key="form_curso_interativo"):
        st.markdown("### ➕ Adicionar Material / Anotação de Curso")
        titulo_curso = st.text_input("Título do Módulo / Regra:")
        desc_curso = st.text_area("Descrição ou Anotações:")
        foto_curso = st.file_uploader("Enviar Foto:", type=["jpg", "png", "jpeg"], key="up_curso")
        btn_salvar_curso = st.form_submit_button("💾 Salvar Material")

        if btn_salvar_curso:
            if titulo_curso.strip() and desc_curso.strip():
                st.session_state.cursos_interativos.append({
                    "titulo": titulo_curso.strip(),
                    "descricao": desc_curso.strip(),
                })
                salvar_tudo()
                st.toast("✅ Material salvo!", icon="📚")

    if st.session_state.cursos_interativos:
        st.markdown("### 📂 Seus Materiais Cadastrados:")
        for ci in st.session_state.cursos_interativos:
            mostrar_html(f"""
            <div class='curso-box'>
                <h3>📚 {esc(ci['titulo'])}</h3>
                <p>{esc(ci['descricao'])}</p>
            </div>
            """)

# ===========================================================================
# ABA 6: AULAS KIDS
# ===========================================================================
with aba_kids:
    st.markdown("<h2 style='text-align: center; color: #fbbf24;'>👶 AULAS & DINÂMICAS KIDS</h2>", unsafe_allow_html=True)

    with st.form(key="form_kids"):
        nome_kids = st.text_input("Nome da Brincadeira:", placeholder="Ex: Pega-Pega do Guardeiro")
        desc_kids = st.text_area("Explicação da Dinâmica:", placeholder="Descreva a brincadeira...")
        audio_kids_input = st.audio_input("Ou Grave um Áudio:")
        btn_add_kids = st.form_submit_button("💾 Salvar Dinâmica Kids")

        if btn_add_kids:
            texto_final_desc = desc_kids.strip()
            if audio_kids_input is not None:
                texto_final_desc += " [Áudio gravado]"
            if nome_kids.strip() and texto_final_desc:
                st.session_state.dinamic_kids_custom.append({"titulo": nome_kids.strip(), "descricao": texto_final_desc})
                salvar_tudo()
                st.toast("✅ Dinâmica Kids salva!", icon="👶")

    if st.session_state.dinamic_kids_custom:
        for dk in st.session_state.dinamic_kids_custom:
            mostrar_html(f"""
            <div class='kids-box'>
                <h3>🧸 {esc(dk['titulo'])}</h3>
                <p>{esc(dk['descricao'])}</p>
            </div>
            """)

# ===========================================================================
# ABA 7: DRILLS
# ===========================================================================
with aba_drills:
    st.markdown("<h2 style='text-align: center; color: #ff1e27;'>⏱️ DRILLS & HIIT DE COMBATE</h2>", unsafe_allow_html=True)
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        t_acao = st.number_input("Tempo de Ação (s):", 10, 120, 30, 5, key="d_a")
    with col_d2:
        t_pausa = st.number_input("Tempo de Pausa (s):", 5, 60, 10, 5, key="d_p")
    with col_d3:
        n_rounds = st.number_input("Rounds:", 1, 30, 8, 1, key="d_r")

    if st.button("▶️ Iniciar Cronômetro", use_container_width=True, key="btn_iniciar_drills_local"):
        st.toast(f"✅ Configurado: {n_rounds} rounds!", icon="⏱️")

# ===========================================================================
# ABA 8: PRESSÃO
# ===========================================================================
with aba_pressao:
    st.markdown("<h2 style='text-align: center; color: #ff1e27;'>🧠 PRESSÃO DE LUTA - FLASHCARDS</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Estude posições difíceis e saídas de sufoco.</p>", unsafe_allow_html=True)

    with st.form(key="form_pressao_flashcard"):
        pergunta_flash = st.text_input("Situação / Perigo:")
        resposta_flash = st.text_area("Resposta / Solução Tática:")
        btn_salvar_flash = st.form_submit_button("💾 Salvar Flashcard")
        if btn_salvar_flash:
            if pergunta_flash.strip() and resposta_flash.strip():
                st.session_state.flashcards_pressao.append(
                    {"pergunta": pergunta_flash.strip(), "resposta": resposta_flash.strip()}
                )
                salvar_tudo()
                st.toast("✅ Flashcard salvo!", icon="🧠")

    if st.session_state.flashcards_pressao:
        for idx, fc in enumerate(st.session_state.flashcards_pressao):
            with st.expander(f"⚡ Situação {idx + 1}: {fc['pergunta']}"):
                mostrar_html(f"<div class='camp-box'><p><b>Saída:</b> {esc(fc['resposta'])}</p></div>")

# ===========================================================================
# ABA 9: GRADUAÇÃO
# ===========================================================================
with aba_grad:
    st.markdown("<h2 style='text-align: center; color: #34d399;'>🥇 GRADUAÇÃO & DIÁRIO DE FAIXA</h2>", unsafe_allow_html=True)

    with st.form(key="form_cadastra_aluno_grad"):
        nome_aluno_g = st.text_input("Nome Completo do Aluno:")
        faixa_atual_g = st.selectbox("Faixa Atual:", ["Branca", "Cinza", "Amarela", "Laranja", "Verde", "Azul", "Roxa", "Castanha", "Preta"])
        graus_atuais_g = st.slider("Graus Atuais:", 0, 4, 0)
        data_inicio_g = st.date_input("Data de Início na Faixa:")
        btn_salv_grad = st.form_submit_button("➕ Salvar Aluno")

        if btn_salv_grad:
            if nome_aluno_g.strip():
                st.session_state.alunos_graduacao.append({
                    "nome": nome_aluno_g.strip(),
                    "faixa": faixa_atual_g,
                    "graus": graus_atuais_g,
                    "data_inicio": data_inicio_g.strftime("%d/%m/%Y"),
                })
                salvar_tudo()
                st.toast(f"✅ Aluno {nome_aluno_g} cadastrado!", icon="🥇")

    if st.session_state.alunos_graduacao:
        for aluno in st.session_state.alunos_graduacao:
            with st.expander(f"🥋 {aluno['nome']} - Faixa {aluno['faixa']} ({aluno['graus']}º Grau)"):
                st.write(f"• **Início na faixa:** {aluno['data_inicio']}")

# ===========================================================================
# ABA 10: KIMONO
# ===========================================================================
with aba_kimono:
    st.markdown("<h2 style='text-align: center; color: #ff1e27;'>🥋 GESTÃO E CUIDADOS COM O KIMONO</h2>", unsafe_allow_html=True)

    nota_kimono = st.text_area("Anotações do Kimono:", placeholder="Lavar com água fria...", key="nota_kimono")
    if st.button("💾 Salvar Nota", use_container_width=True, key="btn_salvar_kimono"):
        if nota_kimono.strip():
            st.session_state.notas_kimono.append(
                {"data": datetime.now().strftime("%d/%m/%Y"), "nota": nota_kimono.strip()}
            )
            salvar_tudo()
            st.toast("✅ Nota salva!", icon="🥋")

    for n in reversed(st.session_state.notas_kimono):
        mostrar_html(f"<div class='curso-box'><p><b>{esc(n['data'])}</b></p><p>{esc(n['nota'])}</p></div>")

# ===========================================================================
# ABA 11: CARD VITÓRIA
# ===========================================================================
with aba_card:
    st.markdown("<h2 style='text-align: center; color: #ff1e27;'>📸 CARD DE VITÓRIA</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Crie seu card personalizado com foto, texto e comemore suas conquistas no tatame!</p>", unsafe_allow_html=True)

    foto_card_up = st.file_uploader("Enviar Foto da Vitória (Arquivos):", type=["jpg", "png", "jpeg"], key="up_card")
    foto_card_cam = st.camera_input("Ou Tire uma Foto com a Câmera:", key="cam_card")
    legenda_card = st.text_area("Legenda / Frase do Card:",
                                value="Tatame lavado, missão cumprida por hoje! 🥋🔥 OSS! #BJJ #OssBot",
                                key="legenda_card")

    if st.button("🚀 Gerar Card de Vitória", use_container_width=True, key="btn_gerar_card"):
        st.toast("✅ Card gerado com sucesso!", icon="📸")
        foto_final = foto_card_cam or foto_card_up
        if foto_final is not None:
            st.image(foto_final, use_container_width=True)
        mostrar_html(f"<div class='placar-box' style='border: 2px solid #ff1e27;'><h3 style='color: #ff1e27;'>🏆 CARD OFICIAL OSSBOT</h3><p style='font-size: 18px; font-weight: bold;'>{esc(legenda_card)}</p></div>")

# ===========================================================================
# ABA 12: CADERNETA DE ALUNOS
# ===========================================================================
with aba_caderneta:
    st.markdown("<h2 style='text-align: center; color: #fbbf24;'>📇 CADERNETA DE ALUNOS & FREQUÊNCIA</h2>", unsafe_allow_html=True)
    novo_aluno = st.text_input("Digite o Nome do Aluno:", placeholder="Ex: Lucas Gabriel", key="input_novo_aluno")
    if st.button("➕ Adicionar Aluno à Turma", use_container_width=True, key="btn_add_aluno"):
        if novo_aluno.strip():
            st.session_state.lista_alunos_academia.append(novo_aluno.strip())
            salvar_tudo()
            st.toast(f"✅ Aluno {novo_aluno} adicionado com sucesso!", icon="📇")
        else:
            st.warning("Digite o nome do aluno.")

    if st.session_state.lista_alunos_academia:
        st.markdown("### 📋 Lista de Alunos Cadastrados:")
        for idx, aluno in enumerate(st.session_state.lista_alunos_academia):
            col_al1, col_al2 = st.columns([3, 1])
            with col_al1:
                st.write(f"🥋 {aluno}")
            with col_al2:
                if st.button("Presença ✔️", key=f"pres_{idx}"):
                    st.toast(f"✅ Presença confirmada para {aluno}!")

# ===========================================================================
# ABA 13: CHAVES DE TORNEIO
# ===========================================================================
with aba_chaves:
    st.markdown("<h2 style='text-align: center; color: #ff1e27;'>⏱️ ORGANIZADOR DE CHAVES DE LUTA</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Organize os confrontos dos atletas de forma limpa e visível.</p>", unsafe_allow_html=True)

    nomes_atletas_txt = st.text_area("Digite os nomes dos atletas (um por linha):",
                                     placeholder="Atleta 1\nAtleta 2\nAtleta 3\nAtleta 4",
                                     key="txt_atletas_chave")

    if st.button("⚔️ Gerar Chaves de Luta", use_container_width=True, key="btn_gerar_chave"):
        atletas = [a.strip() for a in nomes_atletas_txt.split("\n") if a.strip()]
        if len(atletas) < 2:
            st.warning("Digite pelo menos 2 atletas para gerar os confrontos!")
        else:
            mostrar_html("<div class='placar-box'><h3 style='color: #ff1e27;'>⚔️ CONFRONTOS GERADOS</h3></div>")
            for i in range(0, len(atletas) - 1, 2):
                mostrar_html(
                    f"<div style='background-color: #1a1a1a; padding: 10px; border-radius: 8px; margin-bottom: 8px; border: 1px solid #ff1e27;'>"
                    f"<h4 style='color: #ffffff; margin:0;'>🥊 Luta: <span style='color: #ff1e27;'>{esc(atletas[i])}</span> "
                    f"vs <span style='color: #ffffff;'>{esc(atletas[i + 1])}</span></h4></div>"
                )
            if len(atletas) % 2 != 0:
                st.info(f"✨ Atleta aguardando vencedores (Bye): {atletas[-1]}")

# ===========================================================================
# ABA 14: CRONOGRAMA DE AULAS
# ===========================================================================
with aba_cronograma:
    st.markdown("<h2 style='text-align: center; color: #ff4d4d;'>📋 CRONOGRAMA DE AULAS DA SEMANA</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Planeje os temas técnicos das suas aulas para a semana toda.</p>", unsafe_allow_html=True)

    with st.form(key="form_cronograma"):
        dia_semana = st.selectbox("Dia da Semana:", ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado"])
        tema_aula = st.text_input("Tema da Aula (Ex: Passagem de Guarda Emborcando):")
        detalhes_aula = st.text_area("Técnicas / Exercícios Específicos:")
        btn_crono = st.form_submit_button("💾 Salvar Cronograma")

        if btn_crono:
            if tema_aula.strip():
                st.session_state.cronogramas_aulas.append({
                    "dia": dia_semana,
                    "tema": tema_aula.strip(),
                    "detalhes": detalhes_aula.strip()
                })
                salvar_tudo()
                st.toast(f"✅ Aula de {dia_semana} planejada com sucesso!", icon="📋")
            else:
                st.warning("Preencha o tema da aula!")

    st.divider()
    if st.session_state.cronogramas_aulas:
        st.markdown("### 🗓️ Aulas Agendadas:")
        for cr in st.session_state.cronogramas_aulas:
            mostrar_html(f"""
            <div class='curso-box'>
                <h3 style='color: #ff1e27;'>📅 {esc(cr['dia'])}: {esc(cr['tema'])}</h3>
                <p>{esc(cr['detalhes'])}</p>
            </div>
            """)

# ===========================================================================
# ABA 15: RECUPERAÇÃO & PRONTUÁRIO
# ===========================================================================
with aba_recuperacao:
    st.markdown("<h2 style='text-align: center; color: #ff1e27;'>🧘 RECUPERAÇÃO & PRONTUÁRIO RÁPIDO</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Descreva sua lesão ou dor para gerar um guia de primeiros socorros!</p>", unsafe_allow_html=True)

    lesao_texto = st.text_area("Descreva o que aconteceu ou onde está doendo (Ex: Torci o tornozelo caindo de mau jeito):", key="recup_txt")
    lesao_audio = st.audio_input("Ou grave um áudio descrevendo sua lesão:", key="recup_aud")

    if st.button("🩹 Gerar Prontuário de Primeiros Socorros", use_container_width=True, key="btn_gerar_prontuario"):
        relato_final = lesao_texto.strip()
        if lesao_audio is not None:
            relato_final += " [Áudio gravado com o relato da dor]"

        mostrar_html(f"""
        <div class='nutri-box' style='border: 2px solid #ff1e27;'>
            <h3 style='color: #ff1e27;'>📋 PRONTUÁRIO TÁTICO DE PRIMEIROS SOCORROS</h3>
            <p><b>Seu Relato:</b> {esc(relato_final if relato_final else "Dor / Desconforto geral pós-treino")}</p>
            <hr>
            <h4>🚨 Orientações Imediatas (Protocolo R.I.C.E.):</h4>
            <p>1. <b>Repouso:</b> Evite carregar peso ou forçar a articulação afetada.</p>
            <p>2. <b>Gelo (Crio):</b> Aplique compressa de gelo por 15 a 20 minutos a cada 3 horas.</p>
            <p>3. <b>Compressão:</b> Se houver inchaço, use uma enfaixagem elástica sem apertar demais.</p>
            <p>4. <b>Elevação:</b> Mantenha o membro elevado acima do nível do coração quando descansar.</p>
            <p>⚠️ <b>Aviso Importante:</b> Se houver dor severa, deformidade visível ou incapacidade de se mover, procure um médico imediatamente!</p>
        </div>
        """)

# ---------------------------------------------------------------------------
# ETAPA 1: Sistema de Alertas Visuais & Notificações de Elite
# ---------------------------------------------------------------------------
def mostrar_alerta_tatame(tipo, mensagem):
    """Exibe um card de alerta estilizado com a identidade visual do OssBot"""
    cores = {
        "sucesso": ("#00ffcc", "✅"),
        "aviso": ("#fbbf24", "⚠️"),
        "erro": ("#ff1e27", "❌"),
        "info": ("#ffffff", "ℹ️")
    }
    cor, icone = cores.get(tipo, ("#ff1e27", "🥋"))
    st.markdown(f"""
    <div style='background-color: #121212; border-left: 5px solid {cor}; border: 1px solid {cor}; border-radius: 10px; padding: 14px 18px; margin-bottom: 15px; box-shadow: 0 4px 16px rgba(0,0,0,0.6);'>
        <p style='color: #ffffff; margin: 0; font-size: 15px; font-weight: bold;'>{icone} {esc(mensagem)}</p>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# ETAPA 2: Dashboard de Estatísticas & Gráficos da Academia (Painel Master)
# ---------------------------------------------------------------------------
def renderizar_dashboard_academia():
    """Renderiza gráficos e métricas gerais de todos os alunos da academia"""
    st.markdown("<h2 style='text-align: center; color: #ff1e27;'>📊 DASHBOARD EXECUTIVO DA ACADEMIA</h2>", unsafe_allow_html=True)
    
    banco = carregar_banco_usuarios()
    total_alunos = len(banco)
    
    # Coleta dados de todos os alunos cadastrados
    faixas_contagem = {
        "Branca": 0, "Cinza": 0, "Amarela": 0, "Laranja": 0, 
        "Verde": 0, "Azul": 0, "Roxa": 0, "Castanha": 0, "Preta": 0
    }
    
    total_lutas_geral = 0
    
    for usr in banco.keys():
        dados_usr = carregar_dados_usuario(usr)
        f_atual = dados_usr.get("perfil_faixa", "Branca")
        if f_atual in faixas_contagem:
            faixas_contagem[f_atual] += 1
        else:
            faixas_contagem["Branca"] += 1
            
        total_lutas_geral += len(dados_usr.get("historico_lutas", []))

    # Exibição de Métricas Principais (KPIs)
    col_k1, col_k2, col_k3 = st.columns(3)
    with col_k1:
        mostrar_html(f"""
        <div class='placar-box' style='padding: 15px;'>
            <p style='color: #cccccc; margin: 0; font-size: 14px;'>TOTAL DE ATLETAS</p>
            <h2 style='color: #ff1e27; margin: 5px 0 0 0; font-size: 38px;'>{total_alunos}</h2>
        </div>
        """)
    with col_k2:
        mostrar_html(f"""
        <div class='placar-box' style='padding: 15px;'>
            <p style='color: #cccccc; margin: 0; font-size: 14px;'>LUTAS REGISTRADAS</p>
            <h2 style='color: #00ffcc; margin: 5px 0 0 0; font-size: 38px;'>{total_lutas_geral}</h2>
        </div>
        """)
    with col_k3:
        mostrar_html(f"""
        <div class='placar-box' style='padding: 15px;'>
            <p style='color: #cccccc; margin: 0; font-size: 14px;'>STATUS DO SISTEMA</p>
            <h2 style='color: #fbbf24; margin: 5px 0 0 0; font-size: 28px;'>🟢 ATIVO</h2>
        </div>
        """)

    st.divider()
    st.markdown("### 📈 Distribuição de Faixas na Academia")
    
    # Exibe gráfico em barras nativo do Streamlit com as faixas
    faixas_filtradas = {k: v for k, v in faixas_contagem.items() if v > 0}
    if faixas_filtradas:
        st.bar_chart(faixas_filtradas, color="#ff1e27")
    else:
        st.info("Nenhum dado de faixa registrado ainda.")

# ---------------------------------------------------------------------------
# ETAPA 3: Sistema de Gamificação & Badges de Conquista
# ---------------------------------------------------------------------------
def verificar_e_conceder_badges():
    """Calcula e retorna as badges conquistadas com base na atividade do usuário"""
    badges = []
    
    # Badge de Lutas
    total_lutas = len(st.session_state.get("historico_lutas", []))
    if total_lutas >= 1:
        badges.append(("🤼 Guerreiro do Tatame", "Registrou a primeira luta no sistema!"))
    if total_lutas >= 5:
        badges.append(("🔥 Atleta Dedicado", "Já registrou 5 ou mais lutas de treino!"))
        
    # Badge de Cursos / Regras
    total_cursos = len(st.session_state.get("cursos_interativos", []))
    if total_cursos >= 1:
        badges.append(("📚 Estudioso da Arte", "Cadastrou material ou regras de BJJ!"))
        
    # Badge de Competidor
    if st.session_state.get("perfil_status") == "Atleta Competidor 🏆":
        badges.append(("🏆 Competidor Elite", "Perfil configurado como Atleta de Competição!"))
        
    return badges


def renderizar_secao_gamificacao():
    """Exibe as conquistas e medalhas do usuário na interface"""
    st.markdown("<h3 style='color: #fbbf24;'>🏅 Suas Conquistas & Badges</h3>", unsafe_allow_html=True)
    conquistas = verificar_e_conceder_badges()
    
    if not conquistas:
        st.info("Complete atividades no app (como registrar lutas ou adicionar estudos) para desbloquear badges!")
    else:
        cols_b = st.columns(len(conquistas) if len(conquistas) <= 3 else 3)
        for idx, (titulo_badge, desc_badge) in enumerate(conquistas):
            with cols_b[idx % len(cols_b)]:
                mostrar_html(f"""
                <div style='background-color: #161616; border: 1px solid #fbbf24; border-radius: 12px; padding: 12px; text-align: center; margin-bottom: 10px;'>
                    <h4 style='color: #fbbf24; margin: 0 0 5px 0; font-size: 14px;'>{esc(titulo_badge)}</h4>
                    <p style='color: #cccccc; margin: 0; font-size: 12px;'>{esc(desc_badge)}</p>
                </div>
                """)

# ---------------------------------------------------------------------------
# ETAPA 4: Gerador de Relatórios Profissionais em PDF para Atletas
# ---------------------------------------------------------------------------
def gerar_relatorio_pdf_atleta():
    """Gera um resumo formatado em texto simulando um relatório oficial para download"""
    nome = st.session_state.get("perfil_nome", "Atleta")
    faixa = st.session_state.get("perfil_faixa", "Branca")
    graus = st.session_state.get("perfil_graus", 0)
    academia = st.session_state.get("perfil_academia", "Academia BJJ")
    status = st.session_state.get("perfil_status", "Atleta")
    email = st.session_state.get("usuario_email", "")
    total_lutas = len(st.session_state.get("historico_lutas", []))
    
    conteudo_relatorio = f"""
=====================================================
          OSSBOT PRO - RELATÓRIO OFICIAL DE ATLETA
=====================================================
Data de Emissão: {datetime.now().strftime('%d/%m/%Y - %H:%M')}

[DADOS DO ATLETA]
• Nome Completo: {nome}
• E-mail de Contato: {email}
• Academia / Equipe: {academia}
• Graduação: Faixa {faixa} ({graus}º Grau)
• Status Profissional: {status}

[RESUMO DE ATIVIDADES]
• Total de Lutas Registradas: {total_lutas}
• Total de Dinâmicas Kids: {len(st.session_state.get("dinamic_kids_custom", []))}
• Flashcards de Pressão Salvos: {len(st.session_state.get("flashcards_pressao", []))}
• Materiais de Cursos Salvos: {len(st.session_state.get("cursos_interativos", []))}

=====================================================
OssBot Pro - Plataforma Inteligente de Gestão de BJJ
=====================================================
"""
    return conteudo_relatorio


def renderizar_botao_relatorio_pdf():
    """Exibe o botão de download do relatório em formato de texto/documento"""
    st.markdown("### 📄 Relatório Executivo & Prontuário")
    st.markdown("<p style='color: #cccccc;'>Baixe o relatório completo com suas estatísticas e dados de graduação.</p>", unsafe_allow_html=True)
    
    relatorio_texto = gerar_relatorio_pdf_atleta()
    
    st.download_button(
        "📥 Baixar Relatório Oficial (.txt / Relatório)",
        data=relatorio_texto,
        file_name=f"relatorio_ossbot_{st.session_state.get('perfil_nome', 'atleta').lower().replace(' ', '_')}.txt",
        mime="text/plain",
        use_container_width=True,
        help="Baixe o documento oficial resumido com todas as suas informações do tatame."
    )

# ---------------------------------------------------------------------------
# INTEGRAÇÃO VISUAL FINAL: Exibindo Badges, Dashboard e Relatórios na Tela
# ---------------------------------------------------------------------------

# 1. Adicionando as Badges na Barra Lateral (se o usuário estiver logado)
if st.session_state.get("autenticado"):
    with st.sidebar:
        st.divider()
        renderizar_secao_gamificacao()

# 2. Adicionando o Dashboard Executivo e Relatório no Painel Master (para o Admin)
if st.session_state.get("is_admin"):
    st.divider()
    renderizar_dashboard_academia()
    st.divider()
    renderizar_botao_relatorio_pdf()
