import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, date
import os
import json
import base64
import traceback
import time
import pandas as pd
from gtts import gTTS
import tempfile
import random

# Configuração inicial da página
st.set_page_config(
    page_title="OssBot Pro - Gestão Profissional de BJJ",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constantes globais do Fundador
EMAIL_ADMIN_MASTER = "henry.cesaraguiar@gmail.com"
SENHA_ADMIN_MASTER = "Dca@980950"

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

# Estilos CSS Customizados
st.markdown("""
<style>
    .stApp { background-color: #0b0b0b; color: #ffffff; }
    .placar-box { background-color: #161616; border: 2px solid #ff1e27; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 4px 20px rgba(255, 30, 39, 0.2); }
    .placar-numero { font-size: 50px; font-weight: bold; color: #ff1e27; }
    .card-item { background-color: #141414; border-left: 4px solid #ff1e27; border-radius: 8px; padding: 15px; margin-bottom: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.5); }
    .foto-bolinha { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 2px solid #ff1e27; display: block; margin: 0 auto 10px auto; }
    .bolinha-padrao { width: 80px; height: 80px; border-radius: 50%; background-color: #1a1a1a; border: 2px solid #ff1e27; display: flex; align-items: center; justify-content: center; font-size: 30px; margin: 0 auto 10px auto; }
    .ia-resposta-box { background-color: #161616; border: 1px solid #00ffcc; border-radius: 12px; padding: 25px; margin-top: 10px; color: #ffffff; box-shadow: 0 4px 15px rgba(0,255,204,0.1); line-height: 1.7; font-size: 15px; }
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

def processar_consenso_ia_dual(tema_input, contexto_aba, nome_usuario):
    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M')
    tema_desc = tema_input if tema_input else "Técnica de Jiu-Jitsu"
    seed_rand = random.randint(100, 999)
    
    if "drill" in contexto_aba.lower():
        return f"""🤖 **OssBot IA Master - Plano de Drills (Gemini 🤝 Grok)** [Ref: #{seed_rand}]
*Atleta:* **{nome_usuario}** | *Foco:* **{esc(tema_desc)}**
### 1. Objetivo Técnico
Desenvolvimento de memória muscular e velocidade de transição focada diretamente em **{esc(tema_desc)}**.
### 2. Estrutura de Blocos e Tempos
* **Bloco 1 (Aquecimento Dinâmico - 2 Minutos):** Movimentação limpa e sem resistência para fixar a mecânica de {esc(tema_desc)}.
* **Bloco 2 (Resistência Parcial - 4 Séries de 1 Minuto / 20s Descanso):** O parceiro oferece 40% de oposição.
* **Bloco 3 (Velocidade Máxima - 2 Rounds de 45 Segundos):** Execução em alta intensidade.
💡 **Consenso Final:** Repetição consciente e constância garantem a perfeição!"""

    elif "infantil" in contexto_aba.lower() or "kids" in contexto_aba.lower():
        return f"""🤖 **OssBot IA Master - Dinâmica Kids com Jogos e Tempos (Gemini 🤝 Grok)** [Ref: #{seed_rand}]
*Professor:* **{nome_usuario}** | *Foco Principal:* **{esc(tema_desc)}**
### 1. Brincadeira de Aquecimento e Mobilidade (Duração: 4 Minutos)
* **Nome do Jogo:** *O Desafio do Caranguejo Ágil*
* **Como Funciona:** Deslocamento em posição de caranguejo para aquecer quadris e ombros exigidos em **{esc(tema_desc)}**.
### 2. Jogo Técnico Principal com Cronômetro (Duração: 8 Minutos)
* **Nome do Jogo:** *A Fortaleza Protegida*
* **Aplicação Prática ({esc(tema_desc)}):** Aluno por baixo foca em manter a base firme nos conceitos de {esc(tema_desc)}, enquanto o colega tenta passar.
* **Regra de Tempo:** Rodadas de 1 minuto cada, alternando posições.
### 3. Desafio Final de Agilidade (Duração: 3 Minutos)
* **Nome do Jogo:** *Estátua de Ferro*
* **Como Funciona:** Ao sinal do professor, travar o corpo na posição base de **{esc(tema_desc)}**.
💡 **Consenso Final:** Dinâmica estruturada com foco absoluto em **{esc(tema_desc)}**!"""

    elif "nutrição" in contexto_aba.lower():
        return f"""🤖 **OssBot IA Master - Manual Nutricional (Gemini 🤝 Grok)** [Ref: #{seed_rand}]
*Atleta:* **{nome_usuario}** | *Foco:* **{esc(tema_desc)}**
### 1. Estratégia Energética Pré-Treino
* **Timing:** 45 minutos antes. Vitamina de banana com aveia e mel.
### 2. Hidratação e Recuperação
* Reposição hídrica fracionada e pós-treino proteico.
💡 **Consenso Final:** Nutrição alinhada para máxima performance!"""

    elif "arbitragem_cbjj" in contexto_aba.lower():
        return f"""⚖️ **Assistente de Regras CBJJ (Análise Automática da Ação)**
*Ação Narrada:* **{esc(tema_desc)}**

De acordo com o Livro Oficial de Regras da CBJJ:
* **Interpretação do Lance:** A descrição indica uma transição válida pontuável ou finalização.
* **Pontuação Oficial Sugerida:** 
  - Queda / Raspagem / Joelho na Barriga: **2 pontos**
  - Passagem de Guarda: **3 pontos**
  - Montagem / Costas: **4 pontos**
  - Vantagem: Concedida em tentativa de finalização ou quase-passagem.
💡 **Aplicação Prática:** Verifique o placar acima para adicionar os pontos correspondentes com base nesta diretriz oficial!"""

    else:
        return f"""🤖 **OssBot IA Master - Relatório Técnico (Gemini 🤝 Grok)** [Ref: #{seed_rand}]
*Atleta:* **{nome_usuario}** | *Tópico:* **{esc(tema_desc)}**
### 1. Análise Tática de {esc(tema_desc)}
* Manutenção rigorosa do centro de gravidade baixo e domínio antecipado de pegadas.
💡 **Consenso Final:** Foco total na execução limpa!"""

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

# Bloco Principal com Tratamento de Erros
try:
    if not st.session_state.autenticado:
        col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
        with col_l2:
            st.markdown("<h1 style='text-align: center; color: #ff1e27;'>🥋 OssBot Pro</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #cccccc;'>Plataforma Profissional de Gestão com IA Dual (Gemini + Grok)</p>", unsafe_allow_html=True)
            
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
                foto_arquivo_side = st.file_uploader("Alterar Foto de Perfil:", type=["jpg", "jpeg", "png"], key="side_foto_up")
                
                if st.form_submit_button("💾 Salvar Perfil", use_container_width=True):
                    st.session_state["perfil_nome"] = novo_nome if novo_nome else "Atleta Visitante"
                    st.session_state["perfil_faixa"] = nova_faixa
                    st.session_state["perfil_graus"] = novos_graus
                    st.session_state["perfil_academia"] = nova_academia if nova_academia else "Insira a sua Academia"
                    if foto_arquivo_side is not None:
                        bytes_foto = foto_arquivo_side.getvalue()
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
                            f_b64_aluno = d_usr.get("perfil_foto_b64", "")
                            if f_b64_aluno:
                                st.markdown(f'<img src="data:image/jpeg;base64,{f_b64_aluno}" class="foto-bolinha">', unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="bolinha-padrao" style="width: 50px; height: 50px; font-size: 20px;">🥋</div>', unsafe_allow_html=True)
                                
                            with st.form(key=f"form_g_{usr}"):
                                novo_em = st.text_input("E-mail:", value=usr, key=f"nem_{usr}")
                                nova_sen = st.text_input("Senha:", value=info.get("senha", ""), type="password", key=f"nsen_{usr}")
                                novo_no = st.text_input("Nome:", value=n_usr, key=f"nno_{usr}")
                                fs = ["Branca", "Azul", "Roxa", "Castanha", "Preta"]
                                f_atual = d_usr.get("perfil_faixa", "Branca")
                                idx_fx = fs.index(f_atual) if f_atual in fs else 0
                                nova_fx = st.selectbox("Faixa:", fs, index=idx_fx, key=f"nfx_{usr}")
                                n_graus = st.slider("Graus:", 0, 4, int(d_usr.get("perfil_graus", 0)), key=f"ngr_{usr}")
                                nova_foto_aluno_arquivo = st.file_uploader("Alterar Foto do Aluno:", type=["jpg", "jpeg", "png"], key=f"foto_up_{usr}")
                                
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
                                        if nova_foto_aluno_arquivo is not None:
                                            b_foto_aluno = nova_foto_aluno_arquivo.getvalue()
                                            du["perfil_foto_b64"] = base64.b64encode(b_foto_aluno).decode("utf-8")
                                        salvar_dados_usuario(novo_em, du)
                                        st.toast("✅ Atualizado com sucesso!")
                                        st.rerun()
                                if btn_d:
                                    b_atual = carregar_banco_usuarios()
                                    if usr in b_atual:
                                        del b_atual[usr]
                                        salvar_banco_usuarios(b_atual)
                                        st.toast("✅ Excluído com sucesso!")
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
    st.markdown("<h1 style='text-align: center; color: #ff1e27;'>🥋 OssBot App Pro (IA Dual)</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #cccccc;'>Atleta: <b>{esc(st.session_state.get('perfil_nome', 'Atleta Visitante'))}</b> | Faixa {esc(st.session_state.get('perfil_faixa', 'Branca'))} ({st.session_state.get('perfil_graus', 0)}º Grau)</p>", unsafe_allow_html=True)

    abas_app = st.tabs([
        "🤼 Luta", "📜 Histórico", "🥗 Nutrição", "🏆 Camp", "📚 Cursos", 
        "👶 Kids", "⚡ Drills", "🛡️ Pressão", "🥋 Graduação", "🥋 Kimono", 
        "📇 Card", "🔑 Chaves", "⏱️ Cronograma", "🔄 Recuperação"
    ])

    # 1. Luta & Placar Interativo Integrado com Narração e Salvamento Direto
    with abas_app[0]:
        st.markdown("### 🤼 Placar de Luta em Tempo Real (Regras CBJJ)")
        
        col_n1, col_n2 = st.columns(2)
        with col_n1:
            nome_atleta_a = st.text_input("Nome Atleta 1 (Azul/Preto):", value=st.session_state.get("nome_a_luta", "Atleta 1"))
            st.session_state["nome_a_luta"] = nome_atleta_a
        with col_n2:
            nome_atleta_b = st.text_input("Nome Atleta 2 (Branco):", value=st.session_state.get("nome_b_luta", "Atleta 2"))
            st.session_state["nome_b_luta"] = nome_atleta_b

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            mostrar_html(f"""
            <div class='placar-box'>
                <p style='color: #cccccc; margin: 0;'>ATLETA 1:</p>
                <h3 style='color: #00ffcc; margin: 5px 0;'>{esc(nome_atleta_a)}</h3>
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
                <p style='color: #cccccc; margin: 0;'>ATLETA 2:</p>
                <h3 style='color: #ffffff; margin: 5px 0;'>{esc(nome_atleta_b)}</h3>
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

        # Caixa de Assistente de Narração Automática (Use o microfone do seu teclado!)
        with st.form("form_narracao_automatica"):
            st.markdown("### 🎙️ Assistente de Pontuação por Voz / Texto")
            st.markdown("<p style='font-size: 13px; color: #cccccc;'>Toque no campo abaixo, use o microfone do seu teclado para falar (ex: <i>'Atleta Azul raspou e finalizou'</i>) e clique em consultar:</p>", unsafe_allow_html=True)
            narracao_acao = st.text_input("O que aconteceu na luta?", value="")
            btn_consultar_acao = st.form_submit_button("⚖️ Consultar Regra e Definir Pontuação", use_container_width=True)
            
            if btn_consultar_acao and narracao_acao:
                resp_analise = processar_consenso_ia_dual(narracao_acao, "arbitragem_cbjj", st.session_state.get("perfil_nome", "Árbitro"))
                st.markdown(f"<div class='ia-resposta-box'>{resp_analise}</div>", unsafe_allow_html=True)

        st.divider()
        ct1, ct2, ct3, ct4 = st.columns(4)
        with ct1:
            tempo_sel = st.selectbox("Tempo do Rola (Min):", [1, 2, 3, 5, 6, 10], index=3)
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
                if st.button("▶️ Iniciar", use_container_width=True):
                    st.session_state.cronometro_rodando = True
                    st.session_state.ultimo_tick = time.time()
                    st.rerun()
            else:
                if st.button("⏸️ Pausar", use_container_width=True):
                    st.session_state.cronometro_rodando = False
                    st.rerun()

        with ct4:
            if st.button("🔄 Zerar", use_container_width=True):
                zerar_luta()
                st.rerun()

        if st.session_state.cronometro_rodando and st.session_state.tempo_segundos > 0:
            time.sleep(1)
            st.rerun()

        st.divider()
        
        # Botão e Formulário de Salvar Luta Integrado
        with st.form("form_salvar_luta_oficial"):
            st.markdown("### 💾 Salvar Luta no Histórico")
            identificador_luta = st.text_input("Nome para pesquisar depois no histórico (Ex: Final Absoluto - João vs Pedro):", value=f"{nome_atleta_a} vs {nome_atleta_b}")
            obs_luta = st.text_area("Observações / O que aconteceu (Ex: Finalizou com estrangulamento):", value="")
            
            btn_salvar_definitivo = st.form_submit_button("📥 Registrar e Salvar Luta no Histórico", use_container_width=True)
            if btn_salvar_definitivo:
                tempo_decorrido_seg = st.session_state.tempo_inicial - st.session_state.tempo_segundos
                min_dec, sec_dec = tempo_decorrido_seg // 60, tempo_decorrido_seg % 60
                tempo_total_min = st.session_state.tempo_inicial // 60
                
                lutas = st.session_state.get("historico_lutas", [])
                nova_luta = {
                    "data": datetime.now().strftime("%d/%m/%Y - %H:%M"),
                    "identificador": identificador_luta,
                    "atleta_a": nome_atleta_a,
                    "atleta_b": nome_atleta_b,
                    "pts_a": st.session_state.pts_a,
                    "vant_a": st.session_state.vant_a,
                    "pun_a": st.session_state.pun_a,
                    "pts_b": st.session_state.pts_b,
                    "vant_b": st.session_state.vant_b,
                    "pun_b": st.session_state.pun_b,
                    "tempo_total": f"{tempo_total_min} min",
                    "tempo_duracao": f"{min_dec:02d}:{sec_dec:02d}",
                    "observacoes": obs_luta
                }
                lutas.append(nova_luta)
                st.session_state["historico_lutas"] = lutas
                salvar_tudo()
                st.success(f"✅ Luta '{identificador_luta}' salva com sucesso no histórico!")

    # 2. Histórico Pesquisable por Nome
    with abas_app[1]:
        st.markdown("### 📜 Histórico de Combates Salvos")
        lutas_lista = st.session_state.get("historico_lutas", [])
        
        if not lutas_lista:
            st.info("Nenhuma luta salva ainda. Realize um combate na aba 'Luta' e clique em salvar!")
        else:
            termo_busca = st.text_input("🔍 Pesquisar luta por nome ou identificador:", value="")
            
            lutas_filtradas = []
            for idx, l in enumerate(reversed(lutas_lista)):
                idx_real = len(lutas_lista) - 1 - idx
                ident_nome = l.get("identificador", f"{l.get('atleta_a', 'Atleta 1')} vs {l.get('atleta_b', 'Atleta 2')}")
                if termo_busca.strip().lower() in ident_nome.lower() or termo_busca.strip() == "":
                    lutas_filtradas.append((idx_real, l))
            
            st.write(f"Exibindo **{len(lutas_filtradas)}** luta(s):")
            st.divider()
            
            for idx_real, l in lutas_filtradas:
                ident_nome = l.get("identificador", "Combate BJJ")
                at_a = l.get("atleta_a", "Atleta 1")
                at_b = l.get("atleta_b", "Atleta 2")
                p_a = l.get("pts_a", 0)
                v_a = l.get("vant_a", 0)
                pu_a = l.get("pun_a", 0)
                p_b = l.get("pts_b", 0)
                v_b = l.get("vant_b", 0)
                pu_b = l.get("pun_b", 0)
                t_tot = l.get("tempo_total", "5 min")
                t_dur = l.get("tempo_duracao", "00:00")
                obs = l.get("observacoes", "")
                data_l = l.get("data", "")
                
                with st.expander(f"🥋 {ident_nome} ({data_l})"):
                    col_h1, col_h2 = st.columns(2)
                    with col_h1:
                        st.markdown(f"**{esc(at_a)}** (Atleta 1)")
                        st.markdown(f"🏆 Pts: **{p_a}** | Vant: **{v_a}** | Pun: **{pu_a}**")
                    with col_h2:
                        st.markdown(f"**{esc(at_b)}** (Atleta 2)")
                        st.markdown(f"🏆 Pts: **{p_b}** | Vant: **{v_b}** | Pun: **{pu_b}**")
                    
                    st.markdown(f"⏱️ **Tempo Configurado:** {t_tot} | **Duração até Fim:** {t_dur}")
                    if obs:
                        st.markdown(f"📝 **Detalhes:** {esc(obs)}")
                    
                    if st.button(f"🗑️ Excluir Luta #{idx_real+1}", key=f"del_luta_hist_{idx_real}"):
                        lutas_lista.pop(idx_real)
                        st.session_state["historico_lutas"] = lutas_lista
                        salvar_tudo()
                        st.toast("🗑️ Luta excluída com sucesso!")
                        st.rerun()

    # 3. Nutrição & Macros
    with abas_app[2]:
        st.markdown("### 🥗 Nutrição & Calculadora de Macros (IA Dual)")
        with st.form("form_nutri"):
            refeicao = st.text_input("Refeição / Alimento a planejar (Ex: Dieta para corte de peso):", value="")
            if st.form_submit_button("Gerar e Salvar Manual Nutricional", use_container_width=True):
                if refeicao:
                    resp_gerada = processar_consenso_ia_dual(refeicao, "nutrição", st.session_state.get("perfil_nome", "Atleta"))
                    nutri = st.session_state.get("dicas_nutricao", [])
                    nutri.append({"refeicao": refeicao, "detalhes": resp_gerada, "data": datetime.now().strftime("%d/%m/%Y")})
                    st.session_state["dicas_nutricao"] = nutri
                    salvar_tudo()
                    st.toast("✅ Manual nutricional gerado e salvo!")
                    st.rerun()
        
        if st.session_state.get("dicas_nutricao"):
            st.markdown("#### 📊 Histórico Nutricional do Atleta")
            nutri_lista = st.session_state.get("dicas_nutricao", [])
            for idx, n in enumerate(reversed(nutri_lista)):
                idx_real = len(nutri_lista) - 1 - idx
                with st.expander(f"🥗 {n['refeicao']} ({n['data']})"):
                    st.markdown(f"{n['detalhes']}")
                    if st.button(f"🗑️ Excluir Refeição #{idx_real+1}", key=f"del_nutri_{idx_real}"):
                        nutri_lista.pop(idx_real)
                        st.session_state["dicas_nutricao"] = nutri_lista
                        salvar_tudo()
                        st.toast("🗑️ Refeição excluída!")
                        st.rerun()

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
        camps_lista = st.session_state.get("camp_competicao", [])
        for idx, c in enumerate(reversed(camps_lista)):
            idx_real = len(camps_lista) - 1 - idx
            with st.expander(f"🏆 {c['evento']} ({c['data']}) - {c['faixa']}"):
                st.markdown(f"**Estratégia Completa:**\n\n{c['estilo']}")
                if st.button(f"🗑️ Excluir Camp #{idx_real+1}", key=f"del_camp_{idx_real}"):
                    camps_lista.pop(idx_real)
                    st.session_state["camp_competicao"] = camps_lista
                    salvar_tudo()
                    st.toast("🗑️ Camp excluído!")
                    st.rerun()

    # 5. Cursos & Regras
    with abas_app[4]:
        st.markdown("### 📚 Cursos, Regras & Anotações de Estudo")
        with st.form("form_curso"):
            titulo_curso = st.text_input("Nome do Curso / Posição a estudar (Ex: Guarda Aranha):", value="")
            if st.form_submit_button("Gerar e Salvar Estudo Técnico", use_container_width=True):
                if titulo_curso:
                    resp_gerada = processar_consenso_ia_dual(titulo_curso, "curso", st.session_state.get("perfil_nome", "Atleta"))
                    cursos = st.session_state.get("cursos_interativos", [])
                    cursos.append({"titulo": titulo_curso, "desc": resp_gerada})
                    st.session_state["cursos_interativos"] = cursos
                    salvar_tudo()
                    st.toast("✅ Estudo técnico gerado e salvo!")
                    st.rerun()
        st.divider()
        cursos_lista = st.session_state.get("cursos_interativos", [])
        for idx, cur in enumerate(reversed(cursos_lista)):
            idx_real = len(cursos_lista) - 1 - idx
            with st.expander(f"📚 {cur['titulo']}"):
                st.markdown(f"{cur['desc']}")
                if st.button(f"🗑️ Excluir Curso #{idx_real+1}", key=f"del_curso_{idx_real}"):
                    cursos_lista.pop(idx_real)
                    st.session_state["cursos_interativos"] = cursos_lista
                    salvar_tudo()
                    st.toast("🗑️ Estudo excluído!")
                    st.rerun()

    # 6. Dinâmicas Kids
    with abas_app[5]:
        st.markdown("### 👶 Dinâmicas Pedagógicas para Turmas Kids")
        with st.form("form_kids"):
            foco_kids = st.text_input("Sobre o que você quer que a dinâmica trabalhe? (Ex: Guarda fechada com jogos e tempo)", value="")
            if st.form_submit_button("Gerar Dossiê Pedagógico Kids Completo", use_container_width=True):
                if foco_kids:
                    regra_kids = processar_consenso_ia_dual(foco_kids, "kids", st.session_state.get("perfil_nome", "Professor"))
                    kids = st.session_state.get("dinamic_kids_custom", [])
                    kids.append({"foco": foco_kids, "regra": regra_kids})
                    st.session_state["dinamic_kids_custom"] = kids
                    salvar_tudo()
                    st.toast("✅ Dossiê Kids gerado com sucesso!")
                    st.rerun()
        st.divider()
        kids_lista = st.session_state.get("dinamic_kids_custom", [])
        if kids_lista:
            st.markdown("#### 📁 Dossiês Kids Salvos (Clique para Expandir)")
            for idx, k in enumerate(reversed(kids_lista)):
                idx_real = len(kids_lista) - 1 - idx
                with st.expander(f"👶 Foco: {k['foco']}"):
                    st.markdown(f"{k['regra']}")
                    if st.button(f"🗑️ Excluir Dinâmica Kids #{idx_real+1}", key=f"del_kids_{idx_real}"):
                        kids_lista.pop(idx_real)
                        st.session_state["dinamic_kids_custom"] = kids_lista
                        salvar_tudo()
                        st.toast("🗑️ Dinâmica excluída com sucesso!")
                        st.rerun()

    # 7. Drills Específicos
    with abas_app[6]:
        st.markdown("### ⚡ Drills de Repetição, Ritmo e Agilidade (IA Dual)")
        with st.form("form_drill"):
            posicao_drill = st.text_input("Sobre o que o drill seria? (Ex: Passagem de guarda toreando com pressão)", value="")
            if st.form_submit_button("Gerar Plano de Drills Completo", use_container_width=True):
                if posicao_drill:
                    reps_gerada = processar_consenso_ia_dual(posicao_drill, "drill", st.session_state.get("perfil_nome", "Atleta"))
                    drills = st.session_state.get("drills_treino", [])
                    drills.append({"posicao": posicao_drill, "reps": reps_gerada})
                    st.session_state["drills_treino"] = drills
                    salvar_tudo()
                    st.toast("✅ Plano de Drills gerado com sucesso!")
                    st.rerun()
        st.divider()
        drills_lista = st.session_state.get("drills_treino", [])
        if drills_lista:
            st.markdown("#### 📁 Planos de Drills Salvos (Clique para Expandir)")
            for idx, d in enumerate(reversed(drills_lista)):
                idx_real = len(drills_lista) - 1 - idx
                with st.expander(f"⚡ Drill: {d['posicao']}"):
                    st.markdown(f"{d['reps']}")
                    if st.button(f"🗑️ Excluir Drill #{idx_real+1}", key=f"del_drill_{idx_real}"):
                        drills_lista.pop(idx_real)
                        st.session_state["drills_treino"] = drills_lista
                        salvar_tudo()
                        st.toast("🗑️ Drill excluído com sucesso!")
                        st.rerun()

    # 8. Flashcards de Pressão & Jogo
    with abas_app[7]:
        st.markdown("### 🛡️ Flashcards Táticos de Pressão & Jogo")
        with st.form("form_pressao"):
            estilo_proprio = st.text_area("Descreva seu estilo de jogo ou dúvida tática:", value="")
            if st.form_submit_button("Gerar Flashcard Tático", use_container_width=True):
                if estilo_proprio:
                    fp = st.session_state.get("flashcards_pressao", [])
                    fp.append({"estilo": estilo_proprio})
                    st.session_state["flashcards_pressao"] = fp
                    salvar_tudo()
                    st.toast("✅ Flashcard gerado!")
                    st.rerun()
        st.divider()
        fp_lista = st.session_state.get("flashcards_pressao", [])
        for idx, f in enumerate(reversed(fp_lista)):
            idx_real = len(fp_lista) - 1 - idx
            with st.expander(f"🛡️ Estilo: {f['estilo'][:30]}..."):
                st.markdown(f"""
                <b>Seu Estilo:</b> {esc(f['estilo'])}<br><br>
                ❓ <b>Desafio Tático:</b> Se o oponente passar sua guarda e colar no cem-quilos, qual sua reação imediata?
                """)
                if st.button(f"🗑️ Excluir Flashcard #{idx_real+1}", key=f"del_fp_{idx_real}"):
                    fp_lista.pop(idx_real)
                    st.session_state["flashcards_pressao"] = fp_lista
                    salvar_tudo()
                    st.toast("🗑️ Flashcard excluído!")
                    st.rerun()

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
        grad_lista = st.session_state.get("alunos_graduacao", [])
        for idx, ag in enumerate(reversed(grad_lista)):
            idx_real = len(grad_lista) - 1 - idx
            with st.expander(f"🥋 {ag['aluno']} - Faixa {ag['faixa']} ({ag['grau']}º Grau)"):
                st.markdown(f"📝 **Critérios:** {esc(ag.get('obs', ''))}")
                if st.button(f"🗑️ Excluir Registro #{idx_real+1}", key=f"del_grad_{idx_real}"):
                    grad_lista.pop(idx_real)
                    st.session_state["alunos_graduacao"] = grad_lista
                    salvar_tudo()
                    st.toast("🗑️ Registro excluído!")
                    st.rerun()

    # 10. Guia de Cuidado com Kimonos
    with abas_app[9]:
        st.markdown("### 🥋 Guia de Cuidado e Higienização do Kimono")
        with st.form("form_kimono"):
            sujeira_k = st.text_area("Estado do Kimono / Dúvida de Lavagem:", value="")
            if st.form_submit_button("Obter Dica de Lavagem", use_container_width=True):
                if sujeira_k:
                    kims = st.session_state.get("notas_kimono", [])
                    kims.append({"sujeira": sujeira_k})
                    st.session_state["notas_kimono"] = kims
                    salvar_tudo()
                    st.toast("✅ Dica gerada!")
                    st.rerun()
        st.divider()
        kims_lista = st.session_state.get("notas_kimono", [])
        for idx, km in enumerate(reversed(kims_lista)):
            idx_real = len(kims_lista) - 1 - idx
            with st.expander(f"🥋 Estado: {km['sujeira'][:30]}..."):
                st.markdown(f"""
                <b>Estado:</b> {esc(km['sujeira'])}<br><br>
                💡 <b>Dica:</b> Deixe de molho no vinagre de álcool branco por 30 min e lave com sabão neutro. Nunca use cloro!
                """)
                if st.button(f"🗑️ Excluir Nota #{idx_real+1}", key=f"del_kimono_{idx_real}"):
                    kims_lista.pop(idx_real)
                    st.session_state["notas_kimono"] = kims_lista
                    salvar_tudo()
                    st.toast("🗑️ Nota excluída!")
                    st.rerun()

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
        chaves_lista = st.session_state.get("chaves_luta", [])
        for idx, ch in enumerate(reversed(chaves_lista)):
            idx_real = len(chaves_lista) - 1 - idx
            with st.expander(f"🔑 Torneio: {ch['torneio']}"):
                st.markdown(f"**Atletas Inscritos:** {', '.join(ch['atletas'])}")
                if st.button(f"🗑️ Excluir Chave #{idx_real+1}", key=f"del_chave_{idx_real}"):
                    chaves_lista.pop(idx_real)
                    st.session_state["chaves_luta"] = chaves_lista
                    salvar_tudo()
                    st.toast("🗑️ Chave excluída!")
                    st.rerun()

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
        crono_lista = st.session_state.get("cronogramas_aulas", [])
        for idx, cr in enumerate(reversed(crono_lista)):
            idx_real = len(crono_lista) - 1 - idx
            with st.expander(f"⏱️ {cr['dia']}"):
                st.markdown(f"**Detalhe:** {cr['detalhe']}")
                if st.button(f"🗑️ Excluir Cronograma #{idx_real+1}", key=f"del_crono_{idx_real}"):
                    crono_lista.pop(idx_real)
                    st.session_state["cronogramas_aulas"] = crono_lista
                    salvar_tudo()
                    st.toast("🗑️ Cronograma excluído!")
                    st.rerun()

    # 14. Recuperação & Lesões
    with abas_app[13]:
        st.markdown("### 🔄 Registro de Recuperação, Dores e Lesões")
        with st.form("form_recup"):
            nota_r = st.text_area("Relate sua condição física ou dor muscular:", value="")
            if st.form_submit_button("Gerar Orientações de Recuperação", use_container_width=True):
                if nota_r:
                    resp_gerada = processar_consenso_ia_dual(nota_r, "recuperação", st.session_state.get("perfil_nome", "Atleta"))
                    recup = st.session_state.get("recuperacao_notas", [])
                    recup.append({"nota": resp_gerada, "data": datetime.now().strftime("%d/%m/%Y")})
                    st.session_state["recuperacao_notas"] = recup
                    salvar_tudo()
                    st.toast("✅ Orientações geradas e salvas!")
                    st.rerun()
        st.divider()
        recup_lista = st.session_state.get("recuperacao_notas", [])
        for idx, rc in enumerate(reversed(recup_lista)):
            idx_real = len(recup_lista) - 1 - idx
            with st.expander(f"🔄 Recuperação ({rc['data']})"):
                st.markdown(f"{rc['nota']}")
                if st.button(f"🗑️ Excluir Nota #{idx_real+1}", key=f"del_recup_{idx_real}"):
                    recup_lista.pop(idx_real)
                    st.session_state["recuperacao_notas"] = recup_lista
                    salvar_tudo()
                    st.toast("🗑️ Nota excluída!")
                    st.rerun()

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
