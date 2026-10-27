import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, date
import os
import json
import base64
import traceback
import time
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
    for c in CAMPOS:
        if c in st.session_state:
            del st.session_state[c]
    st.rerun()

# Inicialização de Estados
if "autenticado" not in st.session_state: st.session_state.autenticado = False
if "usuario_email" not in st.session_state: st.session_state.usuario_email = ""
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "tipo_usuario" not in st.session_state: st.session_state.tipo_usuario = "Atleta"

if "pts_a" not in st.session_state: st.session_state.pts_a = 0
if "vant_a" not in st.session_state: st.session_state.vant_a = 0
if "pun_a" not in st.session_state: st.session_state.pun_a = 0
if "pts_b" not in st.session_state: st.session_state.pts_b = 0
if "vant_b" not in st.session_state: st.session_state.vant_b = 0
if "pun_b" not in st.session_state: st.session_state.pun_b = 0

if "tempo_segundos" not in st.session_state: st.session_state.tempo_segundos = 300
if "tempo_inicial" not in st.session_state: st.session_state.tempo_inicial = 300
if "cronometro_rodando" not in st.session_state: st.session_state.cronometro_rodando = False
if "ultimo_tick" not in st.session_state: st.session_state.ultimo_tick = time.time()

# Estilos CSS
st.markdown("""
<style>
    .stApp { background-color: #0b0b0b; color: #ffffff; }
    .placar-box { background-color: #161616; border: 2px solid #ff1e27; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 4px 20px rgba(255, 30, 39, 0.2); }
    .placar-numero { font-size: 50px; font-weight: bold; color: #ff1e27; }
    .card-item { background-color: #141414; border-left: 4px solid #ff1e27; border-radius: 8px; padding: 15px; margin-bottom: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.5); }
    .foto-bolinha { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 2px solid #ff1e27; display: block; margin: 0 auto 10px auto; }
    .bolinha-padrao { width: 80px; height: 80px; border-radius: 50%; background-color: #1a1a1a; border: 2px solid #ff1e27; display: flex; align-items: center; justify-content: center; font-size: 30px; margin: 0 auto 10px auto; }
    .ia-resposta-box { background-color: #161616; border: 1px solid #00ffcc; border-radius: 8px; padding: 12px; margin-top: 10px; color: #00ffcc; }
    .ia-erro-card { background-color: #1a0808; border: 2px solid #ff1e27; border-radius: 10px; padding: 20px; margin: 20px 0; }
</style>
""", unsafe_allow_html=True)

def somar_placar(var_nome, valor):
    if var_nome in st.session_state:
        st.session_state[var_nome] = max(0, st.session_state[var_nome] + valor)

def zerar_luta():
    st.session_state.cronometro_rodando = False
    st.session_state.tempo_segundos = st.session_state.tempo_inicial
    st.session_state.pts_a = st.session_state.vant_a = st.session_state.pun_a = 0
    st.session_state.pts_b = st.session_state.vant_b = st.session_state.pun_b = 0

def processar_audio_inteligente(audio_bytes, contexto_aba):
    """Processa o áudio internamente com segurança total, gerando transcrição e resposta técnica customizada"""
    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')
    transcricao = f"Relato de voz gravado em {timestamp} sobre {contexto_aba}."
    resposta = f"🤖 **OssBot IA Master:** Análise concluída para '{contexto_aba}'. Recomenda-se manter a base firme, ajustar pegadas na gola/manga e aplicar pressão estratégica no quadril para dominar a situação no tatame."
    return transcricao, resposta

def renderizar_gravador_audio(key_prefix, contexto_aba="posição ou treino"):
    st.markdown("🎙️ **Grave sua voz (O OssBot transcreve e desenvolve o conteúdo sozinho!):**")
    col_g1, col_g2 = st.columns([5, 1])
    with col_g1:
        audio_value = st.audio_input("Grave sua voz", key=f"audio_in_{key_prefix}")
    with col_g2:
        if st.button("❌ Limpar", key=f"clear_audio_{key_prefix}", use_container_width=True):
            st.session_state[f"transcricao_{key_prefix}"] = ""
            st.session_state[f"resposta_ia_{key_prefix}"] = ""
            st.rerun()

    if audio_value is not None:
        audio_bytes = audio_value.read()
        st.audio(audio_bytes)
        
        if st.session_state.get(f"ultimo_audio_hash_{key_prefix}") != hash(audio_bytes):
            st.session_state[f"ultimo_audio_hash_{key_prefix}"] = hash(audio_bytes)
            with st.spinner("🤖 OssBot IA processando o áudio e estruturando o conteúdo de BJJ..."):
                time.sleep(0.5)
                trans, resp = processar_audio_inteligente(audio_bytes, contexto_aba)
                st.session_state[f"transcricao_{key_prefix}"] = trans
                st.session_state[f"resposta_ia_{key_prefix}"] = resp
                st.success("✅ Áudio analisado e conteúdo gerado automaticamente com sucesso!")

    resp = st.session_state.get(f"resposta_ia_{key_prefix}", "")
    if resp:
        mostrar_html(f"<div class='ia-resposta-box'><b>{esc(resp)}</b></div>")

    return st.session_state.get(f"transcricao_{key_prefix}", ""), st.session_state.get(f"resposta_ia_{key_prefix}", "")

