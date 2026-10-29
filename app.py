import streamlit as st
from datetime import datetime, date
import os
import json
import io
import re
import time
import base64
import hmac
import hashlib
import secrets as pysecrets
import traceback

import pandas as pd
import requests
from gtts import gTTS
from PIL import Image

st.set_page_config(
    page_title="OssBot Pro - Gestão Profissional de BJJ",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CONFIGURAÇÕES E SEGREDOS
# ============================================================
def get_secret(nome, padrao=""):
    try:
        valor = st.secrets.get(nome)
    except Exception:
        valor = None
    return str(valor) if valor else os.environ.get(nome, padrao)


ADMIN_EMAIL = get_secret("ADMIN_EMAIL").strip().lower()
ADMIN_SENHA = get_secret("ADMIN_PASSWORD")
MODELO_IA = get_secret("ANTHROPIC_MODEL", "claude-sonnet-4-6")

CAMPOS = [
    "perfil_nome", "perfil_faixa", "perfil_graus", "perfil_academia",
    "perfil_peso", "perfil_status", "perfil_foto_b64", "historico_lutas",
    "cursos_interativos", "dinamic_kids_custom", "flashcards_pressao",
    "alunos_graduacao", "notas_kimono", "cronogramas_aulas", "dicas_nutricao",
    "camp_competicao", "drills_treino", "chaves_luta", "recuperacao_notas",
    "historico_presencas", "tipo_usuario",
]
CAMPOS_LISTA = [c for c in CAMPOS if c not in (
    "perfil_nome", "perfil_faixa", "perfil_graus", "perfil_academia",
    "perfil_peso", "perfil_status", "perfil_foto_b64", "tipo_usuario")]

TIPO_PROF = "Professor / Instrutor"
TIPO_MASTER = "Master (Fundador)"


def esc(texto):
    if not isinstance(texto, str):
        texto = str(texto)
    return (texto.replace("&", "&amp;").replace("<", "&lt;")
                 .replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;"))


def mostrar_html(html_code):
    st.markdown(html_code, unsafe_allow_html=True)


def is_master_email(email):
    return bool(ADMIN_EMAIL) and email.strip().lower() == ADMIN_EMAIL


# ============================================================
# SENHAS (HASH)
# ============================================================
def hash_senha(senha):
    salt = pysecrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", senha.encode(), bytes.fromhex(salt), 200_000).hex()
    return f"pbkdf2${salt}${dk}"


def conferir_senha(senha, guardado):
    if not guardado:
        return False
    if guardado.startswith("pbkdf2$"):
        try:
            _, salt, dk = guardado.split("$")
            novo = hashlib.pbkdf2_hmac("sha256", senha.encode(), bytes.fromhex(salt), 200_000).hex()
            return hmac.compare_digest(novo, dk)
        except Exception:
            return False
    # Senha antiga em texto puro (será convertida no login)
    return hmac.compare_digest(senha.encode(), guardado.encode())


# ============================================================
# BANCO DE DADOS (JSON)
# ============================================================
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
    return {}


def salvar_banco_usuarios(banco):
    with open(obter_caminho_usuarios(), "w", encoding="utf-8") as f:
        json.dump(banco, f, ensure_ascii=False, indent=2)


def dados_padrao_usuario(email):
    master = is_master_email(email)
    padrao = {
        "perfil_nome": "Henry Cesar" if master else "Atleta Visitante",
        "perfil_faixa": "Branca",
        "perfil_graus": 5 if master else 0,
        "perfil_academia": "GRACIE BARRA ALPHAVILLE ESPLANADA" if master else "Insira a sua Academia",
        "perfil_peso": "Médio",
        "perfil_status": "Atleta Competidor 🏆" if master else "Visitante / Novo Atleta",
        "perfil_foto_b64": "",
        "tipo_usuario": TIPO_MASTER if master else "Atleta",
    }
    for c in CAMPOS_LISTA:
        padrao[c] = []
    return padrao


def carregar_dados_usuario(email):
    padrao = dados_padrao_usuario(email)
    caminho = obter_caminho_usuario(email)
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                salvos = json.load(f)
            for k, v in padrao.items():
                if k not in salvos or (k in CAMPOS_LISTA and not isinstance(salvos[k], list)):
                    salvos[k] = v
            return salvos
        except Exception:
            return padrao
    return padrao


def salvar_dados_usuario(email, dados):
    with open(obter_caminho_usuario(email), "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def carregar_usuario(email):
    email_l = email.strip().lower()
    st.session_state.usuario_email = email_l
    info = carregar_banco_usuarios().get(email_l, {})
    st.session_state.is_admin = is_master_email(email_l) or info.get("is_admin", False)
    st.session_state.professor_aprovado = info.get("aprovado", False)
    st.session_state.tipo_usuario = info.get("tipo_usuario", "Atleta")
    dados = carregar_dados_usuario(email_l)
    for c in CAMPOS:
        st.session_state[c] = dados.get(c)


def salvar_tudo():
    email = st.session_state.get("usuario_email")
    if email:
        salvar_dados_usuario(email, {c: st.session_state.get(c) for c in CAMPOS})


def fazer_logout():
    for c in CAMPOS:
        st.session_state.pop(c, None)
    st.session_state.autenticado = False
    st.session_state.usuario_email = ""
    st.session_state.is_admin = False
    st.session_state.professor_aprovado = False
    st.session_state.tipo_usuario = "Atleta"
    st.rerun()


# ============================================================
# ESTADOS INICIAIS
# ============================================================
_padroes = {
    "autenticado": False, "usuario_email": "", "is_admin": False,
    "professor_aprovado": False, "tipo_usuario": "Atleta",
    "pts_a": 0, "vant_a": 0, "pun_a": 0, "pts_b": 0, "vant_b": 0, "pun_b": 0,
    "tempo_segundos": 300, "tempo_inicial": 300, "cronometro_rodando": False, "fim_ts": 0.0,
}
for _k, _v in _padroes.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ============================================================
# CSS (com contraste corrigido)
# ============================================================
st.markdown("""
<style>
    .stApp { background-color: #0b0b0b; color: #ffffff; }
    label, .stMarkdown, p, span { color: #f2f2f2; }

    /* Campos de texto, áreas e selects: sempre legíveis */
    .stTextInput input, .stTextArea textarea, .stNumberInput input, .stDateInput input {
        background-color: #1c1c1c !important; color: #ffffff !important;
        border: 1px solid #555555 !important; border-radius: 8px !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus { border-color: #ff1e27 !important; }
    .stTextInput input::placeholder, .stTextArea textarea::placeholder { color: #9a9a9a !important; opacity: 1; }
    [data-baseweb="select"] > div { background-color: #1c1c1c !important; color: #ffffff !important; border: 1px solid #555555 !important; }
    [data-baseweb="select"] span, [data-baseweb="select"] input { color: #ffffff !important; }
    [data-testid="stFileUploaderDropzone"] { background-color: #1c1c1c !important; border: 1px dashed #777777 !important; }
    [data-testid="stFileUploaderDropzone"] * { color: #ffffff !important; }

    /* Botões */
    .stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
        background-color: #ff1e27 !important; color: #ffffff !important;
        border: 1px solid #ff1e27 !important; border-radius: 8px !important; font-weight: 600 !important;
    }
    .stButton > button:hover, .stFormSubmitButton > button:hover, .stDownloadButton > button:hover {
        background-color: #c4121a !important; border-color: #c4121a !important; color: #ffffff !important;
    }
    .stButton > button p, .stFormSubmitButton > button p, .stDownloadButton > button p { color: #ffffff !important; }

    /* Componentes do app */
    .placar-box { background-color: #161616; border: 2px solid #ff1e27; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 4px 20px rgba(255, 30, 39, 0.2); }
    .placar-numero { font-size: 50px; font-weight: bold; color: #ff1e27; }
    .card-item { background-color: #141414; border-left: 4px solid #ff1e27; border-radius: 8px; padding: 15px; margin-bottom: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.5); }
    .foto-bolinha { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 2px solid #ff1e27; display: block; margin: 0 auto 10px auto; }
    .bolinha-padrao { width: 80px; height: 80px; border-radius: 50%; background-color: #1a1a1a; border: 2px solid #ff1e27; display: flex; align-items: center; justify-content: center; font-size: 30px; margin: 0 auto 10px auto; }
    .ia-erro-card { background-color: #1a0808; border: 2px solid #ff1e27; border-radius: 10px; padding: 20px; margin: 20px 0; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# IA (Anthropic) + MODO RESERVA
# ============================================================
SISTEMA_BASE = (
    "Você é o OssBot, assistente de Jiu-Jitsu Brasileiro (BJJ) para atletas e professores no Brasil. "
    "Responda em português do Brasil, direto ao ponto, sem introdução longa e sem enrolação. "
    "Seja fiel à realidade: não invente regras, números, estudos ou técnicas. Se não tiver certeza, diga. "
    "Use Markdown simples (títulos curtos, listas, negrito). Priorize sempre a segurança dos praticantes. "
    "Entregue VARIEDADE: opções realmente diferentes entre si, nunca a mesma ideia reescrita."
)

INSTRUCOES = {
    "kids": (
        "Crie dinâmicas lúdicas para turma kids (4 a 12 anos) sobre os temas pedidos. "
        "Para CADA tema, entregue 3 dinâmicas diferentes entre si (por exemplo: jogo de equipe, jogo em duplas, "
        "circuito ou desafio). Para cada dinâmica use exatamente este formato:\n"
        "### Nome da dinâmica\n**Idade:** ...\n**Tempo:** ...\n**Material:** ...\n"
        "**Como funciona:** (2 a 4 passos curtos)\n**Objetivo técnico:** (ligado ao tema)\n**Segurança:** ...\n"
        "Termine com uma 'Dica do professor' de uma linha."
    ),
    "drills": (
        "Monte drills para o tema pedido. Entregue 4 opções diferentes (ex.: velocidade, resistência progressiva, "
        "reação, fluxo/transição). Para cada uma: **Nome**, **Tempo/séries**, **Como fazer** (passos curtos), "
        "**Erro comum a evitar**. Sem texto de enchimento."
    ),
    "nutri": (
        "Responda sobre alimentação para praticante de Jiu-Jitsu. Seja prático: o que comer, quando e por quê, "
        "com 3 opções variadas e acessíveis no Brasil. Não prescreva dieta clínica nem calorias exatas; "
        "diga que ajuste individual deve ser feito com nutricionista. Mencione hidratação quando fizer sentido."
    ),
    "curso": (
        "Explique a técnica, posição ou regra pedida de forma completa e curta: **O que é**, **Passo a passo**, "
        "**Erros comuns**, **Variações/opções**. Se for regra, cite apenas o que você tem certeza (referência IBJJF) "
        "e avise que as regras mudam e devem ser conferidas no regulamento oficial atual."
    ),
    "pressao": (
        "Crie um flashcard tático sobre o estilo de jogo descrito: **Pergunta** (situação de pressão), "
        "**Resposta** (reação ideal em 3 passos), **Plano B**, **Gatilho para treinar**. Seja específico e conciso."
    ),
    "kimono": (
        "Dê cuidados com kimono (lavagem, secagem, odor, manchas, encolhimento) para o problema descrito. "
        "Traga 3 soluções diferentes em ordem de praticidade, com o que NÃO fazer. Seja objetivo e correto."
    ),
    "recup": (
        "Oriente sobre recuperação para praticante de Jiu-Jitsu com o relato descrito: cuidados imediatos gerais, "
        "o que observar, 3 opções de recuperação ativa/descanso. Não faça diagnóstico. Deixe claro quando procurar "
        "médico ou fisioterapeuta (dor forte, inchaço, perda de movimento, formigamento, trauma na cabeça ou pescoço)."
    ),
}


def chamar_ia(instrucao, tema, max_tokens=1800):
    chave = get_secret("ANTHROPIC_API_KEY")
    if not chave:
        return None, "Chave ANTHROPIC_API_KEY não configurada."
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": chave, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={
                "model": MODELO_IA,
                "max_tokens": max_tokens,
                "system": SISTEMA_BASE + "\n\n" + instrucao,
                "messages": [{"role": "user", "content": f"Tema/pedido do usuário: {tema}"}],
            },
            timeout=60,
        )
        if r.status_code != 200:
            return None, f"A IA retornou erro {r.status_code}. Verifique sua chave e o modelo."
        blocos = r.json().get("content", [])
        texto = "".join(b.get("text", "") for b in blocos if b.get("type") == "text").strip()
        return (texto, None) if texto else (None, "A IA não devolveu texto.")
    except Exception as e:
        return None, f"Falha ao conectar com a IA: {e}"


def resposta_reserva(chave, tema):
    """Modo simples, usado só quando a IA não está disponível."""
    temas = [t.strip() for t in re.split(r"[,\n;]|\se\s", tema) if t.strip()] or [tema]
    if chave == "kids":
        modelos = [
            ("Jogo do Espelho", "Em duplas, um lidera o movimento de **{t}** e o outro copia devagar; trocam a cada 30s.", "Coordenação e noção do movimento."),
            ("Desafio do Tatame", "Estações pelo tatame; em cada uma a criança faz 5 repetições leves de **{t}** com um colega.", "Repetição com técnica e controle."),
        ]
        partes = []
        for t in temas:
            for nome, como, obj in modelos:
                partes.append(f"### {nome} ({t})\n**Idade:** 5 a 12 anos\n**Tempo:** 3 a 5 min\n"
                              f"**Como funciona:** {como.format(t=t)}\n**Objetivo técnico:** {obj}\n"
                              f"**Segurança:** peso parecido nas duplas, sem força, professor sempre supervisionando.")
        return "\n\n".join(partes)
    return f"### {tema}\nSem a IA conectada não consigo montar uma resposta detalhada para isso agora. Configure a chave da IA para respostas completas."


def limpar_para_voz(texto):
    t = re.sub(r"[*#`_>|~-]+", " ", texto)
    t = re.sub(r"[^\w\s.,;:!?()%/]", "", t)
    return re.sub(r"\s+", " ", t).strip()[:3000]


def gerar_audio_tts(texto):
    try:
        buf = io.BytesIO()
        gTTS(text=limpar_para_voz(texto), lang="pt", slow=False).write_to_fp(buf)
        return buf.getvalue()
    except Exception:
        return None


# ============================================================
# COMPONENTE GENÉRICO DAS ABAS DE IA
# ============================================================
def _limpar_aba(key):
    st.session_state[f"tema_{key}"] = ""
    st.session_state[f"resp_{key}"] = ""
    st.session_state[f"tema_ok_{key}"] = ""
    st.session_state.pop(f"audio_{key}", None)


def aba_ia(key, ctx, rotulo, placeholder, campo, montar, titulo_fn, corpo_fn, icone):
    tema = st.text_area(rotulo, placeholder=placeholder, key=f"tema_{key}", height=90)
    c1, c2 = st.columns([4, 1])
    gerar = c1.button("✨ Gerar com o OssBot IA", key=f"gerar_{key}", use_container_width=True)
    c2.button("🧹 Limpar", key=f"limpar_{key}", use_container_width=True, on_click=_limpar_aba, args=(key,))

    if gerar:
        if not tema.strip():
            st.warning("⚠️ Escreva o tema ou pedido primeiro.")
        else:
            with st.spinner("🤖 OssBot IA preparando a resposta..."):
                texto, erro = chamar_ia(INSTRUCOES[ctx], tema.strip())
            if not texto:
                st.warning(f"⚠️ {erro} Usando o modo reserva (bem mais simples).")
                texto = resposta_reserva(ctx, tema.strip())
            st.session_state[f"resp_{key}"] = texto
            st.session_state[f"tema_ok_{key}"] = tema.strip()
            st.session_state.pop(f"audio_{key}", None)

    resp = st.session_state.get(f"resp_{key}", "")
    if resp:
        with st.container(border=True):
            st.markdown(resp)
        b1, b2 = st.columns(2)
        if b1.button("💾 Salvar este conteúdo", key=f"salvar_{key}", use_container_width=True):
            lista = st.session_state.get(campo)
            if not isinstance(lista, list):
                lista = []
            lista.append(montar(st.session_state.get(f"tema_ok_{key}", tema), resp))
            st.session_state[campo] = lista
            salvar_tudo()
            st.toast("✅ Salvo com sucesso!", icon="💾")
        if b2.button("🔊 Ouvir resposta", key=f"voz_{key}", use_container_width=True):
            with st.spinner("Gerando áudio..."):
                st.session_state[f"audio_{key}"] = gerar_audio_tts(resp)
        if st.session_state.get(f"audio_{key}"):
            st.audio(st.session_state[f"audio_{key}"], format="audio/mp3")

    st.divider()
    salvos = st.session_state.get(campo) or []
    if salvos:
        st.markdown("#### 📁 Salvos")
    for i in reversed(range(len(salvos))):
        item = salvos[i]
        with st.expander(f"{icone} {titulo_fn(item)}"):
            st.markdown(corpo_fn(item))
            if st.button("🗑️ Excluir", key=f"del_{key}_{i}"):
                salvos.pop(i)
                st.session_state[campo] = salvos
                salvar_tudo()
                st.rerun()


# ============================================================
# PLACAR E CRONÔMETRO
# ============================================================
def somar_placar(var, valor):
    st.session_state[var] = max(0, st.session_state[var] + valor)


def zerar_luta():
    st.session_state.cronometro_rodando = False
    st.session_state.tempo_segundos = st.session_state.tempo_inicial
    for v in ("pts_a", "vant_a", "pun_a", "pts_b", "vant_b", "pun_b"):
        st.session_state[v] = 0


def mudar_tempo():
    if not st.session_state.cronometro_rodando:
        st.session_state.tempo_inicial = st.session_state.tempo_sel * 60
        st.session_state.tempo_segundos = st.session_state.tempo_inicial


def iniciar_cronometro():
    if st.session_state.tempo_segundos <= 0:
        st.session_state.tempo_segundos = st.session_state.tempo_inicial
    st.session_state.fim_ts = time.time() + st.session_state.tempo_segundos
    st.session_state.cronometro_rodando = True


def pausar_cronometro():
    restante = max(0, int(round(st.session_state.fim_ts - time.time())))
    st.session_state.tempo_segundos = restante
    st.session_state.cronometro_rodando = False


def _render_cronometro():
    if st.session_state.cronometro_rodando:
        restante = max(0, int(round(st.session_state.fim_ts - time.time())))
        st.session_state.tempo_segundos = restante
        if restante == 0:
            st.session_state.cronometro_rodando = False
            st.rerun()
    ts = st.session_state.tempo_segundos
    st.markdown(f"<h2 style='text-align: center; color: #ff1e27; margin: 0;'>⏱️ {ts // 60:02d}:{ts % 60:02d}</h2>",
                unsafe_allow_html=True)


def painel_placar(lado, titulo, cor, rotulo):
    mostrar_html(f"""
    <div class='placar-box'>
        <p style='color: #cccccc; margin: 0;'>{rotulo}</p>
        <h3 style='color: {cor}; margin: 5px 0;'>{titulo}</h3>
        <div class='placar-numero'>{st.session_state[f'pts_{lado}']}</div>
        <p style='color: #ffffff; margin: 5px 0;'>Vantagens: {st.session_state[f'vant_{lado}']} | Punições: {st.session_state[f'pun_{lado}']}</p>
    </div>
    """)
    L = lado.upper()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.button(f"+2 Pts ({L})", key=f"p2{lado}", use_container_width=True, on_click=somar_placar, args=(f"pts_{lado}", 2))
        st.button(f"+3 Pts ({L})", key=f"p3{lado}", use_container_width=True, on_click=somar_placar, args=(f"pts_{lado}", 3))
    with c2:
        st.button(f"+4 Pts ({L})", key=f"p4{lado}", use_container_width=True, on_click=somar_placar, args=(f"pts_{lado}", 4))
        st.button(f"Vantagem ({L})", key=f"v1{lado}", use_container_width=True, on_click=somar_placar, args=(f"vant_{lado}", 1))
    with c3:
        st.button(f"Punição ({L})", key=f"pu{lado}", use_container_width=True, on_click=somar_placar, args=(f"pun_{lado}", 1))


# ============================================================
# GAMIFICAÇÃO E RELATÓRIO
# ============================================================
def verificar_e_conceder_badges():
    badges = []
    total = len(st.session_state.get("historico_lutas") or [])
    if total >= 1: badges.append(("🤼 Guerreiro do Tatame", "Registrou a primeira luta!"))
    if total >= 5: badges.append(("🔥 Atleta Dedicado", "5+ lutas registradas!"))
    if len(st.session_state.get("cursos_interativos") or []) >= 1: badges.append(("📚 Estudioso da Arte", "Registro de estudo de BJJ!"))
    if st.session_state.get("perfil_status") == "Atleta Competidor 🏆": badges.append(("🏆 Competidor Elite", "Perfil de Competição ativo!"))
    return badges


def renderizar_secao_gamificacao():
    st.markdown("<h3 style='color: #fbbf24;'>🏅 Conquistas & Badges</h3>", unsafe_allow_html=True)
    conquistas = verificar_e_conceder_badges()
    if not conquistas:
        st.info("Complete atividades no app para desbloquear badges!")
    for titulo, desc in conquistas:
        mostrar_html(f"""
        <div style='background-color: #161616; border: 1px solid #fbbf24; border-radius: 8px; padding: 8px; margin-bottom: 6px;'>
            <h4 style='color: #fbbf24; margin: 0 0 2px 0; font-size: 12px;'>{esc(titulo)}</h4>
            <p style='color: #cccccc; margin: 0; font-size: 10px;'>{esc(desc)}</p>
        </div>
        """)


def gerar_relatorio_atleta():
    g = st.session_state.get
    return f"""
=====================================================
          OSSBOT PRO - RELATÓRIO OFICIAL DE ATLETA
=====================================================
Data: {datetime.now().strftime('%d/%m/%Y - %H:%M')}

[DADOS DO ATLETA]
• Nome: {g('perfil_nome', 'Atleta')}
• E-mail: {g('usuario_email', '')}
• Academia: {g('perfil_academia', '')}
• Graduação: Faixa {g('perfil_faixa', 'Branca')} ({g('perfil_graus', 0)}º Grau)
• Status: {g('perfil_status', 'Atleta')}

[RESUMO DE ATIVIDADES]
• Total de Lutas: {len(g('historico_lutas') or [])}
• Cursos/Técnicas: {len(g('cursos_interativos') or [])}
• Dinâmicas Kids: {len(g('dinamic_kids_custom') or [])}
• Flashcards de Pressão: {len(g('flashcards_pressao') or [])}
• Presenças Registradas: {len(g('historico_presencas') or [])}
=====================================================
"""


def foto_para_b64(arquivo):
    img = Image.open(arquivo).convert("RGB")
    img.thumbnail((200, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()


# ============================================================
# APP PRINCIPAL
# ============================================================
try:
    # ---------------- LOGIN ----------------
    if not st.session_state.autenticado:
        _, col_l2, _ = st.columns([1, 2, 1])
        with col_l2:
            st.markdown("<h1 style='text-align: center; color: #ff1e27;'>🥋 OssBot Pro</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #cccccc;'>Plataforma Profissional de Gestão para Academias de BJJ</p>", unsafe_allow_html=True)

            aba_login, aba_cadastro, aba_recuperar = st.tabs(["🔑 Entrar", "📝 Criar Conta", "🔄 Esqueci a Senha"])

            with aba_login:
                with st.form("form_login"):
                    email_input = st.text_input("E-mail de Acesso:")
                    senha_input = st.text_input("Senha:", type="password")
                    if st.form_submit_button("🚀 Entrar no Sistema", use_container_width=True):
                        email_limpo = email_input.strip().lower()
                        banco = carregar_banco_usuarios()
                        info = banco.get(email_limpo)
                        if info and conferir_senha(senha_input, info.get("senha", "")):
                            if not info["senha"].startswith("pbkdf2$"):
                                info["senha"] = hash_senha(senha_input)
                                salvar_banco_usuarios(banco)
                            carregar_usuario(email_limpo)
                            st.session_state.autenticado = True
                            st.rerun()
                        else:
                            st.error("❌ E-mail ou senha incorretos.")

                with st.expander("👑 Acesso Restrito Master (Admin)"):
                    if not ADMIN_SENHA or not ADMIN_EMAIL:
                        st.info("Configure ADMIN_EMAIL e ADMIN_PASSWORD nos secrets para ativar o acesso master.")
                    else:
                        with st.form("form_admin_login"):
                            senha_master_input = st.text_input("Senha Master:", type="password")
                            if st.form_submit_button("🔒 Entrar como Master", use_container_width=True):
                                if hmac.compare_digest(senha_master_input.encode(), ADMIN_SENHA.encode()):
                                    carregar_usuario(ADMIN_EMAIL)
                                    st.session_state.autenticado = True
                                    st.rerun()
                                else:
                                    st.error("❌ Senha master incorreta.")

                        st.divider()
                        st.markdown("<p style='color: #ff1e27; font-weight: bold;'>➕ Adicionar Novo Administrador</p>", unsafe_allow_html=True)
                        with st.form("form_criar_novo_admin_master"):
                            senha_fundador = st.text_input("Senha Mestre do Fundador:", type="password", key="s_fund_novo")
                            n_email = st.text_input("E-mail do Novo Admin:", key="n_adm_email")
                            n_senha = st.text_input("Senha do Novo Admin (mín. 6):", type="password", key="n_adm_senha")
                            n_nome = st.text_input("Nome do Novo Admin:", key="n_adm_nome")
                            n_tipo = st.selectbox("Nível de Acesso:", [TIPO_PROF, TIPO_MASTER], key="n_adm_tipo")
                            if st.form_submit_button("✨ Criar Novo Acesso Master", use_container_width=True):
                                if not hmac.compare_digest(senha_fundador.encode(), ADMIN_SENHA.encode()):
                                    st.error("❌ Senha mestre do fundador incorreta!")
                                else:
                                    em = n_email.strip().lower()
                                    if not em or not n_senha:
                                        st.warning("⚠️ Preencha e-mail e senha.")
                                    elif len(n_senha) < 6:
                                        st.warning("⚠️ A senha deve ter no mínimo 6 caracteres.")
                                    else:
                                        banco = carregar_banco_usuarios()
                                        banco[em] = {
                                            "senha": hash_senha(n_senha), "tipo_usuario": n_tipo,
                                            "is_admin": True, "aprovado": True, "plano": "ativo",
                                            "data_criacao": datetime.now().strftime("%d/%m/%Y - %H:%M"),
                                        }
                                        salvar_banco_usuarios(banco)
                                        du = carregar_dados_usuario(em)
                                        if n_nome.strip():
                                            du["perfil_nome"] = n_nome.strip()
                                        du["tipo_usuario"] = n_tipo
                                        salvar_dados_usuario(em, du)
                                        st.success(f"✅ Novo admin '{em}' criado com sucesso!")

            with aba_cadastro:
                with st.form("form_cadastro"):
                    novo_email = st.text_input("Seu E-mail:")
                    nova_senha = st.text_input("Crie uma Senha (mín. 6 caracteres):", type="password")
                    nome_inicial = st.text_input("Seu Nome Completo:", value="Atleta Visitante")
                    acad_inicial = st.text_input("Sua Academia:", value="Insira a sua Academia")
                    tipo_registo = st.selectbox("Perfil de Usuário:", ["Atleta", TIPO_PROF])
                    if tipo_registo == TIPO_PROF:
                        st.caption("O acesso ao painel de professor precisa ser aprovado pelo administrador.")
                    if st.form_submit_button("✨ Criar Conta Agora", use_container_width=True):
                        em = novo_email.strip().lower()
                        if not em or not nova_senha:
                            st.warning("⚠️ Preencha e-mail e senha.")
                        elif len(nova_senha) < 6:
                            st.warning("⚠️ A senha deve ter no mínimo 6 caracteres.")
                        else:
                            banco = carregar_banco_usuarios()
                            if em in banco or is_master_email(em):
                                st.error("❌ E-mail já cadastrado.")
                            else:
                                banco[em] = {
                                    "senha": hash_senha(nova_senha), "tipo_usuario": tipo_registo,
                                    "is_admin": False, "aprovado": False, "plano": "ativo",
                                    "data_criacao": datetime.now().strftime("%d/%m/%Y - %H:%M"),
                                }
                                salvar_banco_usuarios(banco)
                                dn = carregar_dados_usuario(em)
                                dn["perfil_nome"] = nome_inicial or "Atleta Visitante"
                                dn["perfil_academia"] = acad_inicial or "Insira a sua Academia"
                                dn["tipo_usuario"] = tipo_registo
                                salvar_dados_usuario(em, dn)
                                st.success("✅ Conta criada com sucesso! Acesse a aba 'Entrar'.")

            with aba_recuperar:
                st.info("Por segurança, a senha não pode ser trocada só com o e-mail. "
                        "Peça ao seu professor ou ao administrador da academia para redefinir a sua senha pelo painel de gestão.")
        st.stop()

    # ---------------- BARRA LATERAL ----------------
    painel_ok = st.session_state.is_admin or (
        st.session_state.tipo_usuario == TIPO_PROF and st.session_state.professor_aprovado)
    sou_master = is_master_email(st.session_state.usuario_email)

    with st.sidebar:
        st.markdown("### 🥋 Carteirinha & Perfil")
        foto_b64 = st.session_state.get("perfil_foto_b64", "")
        if foto_b64:
            st.markdown(f'<img src="data:image/jpeg;base64,{foto_b64}" class="foto-bolinha">', unsafe_allow_html=True)
        else:
            st.markdown('<div class="bolinha-padrao">🥋</div>', unsafe_allow_html=True)

        st.markdown(f"<h4 style='text-align: center; color: #ff1e27; margin: 5px 0;'>{esc(st.session_state.get('perfil_nome', 'Atleta Visitante'))}</h4>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #cccccc; font-size: 13px; margin: 0;'>Faixa {esc(st.session_state.get('perfil_faixa', 'Branca'))} ({st.session_state.get('perfil_graus', 0)}º Grau)</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #00ffcc; font-size: 12px; margin: 5px 0;'>{esc(st.session_state.get('perfil_academia', ''))}</p>", unsafe_allow_html=True)

        with st.expander("✏️ Editar Perfil"):
            with st.form("form_edicao_perfil_sidebar"):
                novo_nome = st.text_input("Nome / Atleta:", value=st.session_state.get("perfil_nome", ""))
                faixas_p = ["Branca", "Cinza", "Amarela", "Laranja", "Verde", "Azul", "Roxa", "Castanha", "Preta", "Vermelha"]
                fx_atual = st.session_state.get("perfil_faixa", "Branca")
                nova_faixa = st.selectbox("Faixa:", faixas_p, index=faixas_p.index(fx_atual) if fx_atual in faixas_p else 0)
                novos_graus = st.slider("Graus:", 0, 11, int(st.session_state.get("perfil_graus", 0) or 0))
                nova_academia = st.text_input("Academia:", value=st.session_state.get("perfil_academia", ""))
                nova_foto = st.file_uploader("Foto de perfil:", type=["jpg", "jpeg", "png"])
                if st.form_submit_button("💾 Salvar Perfil", use_container_width=True):
                    st.session_state["perfil_nome"] = novo_nome or "Atleta Visitante"
                    st.session_state["perfil_faixa"] = nova_faixa
                    st.session_state["perfil_graus"] = novos_graus
                    st.session_state["perfil_academia"] = nova_academia or "Insira a sua Academia"
                    if nova_foto is not None:
                        try:
                            st.session_state["perfil_foto_b64"] = foto_para_b64(nova_foto)
                        except Exception:
                            st.warning("Não consegui ler essa imagem.")
                    salvar_tudo()
                    st.toast("✅ Perfil atualizado!", icon="🥋")
                    st.rerun()

        st.divider()
        renderizar_secao_gamificacao()
        st.divider()

        if painel_ok:
            st.markdown("## 👑 Painel de Gestão & Coach")

            with st.expander("📱 Check-in de Presença (QR Code)"):
                data_hoje_str = datetime.now().strftime("%d/%m/%Y")
                data_api_str = datetime.now().strftime("%Y-%m-%d")
                qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=OssBot-Checkin-{data_api_str}"
                mostrar_html(f"""
                <div style='text-align: center; background: #161616; padding: 10px; border-radius: 8px; border: 1px solid #ff1e27; margin-bottom: 8px;'>
                    <img src='{qr_url}' style='width: 130px; height: 130px; border-radius: 4px;'/>
                    <p style='color: #00ffcc; font-size: 11px; margin-top: 6px;'>📅 {data_hoje_str}</p>
                </div>
                """)
                if st.button("📍 Fazer Check-in Hoje", use_container_width=True):
                    presencas = st.session_state.get("historico_presencas") or []
                    if data_hoje_str not in presencas:
                        presencas.append(data_hoje_str)
                        st.session_state["historico_presencas"] = presencas
                        salvar_tudo()
                        st.success("✅ Check-in registrado!")
                    else:
                        st.info("ℹ️ Já fez check-in hoje!")

            with st.expander("🛠️ Gestão de Alunos e Turmas"):
                banco = carregar_banco_usuarios()
                if st.session_state.tipo_usuario == TIPO_PROF and not sou_master:
                    filtrar_academia = st.session_state.get("perfil_academia", "").strip().lower()
                else:
                    filtrar_academia = None
                st.write(f"📊 **Total de Contas:** {len(banco)}")
                st.divider()

                academias = {}
                for usr, info in banco.items():
                    d_usr = carregar_dados_usuario(usr)
                    acad = d_usr.get("perfil_academia", "Academia Não Informada").strip()
                    if filtrar_academia is not None and acad.lower() != filtrar_academia:
                        continue
                    academias.setdefault(acad, []).append((usr, info, d_usr))

                for acad_nome, lista_alunos in academias.items():
                    st.markdown(f"🏛️ <b>{esc(acad_nome)}</b> ({len(lista_alunos)} alunos)", unsafe_allow_html=True)
                    for usr, info, d_usr in lista_alunos:
                        n_usr = d_usr.get("perfil_nome", "Sem Nome")
                        with st.expander(f"⚙️ {n_usr}"):
                            with st.form(key=f"form_g_{usr}"):
                                novo_em = st.text_input("E-mail:", value=usr, key=f"nem_{usr}").strip().lower()
                                nova_sen = st.text_input("Nova senha (vazio = manter):", type="password", key=f"nsen_{usr}")
                                novo_no = st.text_input("Nome:", value=n_usr, key=f"nno_{usr}")
                                fs = ["Branca", "Azul", "Roxa", "Castanha", "Preta"]
                                f_atual = d_usr.get("perfil_faixa", "Branca")
                                nova_fx = st.selectbox("Faixa:", fs, index=fs.index(f_atual) if f_atual in fs else 0, key=f"nfx_{usr}")
                                n_graus = st.slider("Graus:", 0, 4, min(4, int(d_usr.get("perfil_graus", 0) or 0)), key=f"ngr_{usr}")
                                aprov = info.get("aprovado", False)
                                if sou_master and info.get("tipo_usuario") == TIPO_PROF:
                                    aprov = st.checkbox("Professor aprovado", value=aprov, key=f"apr_{usr}")
                                c_b1, c_b2 = st.columns(2)
                                btn_s = c_b1.form_submit_button("💾 Salvar")
                                btn_d = c_b2.form_submit_button("🗑️ Excluir") if not is_master_email(usr) else False

                                if btn_s:
                                    b_atual = carregar_banco_usuarios()
                                    if novo_em != usr and (novo_em in b_atual or is_master_email(novo_em)):
                                        st.error("❌ E-mail em uso.")
                                    elif is_master_email(usr) and novo_em != usr:
                                        st.error("❌ O e-mail master não pode ser alterado.")
                                    else:
                                        reg = b_atual.pop(usr, {})
                                        if nova_sen:
                                            if len(nova_sen) < 6:
                                                st.error("❌ Senha com menos de 6 caracteres.")
                                                st.stop()
                                            reg["senha"] = hash_senha(nova_sen)
                                        reg["aprovado"] = aprov
                                        b_atual[novo_em] = reg
                                        salvar_banco_usuarios(b_atual)
                                        if novo_em != usr and os.path.exists(obter_caminho_usuario(usr)):
                                            os.replace(obter_caminho_usuario(usr), obter_caminho_usuario(novo_em))
                                        du = carregar_dados_usuario(novo_em)
                                        du["perfil_nome"], du["perfil_faixa"], du["perfil_graus"] = novo_no, nova_fx, n_graus
                                        salvar_dados_usuario(novo_em, du)
                                        st.toast("✅ Atualizado!")
                                        st.rerun()
                                if btn_d:
                                    b_atual = carregar_banco_usuarios()
                                    if usr in b_atual:
                                        del b_atual[usr]
                                        salvar_banco_usuarios(b_atual)
                                        if os.path.exists(obter_caminho_usuario(usr)):
                                            os.remove(obter_caminho_usuario(usr))
                                        st.toast("✅ Excluído!")
                                        st.rerun()

                    df_ac = pd.DataFrame([{
                        "Atleta": d[2].get("perfil_nome"), "Faixa": d[2].get("perfil_faixa"),
                        "Graus": d[2].get("perfil_graus"), "Presenças": len(d[2].get("historico_presencas", [])),
                    } for d in lista_alunos])
                    st.download_button(f"📥 Baixar Planilha ({acad_nome})", data=df_ac.to_csv(index=False).encode("utf-8"),
                                       file_name=f"turma_{re.sub(r'[^A-Za-z0-9_-]', '_', acad_nome)}.csv",
                                       mime="text/csv", use_container_width=True, key=f"dl_{acad_nome}")

        st.divider()
        if st.button("💾 Salvar Alterações Gerais", use_container_width=True):
            salvar_tudo()
            st.toast("✅ Dados salvos com sucesso!", icon="💾")
        if st.button("🚪 Sair da Conta (Logout)", use_container_width=True):
            fazer_logout()

    # ---------------- TELA PRINCIPAL ----------------
    st.markdown("<h1 style='text-align: center; color: #ff1e27;'>🥋 OssBot App Pro</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #cccccc;'>Atleta: <b>{esc(st.session_state.get('perfil_nome', ''))}</b> | Faixa {esc(st.session_state.get('perfil_faixa', 'Branca'))} ({st.session_state.get('perfil_graus', 0)}º Grau)</p>", unsafe_allow_html=True)

    if not get_secret("ANTHROPIC_API_KEY"):
        st.warning("⚠️ Chave da IA não configurada (ANTHROPIC_API_KEY). As abas de IA vão usar o modo reserva, bem mais simples.")

    abas = st.tabs([
        "🤼 Luta", "📜 Histórico", "🥗 Nutrição", "🏆 Camp", "📚 Cursos",
        "👶 Kids", "⚡ Drills", "🛡️ Pressão", "🥋 Graduação", "🥋 Kimono",
        "📇 Card", "🔑 Chaves", "⏱️ Cronograma", "🔄 Recuperação",
    ])

    hoje = lambda: datetime.now().strftime("%d/%m/%Y")

    # 1. Luta
    with abas[0]:
        col_a, col_b = st.columns(2)
        with col_a:
            painel_placar("a", "Atleta Azul", "#00ffcc", "ATLETA 1 (Azul/Preto):")
        with col_b:
            painel_placar("b", "Atleta Branco", "#ffffff", "ATLETA 2 (Branco):")

        st.divider()
        ct1, ct2, ct3 = st.columns(3)
        with ct1:
            st.selectbox("Tempo do Rola (Minutos):", [1, 2, 3, 5, 6, 10], index=3, key="tempo_sel", on_change=mudar_tempo)
        with ct2:
            st.fragment(run_every=1 if st.session_state.cronometro_rodando else None)(_render_cronometro)()
        with ct3:
            if not st.session_state.cronometro_rodando:
                st.button("▶️ Iniciar Cronômetro", use_container_width=True, on_click=iniciar_cronometro)
            else:
                st.button("⏸️ Pausar Cronômetro", use_container_width=True, on_click=pausar_cronometro)
            st.button("🔄 Zerar Luta Completa", use_container_width=True, on_click=zerar_luta)

    # 2. Histórico
    with abas[1]:
        st.markdown("### 📜 Histórico de Lutas & Treinos")
        with st.form("form_nova_luta"):
            adv = st.text_input("Oponente / Companheiro:")
            res = st.selectbox("Resultado:", ["Vitória por Finalização", "Vitória por Pontos", "Empate", "Derrota"])
            det = st.text_area("Detalhes / Posição:")
            if st.form_submit_button("Registrar Luta", use_container_width=True):
                if adv:
                    lutas = st.session_state.get("historico_lutas") or []
                    lutas.append({"data": hoje(), "adversario": adv, "resultado": res, "detalhes": det})
                    st.session_state["historico_lutas"] = lutas
                    salvar_tudo()
                    st.toast("✅ Luta registrada!", icon="🥋")
                    st.rerun()
        st.divider()
        for l in reversed(st.session_state.get("historico_lutas") or []):
            mostrar_html(f"<div class='card-item'><b>{esc(l['data'])}</b> - {esc(l['resultado'])} | Oponente: <b>{esc(l['adversario'])}</b><br>{esc(l['detalhes'])}</div>")

    # 3. Nutrição
    with abas[2]:
        st.markdown("### 🥗 Nutrição para o Atleta")
        aba_ia("nutri", "nutri", "O que você quer saber? (refeição, objetivo, horário do treino...)",
               "Ex.: o que comer antes do treino das 19h e depois do treino pesado",
               "dicas_nutricao",
               lambda t, r: {"refeicao": t[:80], "detalhes": r, "data": hoje()},
               lambda n: f"{n.get('refeicao', '')} ({n.get('data', '')})",
               lambda n: n.get("detalhes", ""), "🥗")

    # 4. Camp
    with abas[3]:
        st.markdown("### 🏆 Camp de Competição & Estratégia")
        with st.form("form_camp"):
            evento = st.text_input("Nome do Campeonato / Torneio:")
            data_camp = st.date_input("Data do Torneio:", value=date.today())
            faixa_camp = st.text_input("Faixa/Categoria:", value=st.session_state.get("perfil_faixa", "Branca"))
            estilo_jogo = st.text_area("Fale um pouco do seu jogo e o que devemos treinar para este campeonato:")
            if st.form_submit_button("Salvar Estratégia de Camp", use_container_width=True):
                if evento:
                    camps = st.session_state.get("camp_competicao") or []
                    camps.append({"evento": evento, "data": data_camp.strftime("%d/%m/%Y"), "faixa": faixa_camp, "estilo": estilo_jogo})
                    st.session_state["camp_competicao"] = camps
                    salvar_tudo()
                    st.toast("✅ Plano de Camp salvo!")
                    st.rerun()
        st.divider()
        for c in reversed(st.session_state.get("camp_competicao") or []):
            with st.expander(f"🏆 {c['evento']} ({c['data']}) - {c['faixa']}"):
                st.markdown(f"**Estratégia:**\n\n{c['estilo']}")

    # 5. Cursos
    with abas[4]:
        st.markdown("### 📚 Cursos, Regras & Anotações de Estudo")
        aba_ia("curso", "curso", "Qual técnica, posição ou regra você quer estudar?",
               "Ex.: raspagem de tesoura da guarda fechada / pontuação da IBJJF",
               "cursos_interativos",
               lambda t, r: {"titulo": t[:80], "desc": r},
               lambda c: c.get("titulo", ""), lambda c: c.get("desc", ""), "📚")

    # 6. Kids
    with abas[5]:
        st.markdown("### 👶 Dinâmicas Pedagógicas para Turmas Kids")
        st.caption("Escreva uma ou mais posições/temas. A IA monta 3 dinâmicas diferentes para cada um.")
        aba_ia("kids", "kids", "Posições / temas da aula kids:",
               "Ex.: pegada de costas, pegada de perna, guarda fechada",
               "dinamic_kids_custom",
               lambda t, r: {"foco": t[:80], "regra": r},
               lambda k: f"Foco: {k.get('foco', '')}", lambda k: k.get("regra", ""), "👶")

    # 7. Drills
    with abas[6]:
        st.markdown("### ⚡ Drills de Repetição, Ritmo e Agilidade")
        aba_ia("drills", "drills", "Posição ou ideia do drill:",
               "Ex.: passagem de guarda com toreada, 20 minutos de treino",
               "drills_treino",
               lambda t, r: {"posicao": t[:80], "reps": r},
               lambda d: f"Drill: {d.get('posicao', '')}", lambda d: d.get("reps", ""), "⚡")

    # 8. Pressão
    with abas[7]:
        st.markdown("### 🛡️ Flashcards Táticos de Pressão & Jogo")
        aba_ia("pressao", "pressao", "Descreva seu estilo de jogo ou a situação:",
               "Ex.: jogo por baixo, puxo guarda e o adversário passa colando o peso",
               "flashcards_pressao",
               lambda t, r: {"estilo": t, "resp": r},
               lambda f: f"Estilo: {f.get('estilo', '')[:40]}...",
               lambda f: f.get("resp") or (f"**Seu estilo:** {f.get('estilo', '')}\n\n❓ **Desafio tático:** se o oponente "
                                           "passar sua guarda e colar o peso, qual sua reação imediata?"), "🛡️")

    # 9. Graduação
    with abas[8]:
        st.markdown("### 🥋 Controle de Graduação & Evolução")
        with st.form("form_grad"):
            aluno_g = st.text_input("Nome do Aluno:")
            faixa_g = st.selectbox("Faixa Alvo:", ["Branca", "Azul", "Roxa", "Castanha", "Preta"])
            grau_g = st.slider("Graus Atuais:", 0, 4)
            obs_g = st.text_area("Critérios técnicos para o próximo grau/faixa:")
            if st.form_submit_button("Registrar Graduação", use_container_width=True):
                if aluno_g:
                    grad = st.session_state.get("alunos_graduacao") or []
                    grad.append({"aluno": aluno_g, "faixa": faixa_g, "grau": grau_g, "obs": obs_g})
                    st.session_state["alunos_graduacao"] = grad
                    salvar_tudo()
                    st.toast("✅ Graduação registrada!")
                    st.rerun()
        st.divider()
        for ag in reversed(st.session_state.get("alunos_graduacao") or []):
            with st.expander(f"🥋 {ag['aluno']} - Faixa {ag['faixa']} ({ag['grau']}º Grau)"):
                st.markdown(f"📝 **Critérios:** {ag.get('obs', '')}")

    # 10. Kimono
    with abas[9]:
        st.markdown("### 🥋 Guia de Cuidado e Higienização do Kimono")
        aba_ia("kimono", "kimono", "Qual o problema com o kimono?",
               "Ex.: cheiro forte que não sai, ficou encolhido, mancha amarelada na gola",
               "notas_kimono",
               lambda t, r: {"sujeira": t, "resp": r},
               lambda k: f"Estado: {k.get('sujeira', '')[:40]}...",
               lambda k: k.get("resp") or (f"**Estado:** {k.get('sujeira', '')}\n\n💡 Deixe de molho em água com vinagre "
                                           "por 30 min e lave com sabão neutro. Evite cloro."), "🥋")

    # 11. Card
    with abas[10]:
        st.markdown("### 📇 Cartão Digital de Atleta")
        mostrar_html(f"""
        <div class='placar-box' style='text-align: left; max-width: 420px; margin: 0 auto 20px auto;'>
            <h3 style='color: #ff1e27; margin-top: 0;'>🥋 OSSBOT - CARTÃO OFICIAL</h3>
            <p><b>Nome:</b> {esc(st.session_state.get('perfil_nome', 'Atleta'))}</p>
            <p><b>Faixa:</b> {esc(st.session_state.get('perfil_faixa', 'Branca'))} ({st.session_state.get('perfil_graus', 0)}º Grau)</p>
            <p><b>Academia:</b> {esc(st.session_state.get('perfil_academia', 'Nenhum'))}</p>
            <p><b>Status:</b> {esc(st.session_state.get('perfil_status', 'Atleta'))}</p>
        </div>
        """)
        st.download_button("📥 Baixar Carteirinha em TXT", data=gerar_relatorio_atleta(),
                           file_name="carteirinha_ossbot.txt", mime="text/plain", use_container_width=True)

    # 12. Chaves
    with abas[11]:
        st.markdown("### 🔑 Gerador de Chaves de Luta")
        with st.form("form_chave"):
            competicao_c = st.text_input("Nome do Torneio:")
            atletas_c = st.text_area("Lista de Atletas (um por linha):")
            if st.form_submit_button("Gerar Chaveamento", use_container_width=True):
                if competicao_c and atletas_c:
                    chaves = st.session_state.get("chaves_luta") or []
                    chaves.append({"torneio": competicao_c, "atletas": [a.strip() for a in atletas_c.split("\n") if a.strip()]})
                    st.session_state["chaves_luta"] = chaves
                    salvar_tudo()
                    st.toast("✅ Chave gerada!")
                    st.rerun()
        st.divider()
        for ch in reversed(st.session_state.get("chaves_luta") or []):
            with st.expander(f"🔑 Torneio: {ch['torneio']}"):
                st.markdown(f"**Atletas Inscritos:** {', '.join(ch['atletas'])}")

    # 13. Cronograma
    with abas[12]:
        st.markdown("### ⏱️ Cronograma Semanal de Treinos")
        with st.form("form_crono"):
            dia_c = st.selectbox("Dia da Semana:", ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"])
            horario_c = st.text_input("Horário e Foco (Ex: 19:00 - Guarda Aranha):")
            if st.form_submit_button("Adicionar ao Cronograma", use_container_width=True):
                if horario_c:
                    crono = st.session_state.get("cronogramas_aulas") or []
                    crono.append({"dia": dia_c, "detalhe": horario_c})
                    st.session_state["cronogramas_aulas"] = crono
                    salvar_tudo()
                    st.toast("✅ Cronograma salvo!")
                    st.rerun()
        st.divider()
        for cr in reversed(st.session_state.get("cronogramas_aulas") or []):
            with st.expander(f"⏱️ {cr['dia']}"):
                st.markdown(f"**Detalhe:** {cr['detalhe']}")

    # 14. Recuperação
    with abas[13]:
        st.markdown("### 🔄 Registro de Recuperação, Dores e Lesões")
        aba_ia("recup", "recup", "Descreva a dor, lesão ou cansaço:",
               "Ex.: dor no ombro direito depois de treino de americana, sem inchaço",
               "recuperacao_notas",
               lambda t, r: {"nota": f"**Relato:** {t}\n\n{r}", "data": hoje()},
               lambda n: f"Recuperação ({n.get('data', '')})", lambda n: n.get("nota", ""), "🔄")

except Exception as e:
    nome_erro = st.session_state.get("perfil_nome", "Usuário")
    adm_erro = st.session_state.get("is_admin", False)
    detalhes = traceback.format_exc()
    st.markdown("<div class='ia-erro-card'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #ff1e27; margin-top: 0;'>🤖 OssBot IA - Assistente de Diagnóstico</h3>", unsafe_allow_html=True)
    if adm_erro:
        st.markdown(f"""
        <p style='color: #ffffff;'><b>Olha só, {esc(nome_erro)}!</b> Ocorreu um erro técnico:</p>
        <div style='background: #0b0b0b; padding: 12px; border-radius: 6px; border: 1px solid #444; color: #ff6b6b; font-family: monospace; font-size: 13px;'>
            <b>Tipo:</b> {esc(type(e).__name__)}<br><b>Descrição:</b> {esc(str(e))}<br><br>
            <pre style='color: #cccccc;'>{esc(detalhes)}</pre>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <p style='color: #ffffff;'><b>Olha só, {esc(nome_erro)}!</b> Ocorreu uma pequena instabilidade nesta função.</p>
        <p style='color: #fbbf24;'>📣 Informe ao administrador do sistema para realizar esse ajuste no código!</p>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
