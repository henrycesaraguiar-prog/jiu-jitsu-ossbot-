import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, date
import os
import json
import base64
import traceback
import pandas as pd

# Configuração inicial da página
st.set_page_config(
    page_title="OssBot Pro - Gestão Profissional de BJJ",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constantes globais do Fundador
EMAIL_ADMIN_MASTER = "henry.cesaraguiar@gmail.com"
SENHA_ADMIN_MASTER = "adminpassword"

CAMPOS = [
    "perfil_nome", "perfil_faixa", "perfil_graus", "perfil_academia", 
    "perfil_peso", "perfil_status", "perfil_foto_b64", "historico_lutas", 
    "cursos_interativos", "dinamic_kids_custom", "flashcards_pressao", 
    "alunos_graduacao", "notas_kimono", "cronogramas_aulas", "dicas_nutricao",
    "camp_competicao", "drills_treino", "chaves_luta", "recuperacao_notas",
    "historico_presencas", "tipo_usuario"
]

def esc(texto):
    if not isinstance(texto, str):
        texto = str(texto)
    return (texto.replace("&", "&amp;")
                 .replace("<", "&lt;")
                 .replace(">", "&gt;")
                 .replace('"', "&quot;")
                 .replace("'", "&#39;"))

def mostrar_html(html_code):
    st.markdown(html_code, unsafe_allow_html=True)

def obter_caminho_usuarios():
    return "usuarios_banco.json"

def obter_caminho_usuario(email):
    email_limpo = email.strip().lower().replace("@", "_at_").replace(".", "_")
    return f"usuario_{email_limpo}.json"

def carregar_banco_usuarios():
    caminho = obter_caminho_usuarios()
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {
        EMAIL_ADMIN_MASTER.lower(): {
            "senha": SENHA_ADMIN_MASTER,
            "tipo_usuario": "Master (Fundador)",
            "is_admin": True,
            "plano": "ativo",
            "data_criacao": datetime.now().strftime("%d/%m/%Y - %H:%M")
        }
    }

def salvar_banco_usuarios(banco):
    caminho = obter_caminho_usuarios()
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(banco, f, ensure_ascii=False, indent=2)

def carregar_dados_usuario(email):
    caminho = obter_caminho_usuario(email)
    
    is_master_global = (email.strip().lower() == EMAIL_ADMIN_MASTER.lower())
    
    nome_padrao = "Henry Cesar" if is_master_global else "Atleta Visitante"
    academia_padrao = "GRACIE BARRA ALPHAVILLE ESPLANADA" if is_master_global else "Insira a sua Academia"
    status_padrao = "Atleta Competidor 🏆" if is_master_global else "Visitante / Novo Atleta"
    
    dados_padrao = {
        "perfil_nome": nome_padrao,
        "perfil_faixa": "Branca",
        "perfil_graus": 5 if is_master_global else 0,
        "perfil_academia": academia_padrao,
        "perfil_peso": "Médio",
        "perfil_status": status_padrao,
        "perfil_foto_b64": "",
        "tipo_usuario": "Master (Fundador)" if is_master_global else "Atleta",
        "historico_lutas": [],
        "cursos_interativos": [],
        "dinamic_kids_custom": [],
        "flashcards_pressao": [],
        "alunos_graduacao": [],
        "notas_kimono": [],
        "cronogramas_aulas": [],
        "dicas_nutricao": [],
        "camp_competicao": [],
        "drills_treino": [],
        "chaves_luta": [],
        "recuperacao_notas": [],
        "historico_presencas": []
    }
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                dados_salvos = json.load(f)
                for k, v in dados_padrao.items():
                    if k not in dados_salvos:
                        dados_salvos[k] = v
                return dados_salvos
        except Exception:
            return dados_padrao
    return dados_padrao

def salvar_dados_usuario(email, dados):
    caminho = obter_caminho_usuario(email)
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

def carregar_usuario(email):
    email_l = email.lower()
    st.session_state.usuario_email = email_l
    banco = carregar_banco_usuarios()
    
    info_banco = banco.get(email_l, {})
    is_master_global = (email_l == EMAIL_ADMIN_MASTER.lower())
    is_admin_banco = info_banco.get("is_admin", False)
    
    st.session_state.is_admin = (is_master_global or is_admin_banco)
    st.session_state.tipo_usuario = info_banco.get("tipo_usuario", "Atleta")
    
    dados = carregar_dados_usuario(email_l)
    for c in CAMPOS:
        st.session_state[c] = dados.get(c, {})

def salvar_tudo():
    email = st.session_state.get("usuario_email")
    if email:
        dados = {}
        for c in CAMPOS:
            dados[c] = st.session_state.get(c)
        salvar_dados_usuario(email, dados)

def fazer_logout():
    st.session_state.autenticado = False
    st.session_state.usuario_email = ""
    st.session_state.is_admin = False
    st.session_state.tipo_usuario = "Atleta"
    # Limpa completamente os campos da sessão para o próximo utilizador entrar limpo
    for c in CAMPOS:
        if c in st.session_state:
            del st.session_state[c]
    st.rerun()

# Inicialização segura dos estados de sessão
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if "usuario_email" not in st.session_state: st.session_state.usuario_email = ""
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "tipo_usuario" not in st.session_state: st.session_state.tipo_usuario = "Atleta"

for p_key in ["pts_a", "vant_a", "pun_a", "pts_b", "vant_b", "pun_b"]:
    if p_key not in st.session_state:
        st.session_state[p_key] = 0

if "tempo_segundos" not in st.session_state: st.session_state.tempo_segundos = 300
if "cronometro_rodando" not in st.session_state: st.session_state.cronometro_rodando = False

# Estilização CSS Glow UI
st.markdown("""
<style>
    .stApp { background-color: #0b0b0b; color: #ffffff; }
    .placar-box { background-color: #161616; border: 2px solid #ff1e27; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 4px 20px rgba(255, 30, 39, 0.2); }
    .placar-numero { font-size: 50px; font-weight: bold; color: #ff1e27; }
    .card-item { background-color: #141414; border-left: 4px solid #ff1e27; border-radius: 8px; padding: 15px; margin-bottom: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.5); }
    .foto-bolinha { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 2px solid #ff1e27; display: block; margin: 0 auto 10px auto; }
    .bolinha-padrao { width: 80px; height: 80px; border-radius: 50%; background-color: #1a1a1a; border: 2px solid #ff1e27; display: flex; align-items: center; justify-content: center; font-size: 30px; margin: 0 auto 10px auto; }
    .ia-erro-card { background-color: #1a0808; border: 2px solid #ff1e27; border-radius: 10px; padding: 20px; margin: 20px 0; }
</style>
""", unsafe_allow_html=True)

def somar(lado, campo, valor):
    chave_completa = f"{campo}_{lado}"
    if chave_completa not in st.session_state:
        st.session_state[chave_completa] = 0
    st.session_state[chave_completa] += valor

def definir_tempo(): st.session_state.tempo_segundos = st.session_state.get("select_tempo", 5) * 60
def iniciar_cronometro(): st.session_state.cronometro_rodando = True
def pausar_cronometro(): st.session_state.cronometro_rodando = False
def zerar_luta():
    st.session_state.cronometro_rodando = False
    st.session_state.tempo_segundos = st.session_state.get("select_tempo", 5) * 60
    st.session_state.pts_a = st.session_state.vant_a = st.session_state.pun_a = 0
    st.session_state.pts_b = st.session_state.vant_b = st.session_state.pun_b = 0

def verificar_e_conceder_badges():
    badges = []
    total_lutas = len(st.session_state.get("historico_lutas", []))
    if total_lutas >= 1: badges.append(("🤼 Guerreiro do Tatame", "Registou a primeira luta!"))
    if total_lutas >= 5: badges.append(("🔥 Atleta Dedicado", "5+ lutas registadas!"))
    if len(st.session_state.get("cursos_interativos", [])) >= 1: badges.append(("📚 Estudioso da Arte", "Registo de material de BJJ!"))
    if st.session_state.get("perfil_status") == "Atleta Competidor 🏆": badges.append(("🏆 Competidor Elite", "Perfil de Competição ativo!"))
    return badges

def renderizar_secao_gamificacao():
    st.markdown("<h3 style='color: #fbbf24;'>🏅 Conquistas & Badges</h3>", unsafe_allow_html=True)
    conquistas = verificar_e_conceder_badges()
    if not conquistas:
        st.info("Complete atividades para desbloquear badges!")
    else:
        for titulo, desc in conquistas:
            mostrar_html(f"""
            <div style='background-color: #161616; border: 1px solid #fbbf24; border-radius: 8px; padding: 8px; margin-bottom: 6px;'>
                <h4 style='color: #fbbf24; margin: 0 0 2px 0; font-size: 12px;'>{esc(titulo)}</h4>
                <p style='color: #cccccc; margin: 0; font-size: 10px;'>{esc(desc)}</p>
            </div>
            """)

def gerar_relatorio_pdf_atleta():
    nome = st.session_state.get("perfil_nome", "Atleta")
    faixa = st.session_state.get("perfil_faixa", "Branca")
    graus = st.session_state.get("perfil_graus", 0)
    academia = st.session_state.get("perfil_academia", "Academia BJJ")
    status = st.session_state.get("perfil_status", "Atleta")
    email = st.session_state.get("usuario_email", "")
    total_lutas = len(st.session_state.get("historico_lutas", []))
    
    return f"""
=====================================================
          OSSBOT PRO - RELATÓRIO OFICIAL DE ATLETA
=====================================================
Data: {datetime.now().strftime('%d/%m/%Y - %H:%M')}

[DADOS DO ATLETA]
• Nome: {nome}
• E-mail: {email}
• Academia: {academia}
• Graduação: Faixa {faixa} ({graus}º Grau)
• Status: {status}

[RESUMO DE ATIVIDADES]
• Total de Lutas: {total_lutas}
• Cursos/Técnicas: {len(st.session_state.get("cursos_interativos", []))}
• Dinâmicas Kids: {len(st.session_state.get("dinamic_kids_custom", []))}
• Flashcards de Pressão: {len(st.session_state.get("flashcards_pressao", []))}
• Presenças Registadas: {len(st.session_state.get("historico_presencas", []))}
=====================================================
"""

# ---------------------------------------------------------------------------
# BLOCO PRINCIPAL DO APLICATIVO COM CAPTURA INTELIGENTE DE ERROS DA OSSBOT IA
# ---------------------------------------------------------------------------
try:
    if not st.session_state.autenticado:
        col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
        with col_l2:
            st.markdown("<h1 style='text-align: center; color: #ff1e27;'>🥋 OssBot Pro</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #cccccc;'>Plataforma Profissional de Gestão para Academias de BJJ</p>", unsafe_allow_html=True)
            
            st.markdown("""
            <div style='background: #161616; border: 1px dashed #ff1e27; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 15px;'>
                <p style='color: #00ffcc; font-size: 12px; margin: 0;'><b>💡 Novo utilizador / Visitante?</b><br>Vá na aba <i>'Criar Conta'</i> e registe um novo e-mail para começar com o perfil limpo!</p>
            </div>
            """, unsafe_allow_html=True)
            
            aba_login, aba_cadastro, aba_recuperar = st.tabs(["🔑 Entrar", "📝 Criar Conta", "🔄 Esqueci a Senha"])
            
            with aba_login:
                with st.form("form_login"):
                    email_input = st.text_input("E-mail de Acesso:")
                    senha_input = st.text_input("Palavra-passe:", type="password")
                    btn_entrar = st.form_submit_button("🚀 Entrar no Sistema", use_container_width=True)
                    
                    if btn_entrar:
                        email_limpo = email_input.strip().lower()
                        banco = carregar_banco_usuarios()
                        if email_limpo in banco and banco[email_limpo]["senha"] == senha_input:
                            carregar_usuario(email_limpo)
                            st.session_state.autenticado = True
                            st.toast("✅ Login realizado com sucesso!", icon="🥋")
                            st.rerun()
                        else:
                            st.error("❌ E-mail ou palavra-passe incorretos.")
                            
                with st.expander("👑 Acesso Restrito Master (Admin)"):
                    with st.form("form_admin_login"):
                        senha_master_input = st.text_input("Palavra-passe de Administrador Master:", type="password")
                        btn_admin_entrar = st.form_submit_button("🔒 Entrar como Master", use_container_width=True)
                        if btn_admin_entrar:
                            if senha_master_input == SENHA_ADMIN_MASTER:
                                carregar_usuario(EMAIL_ADMIN_MASTER)
                                st.session_state.autenticado = True
                                st.toast("✅ Acesso Master autorizado!", icon="👑")
                                st.rerun()
                            else:
                                st.error("❌ Palavra-passe de administrador incorreta.")
                    
                    st.divider()
                    st.markdown("<p style='color: #ff1e27; font-weight: bold;'>➕ Adicionar Novo Administrador</p>", unsafe_allow_html=True)
                    with st.form("form_criar_novo_admin_master"):
                        senha_fundador_check = st.text_input("Palavra-passe Mestre do Fundador (Sua Palavra-passe):", type="password", key="s_fund_novo")
                        novo_admin_email = st.text_input("E-mail do Novo Admin:", key="n_adm_email")
                        novo_admin_senha = st.text_input("Palavra-passe do Novo Admin (mín. 6):", type="password", key="n_adm_senha")
                        novo_admin_nome = st.text_input("Nome do Novo Admin:", value="", key="n_adm_nome")
                        tipo_novo_admin = st.selectbox("Nível de Acesso:", ["Professor / Instrutor", "Master (Fundador)"], key="n_adm_tipo")
                        btn_criar_admin = st.form_submit_button("✨ Criar Novo Acesso Master", use_container_width=True)
                        
                        if btn_criar_admin:
                            if senha_fundador_check != SENHA_ADMIN_MASTER:
                                st.error("❌ Palavra-passe mestre do fundador incorreta! Acesso negado.")
                            else:
                                email_limpo_adm = novo_admin_email.strip().lower()
                                if not email_limpo_adm or not novo_admin_senha:
                                    st.warning("⚠️ Preencha o e-mail e a palavra-passe do novo admin.")
                                elif len(novo_admin_senha) < 6:
                                    st.warning("⚠️ A palavra-passe deve ter no mínimo 6 caracteres.")
                                else:
                                    banco = carregar_banco_usuarios()
                                    banco[email_limpo_adm] = {
                                        "senha": novo_admin_senha,
                                        "tipo_usuario": tipo_novo_admin,
                                        "is_admin": True,
                                        "plano": "ativo",
                                        "data_criacao": datetime.now().strftime("%d/%m/%Y - %H:%M")
                                    }
                                    salvar_banco_usuarios(banco)
                                    
                                    du = carregar_dados_usuario(email_limpo_adm)
                                    if novo_admin_nome.strip():
                                        du["perfil_nome"] = novo_admin_nome.strip()
                                    du["tipo_usuario"] = tipo_novo_admin
                                    salvar_dados_usuario(email_limpo_adm, du)
                                    st.success(f"✅ Novo administrador '{email_limpo_adm}' criado com sucesso!")

            with aba_cadastro:
                with st.form("form_cadastro"):
                    novo_email = st.text_input("O seu E-mail:")
                    nova_senha = st.text_input("Crie uma Palavra-passe (mín. 6 caracteres):", type="password")
                    nome_inicial = st.text_input("O seu Nome Completo:", value="Atleta Visitante")
                    acad_inicial = st.text_input("A sua Academia:", value="Insira a sua Academia")
                    tipo_registo = st.selectbox("Perfil de Utilizador:", ["Atleta", "Professor / Instrutor"])
                    btn_cadastrar = st.form_submit_button("✨ Criar Conta Agora", use_container_width=True)
                    
                    if btn_cadastrar:
                        email_limpo = novo_email.strip().lower()
                        if not email_limpo or not nova_senha:
                            st.warning("⚠️ Preencha o e-mail e a palavra-passe.")
                        elif len(nova_senha) < 6:
                            st.warning("⚠️ A palavra-passe deve ter no mínimo 6 caracteres.")
                        else:
                            banco = carregar_banco_usuarios()
                            if email_limpo in banco:
                                st.error("❌ Este e-mail já está registado.")
                            else:
                                is_adm_flag = (tipo_registo == "Professor / Instrutor")
                                banco[email_limpo] = {
                                    "senha": nova_senha,
                                    "tipo_usuario": tipo_registo,
                                    "is_admin": is_adm_flag,
                                    "plano": "ativo",
                                    "data_criacao": datetime.now().strftime("%d/%m/%Y - %H:%M")
                                }
                                salvar_banco_usuarios(banco)
                                
                                dados_novos = carregar_dados_usuario(email_limpo)
                                dados_novos["perfil_nome"] = nome_inicial if nome_inicial else "Atleta Visitante"
                                dados_novos["perfil_academia"] = acad_inicial if acad_inicial else "Insira a sua Academia"
                                dados_novos["tipo_usuario"] = tipo_registo
                                salvar_dados_usuario(email_limpo, dados_novos)
                                
                                st.success("✅ Conta criada com sucesso! Vá na aba 'Entrar' para aceder.")

            with aba_recuperar:
                with st.form("form_esqueci_senha"):
                    st.markdown("<p style='color: #cccccc; font-size: 13px;'>Digite o seu e-mail registado e defina uma nova palavra-passe instantaneamente:</p>", unsafe_allow_html=True)
                    email_recup = st.text_input("E-mail Registado:")
                    nova_senha_recup = st.text_input("Nova Palavra-passe (mín. 6 caracteres):", type="password")
                    btn_resetar = st.form_submit_button("🔄 Atualizar Palavra-passe Agora", use_container_width=True)
                    
                    if btn_resetar:
                        email_limpo = email_recup.strip().lower()
                        banco = carregar_banco_usuarios()
                        if email_limpo in banco:
                            if len(nova_senha_recup) < 6:
                                st.warning("⚠️ A nova palavra-passe deve ter no mínimo 6 caracteres.")
                            else:
                                banco[email_limpo]["senha"] = nova_senha_recup
                                salvar_banco_usuarios(banco)
                                st.success("✅ Palavra-passe atualizada com sucesso! Vá na aba 'Entrar' para aceder.")
                        else:
                            st.error("❌ E-mail não encontrado na base de dados.")
        st.stop()

    # Barra Lateral (Sidebar) com Edição de Perfil Integrada
    with st.sidebar:
        st.markdown("### 🥋 Carteirinha & Perfil")
        foto_b64 = st.session_state.get("perfil_foto_b64", "")
        if foto_b64:
            st.markdown(f'<img src="data:image/jpeg;base64,{foto_b64}" class="foto-bolinha">', unsafe_allow_html=True)
        else:
            st.markdown('<div class="bolinha-padrao">🥋</div>', unsafe_allow_html=True)
            
        st.markdown(f"<h4 style='text-align: center; color: #ff1e27; margin: 5px 0;'>{esc(st.session_state.get('perfil_nome', 'Atleta Visitante'))}</h4>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #cccccc; font-size: 13px; margin: 0;'>Faixa {esc(st.session_state.get('perfil_faixa', 'Branca'))} ({st.session_state.get('perfil_graus', 0)}º Grau)</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #00ffcc; font-size: 12px; margin: 5px 0 5px 0;'>{esc(st.session_state.get('perfil_academia', 'Insira a sua Academia'))}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #fbbf24; font-size: 11px; margin: 0 0 10px 0;'>Perfil: <b>{esc(st.session_state.get('tipo_usuario', 'Atleta'))}</b></p>", unsafe_allow_html=True)
        
        # Expander direto na barra lateral para edição rápida do perfil
        with st.expander("✏️ Editar o Meu Perfil"):
            with st.form("form_edicao_perfil_sidebar"):
                novo_nome = st.text_input("Nome / Atleta:", value=st.session_state.get("perfil_nome", ""))
                
                faixas_p = ["Branca", "Cinza", "Amarela", "Laranja", "Verde", "Azul", "Roxa", "Castanha", "Preta", "Vermelha e Preta", "Vermelha e Branca", "Vermelha"]
                fx_atual = st.session_state.get("perfil_faixa", "Branca")
                idx_fx = faixas_p.index(fx_atual) if fx_atual in faixas_p else 0
                nova_faixa = st.selectbox("Faixa:", faixas_p, index=idx_fx)
                
                novos_graus = st.slider("Graus:", 0, 11, int(st.session_state.get("perfil_graus", 0)))
                nova_academia = st.text_input("Academia:", value=st.session_state.get("perfil_academia", ""))
                novo_status = st.selectbox("Status:", ["Atleta Competidor 🏆", "Praticante / Hobby", "Professor / Instrutor"], index=0 if "Competidor" in st.session_state.get("perfil_status", "") else 1)
                
                arquivo_foto = st.file_uploader("Foto (JPG/PNG):", type=["jpg", "png", "jpeg"])
                
                if st.form_submit_button("💾 Salvar Perfil", use_container_width=True):
                    st.session_state["perfil_nome"] = novo_nome if novo_nome else "Atleta Visitante"
                    st.session_state["perfil_faixa"] = nova_faixa
                    st.session_state["perfil_graus"] = novos_graus
                    st.session_state["perfil_academia"] = nova_academia if nova_academia else "Insira a sua Academia"
                    st.session_state["perfil_status"] = novo_status
                    
                    if arquivo_foto is not None:
                        bytes_foto = arquivo_foto.read()
                        st.session_state["perfil_foto_b64"] = base64.b64encode(bytes_foto).decode("utf-8")
                        
                    salvar_tudo()
                    st.toast("✅ Perfil atualizado!", icon="🥋")
                    st.rerun()

        st.divider()
        renderizar_secao_gamificacao()
        st.divider()
        
        if st.session_state.get("is_admin", False) or st.session_state.get("tipo_usuario") in ["Professor / Instrutor", "Master (Fundador)"]:
            st.markdown("## 👑 Painel de Gestão & Coach")
            
            with st.expander("📱 Check-in de Presença (QR Code)"):
                st.markdown("<p style='font-size: 12px; color: #cccccc;'>Aponte a câmara para o QR Code do dia para fazer o check-in:</p>", unsafe_allow_html=True)
                
                data_hoje_str = datetime.now().strftime("%d/%m/%Y")
                data_api_str = datetime.now().strftime("%Y-%m-%d")
                qr_url_dia = f"https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=OssBot-Checkin-{data_api_str}"
                
                st.markdown(f"""
                <div style='text-align: center; background: #161616; padding: 12px; border-radius: 8px; border: 1px solid #ff1e27; margin-bottom: 10px;'>
                    <img src='{qr_url_dia}' style='border-radius: 6px; width: 140px; height: 140px; border: 2px solid #ffffff;'/>
                    <p style='color: #00ffcc; font-size: 12px; margin-top: 8px; font-weight: bold;'>📅 QR Code de Hoje: {data_hoje_str}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("📍 Fazer Check-in na Aula Hoje", use_container_width=True):
                    presencas = st.session_state.get("historico_presencas", [])
                    if data_hoje_str not in presencas:
                        presencas.append(data_hoje_str)
                        st.session_state["historico_presencas"] = presencas
                        salvar_tudo()
                        st.success(f"✅ Presença registada para hoje ({data_hoje_str})!")
                        st.rerun()
                    else:
                        st.info("ℹ️ Já fez check-in hoje!")
                st.write(f"Total de presenças: **{len(st.session_state.get('historico_presencas', []))}**")

            with st.expander("🛠️ Gestão de Alunos e Academias"):
                banco = carregar_banco_usuarios()
                tipo_atual = st.session_state.get("tipo_usuario")
                academia_atual = st.session_state.get("perfil_academia", "").strip().lower()
                
                st.write(f"📊 **Total de Contas no Sistema:** {len(banco)}")
                st.divider()
                
                academias_dict = {}
                for usr, info in banco.items():
                    dados_usr = carregar_dados_usuario(usr)
                    acad = dados_usr.get("perfil_academia", "Academia Não Informada").strip()
                    
                    if tipo_atual == "Professor / Instrutor" and acad.lower() != academia_atual:
                        continue
                        
                    if acad not in academias_dict:
                        academias_dict[acad] = []
                    academias_dict[acad].append((usr, info, dados_usr))
                
                if not academias_dict:
                    st.info("Nenhum aluno encontrado na sua academia.")
                
                for acad_nome, lista_alunos in academias_dict.items():
                    st.markdown(f"🏛️ **Academia:** <span style='color: #ff1e27; font-size: 15px; font-weight: bold;'>{esc(acad_nome)}</span>", unsafe_allow_html=True)
                    st.write(f"👥 Alunos cadastrados: {len(lista_alunos)}")
                    
                    for usr, info, dados_usr in lista_alunos:
                        nome_usr = dados_usr.get("perfil_nome", "Sem Nome")
                        faixa_usr = dados_usr.get("perfil_faixa", "Branca")
                        graus_usr = dados_usr.get("perfil_graus", 0)
                        presencas_aluno = len(dados_usr.get("historico_presencas", []))
                        
                        status_grad = "🟢 Ritmo Normal"
                        if presencas_aluno >= 15 and graus_usr < 4:
                            status_grad = "🔥 APTO PARA GRAU!"
                        elif presencas_aluno >= 50:
                            status_grad = "🏆 APTO PARA FAIXA!"
                        
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;• **{esc(nome_usr)}** ({faixa_usr} - {graus_usr}º Grau) | *{status_grad}*")
                        
                        with st.expander(f"⚙️ Gerir: {nome_usr} ({usr})"):
                            with st.form(key=f"form_gestao_aluno_unico_{usr}"):
                                novo_email_input = st.text_input("Novo E-mail:", value=usr, key=f"nem_u_{usr}")
                                nova_senha_input = st.text_input("Nova Palavra-passe:", value=info.get("senha", ""), type="password", key=f"nsem_u_{usr}")
                                novo_nome_input = st.text_input("Nome:", value=nome_usr, key=f"nnome_u_{usr}")
                                
                                faixas_possiveis = ["Branca", "Cinza", "Amarela", "Laranja", "Verde", "Azul", "Roxa", "Castanha", "Preta", "Vermelha e Preta", "Vermelha e Branca", "Vermelha"]
                                idx_f = faixas_possiveis.index(faixa_usr) if faixa_usr in faixas_possiveis else 0
                                nova_faixa_input = st.selectbox("Faixa:", faixas_possiveis, index=idx_f, key=f"nfaixa_u_{usr}")
                                novos_graus_input = st.slider("Graus:", 0, 11, int(graus_usr), key=f"slider_mg_u_{usr}")
                                
                                col_b1, col_b2 = st.columns(2)
                                with col_b1:
                                    btn_salvar_aluno = st.form_submit_button("💾 Salvar Aluno", use_container_width=True)
                                with col_b2:
                                    btn_excluir_aluno = st.form_submit_button("🗑️ Excluir Aluno", use_container_width=True)
                                
                                if btn_salvar_aluno:
                                    novo_email_limpo = novo_email_input.strip().lower()
                                    if not novo_email_limpo or not nova_senha_input:
                                        st.warning("⚠️ Preencha o e-mail e a palavra-passe.")
                                    else:
                                        banco_atual = carregar_banco_usuarios()
                                        if novo_email_limpo != usr and novo_email_limpo in banco_atual:
                                            st.error("❌ E-mail já em uso.")
                                        else:
                                            dados_antigos = banco_atual.pop(usr)
                                            dados_antigos["senha"] = nova_senha_input
                                            banco_atual[novo_email_limpo] = dados_antigos
                                            salvar_banco_usuarios(banco_atual)
                                            
                                            du = carregar_dados_usuario(novo_email_limpo)
                                            du["perfil_nome"] = novo_nome_input
                                            du["perfil_faixa"] = nova_faixa_input
                                            du["perfil_graus"] = novos_graus_input
                                            salvar_dados_usuario(novo_email_limpo, du)
                                            
                                            ca = obter_caminho_usuario(usr)
                                            cn = obter_caminho_usuario(novo_email_limpo)
                                            if os.path.exists(ca) and ca != cn:
                                                try: os.replace(ca, cn)
                                                except: pass
                                            st.toast("✅ Atualizado com sucesso!", icon="👑")
                                            st.rerun()
                                            
                                if btn_excluir_aluno:
                                    banco_atual = carregar_banco_usuarios()
                                    if usr in banco_atual:
                                        del banco_atual[usr]
                                        salvar_banco_usuarios(banco_atual)
                                        caminho_arq_aluno = obter_caminho_usuario(usr)
                                        if os.path.exists(caminho_arq_aluno):
                                            try: os.remove(caminho_arq_aluno)
                                            except: pass
                                        st.toast("✅ Aluno excluído com sucesso!", icon="🗑️")
                                        st.rerun()

                    with st.expander(f"📊 Dashboard & Planilha: {acad_nome}"):
                        total_lutas_acad = sum(len(d[2].get("historico_lutas", [])) for d in lista_alunos)
                        st.markdown(f"<p style='color: #00ffcc;'><b>Total de Lutas da Turma:</b> {total_lutas_acad}</p>", unsafe_allow_html=True)
                        
                        dados_planilha = []
                        for _, _, d_usr in lista_alunos:
                            pres_count = len(d_usr.get("historico_presencas", []))
                            status_apto = "Normal"
                            if pres_count >= 15: status_apto = "Apto p/ Grau"
                            dados_planilha.append({
                                "Atleta": d_usr.get("perfil_nome", "Sem Nome"),
                                "Faixa": d_usr.get("perfil_faixa", "Branca"),
                                "Graus": d_usr.get("perfil_graus", 0),
                                "Status": d_usr.get("perfil_status", "Atleta"),
                                "Presenças": pres_count,
                                "Avaliação Graduação": status_apto,
                                "Total Lutas": len(d_usr.get("historico_lutas", []))
                            })
                        
                        df_academia = pd.DataFrame(dados_planilha)
                        st.dataframe(df_academia, use_container_width=True)
                        
                        csv_export = df_academia.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label=f"📥 Descarregar Planilha da Turma (.csv)",
                            data=csv_export,
                            file_name=f"dashboard_{acad_nome.lower().replace(' ', '_')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    st.markdown("---")

        if st.button("💾 Salvar Alterações Gerais", use_container_width=True):
            salvar_tudo()
            st.toast("✅ Dados salvos com sucesso!", icon="💾")
        if st.button("🚪 Sair da Conta (Logout)", use_container_width=True):
            fazer_logout()

    # Ecrã Principal & 14 Abas Interativas (Aba Perfil integrada na Sidebar)
    st.markdown("<h1 style='text-align: center; color: #ff1e27;'>🥋 OssBot App Pro</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #cccccc;'>Atleta: <b>{esc(st.session_state.get('perfil_nome', 'Atleta Visitante'))}</b> | Faixa {esc(st.session_state.get('perfil_faixa', 'Branca'))} ({st.session_state.get('perfil_graus', 0)}º Grau)</p>", unsafe_allow_html=True)

    with st.expander("📊 Painel de Analytics & Evolução Visual", expanded=False):
        lutas_list = st.session_state.get("historico_lutas", [])
        if not lutas_list:
            st.info("💡 Registe as suas lutas na aba 'Histórico' para visualizar os seus gráficos de desempenho em tempo real!")
        else:
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.markdown("##### 📈 Distribuição de Resultados")
                resultados_count = {}
                for l in lutas_list:
                    res = l.get("resultado", "Outro")
                    resultados_count[res] = resultados_count.get(res, 0) + 1
                df_res = pd.DataFrame(list(resultados_count.items()), columns=["Resultado", "Quantidade"])
                st.bar_chart(df_res.set_index("Resultado"))
                
            with col_g2:
                st.markdown("##### 🗓️ Frequência de Presenças nas Aulas")
                presencas_list = st.session_state.get("historico_presencas", [])
                if presencas_list:
                    df_pres = pd.DataFrame({"Data": presencas_list, "Presença": [1]*len(presencas_list)})
                    st.line_chart(df_pres.set_index("Data"))
                else:
                    st.write("Nenhuma presença registada via QR Code ainda.")

    st.divider()

    abas_app = st.tabs([
        "🤼 Luta", "📜 Histórico", "🥗 Nutrição", "🏆 Camp", "📚 Cursos", 
        "👶 Kids", "⚡ Drills", "🛡️ Pressão", "🥋 Graduação", "🥋 Kimono", 
        "📇 Card", "🔑 Chaves", "⏱️ Cronograma", "🔄 Recuperação"
    ])

    # 1. Luta & Placar
    with abas_app[0]:
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            pts_a_val = st.session_state.get("pts_a", 0)
            vant_a_val = st.session_state.get("vant_a", 0)
            pun_a_val = st.session_state.get("pun_a", 0)
            mostrar_html(f"""
            <div class='placar-box'>
                <p style='color: #cccccc; margin: 0;'>ATLETA 1 (Azul/Preto):</p>
                <h3 style='color: #00ffcc; margin: 5px 0;'>Atleta Azul</h3>
                <div class='placar-numero'>{pts_a_val}</div>
                <p style='color: #ffffff; margin: 5px 0;'>Vantagens: {vant_a_val} | Punições: {pun_a_val}</p>
            </div>
            """)
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("+2 Pts (A)", use_container_width=True): somar("a", "pts_a", 2); st.rerun()
                if st.button("+3 Pts (A)", use_container_width=True): somar("a", "pts_a", 3); st.rerun()
            with c2:
                if st.button("+4 Pts (A)", use_container_width=True): somar("a", "pts_a", 4); st.rerun()
                if st.button("Vantagem (A)", use_container_width=True): somar("a", "vant_a", 1); st.rerun()
            with c3:
                if st.button("Punição (A)", use_container_width=True): somar("a", "pun_a", 1); st.rerun()
                
        with col_p2:
            pts_b_val = st.session_state.get("pts_b", 0)
            vant_b_val = st.session_state.get("vant_b", 0)
            pun_b_val = st.session_state.get("pun_b", 0)
            mostrar_html(f"""
            <div class='placar-box'>
                <p style='color: #cccccc; margin: 0;'>ATLETA 2 (Branco):</p>
                <h3 style='color: #ffffff; margin: 5px 0;'>Atleta Branco</h3>
                <div class='placar-numero'>{pts_b_val}</div>
                <p style='color: #ffffff; margin: 5px 0;'>Vantagens: {vant_b_val} | Punições: {pun_b_val}</p>
            </div>
            """)
            cb1, cb2, cb3 = st.columns(3)
            with cb1:
                if st.button("+2 Pts (B)", use_container_width=True): somar("b", "pts_b", 2); st.rerun()
                if st.button("+3 Pts (B)", use_container_width=True): somar("b", "pts_b", 3); st.rerun()
            with cb2:
                if st.button("+4 Pts (B)", use_container_width=True): somar("b", "pts_b", 4); st.rerun()
                if st.button("Vantagem (B)", use_container_width=True): somar("b", "vant_b", 1); st.rerun()
            with cb3:
                if st.button("Punição (B)", use_container_width=True): somar("b", "pun_b", 1); st.rerun()

        st.divider()
        ct1, ct2, ct3 = st.columns(3)
        with ct1: st.selectbox("Tempo do Rola:", [1, 2, 3, 5, 6, 10], key="select_tempo", on_change=definir_tempo)
        with ct2:
            ts = st.session_state.get("tempo_segundos", 300)
            mr, sr = ts // 60, ts % 60
            st.markdown(f"<h2 style='text-align: center; color: #ff1e27; margin: 0;'>⏱️ {mr:02d}:{sr:02d}</h2>", unsafe_allow_html=True)
        with ct3:
            if not st.session_state.get("cronometro_rodando", False):
                if st.button("▶️ Iniciar", use_container_width=True): iniciar_cronometro(); st.rerun()
            else:
                if st.button("⏸️ Pausar", use_container_width=True): pausar_cronometro(); st.rerun()
            if st.button("🔄 Zerar Luta", use_container_width=True): zerar_luta(); st.rerun()

    # 2. Histórico
    with abas_app[1]:
        st.markdown("### 📜 Histórico de Lutas & Treinos")
        with st.form("form_nova_luta"):
            adv = st.text_input("Oponente / Companheiro:")
            res = st.selectbox("Resultado:", ["Vitória por Finalização", "Vitória por Pontos", "Empate", "Derrota"])
            det = st.text_area("Detalhes / Posição:")
            if st.form_submit_button("Registrar Luta", use_container_width=True):
                if adv:
                    lutas = st.session_state.get("historico_lutas", [])
                    lutas.append({"data": datetime.now().strftime("%d/%m/%Y"), "adversario": adv, "resultado": res, "detalhes": det})
                    st.session_state["historico_lutas"] = lutas
                    salvar_tudo()
                    st.toast("✅ Luta registada!", icon="🥋")
                    st.rerun()
                else:
                    st.warning("⚠️ Insira o nome do oponente.")
        st.divider()
        for l in reversed(st.session_state.get("historico_lutas", [])):
            st.markdown(f"""
            <div class='card-item'>
                <p style='color: #00ffcc; margin: 0;'><b>{esc(l['data'])}</b> - {esc(l['resultado'])}</p>
                <p style='color: #ffffff; margin: 5px 0 0 0;'>Oponente: <b>{esc(l['adversario'])}</b></p>
                <p style='color: #cccccc; margin: 3px 0 0 0; font-size: 13px;'>{esc(l['detalhes'])}</p>
            </div>
            """, unsafe_allow_html=True)

    # 3. Nutrição
    with abas_app[2]:
        st.markdown("### 🥗 Nutrição & Corte de Peso")
        with st.form("form_nutri"):
            refeicao = st.text_input("Refeição / Dieta:")
            kcal = st.text_input("Calorias / Hidratação:")
            if st.form_submit_button("Adicionar Registo Nutricional", use_container_width=True):
                if refeicao:
                    nutri = st.session_state.get("dicas_nutricao", [])
                    nutri.append({"refeicao": refeicao, "kcal": kcal})
                    st.session_state["dicas_nutricao"] = nutri
                    salvar_tudo()
                    st.toast("✅ Nutrição salva!")
                    st.rerun()
        st.divider()
        for n in st.session_state.get("dicas_nutricao", []):
            st.markdown(f"<div class='card-item'><b>{esc(n['refeicao'])}</b> - {esc(n['kcal'])}</div>", unsafe_allow_html=True)

    # 4. Camp
    with abas_app[3]:
        st.markdown("### 🏆 Camp de Competição")
        with st.form("form_camp"):
            evento = st.text_input("Nome do Campeonato / Meta:")
            objetivo = st.text_area("Foco de Treino:")
            if st.form_submit_button("Salvar Camp", use_container_width=True):
                if evento:
                    camps = st.session_state.get("camp_competicao", [])
                    camps.append({"evento": evento, "objetivo": objetivo})
                    st.session_state["camp_competicao"] = camps
                    salvar_tudo()
                    st.toast("✅ Camp salvo!")
                    st.rerun()
        st.divider()
        for c in st.session_state.get("camp_competicao", []):
            st.markdown(f"<div class='card-item'>🏆 <b>{esc(c['evento'])}</b>: {esc(c['objetivo'])}</div>", unsafe_allow_html=True)

    # 5. Cursos
    with abas_app[4]:
        st.markdown("### 📚 Cursos & Regras IBJJF")
        with st.form("form_curso"):
            titulo_curso = st.text_input("Nome da Posição / Regra:")
            desc_curso = st.text_area("Explicação / Anotação:")
            if st.form_submit_button("Salvar Estudo", use_container_width=True):
                if titulo_curso:
                    cursos = st.session_state.get("cursos_interativos", [])
                    cursos.append({"titulo": titulo_curso, "desc": desc_curso})
                    st.session_state["cursos_interativos"] = cursos
                    salvar_tudo()
                    st.toast("✅ Estudo salvo!")
                    st.rerun()
        st.divider()
        for cur in st.session_state.get("cursos_interativos", []):
            st.markdown(f"<div class='card-item'>📚 <b>{esc(cur['titulo'])}</b><br>{esc(cur['desc'])}</div>", unsafe_allow_html=True)

    # 6. Kids
    with abas_app[5]:
        st.markdown("### 👶 Dinâmicas para Turmas Kids")
        with st.form("form_kids"):
            nome_dinamica = st.text_input("Nome da Brincadeira / Dinâmica:")
            regra_kids = st.text_area("Como aplicar na aula infantil:")
            if st.form_submit_button("Salvar Dinâmica", use_container_width=True):
                if nome_dinamica:
                    kids = st.session_state.get("dinamic_kids_custom", [])
                    kids.append({"nome": nome_dinamica, "regra": regra_kids})
                    st.session_state["dinamic_kids_custom"] = kids
                    salvar_tudo()
                    st.toast("✅ Dinâmica kids salva!")
                    st.rerun()
        st.divider()
        for k in st.session_state.get("dinamic_kids_custom", []):
            st.markdown(f"<div class='card-item'>👶 <b>{esc(k['nome'])}</b><br>{esc(k['regra'])}</div>", unsafe_allow_html=True)

    # 7. Drills
    with abas_app[6]:
        st.markdown("### ⚡ Drills de Repetição & Velocidade")
        with st.form("form_drill"):
            nome_drill = st.text_input("Movimento / Posição do Drill:")
            reps = st.text_input("Repetições / Tempo:")
            if st.form_submit_button("Salvar Drill", use_container_width=True):
                if nome_drill:
                    drills = st.session_state.get("drills_treino", [])
                    drills.append({"drill": nome_drill, "reps": reps})
                    st.session_state["drills_treino"] = drills
                    salvar_tudo()
                    st.toast("✅ Drill salvo!")
                    st.rerun()
        st.divider()
        for d in st.session_state.get("drills_treino", []):
            st.markdown(f"<div class='card-item'>⚡ <b>{esc(d['drill'])}</b> ({esc(d['reps'])})</div>", unsafe_allow_html=True)

    # 8. Pressão
    with abas_app[7]:
        st.markdown("### 🛡️ Flashcards de Controlo & Pressão")
        with st.form("form_pressao"):
            posicao_p = st.text_input("Posição (Ex: Cem-Quilos):")
            detalhe_p = st.text_area("Detalhe de Ajuste de Peso/Pegada:")
            if st.form_submit_button("Salvar Flashcard", use_container_width=True):
                if posicao_p:
                    fp = st.session_state.get("flashcards_pressao", [])
                    fp.append({"posicao": posicao_p, "detalhe": detalhe_p})
                    st.session_state["flashcards_pressao"] = fp
                    salvar_tudo()
                    st.toast("✅ Flashcard salvo!")
                    st.rerun()
        st.divider()
        for f in st.session_state.get("flashcards_pressao", []):
            st.markdown(f"<div class='card-item'>🛡️ <b>{esc(f['posicao'])}</b><br>{esc(f.get('detalhe', ''))}</div>", unsafe_allow_html=True)

    # 9. Graduação
    with abas_app[8]:
        st.markdown("### 🥋 Controlo de Graduação")
        with st.form("form_grad"):
            aluno_g = st.text_input("Nome do Aluno:")
            faixa_g = st.selectbox("Faixa:", ["Branca", "Azul", "Roxa", "Castanha", "Preta"])
            grau_g = st.slider("Grau:", 0, 4)
            if st.form_submit_button("Salvar Aluno Graduação", use_container_width=True):
                if aluno_g:
                    grad = st.session_state.get("alunos_graduacao", [])
                    grad.append({"aluno": aluno_g, "faixa": faixa_g, "grau": grau_g})
                    st.session_state["alunos_graduacao"] = grad
                    salvar_tudo()
                    st.toast("✅ Graduação salva!")
                    st.rerun()
        st.divider()
        for ag in st.session_state.get("alunos_graduacao", []):
            st.markdown(f"<div class='card-item'>🥋 <b>{esc(ag['aluno'])}</b> - Faixa {esc(ag['faixa'])} ({ag['grau']}º Grau)</div>", unsafe_allow_html=True)

    # 10. Kimono
    with abas_app[9]:
        st.markdown("### 🥋 Notas de Kimonos & Equipamentos")
        with st.form("form_kimono"):
            item_k = st.text_input("Marca / Modelo do Kimono:")
            estado_k = st.text_input("Estado / Medida / Observação:")
            if st.form_submit_button("Salvar Kimono", use_container_width=True):
                if item_k:
                    kims = st.session_state.get("notas_kimono", [])
                    kims.append({"item": item_k, "estado": estado_k})
                    st.session_state["notas_kimono"] = kims
                    salvar_tudo()
                    st.toast("✅ Kimono salvo!")
                    st.rerun()
        st.divider()
        for km in st.session_state.get("notas_kimono", []):
            st.markdown(f"<div class='card-item'>🥋 <b>{esc(km['item'])}</b>: {esc(km['estado'])}</div>", unsafe_allow_html=True)

    # 11. Card & Relatório
    with abas_app[10]:
        st.markdown("### 📇 Cartão Digital & Relatório Oficial")
        st.markdown(f"""
        <div class='placar-box' style='text-align: left; max-width: 400px; margin: 0 auto 20px auto;'>
            <h3 style='color: #ff1e27; margin-top: 0;'>🥋 CARTÃO OFICIAL</h3>
            <p><b>Nome:</b> {esc(st.session_state.get('perfil_nome', ''))}</p>
            <p><b>Faixa:</b> {esc(st.session_state.get('perfil_faixa', ''))} ({st.session_state.get('perfil_graus', 0)}º Grau)</p>
            <p><b>Academia:</b> {esc(st.session_state.get('perfil_academia', ''))}</p>
            <p><b>Status:</b> {esc(st.session_state.get('perfil_status', ''))}</p>
            <p><b>Perfil:</b> {esc(st.session_state.get('tipo_usuario', ''))}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        st.markdown("### 📄 Relatório Executivo & Prontuário")
        st.download_button(
            "📥 Descarregar Relatório Oficial (.txt)",
            data=gerar_relatorio_pdf_atleta(),
            file_name=f"relatorio_ossbot_{st.session_state.get('perfil_nome', 'atleta').lower().replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    # 12. Chaves
    with abas_app[11]:
        st.markdown("### 🔑 Gerador de Chaves de Luta")
        with st.form("form_chave"):
            competicao_c = st.text_input("Nome do Torneio:")
            atletas_c = st.text_area("Lista de Atletas (um por linha):")
            if st.form_submit_button("Gerar Chaveamento", use_container_width=True):
                if competicao_c and atletas_c:
                    chaves = st.session_state.get("chaves_luta", [])
                    lista_at = [a.strip() for a in atletas_c.split("\n") if a.strip()]
                    chaves.append({"torneio": competicao_c, "atletas": lista_at})
                    st.session_state["chaves_luta"] = chaves
                    salvar_tudo()
                    st.toast("✅ Chave gerada!")
                    st.rerun()
        st.divider()
        for ch in st.session_state.get("chaves_luta", []):
            st.markdown(f"<div class='card-item'>🔑 <b>{esc(ch['torneio'])}</b><br>Atletas: {', '.join(ch['atletas'])}</div>", unsafe_allow_html=True)

    # 13. Cronograma
    with abas_app[12]:
        st.markdown("### ⏱️ Cronograma Semanal de Treinos")
        with st.form("form_crono"):
            dia_c = st.selectbox("Dia da Semana:", ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"])
            horario_c = st.text_input("Horário e Foco (Ex: 19:00 - Guarda Aranha):")
            if st.form_submit_button("Adicionar ao Cronograma", use_container_width=True):
                if horario_c:
                    crono = st.session_state.get("cronogramas_aulas", [])
                    crono.append({"dia": dia_c, "detalhe": horario_c})
                    st.session_state["cronogramas_aulas"] = crono
                    salvar_tudo()
                    st.toast("✅ Cronograma salvo!")
                    st.rerun()
        st.divider()
        for cr in st.session_state.get("cronogramas_aulas", []):
            st.markdown(f"<div class='card-item'>⏱️ <b>{esc(cr['dia'])}</b>: {esc(cr['detalhe'])}</div>", unsafe_allow_html=True)

    # 14. Recuperação
    with abas_app[13]:
        st.markdown("### 🔄 Recuperação, Sono & Lesões")
        with st.form("form_recup"):
            nota_r = st.text_area("Anotações de descanso, sono ou cuidados com lesões:")
            if st.form_submit_button("Salvar Nota de Recuperação", use_container_width=True):
                if nota_r:
                    recup = st.session_state.get("recuperacao_notas", [])
                    recup.append({"nota": nota_r, "data": datetime.now().strftime("%d/%m/%Y")})
                    st.session_state["recuperacao_notas"] = recup
                    salvar_tudo()
                    st.toast("✅ Nota salva!")
                    st.rerun()
        st.divider()
        for rc in st.session_state.get("recuperacao_notas", []):
            st.markdown(f"<div class='card-item'>🔄 <b>{esc(rc['data'])}</b><br>{esc(rc['nota'])}</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# CAPTURA DE ERROS COM MENSAGEM INTELIGENTE DA IA DO JIU-JITSU (OSSBOT IA)
# ---------------------------------------------------------------------------
except Exception as e:
    nome_usr_erro = st.session_state.get("perfil_nome", "Usuário")
    is_adm_erro = st.session_state.get("is_admin", False) or (st.session_state.get("usuario_email", "").lower() == EMAIL_ADMIN_MASTER.lower())
    detalhes_erro_str = traceback.format_exc()

    st.markdown("<div class='ia-erro-card'>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: #ff1e27; margin-top: 0;'>🤖 OssBot IA - Assistente de Diagnóstico</h3>", unsafe_allow_html=True)
    
    if is_adm_erro:
        st.markdown(f"""
        <p style='color: #ffffff; font-size: 15px;'>
            <b>Olha só, {esc(nome_usr_erro)}!</b> Ocorreu um imprevisto técnico na execução do seu código. 
            Como você é o <b>Administrador/Fundador</b>, aqui está o diagnóstico detalhado para você ajustar no Python:
        </p>
        <div style='background: #0b0b0b; padding: 12px; border-radius: 6px; border: 1px solid #444; color: #ff6b6b; font-family: monospace; font-size: 13px;'>
            <b>Tipo de Erro:</b> {esc(type(e).__name__)}<br>
            <b>Descrição:</b> {esc(str(e))}<br><br>
            <b>Caminho e Linha da Falha:</b><br>
            <pre style='color: #cccccc;'>{esc(detalhes_erro_str)}</pre>
        </div>
        <p style='color: #00ffcc; font-size: 14px; margin-top: 10px;'>
            💡 <b>Como Resolver:</b> Acesse o seu repositório no GitHub, abra o arquivo <code>app.py</code> e verifique a linha indicada no relatório acima para ajustar a sintaxe ou inicialização da variável.
        </p>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <p style='color: #ffffff; font-size: 15px;'>
            <b>Olha só, {esc(nome_usr_erro)}!</b> Ocorreu uma pequena instabilidade temporária nesta função do sistema.
        </p>
        <div style='background: #0b0b0b; padding: 12px; border-radius: 6px; border: 1px solid #ff1e27; color: #cccccc; font-size: 13px;'>
            <b>Motivo informado pela IA:</b> {esc(str(e))}
        </div>
        <p style='color: #fbbf24; font-size: 14px; margin-top: 10px;'>
            📣 <b>Orientação:</b> Por favor, informe ao dono da academia ou ao administrador da plataforma para que eles realizem essa pequena melhoria no código do sistema!
        </p>
        """, unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)
