import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, date
import os
import json
import base64

# Configuração inicial da página
st.set_page_config(
    page_title="OssBot Pro - Gestão de BJJ",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constantes globais
EMAIL_ADMIN_MASTER = "henry.cesaraguiar@gmail.com"

CAMPOS = [
    "perfil_nome", "perfil_faixa", "perfil_graus", "perfil_academia", 
    "perfil_peso", "perfil_status", "perfil_foto_b64", "historico_lutas", 
    "cursos_interativos", "dinamic_kids_custom", "flashcards_pressao", 
    "alunos_graduacao", "notas_kimono", "cronogramas_aulas"
]

def esc(texto):
    """Escapa caracteres especiais para segurança em HTML"""
    if not isinstance(texto, str):
        texto = str(texto)
    return (texto.replace("&", "&amp;")
                 .replace("<", "&lt;")
                 .replace(">", "&gt;")
                 .replace('"', "&quot;")
                 .replace("'", "&#39;"))

def mostrar_html(html_code):
    """Renderiza HTML seguro no Streamlit"""
    st.markdown(html_code, unsafe_allow_html=True)

# Gerenciamento de arquivos e banco de dados por usuário
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
            "senha": "adminpassword",
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
    dados_padrao = {
        "perfil_nome": "Henry Cesar",
        "perfil_faixa": "Branca",
        "perfil_graus": 5,
        "perfil_academia": "GRACIE BARRA ALPHAVILLE ESPLANADA",
        "perfil_peso": "Médio",
        "perfil_status": "Atleta Competidor 🏆",
        "perfil_foto_b64": "",
        "historico_lutas": [],
        "cursos_interativos": [],
        "dinamic_kids_custom": [],
        "flashcards_pressao": [],
        "alunos_graduacao": [],
        "notas_kimono": [],
        "cronogramas_aulas": []
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
    st.session_state.usuario_email = email.lower()
    st.session_state.is_admin = (email.lower() == EMAIL_ADMIN_MASTER.lower())
    dados = carregar_dados_usuario(email)
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
    st.rerun()

# Inicialização de estados de autenticação
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario_email" not in st.session_state:
    st.session_state.usuario_email = ""
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# ---------------------------------------------------------------------------
# Estilização CSS Glow UI (Tema Preto & Vermelho)
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #0b0b0b;
        color: #ffffff;
    }
    .placar-box {
        background-color: #161616;
        border: 2px solid #ff1e27;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(255, 30, 39, 0.2);
    }
    .placar-numero {
        font-size: 50px;
        font-weight: bold;
        color: #ff1e27;
    }
    .nutri-box, .camp-box, .curso-box, .kids-box {
        background-color: #141414;
        border-left: 4px solid #ff1e27;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.5);
    }
    .foto-bolinha {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #ff1e27;
        display: block;
        margin: 0 auto 10px auto;
    }
    .bolinha-padrao {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background-color: #1a1a1a;
        border: 2px solid #ff1e27;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 30px;
        margin: 0 auto 10px auto;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Tela de Login e Cadastro
# ---------------------------------------------------------------------------
if not st.session_state.autenticado:
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown("<h1 style='text-align: center; color: #ff1e27;'>🥋 OssBot Pro</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #cccccc;'>Plataforma Profissional de Gestão para Academias de BJJ</p>", unsafe_allow_html=True)
        
        aba_login, aba_cadastro = st.tabs(["🔑 Entrar", "📝 Criar Conta"])
        
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
                        
            if st.button("👑 Acesso Rápido Master (Admin)", use_container_width=True):
                carregar_usuario(EMAIL_ADMIN_MASTER)
                st.session_state.autenticado = True
                st.rerun()

        with aba_cadastro:
            with st.form("form_cadastro"):
                novo_email = st.text_input("Seu E-mail:")
                nova_senha = st.text_input("Crie uma Senha (mín. 6 caracteres):", type="password")
                nome_inicial = st.text_input("Seu Nome Completo:", value="Henry Cesar")
                acad_inicial = st.text_input("Sua Academia:", value="GRACIE BARRA ALPHAVILLE ESPLANADA")
                btn_cadastrar = st.form_submit_button("✨ Criar Conta Agora", use_container_width=True)
                
                if btn_cadastrar:
                    email_limpo = novo_email.strip().lower()
                    if not email_limpo or not nova_senha:
                        st.warning("⚠️ Preencha o e-mail e a senha.")
                    elif len(nova_senha) < 6:
                        st.warning("⚠️ A senha deve ter no mínimo 6 caracteres.")
                    else:
                        banco = carregar_banco_usuarios()
                        if email_limpo in banco:
                            st.error("❌ Este e-mail já está cadastrado.")
                        else:
                            banco[email_limpo] = {
                                "senha": nova_senha,
                                "plano": "ativo",
                                "data_criacao": datetime.now().strftime("%d/%m/%Y - %H:%M")
                            }
                            salvar_banco_usuarios(banco)
                            
                            # Inicializa dados do novo usuário
                            dados_novos = carregar_dados_usuario(email_limpo)
                            dados_novos["perfil_nome"] = nome_inicial
                            dados_novos["perfil_academia"] = acad_inicial
                            salvar_dados_usuario(email_limpo, dados_novos)
                            
                            st.success("✅ Conta criada com sucesso! Vá na aba 'Entrar' para acessar.")
    st.stop()

# Funções de Apoio às Novas Funcionalidades (Alertas, Gamificação e Relatórios)
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

def verificar_e_conceder_badges():
    """Calcula e retorna as badges conquistadas com base na atividade do usuário"""
    badges = []
    total_lutas = len(st.session_state.get("historico_lutas", []))
    if total_lutas >= 1:
        badges.append(("🤼 Guerreiro do Tatame", "Registrou a primeira luta no sistema!"))
    if total_lutas >= 5:
        badges.append(("🔥 Atleta Dedicado", "Já registrou 5 ou mais lutas de treino!"))
        
    total_cursos = len(st.session_state.get("cursos_interativos", []))
    if total_cursos >= 1:
        badges.append(("📚 Estudioso da Arte", "Cadastrou material ou regras de BJJ!"))
        
    if st.session_state.get("perfil_status") == "Atleta Competidor 🏆":
        badges.append(("🏆 Competidor Elite", "Perfil configurado como Atleta de Competição!"))
        
    return badges

def renderizar_secao_gamificacao():
    """Exibe as conquistas e medalhas do usuário na interface"""
    st.markdown("<h3 style='color: #fbbf24;'>🏅 Suas Conquistas & Badges</h3>", unsafe_allow_html=True)
    conquistas = verificar_e_conceder_badges()
    if not conquistas:
        st.info("Complete atividades no app para desbloquear badges!")
    else:
        for titulo_badge, desc_badge in conquistas:
            mostrar_html(f"""
            <div style='background-color: #161616; border: 1px solid #fbbf24; border-radius: 10px; padding: 10px; margin-bottom: 8px;'>
                <h4 style='color: #fbbf24; margin: 0 0 3px 0; font-size: 13px;'>{esc(titulo_badge)}</h4>
                <p style='color: #cccccc; margin: 0; font-size: 11px;'>{esc(desc_badge)}</p>
            </div>
            """)

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

# Funções auxiliares do cronômetro de luta
def somar(lado, campo, valor):
    st.session_state[f"{campo}_{lado}"] += valor

def definir_tempo():
    minutos = st.session_state.select_tempo
    st.session_state.tempo_segundos = minutos * 60

def iniciar_cronometro():
    st.session_state.cronometro_rodando = True

def pausar_cronometro():
    st.session_state.cronometro_rodando = False

def zerar_luta():
    st.session_state.cronometro_rodando = False
    st.session_state.tempo_segundos = st.session_state.get("select_tempo", 5) * 60
    st.session_state.pts_a = 0
    st.session_state.vant_a = 0
    st.session_state.pun_a = 0
    st.session_state.pts_b = 0
    st.session_state.vant_b = 0
    st.session_state.pun_b = 0

# Inicialização de estados da luta
if "pts_a" not in st.session_state: st.session_state.pts_a = 0
if "vant_a" not in st.session_state: st.session_state.vant_a = 0
if "pun_a" not in st.session_state: st.session_state.pun_a = 0
if "pts_b" not in st.session_state: st.session_state.pts_b = 0
if "vant_b" not in st.session_state: st.session_state.vant_b = 0
if "pun_b" not in st.session_state: st.session_state.pun_b = 0
if "tempo_segundos" not in st.session_state: st.session_state.tempo_segundos = 300
if "cronometro_rodando" not in st.session_state: st.session_state.cronometro_rodando = False

# ---------------------------------------------------------------------------
# BARRA LATERAL (SIDEBAR) & PERFIL DO USUÁRIO
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🥋 Carteirinha & Perfil")
    
    # Foto de perfil ou bolinha padrão
    foto_b64 = st.session_state.get("perfil_foto_b64", "")
    if foto_b64:
        st.markdown(f'<img src="data:image/jpeg;base64,{foto_b64}" class="foto-bolinha">', unsafe_allow_html=True)
    else:
        st.markdown('<div class="bolinha-padrao">🥋</div>', unsafe_allow_html=True)
        
    st.markdown(f"<h4 style='text-align: center; color: #ff1e27; margin: 5px 0;'>{esc(st.session_state.get('perfil_nome', 'Atleta'))}</h4>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #cccccc; font-size: 13px; margin: 0;'>Faixa {esc(st.session_state.get('perfil_faixa', 'Branca'))} ({st.session_state.get('perfil_graus', 0)}º Grau)</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #00ffcc; font-size: 12px; margin: 5px 0 15px 0;'>{esc(st.session_state.get('perfil_academia', 'Academia BJJ'))}</p>", unsafe_allow_html=True)
    
    st.divider()
    
    # Exibe as Badges de Gamificação na Barra Lateral
    renderizar_secao_gamificacao()
    
    st.divider()
    
    # PAINEL MASTER INTERATIVO - GESTÃO TOTAL POR ACADEMIA E DASHBOARD
    if st.session_state.get("is_admin", False):
        st.markdown("## 👑 Painel Master")
        with st.expander("🛠️ Gestão de Alunos e Academias"):
            banco = carregar_banco_usuarios()
            st.write(f"📊 **Total de Contas:** {len(banco)}")
            st.divider()
            
            # Agrupa os alunos por academia automaticamente
            academias_dict = {}
            for usr, info in banco.items():
                dados_usr = carregar_dados_usuario(usr)
                acad = dados_usr.get("perfil_academia", "Academia Não Informada").strip()
                if acad not in academias_dict:
                    academias_dict[acad] = []
                academias_dict[acad].append((usr, info, dados_usr))
            
            # Exibe por Academia
            for acad_nome, lista_alunos in academias_dict.items():
                st.markdown(f"🏛️ **Academia:** <span style='color: #ff1e27; font-size: 15px; font-weight: bold;'>{esc(acad_nome)}</span>", unsafe_allow_html=True)
                st.write(f"👥 Alunos cadastrados: {len(lista_alunos)}")
                
                # Lista os alunos desta academia
                for usr, info, dados_usr in lista_alunos:
                    nome_usr = dados_usr.get("perfil_nome", "Sem Nome")
                    faixa_usr = dados_usr.get("perfil_faixa", "Branca")
                    graus_usr = dados_usr.get("perfil_graus", 0)
                    
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;• **{esc(nome_usr)}** ({faixa_usr} - {graus_usr}º Grau)")
                    
                    # Painel de gestão individual ao clicar no aluno (com chaves únicas)
                    with st.expander(f"⚙️ Gerenciar: {nome_usr} ({usr})"):
                        with st.form(key=f"form_gestao_aluno_unico_{usr}"):
                            st.markdown("### ✏️ Editar Credenciais")
                            novo_email_input = st.text_input("Novo E-mail (Login):", value=usr, key=f"nem_unico_{usr}")
                            nova_senha_input = st.text_input("Nova Senha:", value=info.get("senha", ""), type="password", key=f"nsem_unico_{usr}")
                            
                            st.markdown("### 🥋 Graduação e Perfil")
                            novo_nome_input = st.text_input("Nome do Aluno:", value=nome_usr, key=f"nnome_unico_{usr}")
                            
                            faixas_possiveis = ["Branca", "Cinza", "Amarela", "Laranja", "Verde", "Azul", "Roxa", "Castanha", "Preta", "Vermelha e Preta", "Vermelha e Branca", "Vermelha"]
                            idx_faixa = faixas_possiveis.index(faixa_usr) if faixa_usr in faixas_possiveis else 0
                            
                            nova_faixa_input = st.selectbox(
                                "Nova Faixa:",
                                faixas_possiveis,
                                index=idx_faixa,
                                key=f"nfaixa_unico_{usr}"
                            )
                            novos_graus_input = st.slider("Novos Graus:", 0, 11, int(graus_usr), key=f"slider_master_graus_unico_{usr}")
                            
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
                                        dados_antigos = banco_atualizado.pop(usr)
                                        dados_antigos["senha"] = nova_senha_input
                                        banco_atualizado[novo_email_limpo] = dados_antigos
                                        salvar_banco_usuarios(banco_atualizado)
                                        
                                        dados_aluno_atual = carregar_dados_usuario(novo_email_limpo)
                                        dados_aluno_atual["perfil_nome"] = novo_nome_input
                                        dados_aluno_atual["perfil_faixa"] = nova_faixa_input
                                        dados_aluno_atual["perfil_graus"] = novos_graus_input
                                        salvar_dados_usuario(novo_email_limpo, dados_aluno_atual)
                                        
                                        caminho_antigo = obter_caminho_usuario(usr)
                                        caminho_novo = obter_caminho_usuario(novo_email_limpo)
                                        if os.path.exists(caminho_antigo) and caminho_antigo != caminho_novo:
                                            try:
                                                os.replace(caminho_antigo, caminho_novo)
                                            except Exception:
                                                pass
                                                
                                        st.toast("✅ Aluno atualizado com sucesso!", icon="👑")
                                        st.rerun()

                # BOTÃO DE DASHBOARD E RENDIMENTO LOGO ABAIXO DOS ALUNOS DAQUELA ACADEMIA
                with st.expander(f"📊 Ver Dashboard e Rendimento: {acad_nome}"):
                    total_lutas_acad = sum(len(d[2].get("historico_lutas", [])) for d in lista_alunos)
                    st.markdown(f"<p style='color: #00ffcc;'><b>Total de Lutas da Turma:</b> {total_lutas_acad}</p>", unsafe_allow_html=True)
                    
                    faixas_acad = {}
                    for _, _, d_usr in lista_alunos:
                        fx = d_usr.get("perfil_faixa", "Branca")
                        faixas_acad[fx] = faixas_acad.get(fx, 0) + 1
                    
                    if faixas_acad:
                        st.bar_chart(faixas_acad, color="#ff1e27")
                
                st.markdown("---")

    if st.button("💾 Salvar Alterações Gerais", use_container_width=True):
        salvar_tudo()
        st.toast("✅ Dados salvos com sucesso!", icon="💾")
        
    if st.button("🚪 Sair da Conta (Logout)", use_container_width=True):
        fazer_logout()

# ---------------------------------------------------------------------------
# TELA PRINCIPAL & ABAS DO APLICATIVO
# ---------------------------------------------------------------------------
st.markdown("<h1 style='text-align: center; color: #ff1e27;'>🥋 OssBot App Pro</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #cccccc;'>Atleta: <b>{esc(st.session_state.get('perfil_nome', 'Atleta'))}</b> | Faixa {esc(st.session_state.get('perfil_faixa', 'Branca'))} ({st.session_state.get('perfil_graus', 0)}º Grau)</p>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #00ffcc; font-size: 14px;'>{esc(st.session_state.get('perfil_academia', 'Academia BJJ'))} | {esc(st.session_state.get('perfil_status', 'Atleta'))}</p>", unsafe_allow_html=True)

# Abas funcionais do OssBot Pro
abas_app = st.tabs([
    "🤼 Luta", "📜 Histórico", "🥗 Nutrição", "🏆 Camp", "📚 Cursos", 
    "👶 Kids", "⚡ Drills", "🛡️ Pressão", "🥋 Graduação", "🥋 Kimono", 
    "📇 Card", "👥 Alunos", "🔑 Chaves", "⏱️ Cronograma", "🔄 Recuperação"
])

with abas_app[0]: # Aba Luta & Placar
    mostrar_alerta_tatame("sucesso", "Sistema de Placar e Cronômetro de Luta pronto para o treino!")
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
            if st.button("+2 Pts (A)", use_container_width=True): somar("a", "pts_a", 2); st.rerun()
            if st.button("+3 Pts (A)", use_container_width=True): somar("a", "pts_a", 3); st.rerun()
        with c2:
            if st.button("+4 Pts (A)", use_container_width=True): somar("a", "pts_a", 4); st.rerun()
            if st.button("Vantagem (A)", use_container_width=True): somar("a", "vant_a", 1); st.rerun()
        with c3:
            if st.button("Punição (A)", use_container_width=True): somar("a", "pun_a", 1); st.rerun()
            
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
            if st.button("+2 Pts (B)", use_container_width=True): somar("b", "pts_b", 2); st.rerun()
            if st.button("+3 Pts (B)", use_container_width=True): somar("b", "pts_b", 3); st.rerun()
        with cb2:
            if st.button("+4 Pts (B)", use_container_width=True): somar("b", "pts_b", 4); st.rerun()
            if st.button("Vantagem (B)", use_container_width=True): somar("b", "vant_b", 1); st.rerun()
        with cb3:
            if st.button("Punição (B)", use_container_width=True): somar("b", "pun_b", 1); st.rerun()

    st.divider()
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        st.selectbox("Tempo do Rola:", [1, 2, 3, 5, 6, 10], key="select_tempo", on_change=definir_tempo)
    with col_t2:
        minutos_restantes = st.session_state.tempo_segundos // 60
        segundos_restantes = st.session_state.tempo_segundos % 60
        st.markdown(f"<h2 style='text-align: center; color: #ff1e27; margin: 0;'>⏱️ {minutos_restantes:02d}:{segundos_restantes:02d}</h2>", unsafe_allow_html=True)
    with col_t3:
        if not st.session_state.cronometro_rodando:
            if st.button("▶️ Iniciar", use_container_width=True): iniciar_cronometro(); st.rerun()
        else:
            if st.button("⏸️ Pausar", use_container_width=True): pausar_cronometro(); st.rerun()
        if st.button("🔄 Zerar Luta", use_container_width=True): zerar_luta(); st.rerun()

with abas_app[1]: # Histórico
    st.markdown("### 📜 Histórico de Lutas & Treinos")
    with st.form("form_nova_luta"):
        adversario = st.text_input("Nome do Oponente / Companheiro de Treino:")
        resultado = st.selectbox("Resultado:", ["Vitória por Finalização", "Vitória por Pontos", "Empate", "Derrota"])
        detalhes = st.text_area("Detalhes / Posição Final:")
        btn_add_luta = st.form_submit_button("Registrar Luta", use_container_width=True)
        if btn_add_luta:
            if adversario:
                lutas = st.session_state.get("historico_lutas", [])
                lutas.append({"data": datetime.now().strftime("%d/%m/%Y"), "adversario": adversario, "resultado": resultado, "detalhes": detalhes})
                st.session_state["historico_lutas"] = lutas
                salvar_tudo()
                st.toast("✅ Luta registrada com sucesso!", icon="🥋")
                st.rerun()
            else:
                st.warning("⚠️ Insira o nome do oponente.")
                
    st.divider()
    lutas_salvas = st.session_state.get("historico_lutas", [])
    if not lutas_salvas:
        st.info("Nenhuma luta registrada no histórico ainda.")
    else:
        for l in reversed(lutas_salvas):
            st.markdown(f"""
            <div style='background-color: #141414; border-left: 4px solid #00ffcc; border-radius: 8px; padding: 12px; margin-bottom: 10px;'>
                <p style='color: #00ffcc; margin: 0; font-size: 13px;'><b>{esc(l['data'])}</b> - {esc(l['resultado'])}</p>
                <p style='color: #ffffff; margin: 5px 0 0 0; font-size: 14px;'>Oponente: <b>{esc(l['adversario'])}</b></p>
                <p style='color: #cccccc; margin: 3px 0 0 0; font-size: 12px;'>{esc(l['detalhes'])}</p>
            </div>
            """, unsafe_allow_html=True)

with abas_app[2]: # Nutrição
    st.markdown("### 🥗 Nutrição & Corte de Peso para Atletas")
    st.info("Dicas e controle de hidratação e dieta para lutadores de BJJ.")

with abas_app[3]: # Camp
    st.markdown("### 🏆 Camp de Competição")
    st.info("Planejamento de treinos focados em campeonatos e seletivas.")

with abas_app[4]: # Cursos
    st.markdown("### 📚 Cursos & Regras IBJJF")
    st.info("Estudo de posições, fundamentos e regras oficiais da Federação.")

with abas_app[5]: # Kids
    st.markdown("### 👶 Dinâmicas para Turmas Kids")
    st.info("Brincadeiras educativas e lúdicas para introduzir o jiu-jitsu infantil.")

with abas_app[6]: # Drills
    st.markdown("### ⚡ Drills de Repetição & Velocidade")
    st.info("Sequências de movimentação para ganho de reflexo e agilidade.")

with abas_app[7]: # Pressão
    st.markdown("### 🛡️ Flashcards de Controle & Pressão")
    st.info("Técnicas de estabilização de cem-quilos, montada e costas.")

with abas_app[8]: # Graduação
    st.markdown("### 🥋 Controle de Graduação de Alunos")
    st.info("Acompanhamento de evolução de graus e faixas.")

with abas_app[9]: # Kimono
    st.markdown("### 🥋 Notas de Kimonos & Equipamentos")
    st.info("Controle de conservação e medidas de materiais de treino.")

with abas_app[10]: # Card
    st.markdown("### 📇 Carteirinha Digital do Atleta")
    st.markdown(f"""
    <div class='placar-box' style='text-align: left; max-width: 400px; margin: 0 auto;'>
        <h3 style='color: #ff1e27; margin-top: 0;'>🥋 CARTEIRINHA OFICIAL</h3>
        <p><b>Nome:</b> {esc(st.session_state.get('perfil_nome', ''))}</p>
        <p><b>Faixa:</b> {esc(st.session_state.get('perfil_faixa', ''))} ({st.session_state.get('perfil_graus', 0)}º Grau)</p>
        <p><b>Academia:</b> {esc(st.session_state.get('perfil_academia', ''))}</p>
        <p><b>Status:</b> {esc(st.session_state.get('perfil_status', ''))}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    # Botão para baixar o relatório em PDF/Texto criado na Parte 3
    st.markdown("### 📄 Relatório Executivo & Prontuário")
    st.download_button(
        "📥 Baixar Relatório Oficial (.txt / Relatório)",
        data=gerar_relatorio_pdf_atleta(),
        file_name=f"relatorio_ossbot_{st.session_state.get('perfil_nome', 'atleta').lower().replace(' ', '_')}.txt",
        mime="text/plain",
        use_container_width=True,
        help="Baixe o documento oficial resumido com todas as suas informações do tatame."
    )

with abas_app[11]: # Alunos
    st.markdown("### 👥 Gestão Geral de Alunos")
    st.write("Visualize e atualize os atletas cadastrados na plataforma.")

with abas_app[12]: # Chaves
    st.markdown("### 🔑 Gerador de Chaves de Luta (Chaveamento)")
    st.info("Monte chaves de torneios e lutas casadas rapidamente.")

with abas_app[13]: # Cronograma
    st.markdown("### ⏱️ Cronograma Semanal de Treinos")
    st.info("Organize horários de treinos técnicos, físicos e específicos.")

with abas_app[14]: # Recuperação
    st.markdown("### 🔄 Recuperação, Sono & Lesões")
    st.info("Dicas de prevenção de lesões e descanso para atletas de alto rendimento.")