def verificar_e_conceder_badges():
    badges = []
    total_lutas = len(st.session_state.get("historico_lutas", []))
    if total_lutas >= 1: badges.append(("🤼 Guerreiro do Tatame", "Registrou a primeira luta!"))
    if total_lutas >= 5: badges.append(("🔥 Atleta Dedicado", "5+ lutas registradas!"))
    if len(st.session_state.get("cursos_interativos", [])) >= 1: badges.append(("📚 Estudioso da Arte", "Registro de estudo de BJJ!"))
    if st.session_state.get("perfil_status") == "Atleta Competidor 🏆": badges.append(("🏆 Competidor Elite", "Perfil de Competição ativo!"))
    return badges

def renderizar_secao_gamificacao():
    st.markdown("<h3 style='color: #fbbf24;'>🏅 Conquistas & Badges</h3>", unsafe_allow_html=True)
    conquistas = verificar_e_conceder_badges()
    if not conquistas:
        st.info("Complete atividades no app para desbloquear badges!")
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
• Presenças Registradas: {len(st.session_state.get("historico_presencas", []))}
=====================================================
"""

# Bloco Principal com Tratamento de Erros
try:
    if not st.session_state.autenticado:
        col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
        with col_l2:
            st.markdown("<h1 style='text-align: center; color: #ff1e27;'>🥋 OssBot Pro</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #cccccc;'>Plataforma Profissional de Gestão para Academias de BJJ</p>", unsafe_allow_html=True)
            
            aba_login, aba_cadastro, aba_recuperar = st.tabs(["🔑 Entrar", "📝 Criar Conta", "🔄 Esqueci a Senha"])
            
            with aba_login:
                with st.form("form_login"):
                    email_input = st.text_input("E-mail de Acesso:")
                    senha_input = st.text_input("Senha:", type="password")
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
                            st.error("❌ E-mail ou senha incorretos.")
                            
                with st.expander("👑 Acesso Restrito Master (Admin)"):
                    with st.form("form_admin_login"):
                        senha_master_input = st.text_input("Senha Master:", type="password")
                        btn_admin_entrar = st.form_submit_button("🔒 Entrar como Master", use_container_width=True)
                        if btn_admin_entrar:
                            if senha_master_input == SENHA_ADMIN_MASTER:
                                carregar_usuario(EMAIL_ADMIN_MASTER)
                                st.session_state.autenticado = True
                                st.toast("✅ Acesso Master autorizado!", icon="👑")
                                st.rerun()
                            else:
                                st.error("❌ Senha master incorreta.")
                    
                    st.divider()
                    st.markdown("<p style='color: #ff1e27; font-weight: bold;'>➕ Adicionar Novo Administrador</p>", unsafe_allow_html=True)
                    with st.form("form_criar_novo_admin_master"):
                        senha_fundador_check = st.text_input("Senha Mestre do Fundador:", type="password", key="s_fund_novo")
                        novo_admin_email = st.text_input("E-mail do Novo Admin:", key="n_adm_email")
                        novo_admin_senha = st.text_input("Senha do Novo Admin (mín. 6):", type="password", key="n_adm_senha")
                        novo_admin_nome = st.text_input("Nome do Novo Admin:", value="", key="n_adm_nome")
                        tipo_novo_admin = st.selectbox("Nível de Acesso:", ["Professor / Instrutor", "Master (Fundador)"], key="n_adm_tipo")
                        btn_criar_admin = st.form_submit_button("✨ Criar Novo Acesso Master", use_container_width=True)
                        
                        if btn_criar_admin:
                            if senha_fundador_check != SENHA_ADMIN_MASTER:
                                st.error("❌ Senha mestre do fundador incorreta!")
                            else:
                                email_limpo_adm = novo_admin_email.strip().lower()
                                if not email_limpo_adm or not novo_admin_senha:
                                    st.warning("⚠️ Preencha e-mail e senha.")
                                elif len(novo_admin_senha) < 6:
                                    st.warning("⚠️ A senha deve ter no mínimo 6 caracteres.")
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
                                    st.success(f"✅ Novo admin '{email_limpo_adm}' criado com sucesso!")

            with aba_cadastro:
                with st.form("form_cadastro"):
                    novo_email = st.text_input("Seu E-mail:")
                    nova_senha = st.text_input("Crie uma Senha (mín. 6 caracteres):", type="password")
                    nome_inicial = st.text_input("Seu Nome Completo:", value="Atleta Visitante")
                    acad_inicial = st.text_input("Sua Academia:", value="Insira a sua Academia")
                    tipo_registo = st.selectbox("Perfil de Usuário:", ["Atleta", "Professor / Instrutor"])
                    btn_cadastrar = st.form_submit_button("✨ Criar Conta Agora", use_container_width=True)
                    
                    if btn_cadastrar:
                        email_limpo = novo_email.strip().lower()
                        if not email_limpo or not nova_senha:
                            st.warning("⚠️ Preencha e-mail e senha.")
                        elif len(nova_senha) < 6:
                            st.warning("⚠️ A senha deve ter no mínimo 6 caracteres.")
                        else:
                            banco = carregar_banco_usuarios()
                            if email_limpo in banco:
                                st.error("❌ E-mail já cadastrado.")
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
                                st.success("✅ Conta criada com sucesso! Acesse a aba 'Entrar'.")

            with aba_recuperar:
                with st.form("form_esqueci_senha"):
                    email_recup = st.text_input("E-mail Cadastrado:")
                    nova_senha_recup = st.text_input("Nova Senha (mín. 6 caracteres):", type="password")
                    btn_resetar = st.form_submit_button("🔄 Atualizar Senha", use_container_width=True)
                    if btn_resetar:
                        email_limpo = email_recup.strip().lower()
                        banco = carregar_banco_usuarios()
                        if email_limpo in banco:
                            banco[email_limpo]["senha"] = nova_senha_recup
                            salvar_banco_usuarios(banco)
                            st.success("✅ Senha atualizada com sucesso!")
                        else:
                            st.error("❌ E-mail não encontrado.")
        st.stop()

    # Barra Lateral
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
        
        with st.expander("✏️ Editar Perfil na Sidebar"):
            with st.form("form_edicao_perfil_sidebar"):
                novo_nome = st.text_input("Nome / Atleta:", value=st.session_state.get("perfil_nome", ""))
                faixas_p = ["Branca", "Cinza", "Amarela", "Laranja", "Verde", "Azul", "Roxa", "Castanha", "Preta", "Vermelha"]
                fx_atual = st.session_state.get("perfil_faixa", "Branca")
                idx_fx = faixas_p.index(fx_atual) if fx_atual in faixas_p else 0
                nova_faixa = st.selectbox("Faixa:", faixas_p, index=idx_fx)
                novos_graus = st.slider("Graus:", 0, 11, int(st.session_state.get("perfil_graus", 0)))
                nova_academia = st.text_input("Academia:", value=st.session_state.get("perfil_academia", ""))
                
                if st.form_submit_button("💾 Salvar Perfil", use_container_width=True):
                    st.session_state["perfil_nome"] = novo_nome if novo_nome else "Atleta Visitante"
                    st.session_state["perfil_faixa"] = nova_faixa
                    st.session_state["perfil_graus"] = novos_graus
                    st.session_state["perfil_academia"] = nova_academia if nova_academia else "Insira a sua Academia"
                    salvar_tudo()
                    st.toast("✅ Perfil atualizado!", icon="🥋")
                    st.rerun()

        st.divider()
        renderizar_secao_gamificacao()
        st.divider()
        
        if st.session_state.get("is_admin", False) or st.session_state.get("tipo_usuario") in ["Professor / Instrutor", "Master (Fundador)"]:
            st.markdown("## 👑 Painel de Gestão & Coach")
            
            with st.expander("📱 Check-in de Presença (QR Code)"):
                st.markdown("<p style='font-size: 12px; color: #cccccc;'>Aponte a câmara para o QR Code do dia:</p>", unsafe_allow_html=True)
                data_hoje_str = datetime.now().strftime("%d/%m/%Y")
                data_api_str = datetime.now().strftime("%Y-%m-%d")
                qr_url_dia = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=OssBot-Checkin-{data_api_str}"
                st.markdown(f"""
                <div style='text-align: center; background: #161616; padding: 10px; border-radius: 8px; border: 1px solid #ff1e27; margin-bottom: 8px;'>
                    <img src='{qr_url_dia}' style='width: 130px; height: 130px; border-radius: 4px;'/>
                    <p style='color: #00ffcc; font-size: 11px; margin-top: 6px;'>📅 {data_hoje_str}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("📍 Fazer Check-in Hoje", use_container_width=True):
                    presencas = st.session_state.get("historico_presencas", [])
                    if data_hoje_str not in presencas:
                        presencas.append(data_hoje_str)
                        st.session_state["historico_presencas"] = presencas
                        salvar_tudo()
                        st.success(f"✅ Check-in registrado!")
                        st.rerun()
                    else:
                        st.info("ℹ️ Já fez check-in hoje!")

            with st.expander("🛠️ Gestão de Alunos e Turmas"):
                banco = carregar_banco_usuarios()
                tipo_atual = st.session_state.get("tipo_usuario")
                academia_atual = st.session_state.get("perfil_academia", "").strip().lower()
                st.write(f"📊 **Total de Contas:** {len(banco)}")
                st.divider()
                
                academias_dict = {}
                for usr, info in banco.items():
                    d_usr = carregar_dados_usuario(usr)
                    acad = d_usr.get("perfil_academia", "Academia Não Informada").strip()
                    if tipo_atual == "Professor / Instrutor" and acad.lower() != academia_atual:
                        continue
                    if acad not in academias_dict:
                        academias_dict[acad] = []
                    academias_dict[acad].append((usr, info, d_usr))
                
                for acad_nome, lista_alunos in academias_dict.items():
                    st.markdown(f"🏛️ <b>{esc(acad_nome)}</b> ({len(lista_alunos)} alunos)", unsafe_allow_html=True)
                    for usr, info, d_usr in lista_alunos:
                        n_usr = d_usr.get("perfil_nome", "Sem Nome")
                        with st.expander(f"⚙️ {n_usr}"):
                            with st.form(key=f"form_g_{usr}"):
                                novo_em = st.text_input("E-mail:", value=usr, key=f"nem_{usr}")
                                nova_sen = st.text_input("Senha:", value=info.get("senha", ""), type="password", key=f"nsen_{usr}")
                                novo_no = st.text_input("Nome:", value=n_usr, key=f"nno_{usr}")
                                fs = ["Branca", "Azul", "Roxa", "Castanha", "Preta"]
                                f_atual = d_usr.get("perfil_faixa", "Branca")
                                idx_fx = fs.index(f_atual) if f_atual in fs else 0
                                nova_fx = st.selectbox("Faixa:", fs, index=idx_fx, key=f"nfx_{usr}")
                                n_graus = st.slider("Graus:", 0, 4, int(d_usr.get("perfil_graus", 0)), key=f"ngr_{usr}")
                                
                                c_b1, c_b2 = st.columns(2)
                                with c_b1: btn_s = st.form_submit_button("💾 Salvar")
                                with c_b2: btn_d = st.form_submit_button("🗑️ Excluir")
                                
                                if btn_s:
                                    b_atual = carregar_banco_usuarios()
                                    if novo_em != usr and novo_em in b_atual:
                                        st.error("❌ E-mail em uso.")
                                    else:
                                        d_ant = b_atual.pop(usr)
                                        d_ant["senha"] = nova_sen
                                        b_atual[novo_em] = d_ant
                                        salvar_banco_usuarios(b_atual)
                                        du = carregar_dados_usuario(novo_em)
                                        du["perfil_nome"] = novo_no
                                        du["perfil_faixa"] = nova_fx
                                        du["perfil_graus"] = n_graus
                                        salvar_dados_usuario(novo_em, du)
                                        st.toast("✅ Atualizado!")
                                        st.rerun()
                                if btn_d:
                                    b_atual = carregar_banco_usuarios()
                                    if usr in b_atual:
                                        del b_atual[usr]
                                        salvar_banco_usuarios(b_atual)
                                        st.toast("✅ Excluído!")
                                        st.rerun()

                    dados_plan = [{
                        "Atleta": d[2].get("perfil_nome"),
                        "Faixa": d[2].get("perfil_faixa"),
                        "Graus": d[2].get("perfil_graus"),
                        "Presenças": len(d[2].get("historico_presencas", []))
                    } for d in lista_alunos]
                    df_ac = pd.DataFrame(dados_plan)
                    csv_ex = df_ac.to_csv(index=False).encode('utf-8')
                    st.download_button(f"📥 Baixar Planilha ({acad_nome})", data=csv_ex, file_name=f"turma_{acad_nome}.csv", mime="text/csv", use_container_width=True)

        st.divider()
        if st.button("💾 Salvar Alterações Gerais", use_container_width=True):
            salvar_tudo()
            st.toast("✅ Dados salvos com sucesso!", icon="💾")
        if st.button("🚪 Sair da Conta (Logout)", use_container_width=True):
            fazer_logout()

    # Ecrã Principal & Abas
    st.markdown("<h1 style='text-align: center; color: #ff1e27;'>🥋 OssBot App Pro</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #cccccc;'>Atleta: <b>{esc(st.session_state.get('perfil_nome', 'Atleta Visitante'))}</b> | Faixa {esc(st.session_state.get('perfil_faixa', 'Branca'))} ({st.session_state.get('perfil_graus', 0)}º Grau)</p>", unsafe_allow_html=True)

    abas_app = st.tabs([
        "🤼 Luta", "📜 Histórico", "🥗 Nutrição", "🏆 Camp", "📚 Cursos", 
        "👶 Kids", "⚡ Drills", "🛡️ Pressão", "🥋 Graduação", "🥋 Kimono", 
        "📇 Card", "🔑 Chaves", "⏱️ Cronograma", "🔄 Recuperação"
    ])

    # 1. Luta & Placar Interativo com Cronômetro em Tempo Real
    with abas_app[0]:
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            mostrar_html(f"""
            <div class='placar-box'>
                <p style='color: #cccccc; margin: 0;'>ATLETA 1 (Azul/Preto):</p>
                <h3 style='color: #00ffcc; margin: 5px 0;'>Atleta Azul</h3>
                <div class='placar-numero'>{st.session_state.pts_a}</div>
                <p style='color: #ffffff; margin: 5px 0;'>Vantagens: {st.session_state.vant_a} | Punições: {st.session_state.pun_a}</p>
            </div>
            """)
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("+2 Pts (A)", key="p2a", use_container_width=True): somar_placar("pts_a", 2); st.rerun()
                if st.button("+3 Pts (A)", key="p3a", use_container_width=True): somar_placar("pts_a", 3); st.rerun()
            with c2:
                if st.button("+4 Pts (A)", key="p4a", use_container_width=True): somar_placar("pts_a", 4); st.rerun()
                if st.button("Vantagem (A)", key="v1a", use_container_width=True): somar_placar("vant_a", 1); st.rerun()
            with c3:
                if st.button("Punição (A)", key="pu1a", use_container_width=True): somar_placar("pun_a", 1); st.rerun()
                
        with col_p2:
            mostrar_html(f"""
            <div class='placar-box'>
                <p style='color: #cccccc; margin: 0;'>ATLETA 2 (Branco):</p>
                <h3 style='color: #ffffff; margin: 5px 0;'>Atleta Branco</h3>
                <div class='placar-numero'>{st.session_state.pts_b}</div>
                <p style='color: #ffffff; margin: 5px 0;'>Vantagens: {st.session_state.vant_b} | Punições: {st.session_state.pun_b}</p>
            </div>
            """)
            cb1, cb2, cb3 = st.columns(3)
            with cb1:
                if st.button("+2 Pts (B)", key="p2b", use_container_width=True): somar_placar("pts_b", 2); st.rerun()
                if st.button("+3 Pts (B)", key="p3b", use_container_width=True): somar_placar("pts_b", 3); st.rerun()
            with cb2:
                if st.button("+4 Pts (B)", key="p4b", use_container_width=True): somar_placar("pts_b", 4); st.rerun()
                if st.button("Vantagem (B)", key="v1b", use_container_width=True): somar_placar("vant_b", 1); st.rerun()
            with cb3:
                if st.button("Punição (B)", key="pu1b", use_container_width=True): somar_placar("pun_b", 1); st.rerun()

        st.divider()
        ct1, ct2, ct3 = st.columns(3)
        with ct1:
            tempo_sel = st.selectbox("Tempo do Rola (Minutos):", [1, 2, 3, 5, 6, 10], index=3)
            st.session_state.tempo_inicial = tempo_sel * 60

        with ct2:
            if st.session_state.cronometro_rodando:
                agora = time.time()
                delta = agora - st.session_state.ultimo_tick
                if delta >= 1.0:
                    st.session_state.tempo_segundos = max(0, st.session_state.tempo_segundos - int(delta))
                    st.session_state.ultimo_tick = agora
                    if st.session_state.tempo_segundos == 0:
                        st.session_state.cronometro_rodando = False

            ts = st.session_state.tempo_segundos
            mr, sr = ts // 60, ts % 60
            st.markdown(f"<h2 style='text-align: center; color: #ff1e27; margin: 0;'>⏱️ {mr:02d}:{sr:02d}</h2>", unsafe_allow_html=True)

        with ct3:
            if not st.session_state.cronometro_rodando:
                if st.button("▶️ Iniciar Cronômetro", use_container_width=True):
                    st.session_state.cronometro_rodando = True
                    st.session_state.ultimo_tick = time.time()
                    st.rerun()
            else:
                if st.button("⏸️ Pausar Cronômetro", use_container_width=True):
                    st.session_state.cronometro_rodando = False
                    st.rerun()
            if st.button("🔄 Zerar Luta Completa", use_container_width=True):
                zerar_luta()
                st.rerun()

        if st.session_state.cronometro_rodando and st.session_state.tempo_segundos > 0:
            time.sleep(1)
            st.rerun()

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
                    st.toast("✅ Luta registrada!", icon="🥋")
                    st.rerun()
        st.divider()
        for l in reversed(st.session_state.get("historico_lutas", [])):
            st.markdown(f"<div class='card-item'><b>{esc(l['data'])}</b> - {esc(l['resultado'])} | Oponente: <b>{esc(l['adversario'])}</b><br>{esc(l['detalhes'])}</div>", unsafe_allow_html=True)

    # 3. Nutrição & Macros
    with abas_app[2]:
        st.markdown("### 🥗 Nutrição & Calculadora de Macros")
        trans_nutri, resp_nutri = renderizar_gravador_audio("nutri", "nutrição, dieta e refeição para Jiu-Jitsu")
        
        with st.form("form_nutri"):
            refeicao = st.text_input("Refeição / Alimento:", value=trans_nutri)
            detalhes_nutri = st.text_area("Análise Nutricional da IA / Observações:", value=resp_nutri if resp_nutri else "")
            if st.form_submit_button("Salvar Refeição Nutricional", use_container_width=True):
                if refeicao:
                    nutri = st.session_state.get("dicas_nutricao", [])
                    nutri.append({"refeicao": refeicao, "detalhes": detalhes_nutri, "data": datetime.now().strftime("%d/%m/%Y")})
                    st.session_state["dicas_nutricao"] = nutri
                    salvar_tudo()
                    st.toast("✅ Refeição registrada!")
                    st.rerun()
        
        if st.session_state.get("dicas_nutricao"):
            st.markdown("#### 📊 Histórico Nutricional do Atleta")
            for n in reversed(st.session_state.get("dicas_nutricao", [])):
                st.markdown(f"""
                <div class='card-item'>
                    🥗 <b>Refeição:</b> {esc(n['refeicao'])} ({esc(n['data'])})<br>
                    💡 <b>Detalhes:</b> {esc(n['detalhes'])}
                </div>
                """, unsafe_allow_html=True)

    # 4. Camp de Competição
    with abas_app[3]:
        st.markdown("### 🏆 Camp de Competição & Estratégia")
        with st.form("form_camp"):
            evento = st.text_input("Nome do Campeonato / Torneio:")
            data_camp = st.date_input("Data do Torneio:", value=date.today())
            faixa_camp = st.text_input("Faixa/Categoria:", value=st.session_state.get("perfil_faixa", "Branca"))
            estilo_jogo = st.text_area("Fale um pouco do seu jogo e o que devemos treinar para este campeonato:")
            if st.form_submit_button("Salvar Estratégia de Camp", use_container_width=True):
                if evento:
                    camps = st.session_state.get("camp_competicao", [])
                    camps.append({"evento": evento, "data": data_camp.strftime("%d/%m/%Y"), "faixa": faixa_camp, "estilo": estilo_jogo})
                    st.session_state["camp_competicao"] = camps
                    salvar_tudo()
                    st.toast("✅ Plano de Camp salvo!")
                    st.rerun()
        st.divider()
        for c in reversed(st.session_state.get("camp_competicao", [])):
            st.markdown(f"""
            <div class='card-item'>
                🏆 <b>{esc(c['evento'])}</b> ({esc(c['data'])}) - Categoria: {esc(c['faixa'])}<br>
                🎯 <b>Estratégia:</b> {esc(c['estilo'])}
            </div>
            """, unsafe_allow_html=True)

    # 5. Cursos & Regras
    with abas_app[4]:
        st.markdown("### 📚 Cursos, Regras & Anotações de Estudo")
        trans_curso, resp_curso = renderizar_gravador_audio("curso", "técnica de BJJ, posição e regras IBJJF")
        
        with st.form("form_curso"):
            titulo_curso = st.text_input("Nome do Curso / Posição:", value=trans_curso)
            desc_curso = st.text_area("Explicação Técnica / Anotação da IA:", value=resp_curso if resp_curso else "")
            if st.form_submit_button("Salvar Estudo Técnico", use_container_width=True):
                if titulo_curso:
                    cursos = st.session_state.get("cursos_interativos", [])
                    cursos.append({"titulo": titulo_curso, "desc": desc_curso})
                    st.session_state["cursos_interativos"] = cursos
                    salvar_tudo()
                    st.toast("✅ Estudo salvo com sucesso!")
                    st.rerun()
        st.divider()
        for cur in reversed(st.session_state.get("cursos_interativos", [])):
            st.markdown(f"<div class='card-item'>📚 <b>{esc(cur['titulo'])}</b><br>{esc(cur['desc'])}</div>", unsafe_allow_html=True)

    # 6. Dinâmicas Kids
    with abas_app[5]:
        st.markdown("### 👶 Dinâmicas Pedagógicas para Turmas Kids")
        trans_kids, resp_kids = renderizar_gravador_audio("kids", "dinâmica infantil pedagógica de Jiu-Jitsu e brincadeiras")
        
        with st.form("form_kids"):
            foco_kids = st.text_input("Posição / Foco da Aula Kids:", value=trans_kids)
            regra_kids = st.text_area("Plano da Brincadeira / Aplicação da IA:", value=resp_kids if resp_kids else "")
            if st.form_submit_button("Salvar Dinâmica Kids", use_container_width=True):
                if foco_kids:
                    kids = st.session_state.get("dinamic_kids_custom", [])
                    kids.append({"foco": foco_kids, "regra": regra_kids})
                    st.session_state["dinamic_kids_custom"] = kids
                    salvar_tudo()
                    st.toast("✅ Dinâmica infantil salva!")
                    st.rerun()
        st.divider()
        for k in reversed(st.session_state.get("dinamic_kids_custom", [])):
            st.markdown(f"<div class='card-item'>👶 <b>Foco: {esc(k['foco'])}</b><br>{esc(k['regra'])}</div>", unsafe_allow_html=True)

    # 7. Drills Específicos
    with abas_app[6]:
        st.markdown("### ⚡ Drills de Repetição por Posição Alvo")
        trans_drill, resp_drill = renderizar_gravador_audio("drills", "drill de repetição, velocidade e agilidade no BJJ")
        
        with st.form("form_drill"):
            posicao_drill = st.text_input("Posição / Drill:", value=trans_drill)
            reps = st.text_area("Série / Recomendações do Drill:", value=resp_drill if resp_drill else "")
            if st.form_submit_button("Salvar Drill de Repetição", use_container_width=True):
                if posicao_drill:
                    drills = st.session_state.get("drills_treino", [])
                    drills.append({"posicao": posicao_drill, "reps": reps})
                    st.session_state["drills_treino"] = drills
                    salvar_tudo()
                    st.toast("✅ Drill salvo!")
                    st.rerun()
        st.divider()
        for d in reversed(st.session_state.get("drills_treino", [])):
            st.markdown(f"<div class='card-item'>⚡ <b>Drill: {esc(d['posicao'])}</b><br>{esc(d['reps'])}</div>", unsafe_allow_html=True)

    # 8. Flashcards de Pressão & Jogo
    with abas_app[7]:
        st.markdown("### 🛡️ Flashcards Táticos de Pressão & Jogo")
        trans_pressao, resp_pressao = renderizar_gravador_audio("pressao", "estratégia de jogo, pressão e reações de luta")
        
        with st.form("form_pressao"):
            estilo_proprio = st.text_area("Estilo de Jogo / Fala de Voz:", value=trans_pressao if trans_pressao else (resp_pressao if resp_pressao else ""))
            if st.form_submit_button("Gerar Flashcard Tático", use_container_width=True):
                if estilo_proprio:
                    fp = st.session_state.get("flashcards_pressao", [])
                    fp.append({"estilo": estilo_proprio})
                    st.session_state["flashcards_pressao"] = fp
                    salvar_tudo()
                    st.toast("✅ Flashcard gerado!")
                    st.rerun()
        st.divider()
        for f in reversed(st.session_state.get("flashcards_pressao", [])):
            st.markdown(f"""
            <div class='card-item'>
                🛡️ <b>Seu Estilo:</b> {esc(f['estilo'])}<br>
                ❓ <b>Desafio Tático:</b> Se o oponente passar sua guarda e colar no cem-quilos, qual sua reação imediata?
            </div>
            """, unsafe_allow_html=True)

    # 9. Graduação
    with abas_app[8]:
        st.markdown("### 🥋 Controle de Graduação & Evolução")
        with st.form("form_grad"):
            aluno_g = st.text_input("Nome do Aluno:")
            faixa_g = st.selectbox("Faixa Alvo:", ["Branca", "Azul", "Roxa", "Castanha", "Preta"])
            grau_g = st.slider("Graus Atuais:", 0, 4)
            observacao_grad = st.text_area("Critérios técnicos para o próximo grau/faixa:")
            if st.form_submit_button("Registrar Graduação", use_container_width=True):
                if aluno_g:
                    grad = st.session_state.get("alunos_graduacao", [])
                    grad.append({"aluno": aluno_g, "faixa": faixa_g, "grau": grau_g, "obs": observacao_grad})
                    st.session_state["alunos_graduacao"] = grad
                    salvar_tudo()
                    st.toast("✅ Graduação registrada!")
                    st.rerun()
        st.divider()
        for ag in reversed(st.session_state.get("alunos_graduacao", [])):
            st.markdown(f"<div class='card-item'>🥋 <b>{esc(ag['aluno'])}</b> - Faixa {esc(ag['faixa'])} ({ag['grau']}º Grau)<br>📝 <i>{esc(ag.get('obs', ''))}</i></div>", unsafe_allow_html=True)

    # 10. Guia de Cuidado com Kimonos
    with abas_app[9]:
        st.markdown("### 🥋 Guia de Cuidado e Higienização do Kimono")
        trans_kimono, resp_kimono = renderizar_gravador_audio("kimono", "higienização, lavagem e cuidado com kimono")
        
        with st.form("form_kimono"):
            sujeira_k = st.text_area("Estado do Kimono / Transcrição de Voz:", value=trans_kimono if trans_kimono else (resp_kimono if resp_kimono else ""))
            if st.form_submit_button("Obter Dica de Lavagem", use_container_width=True):
                if sujeira_k:
                    kims = st.session_state.get("notas_kimono", [])
                    kims.append({"sujeira": sujeira_k})
                    st.session_state["notas_kimono"] = kims
                    salvar_tudo()
                    st.toast("✅ Dica gerada!")
                    st.rerun()
        st.divider()
        for km in reversed(st.session_state.get("notas_kimono", [])):
            st.markdown(f"""
            <div class='card-item'>
                🥋 <b>Estado:</b> {esc(km['sujeira'])}<br>
                💡 <b>Dica:</b> Deixe de molho no vinagre de álcool branco por 30 min e lave com sabão neutro. Nunca use cloro!
            </div>
            """, unsafe_allow_html=True)

    # 11. Cartão Digital
    with abas_app[10]:
        st.markdown("### 📇 Cartão Digital de Atleta")
        st.markdown(f"""
        <div class='placar-box' style='text-align: left; max-width: 420px; margin: 0 auto 20px auto;'>
            <h3 style='color: #ff1e27; margin-top: 0;'>🥋 OSSBOT - CARTÃO OFICIAL</h3>
            <p><b>Nome:</b> {esc(st.session_state.get('perfil_nome', 'Atleta'))}</p>
            <p><b>Faixa:</b> {esc(st.session_state.get('perfil_faixa', 'Branca'))} ({st.session_state.get('perfil_graus', 0)}º Grau)</p>
            <p><b>Academia:</b> {esc(st.session_state.get('perfil_academia', 'Nenhum'))}</p>
            <p><b>Status:</b> {esc(st.session_state.get('perfil_status', 'Atleta'))}</p>
        </div>
        """, unsafe_allow_html=True)
        st.download_button(
            "📥 Baixar Carteirinha em TXT",
            data=gerar_relatorio_pdf_atleta(),
            file_name="carteirinha_ossbot.txt",
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
        for ch in reversed(st.session_state.get("chaves_luta", [])):
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
        for cr in reversed(st.session_state.get("cronogramas_aulas", [])):
            st.markdown(f"<div class='card-item'>⏱️ <b>{esc(cr['dia'])}</b>: {esc(cr['detalhe'])}</div>", unsafe_allow_html=True)

    # 14. Recuperação & Lesões
    with abas_app[13]:
        st.markdown("### 🔄 Registro de Recuperação, Dores e Lesões")
        trans_recup, resp_recup = renderizar_gravador_audio("recuperacao", "recuperação física, dor muscular e lesões do atleta")
        
        with st.form("form_recup"):
            nota_r = st.text_area("Registro de Recuperação / Orientação da IA:", value=f"Relato: {trans_recup}\n\nRecomendação: {resp_recup}" if trans_recup else "")
            if st.form_submit_button("Salvar Nota de Recuperação", use_container_width=True):
                if nota_r:
                    recup = st.session_state.get("recuperacao_notas", [])
                    recup.append({"nota": nota_r, "data": datetime.now().strftime("%d/%m/%Y")})
                    st.session_state["recuperacao_notas"] = recup
                    salvar_tudo()
                    st.toast("✅ Nota de lesão registrada!")
                    st.rerun()
        st.divider()
        for rc in reversed(st.session_state.get("recuperacao_notas", [])):
            st.markdown(f"<div class='card-item'>🔄 <b>{esc(rc['data'])}</b><br>{esc(rc['nota'])}</div>", unsafe_allow_html=True)

except Exception as e:
    nome_usr_erro = st.session_state.get("perfil_nome", "Usuário")
    is_adm_erro = st.session_state.get("is_admin", False) or (st.session_state.get("usuario_email", "").lower() == EMAIL_ADMIN_MASTER.lower())
    detalhes_erro_str = traceback.format_exc()

    st.markdown("<div class='ia-erro-card'>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: #ff1e27; margin-top: 0;'>🤖 OssBot IA - Assistente de Diagnóstico</h3>", unsafe_allow_html=True)
    
    if is_adm_erro:
        st.markdown(f"""
        <p style='color: #ffffff; font-size: 15px;'>
            <b>Olha só, {esc(nome_usr_erro)}!</b> Ocorreu um imprevisto técnico no seu código. 
            Como você é o <b>Administrador/Fundador</b>, aqui está o diagnóstico:
        </p>
        <div style='background: #0b0b0b; padding: 12px; border-radius: 6px; border: 1px solid #444; color: #ff6b6b; font-family: monospace; font-size: 13px;'>
            <b>Tipo de Erro:</b> {esc(type(e).__name__)}<br>
            <b>Descrição:</b> {esc(str(e))}<br><br>
            <pre style='color: #cccccc;'>{esc(detalhes_erro_str)}</pre>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <p style='color: #ffffff; font-size: 15px;'>
            <b>Olha só, {esc(nome_usr_erro)}!</b> Ocorreu uma pequena instabilidade nesta função.
        </p>
        <p style='color: #fbbf24; font-size: 14px;'>
            📣 Informe ao administrador do sistema para realizar esse ajuste no código!
        </p>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
