import re
import json
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import streamlit as st
import requests

try:
    from langchain_openai import ChatOpenAI
    from langchain.schema import SystemMessage, HumanMessage
except Exception:
    ChatOpenAI = None
    SystemMessage = HumanMessage = None


# --------- CONFIG ------------
APP_NAME = "Hola soy MARIA, ¿En que puedo ayudarte hoy?"
st.set_page_config(layout="wide", page_title=APP_NAME, page_icon="🍃")

st.markdown(
    """
    <style>
        .main { background-color:#f0f5ff; padding:0; }
        .container-box { background-color: white; border-radius: 20px; padding: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.15); margin: 1rem auto; max-width: 1200px; }
        .chat-bubble-user { background:#F3F4F6; border-radius: 14px; padding: 12px 14px; margin: 8px 0; }
        .chat-bubble-ai { background:#EFF6FF; border:1px solid #BFDBFE; border-radius: 14px; padding: 12px 14px; margin: 8px 0; white-space: pre-wrap; }
        .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #111827; color: white; text-align: center; padding: 8px 0; }
        .small-note { color:#6B7280; font-size:12px; }
    </style>
    """,
    unsafe_allow_html=True,
)

OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.warning("Configura OPENAI_API_KEY en st.secrets para habilitar el motor experto (opcional).")

llm = None
if OPENAI_API_KEY and ChatOpenAI is not None:
    llm = ChatOpenAI(model="gpt-4o", temperature=0.2, openai_api_key=OPENAI_API_KEY)

# ---------- UTILS ------------

def slug(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[áàäâ]", "a", s)
    s = re.sub(r"[éèëê]", "e", s)
    s = re.sub(r"[íìïî]", "i", s)
    s = re.sub(r"[óòöô]", "o", s)
    s = re.sub(r"[úùüû]", "u", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return s.strip()


# ----- CARGA DESDE URL --------

GSHEET_D_EDIT = re.compile(r"https?://docs\.google\.com/spreadsheets/d/([A-Za-z0-9-_]+)")
GSHEET_D_E = re.compile(r"https?://docs\.google\.com/spreadsheets/d/e/([A-Za-z0-9-_]+)")

def normalize_gsheet_export_url(url: str, fmt: str = "csv") -> str:
    """Normaliza enlaces de Google Sheets/Forms a export estable (csv/xlsx)."""
    u = (url or "").strip()
    if not u:
        return u

    # Ya es CSV/XLSX export
    if u.endswith(".csv") or "output=csv" in u.lower() or "format=xlsx" in u.lower():
        return re.sub(r"output=[^&#?]+", f"output={fmt}", u)

    # Publicado (d/e/.../pub)
    m_e = GSHEET_D_E.search(u)
    if m_e:
        sep = "&" if "?" in u else "?"
        return re.sub(r"output=[^&#?]+", f"output={fmt}", u) if "output=" in u else f"{u}{sep}output={fmt}"

    # Enlace de edición (d/<id>)
    m_d = GSHEET_D_EDIT.search(u)
    if m_d:
        sid = m_d.group(1)
        gid_match = re.search(r"gid=([0-9]+)", u)
        gid = f"&gid={gid_match.group(1)}" if gid_match else ""
        return f"https://docs.google.com/spreadsheets/d/{sid}/export?format={fmt}{gid}"

    return u

@st.cache_data(ttl=3600, show_spinner=True)
def load_table(url: str) -> pd.DataFrame:
    """Lee CSV/XLSX desde URL (idealmente Google Sheets publicado)."""
    if not url:
        raise ValueError("Proporciona una URL pública válida (Google Sheets/Forms publicado).")
    url_norm = normalize_gsheet_export_url(url, fmt="csv")
    # CSV por defecto (admite comas decimales)
    df = pd.read_csv(url_norm)
    df.columns = df.columns.astype(str).str.replace(r"\s+", " ", regex=True).str.strip()
    return df

# Encuesta a planta activa (intención y drivers)
ACTIVE_REQUIRED = {
    "id": ["Marca temporal", "id", "documento", "employee id", "cédula", "cedula"],
    "area": ["¿En qué área trabajas?", "area", "área", "departamento"],
    "rol": ["¿En qué cargo trabajas?", "rol", "cargo", "puesto", "title"],
    "intencion_salida": ["Estoy pensando en dejar la empresa en los próximos 12 meses."],
}

ACTIVE_OPTIONAL = {
    # Señales adicionales de intención
    "intencion_salida_aux": ["En los últimos 3 meses, ¿has considerado o explorado oportunidades laborales fuera de la empresa?"],
    "preferencia_quedar": ["Si otra empresa me ofreciera un trabajo similar, preferiría quedarme aquí."],

    # Engagement/NPS
    "satisfaccion_general": ["En una escala de 0 a 10, ¿Qué probabilidad hay de que recomiendes a un amigo trabajar en esta empresa?" ],

    # Drivers (acuerdos tipo Likert)
    "autonomia": ["Siento que tengo la autonomía necesaria para tomar decisiones en mi trabajo."],
    "respeto_inclusion": ["Me siento respetado(a) e incluido(a) en esta organización."],
    "confianza_liderazgo": ["Confío en la capacidad de liderazgo de quienes dirigen la organización."],
    "voz_opiniones": ["Mi voz y mis opiniones son escuchadas por la organización."],
    "comunicacion": ["La comunicación dentro de la organización es clara, transparente y efectiva."],
    "carga_laboral": ["Mi carga de trabajo es razonable y puedo manejarla sin exceso de estrés."],
    "desconexion": ["Tengo la posibilidad de desconectarme y descansar fuera del horario laboral."],
    "claridad_funciones": ["Sé claramente cuáles son mis funciones y lo que se espera de mí."],
    "herramientas": ["Cuento con las herramientas y recursos necesarios para hacer bien mi trabajo."],
    "crecimiento": ["Tengo oportunidades reales de crecer y desarrollarme dentro de la empresa."],
    "feedback": ["En los últimos 3 meses he recibido retroalimentación que me ha ayudado a mejorar."],
    "jefe_respeto": ["Mi jefe me apoya y me respeta"],
    "jefe_confia": ["Mi jefe confía en mi y valora mi trabajo"],
    "reconocimiento": ["En esta empresa se valora y reconoce cuando hago bien mi trabajo."],
    "compensacion": ["Considero que mi salario es justo frente al mercado laboral colombiano."],
    "beneficios_adecuados": ["Los beneficios que ofrece la empresa son adecuados."],
    "seguridad_psico": ["Siento que puedo dar mis ideas y opiniones sin temor a represalias."],
    "respeto_equipo": ["En mi equipo hay respeto e inclusión para todos."],
    "confianza_direccion": ["Confío en la dirección que esta tomando la empresa"],
    "motivacion": ["Me siento motivado/a para dar lo mejor de mi cada día"],

    # Texto libre
    "razon_calificacion": ["¿Cuál fue la razón principal de tu calificación anterior?"],
    "razones_posible_salida": ["Si algún día decidieras dejar la empresa, ¿Cuáles serían las principales razones? (Máximo 3)"],
    "cambio_para_quedarte": ["Si pudieras cambiar una sola cosa en la empresa para quedarte por más tiempo, ¿Qué sería?"],
    "comentario_adicional": ["¿Quieres dejar algún comentario adicional que nos ayude a mejorar?"],
}

# Encuesta de egreso (leavers)
LEAVER_REQUIRED = {
    "motivo_salida": ["¿Cuál es el motivo principal por el que decidiste irte de la empresa?", "motivo"],
}
LEAVER_OPTIONAL = {
    "area": ["¿En qué área trabajabas?", "area", "departamento"],
    "rol": ["¿En qué cargo trabajabas?", "rol", "cargo"],
    "antiguedad_meses": ["¿Cuánto tiempo estuviste en la empresa?", "antiguedad", "meses"],
    "nps": ["En una escala de 0 a 10, ¿Qué probabilidad hay de que recomiendes a un amigo trabajar en esta empresa?"],
    "otros_factores": ["Además del motivo principal, ¿Qué otros factores influyeron en tu decisión? (Máximo 3)"],
    "mejoras_retencion": ["¿Qué tres mejoras habrían hecho más probable que te quedaras en la empresa?"],
    "sugerencia_final": ["¿Quieres dejarnos alguna sugerencia final para mejorar?"],
}

# Encuesta de Gestión Humana
HR_REQUIRED = {
    "marca": ["Marca temporal"],
}
HR_OPTIONAL = {
    # KPIs
    "headcount": ["¿Cuántas personas trabajan en la organización actualmente?"],
    "rotacion_6m": ["¿Cual es el indice de rotación de tu roganización en los ultimos 6 meses?"],
    "hr_headcount": ["¿Cuántas personas trabajan en el área de Gestión Humana?"],
    "vacantes_mes": ["En promedio, ¿Cuántas vacantes tienen abiertas cada mes?"],
    "perfiles_dificiles": ["¿Cuáles son los perfiles o cargos más difíciles de cubrir?"],

    # Desajuste selección
    "dificultad_ajuste": ["En los procesos de selección hemos identificado dificultades para lograr que el perfil de los candidatos se ajuste a la complejidad real del cargo."],
    "sobrecalificados": ["En ocasiones contratamos personas sobre calificadas para cargos operativos (ej. con más estudios o experiencia de la necesaria)."],
    "subcalificados": ["En ocasiones contratamos personas sub calificadas para cargos que requieren mayor experiencia o competencias."],
    "ajuste_contribuye_rotacion": ["Considero que este desajuste entre perfil y cargo contribuye a la rotación de personal en la empresa."],
    "factores_desajuste": ["¿Qué factores crees que explican este desajuste?"],

    # Prácticas y políticas
    "indicadores_rotacion": ["En el área llevamos indicadores claros de rotación y los revisamos con frecuencia."],
    "medimos_tiempo_cobertura": ["Medimos el tiempo promedio para cubrir vacantes."],
    "medimos_costo_reemplazo": ["Medimos el costo de reemplazar personal."],
    "plan_retencion": ["Tenemos un plan formal de fidelización para los cargos más críticos."],
    "movilidad_interna": ["Contamos con políticas de movilidad interna para ofrecer nuevas oportunidades."],
    "revision_salarial_anual": ["Revisamos los salarios al menos una vez al año comparándolos con el mercado."],
    "flexibilidad_laboral": ["Ofrecemos flexibilidad laboral (teletrabajo, horarios flexibles) según el rol."],
    "encuestas_clima": ["Aplicamos encuestas de clima laboral y damos seguimiento a los resultados."],

    # Causas según HR
    "causa_compensacion": ["Considero que la compensación es una de las principales causas de salida de la gente."],
    "causa_jefes": ["Considero que la relación con los jefes es una de las principales causas de salida."],
    "causa_sobrecarga": ["Considero que la sobrecarga laboral es una de las principales causas de salida."],
    "causa_proyeccion": ["Considero que la falta de proyección es una de las principales causas de salida."],
    "causa_modalidad": ["Considero que la modalidad de trabajo (remoto/presencial) es una de las principales causas de salida."],

    # Efectividad de acciones
    "eff_ajuste_salarios": ["Nuestras acciones actuales son efectivas para ajustar salarios cuando es necesario."],
    "eff_liderazgo": ["Nuestras acciones actuales son efectivas para desarrollar programas de liderazgo."],
    "eff_bienestar": ["Nuestras acciones actuales son efectivas para promover bienestar y salud mental."],
    "eff_reconocimiento": ["Nuestras acciones actuales son efectivas para reconocer el buen desempeño."],
    "eff_capacitacion": ["Nuestras acciones actuales son efectivas para dar oportunidades de capacitación y planes de carrera."],

    # Analítica y sponsorship
    "usa_analitica": ["En la empresa usamos analítica de datos para predecir riesgos de salida."],
    "sponsorship_alta_direccion": ["La alta dirección participa activamente en las acciones de fidelización."],

    # Segmentación rotación
    "identifico_quien_se_va": ["En los últimos 12 meses, ¿la empresa ha identificado qué tipo de personas están dejando la organización?"],
    "percepcion_rotacion": ["Consideras que en la mayoría de los casos la rotación actual de la empresa es"],

    # Acciones inmediatas
    "acciones_6m": ["Si tuvieras que priorizar tres acciones inmediatas para reducir la rotación en los próximos 6 meses, ¿Cuáles serían?"],
}

# ----- MAPEADOR DE COLUMNAS ---

def guess_col(df: pd.DataFrame, hints: List[str], default: Optional[str] = None) -> Optional[str]:
    slugs = {slug(c): c for c in df.columns}
    for h in hints:
        if slug(h) in slugs:
            return slugs[slug(h)]
    return default

def map_cols(df: pd.DataFrame, req: Dict[str, List[str]], opt: Dict[str, List[str]]) -> Dict[str, Optional[str]]:
    m: Dict[str, Optional[str]] = {}
    for k, hints in req.items():
        c = guess_col(df, hints)
        if not c:
            c = df.columns[0]
        m[k] = c
    for k, hints in opt.items():
        m[k] = guess_col(df, hints, default=None)
    return m

# ---- PREP & SCORING LOGIC ----

KEYWORDS_BUCKETS = {
    "compensacion": ["salario", "pago", "compens", "sueldo", "bono"],
    "beneficios": ["beneficio", "prestacion", "eps", "auxilio", "bonificación"],
    "liderazgo": ["jefe", "lider", "manager", "trato", "feedback", "retroaliment", "reconocimiento"],
    "carrera": ["crecimiento", "desarrollo", "ascenso", "aprendizaje", "formacion", "proyeccion", "carrera"],
    "carga": ["carga", "horas", "turno", "estres", "estrés", "burnout", "sobre carga", "sobrecarga"],
    "flexibilidad": ["flexibilidad", "teletrabajo", "hibrido", "híbrido", "home office", "horario", "presencial", "remoto"],
    "ambiente": ["clima", "ambiente", "equipo", "cultura", "respeto", "inclusion", "inclusión", "seguridad"],
    "comunicacion": ["comunicacion", "comunicación", "transparencia", "informacion"],
    "herramientas": ["herramienta", "equipo", "recurso", "software"],
    "claridad_rol": ["claridad", "funciones", "objetivo", "rol"],
    "autonomia": ["autonomia", "autonomía", "decisiones"],
    "seleccion_ajuste": ["ajuste", "perfil", "seleccion", "selección", "sobrecali", "subcali"],
}

def map_spanish_likert_to_numeric(series: pd.Series) -> pd.Series:
    """Mapea respuestas en español a números y **garantiza dtype numérico**.
    - Soporta Likert textual (1..5), sí/no y números ("8", "10", "10,0").
    - Convierte valores como "—", "n/a", "no aplica" en NaN.
    """
    s = series.astype(str).str.strip().str.lower()
    s = s.replace({
        "": np.nan,
        "-": np.nan,
        "—": np.nan,
        "na": np.nan,
        "n/a": np.nan,
        "no aplica": np.nan,
        "prefiero no responder": np.nan,
        "sin respuesta": np.nan,
    })

    LIKERT_ES_MAP = {
        "totalmente en desacuerdo": 1,
        "en desacuerdo": 2,
        "ni de acuerdo ni en desacuerdo": 3,
        "de acuerdo": 4,
        "totalmente de acuerdo": 5,
    }

    mapped = s.map(LIKERT_ES_MAP)

    mapped = mapped.fillna(s.replace({"sí": 5, "si": 5, "yes": 5, "no": 1}))

    numeric = pd.to_numeric(s.str.replace(",", ".", regex=False), errors="coerce")

    out = mapped.fillna(numeric)
    out = pd.to_numeric(out, errors="coerce")
    return out

def normalize_likert(series: pd.Series) -> pd.Series:
    """Normaliza a 0-100 soportando 1-5, 0-10 y 0-100.
    Evita errores de comparación cuando hay strings mezclados.
    """
    s = map_spanish_likert_to_numeric(series)
    mx = s.max(skipna=True)
    if pd.notna(mx) and mx <= 5:
        return (s - 1) / 4 * 100
    if pd.notna(mx) and mx <= 10:
        return (s / 10) * 100
    return s.clip(0, 100)

def _score_agreement(series: pd.Series, positive_is_risk: bool = True) -> pd.Series:
    s = map_spanish_likert_to_numeric(series)
    mx = s.max(skipna=True)
    if pd.isna(mx):
        score = s 
    elif mx <= 5:
        score = (s - 1) / 4
    elif mx <= 10:
        score = s / 10
    else:
        score = (s.clip(0, 100)) / 100
    return score if positive_is_risk else (1 - score)

def _score_yesno(series: pd.Series, yes_risk: bool = True) -> pd.Series:
    s = series.astype(str).str.strip().str.lower()
    s = s.replace({
        "": np.nan,
        "-": np.nan,
        "—": np.nan,
        "na": np.nan,
        "n/a": np.nan,
        "no aplica": np.nan,
        "prefiero no responder": np.nan,
        "sin respuesta": np.nan,
    })
    yes = s.isin(["sí", "si", "yes", "true", "verdadero"]) | s.str.contains(r"\b(s[ií])\b", na=False)
    no = s.isin(["no", "false", "falso"]) | s.str.contains(r"\bno\b", na=False)
    base = pd.Series(np.nan, index=s.index, dtype="float")
    base[yes] = 1.0
    base[no] = 0.0

    s_num = pd.to_numeric(s.str.replace(',', '.', regex=False), errors='coerce')
    base = base.fillna(s_num.apply(lambda x: np.nan if pd.isna(x) else (1.0 if x >= 1 else 0.0)))
    return base if yes_risk else 1 - base

def infer_intent_from_active(df_active: pd.DataFrame, m_active: Dict[str, Optional[str]]) -> pd.Series:
    """Construye un score de intención de salida combinando 2-3 señales."""
    parts = []

    col_main = m_active.get("intencion_salida")
    if col_main and col_main in df_active.columns:
        parts.append(_score_agreement(df_active[col_main], positive_is_risk=True))

    col_aux = m_active.get("intencion_salida_aux")
    if col_aux and col_aux in df_active.columns:
        parts.append(_score_yesno(df_active[col_aux], yes_risk=True))

    col_stay = m_active.get("preferencia_quedar")
    if col_stay and col_stay in df_active.columns:
        parts.append(_score_agreement(df_active[col_stay], positive_is_risk=False))

    if not parts:
        return pd.Series(0.0, index=df_active.index)

    X = pd.concat(parts, axis=1)
    return X.mean(axis=1).fillna(0.0)

def correlate_with_intent(df_active: pd.DataFrame, m_active: Dict[str, Optional[str]]) -> pd.DataFrame:
    """Calcula correlaciones de drivers con intención de salida."""
    y = infer_intent_from_active(df_active, m_active)
    drivers = {}
    skip_keys = {"id", "area", "rol", "intencion_salida", "intencion_salida_aux", "preferencia_quedar", "razones_texto"}
    for key, col in m_active.items():
        if key in skip_keys:
            continue
        if not col or col not in df_active.columns:
            continue
        x = normalize_likert(df_active[col])
        drivers[key] = x
    if not drivers:
        return pd.DataFrame()
    X = pd.DataFrame(drivers)
    corr = X.assign(intent=y).corr(numeric_only=True)["intent"].drop("intent")
    out = (
        corr.rename("correlacion_intencion")
        .sort_values(ascending=True)  # negativo = protector; positivo = riesgo
        .to_frame()
    )
    out.index.name = "driver"
    return out

def tokenize(s: str) -> List[str]:
    return re.findall(r"[a-záéíóúüñ0-9]+", str(s).lower())

def bucketize_reason(text: str) -> Dict[str, int]:
    tokens = tokenize(text)
    counts = {k: 0 for k in KEYWORDS_BUCKETS}
    for k, words in KEYWORDS_BUCKETS.items():
        counts[k] = sum(1 for t in tokens for w in words if w in t)
    return counts

def summarize_reasons(df_active: pd.DataFrame, df_leaver: pd.DataFrame, m_active: Dict[str, Optional[str]], m_leaver: Dict[str, Optional[str]]) -> pd.DataFrame:
    buckets = {k: 0 for k in KEYWORDS_BUCKETS}
    # Activos – texto consolidado
    col_txt_a = m_active.get("razones_texto")
    if col_txt_a and col_txt_a in df_active.columns:
        for txt in df_active[col_txt_a].dropna().astype(str).tolist():
            counts = bucketize_reason(txt)
            for k, v in counts.items():
                buckets[k] += v
    # Egresos – texto consolidado y motivo estructurado
    col_txt_l = m_leaver.get("comentarios")
    if col_txt_l and col_txt_l in df_leaver.columns:
        for txt in df_leaver[col_txt_l].dropna().astype(str).tolist():
            counts = bucketize_reason(txt)
            for k, v in counts.items():
                buckets[k] += v
    col_mot = m_leaver.get("motivo_salida")
    if col_mot and col_mot in df_leaver.columns:
        for txt in df_leaver[col_mot].dropna().astype(str).tolist():
            counts = bucketize_reason(txt)
            for k, v in counts.items():
                buckets[k] += v
    df = pd.DataFrame([
        {"categoria": k, "menciones": v} for k, v in buckets.items()
    ]).sort_values("menciones", ascending=False)
    df["peso_relativo_%"] = (df["menciones"] / max(1, df["menciones"].sum())) * 100
    return df

def area_risk(df_active: pd.DataFrame, m_active: Dict[str, Optional[str]]) -> pd.DataFrame:
    a_col = m_active.get("area")
    if not a_col or a_col not in df_active.columns:
        return pd.DataFrame()
    intent = infer_intent_from_active(df_active, m_active)
    # drivers principales si existen
    drv_cols_keys = [
        "satisfaccion_general", "compensacion", "jefe_respeto", "jefe_confia", "crecimiento",
        "carga_laboral", "comunicacion", "reconocimiento"
    ]
    drv_cols = [m_active.get(k) for k in drv_cols_keys]
    drv_cols = [c for c in drv_cols if c and c in df_active.columns]
    df = df_active[[a_col]].copy()
    df["intent"] = intent
    for c in drv_cols:
        df[c+"_norm"] = normalize_likert(df_active[c])
    agg = df.groupby(a_col).agg(
        intent_media=("intent", "mean"),
        n=("intent", "size"),
        **{c+"_avg": (c+"_norm", "mean") for c in drv_cols}
    ).reset_index()
    sat_key = m_active.get("satisfaccion_general")
    if sat_key and (sat_key+"_avg") in agg.columns:
        agg["riesgo"] = 0.5*agg["intent_media"] + 0.5*(100 - agg[sat_key+"_avg"]) / 100
    else:
        agg["riesgo"] = agg["intent_media"]
    agg["riesgo_%"] = (agg["riesgo"]*100).round(1)
    agg = agg.sort_values(["riesgo", "n"], ascending=[False, False])
    return agg

# --------- HR DASHBOARD -------

def to_bool(s: pd.Series) -> pd.Series:
    x = s.astype(str).str.strip().str.lower()
    yes_like = x.isin(["sí", "si", "yes", "true"]) | x.str.contains(r"de acuerdo|aplica|cumple|si\b|sí\b", na=False)
    no_like = x.isin(["no", "false"]) | x.str.contains(r"no aplica|no cumple|en desacuerdo", na=False)
    out = pd.Series(np.nan, index=x.index, dtype="float")
    out[yes_like] = 1.0
    out[no_like] = 0.0
    # fallback numérico
    out = out.fillna(pd.to_numeric(x.str.replace(",", ".", regex=False), errors="coerce").apply(
        lambda v: np.nan if pd.isna(v) else (1.0 if v >= 1 else 0.0)
    ))
    return out

def hr_dashboard(df_hr: pd.DataFrame, m_hr: Dict[str, Optional[str]]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, str]:
    # KPIs simples
    kpis = []
    def _num(col_key):
        col = m_hr.get(col_key)
        if col and col in df_hr.columns:
            return pd.to_numeric(df_hr[col].astype(str).str.replace(",", ".", regex=False), errors="coerce").dropna().mean()
        return np.nan

    hc = _num("headcount")
    rot = _num("rotacion_6m")
    hr_hc = _num("hr_headcount")
    vac = _num("vacantes_mes")
    ratio_hr = (hr_hc / hc * 100) if (pd.notna(hr_hc) and pd.notna(hc) and hc > 0) else np.nan

    kpis.append({"indicador": "Headcount", "valor": hc})
    kpis.append({"indicador": "Rotación 6m (%)", "valor": rot})
    kpis.append({"indicador": "Headcount HR", "valor": hr_hc})
    kpis.append({"indicador": "Vacantes/mes", "valor": vac})
    kpis.append({"indicador": "% HR sobre total", "valor": ratio_hr})
    kpis_df = pd.DataFrame(kpis)

    # Causas según HR
    causas_keys = [
        ("causa_compensacion", "Compensación"),
        ("causa_jefes", "Jefes/Liderazgo"),
        ("causa_sobrecarga", "Sobrecarga"),
        ("causa_proyeccion", "Falta de proyección"),
        ("causa_modalidad", "Modalidad trabajo"),
    ]
    causas_rows = []
    for key, label in causas_keys:
        col = m_hr.get(key)
        if col and col in df_hr.columns:
            val = to_bool(df_hr[col]).mean()
            causas_rows.append({"causa": label, "% acuerdo": round(val*100, 1) if pd.notna(val) else np.nan})
    causas_df = pd.DataFrame(causas_rows).sort_values("% acuerdo", ascending=False) if causas_rows else pd.DataFrame()

    pract_keys = [
        ("indicadores_rotacion", "Indicadores de rotación"),
        ("medimos_tiempo_cobertura", "Medimos tiempo de cobertura"),
        ("medimos_costo_reemplazo", "Medimos costo de reemplazo"),
        ("plan_retencion", "Plan de retención"),
        ("movilidad_interna", "Movilidad interna"),
        ("revision_salarial_anual", "Revisión salarial anual"),
        ("flexibilidad_laboral", "Flexibilidad laboral"),
        ("encuestas_clima", "Encuestas de clima"),
        ("usa_analitica", "Analítica de rotación"),
        ("sponsorship_alta_direccion", "Sponsorship Alta Dirección"),
        ("eff_ajuste_salarios", "Efectivo: ajuste salarios"),
        ("eff_liderazgo", "Efectivo: liderazgo"),
        ("eff_bienestar", "Efectivo: bienestar/SM"),
        ("eff_reconocimiento", "Efectivo: reconocimiento"),
        ("eff_capacitacion", "Efectivo: capacitación/carrera"),
    ]
    pract_rows = []
    for key, label in pract_keys:
        col = m_hr.get(key)
        if col and col in df_hr.columns:
            val = to_bool(df_hr[col]).mean()
            pract_rows.append({"práctica": label, "% sí/efectivo": round(val*100, 1) if pd.notna(val) else np.nan})
    pract_df = pd.DataFrame(pract_rows).sort_values("% sí/efectivo", ascending=False) if pract_rows else pd.DataFrame()

    # Campos de texto
    perfiles = m_hr.get("perfiles_dificiles")
    acciones = m_hr.get("acciones_6m")
    text_concat = []
    if perfiles and perfiles in df_hr.columns:
        text_concat += ["Perfiles difíciles: " + "; ".join(df_hr[perfiles].dropna().astype(str).tolist())]
    if acciones and acciones in df_hr.columns:
        text_concat += ["Acciones 6m sugeridas: " + "; ".join(df_hr[acciones].dropna().astype(str).tolist())]
    text_blob = " | ".join(text_concat)

    return kpis_df, causas_df, pract_df, text_blob

# --------- PROMPTS -----------
SYSTEM_PROMPT = (
    "Eres MARIA, una consultora ejecutiva experta en retención y fidelización de talento y reducción de rotación. "
    "Siempre respondes en español, en tono claro, ejecutivo y accionable. "
    "Eres rigurosa con supuestos; separas 'dato' de 'supuesto' y justificas. "
    "Entregas diagnóstico de drivers de salida, priorización de iniciativas (alto impacto/baja complejidad), "
    "y hoja de ruta trimestral con responsables y métricas. "
    "Evitas lenguaje discriminatorio; promueves decisiones basadas en evidencia. "
    "Cuando se provea contexto de HR, alinea recomendaciones con beneficios y restricciones actuales. "
    "Incluye advertencia breve: 'Contenido referencial; no reemplaza asesoría legal/SSO.'"
)

CHAT_INSTRUCTIONS = """
Responde como experta en **retención**, **fidelización** y **experiencia del colaborador**.
- Identifica drivers de riesgo y protectores a partir de correlaciones y texto libre.
- Prioriza acciones en 3 horizontes: quick wins (0-30 días), 60-90 días, 90-180 días.
- Usa palancas: compensación, liderazgo, carrera, flexibilidad, carga, beneficios.
- Sugiere métricas: intención de salida, tiempo de cobertura de vacantes, eNPS, % adopción de beneficios clave.
- No inventes datos: si faltan, explícitalo y sugiere cómo obtenerlos.
- Cierra con: *Contenido referencial; no reemplaza asesoría legal/SSO.*
"""

def build_llm_answer(base_context: Dict[str, object], user_q: str) -> str:
    if llm is None or SystemMessage is None or HumanMessage is None:
        return (
            "Motor experto deshabilitado. Agrega `OPENAI_API_KEY` en `st.secrets` para activar respuestas generativas.\n\n"
            "Puedes seguir usando el Tab de Conclusiones para el diagnóstico determinista."
        )
    system = SystemMessage(content=SYSTEM_PROMPT)
    human = HumanMessage(content=f"Contexto JSON (si disponible): {json.dumps(base_context, ensure_ascii=False)}\n\nPregunta: {user_q}\n\nInstrucciones específicas:\n{CHAT_INSTRUCTIONS}")
    try:
        resp = llm.invoke([system, human])
        return resp.content
    except Exception as e:
        return f"Error al consultar el modelo: {e}\n\nSugerencia: verifica OPENAI_API_KEY en st.secrets."

# -------------- UI -----------
st.markdown("<div class='container-box'>", unsafe_allow_html=True)
st.title(f"🍃 {APP_NAME}")

with st.sidebar:
    st.header("⚙️ Origen de datos (URLs)")
    st.caption("Los enlaces se cargan automáticamente desde tu cuenta.")

    # ⚠️ El email llega desde React en la URL del iframe
    email_usuario = st.query_params.get("email", None)  # ej: http://localhost:8501/?email=user@gmail.com

    url_active = url_leaver = url_hr = None

    if email_usuario:
        try:
            resp = requests.get(f"http://127.0.0.1:8000/api/accounts/user-links/?email={email_usuario}")
            if resp.status_code == 200:
                data = resp.json()
                url_active = data.get("form_link1", "")
                url_leaver = data.get("form_link2", "")
                url_hr = data.get("form_link3", "")
                st.success("✅ Links cargados desde tu cuenta.")
            else:
                st.error("No se pudieron cargar los links del usuario.")
        except Exception as e:
            st.error(f"Error conectando con backend: {e}")
    else:
        st.warning("No se recibió el email del usuario en la URL (ej: ?email=correo@ejemplo.com)")

    st.divider()
    st.subheader("Parámetros")
    min_responses = st.number_input("Mín. respuestas por área para mostrar (umbral)", value=10, min_value=1, step=1)
    top_n = st.slider("Top N drivers a destacar", 3, 15, 7, step=1)

if not (url_active and url_leaver and url_hr):
    st.info("Pega las **tres** URLs públicas para continuar.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

try:
    df_active = load_table(url_active)
    df_leaver = load_table(url_leaver)
    df_hr = load_table(url_hr)
    st.success(f"Cargados: activos {len(df_active):,} filas · egresos {len(df_leaver):,} · HR {len(df_hr):,}")
except Exception as e:
    st.error(f"No se pudieron leer las URLs: {e}")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# Mapear columnas
m_active = map_cols(df_active, ACTIVE_REQUIRED, ACTIVE_OPTIONAL)
m_leaver = map_cols(df_leaver, LEAVER_REQUIRED, LEAVER_OPTIONAL)
m_hr = map_cols(df_hr, HR_REQUIRED, HR_OPTIONAL)

TAB1, TAB2, TAB3 = st.tabs(["Conclusiones y correlaciones", "Chat experto", "Explorar archivos"])

# TAB 1 – CONCLUSIONES Y CORRELACIONES

with TAB1:
    st.subheader("🧭 Diagnóstico integral de rotación")

    active_text_cols = [
        m_active.get("razon_calificacion"),
        m_active.get("razones_posible_salida"),
        m_active.get("cambio_para_quedarte"),
        m_active.get("comentario_adicional"),
    ]
    active_text_cols = [c for c in active_text_cols if c and c in df_active.columns]
    if active_text_cols:
        df_active["__reasons_text_activos"] = df_active[active_text_cols].astype(str).agg(" | ".join, axis=1)
        m_active["razones_texto"] = "__reasons_text_activos"

    leaver_text_cols = [
        m_leaver.get("otros_factores"),
        m_leaver.get("mejoras_retencion"),
        m_leaver.get("sugerencia_final"),
    ]
    leaver_text_cols = [c for c in leaver_text_cols if c and c in df_leaver.columns]
    if leaver_text_cols:
        df_leaver["__reasons_text_egresos"] = df_leaver[leaver_text_cols].astype(str).agg(" | ".join, axis=1)
        m_leaver["comentarios"] = "__reasons_text_egresos"

    try:
        corr_df = correlate_with_intent(df_active, m_active)
    except Exception as e:
        st.error(f"Error calculando correlaciones: {e}")
        corr_df = pd.DataFrame()

    try:
        reasons_df = summarize_reasons(df_active, df_leaver, m_active, m_leaver)
    except Exception as e:
        st.error(f"Error procesando razones de salida: {e}")
        reasons_df = pd.DataFrame()

    try:
        risk_df = area_risk(df_active, m_active)
        if len(risk_df):
            risk_df = risk_df[risk_df["n"] >= min_responses]
    except Exception as e:
        st.error(f"Error calculando riesgo por área: {e}")
        risk_df = pd.DataFrame()

    cols = st.columns(2)
    with cols[0]:
        st.markdown("**Drivers asociados a intención de salida** (corr. Pearson; negativo = protector, positivo = riesgo)")
        if len(corr_df):
            st.dataframe(corr_df.head(top_n), use_container_width=True)
        else:
            st.info("No se pudieron calcular correlaciones. Revisa columnas de drivers en la encuesta de activos.")
    with cols[1]:
        st.markdown("**Razones más mencionadas (activos + egresos)**")
        if len(reasons_df):
            st.dataframe(reasons_df.head(top_n), use_container_width=True)
        else:
            st.info("No se detectaron razones. Revisa campos de texto y motivo de salida.")

    st.markdown("---")
    st.markdown("**Riesgo por área (intención y eNPS/engagement)**")
    if len(risk_df):
        st.dataframe(risk_df, use_container_width=True)
    else:
        st.info("No hay suficientes datos por área o faltan columnas clave (área, intención, eNPS/engagement).")


    st.markdown("---")
    st.subheader("🏢 Gestión Humana: KPIs, causas y capacidades")
    try:
        kpis_df, causas_df, pract_df, hr_text = hr_dashboard(df_hr, m_hr)
        if len(kpis_df):
            st.markdown("**KPIs**")
            st.dataframe(kpis_df, use_container_width=True)
        if len(causas_df):
            st.markdown("**Causas de rotación (percepción HR)**")
            st.dataframe(causas_df, use_container_width=True)
        if len(pract_df):
            st.markdown("**Capacidades y prácticas (sí/efectivo)**")
            st.dataframe(pract_df.head(15), use_container_width=True)
        if hr_text:
            st.caption(hr_text[:1000])
    except Exception as e:
        st.error(f"Error en panel HR: {e}")

    # Conclusiones accionables
    st.markdown("---")
    st.subheader("📌 Conclusiones y recomendaciones (automático)")

    def render_takeaways():
        items = []
        if len(corr_df):
            worst = corr_df.tail(3).index.tolist()
            best = corr_df.head(3).index.tolist()
            items.append(f"**Drivers de mayor riesgo**: {', '.join(worst)}")
            items.append(f"**Drivers protectores**: {', '.join(best)}")
        if len(reasons_df):
            top_reasons = reasons_df.head(3)["categoria"].tolist()
            items.append(f"**Motivos más reportados**: {', '.join(top_reasons)}")
        if len(risk_df):
            high_risk = risk_df.head(3)[m_active.get("area")].tolist()
            items.append(f"**Áreas con mayor riesgo**: {', '.join(high_risk)}")
        if 'causas_df' in locals() and len(causas_df):
            focus = causas_df.head(3)["causa"].tolist()
            items.append(f"**Causas según HR**: {', '.join(focus)}")
        if 'pract_df' in locals() and len(pract_df):
            gaps = pract_df.sort_values("% sí/efectivo").head(3)["práctica"].tolist()
            items.append(f"**Brechas de capacidad en HR**: {', '.join(gaps)}")
        if not items:
            items.append("No hay suficientes datos para inferir conclusiones. Verifica mapeo de columnas y calidad de respuestas.")
        return items

    for bullet in render_takeaways():
        st.markdown(f"- {bullet}")

    st.caption("*Contenido referencial; no reemplaza asesoría legal/SSO.*")

# TAB 2 – CHAT EXPERTO
with TAB2:
    st.subheader("💬 Chat experto en fidelización y experiencia del colaborador")

    if "rot_chat_history" not in st.session_state:
        st.session_state.rot_chat_history = []

    base_context = {
        "active_cols": list(df_active.columns),
        "leaver_cols": list(df_leaver.columns),
        "hr_cols": list(df_hr.columns),
        "m_active": m_active,
        "m_leaver": m_leaver,
        "m_hr": m_hr,
        "corr_top": corr_df.tail(min(5, len(corr_df))).reset_index().to_dict(orient="records") if 'corr_df' in locals() and len(corr_df) else [],
        "reasons_top": reasons_df.head(min(5, len(reasons_df))).to_dict(orient="records") if 'reasons_df' in locals() and len(reasons_df) else [],
        "risk_top": risk_df.head(min(5, len(risk_df))).to_dict(orient="records") if 'risk_df' in locals() and len(risk_df) else [],
    }
    # Historial
    for role, msg in st.session_state.rot_chat_history:
        with st.chat_message(role):
            st.markdown(msg)

    user_q = st.chat_input("Pregunta algo como: '¿qué quick wins implementar en 30 días?' o '¿cómo reducir salidas por liderazgo?'")
    if user_q:
        st.session_state.rot_chat_history.append(("user", user_q))
        with st.chat_message("user"):
            st.markdown(user_q)

        answer = build_llm_answer(base_context, user_q)

        with st.chat_message("assistant"):
            st.markdown(answer)
        st.session_state.rot_chat_history.append(("assistant", answer))

# TAB 3 – EXPLORAR ARCHIVOS
with TAB3:
    st.subheader("👀 Ver/filtrar encuestas")

    ds = {
        "Activos": df_active,
        "Egresos": df_leaver,
        "Gestión Humana": df_hr,
    }
    which = st.selectbox("Selecciona dataset", options=list(ds.keys()))
    df = ds[which]

    if len(df) == 0:
        st.warning("La fuente no tiene filas.")
    else:
        max_preview = min(1000, len(df))
        default_preview = min(20, max_preview)

        if max_preview == 1:
            n_preview = 1
            st.caption("Mostrando 1 fila (no hay más para previsualizar).")
        else:
            n_preview = st.slider(
                "Filas a mostrar (preview)",
                min_value=1,
                max_value=max_preview,
                value=default_preview,
                step=1,
                key=f"slider_{which}",
            )

        cols_sel = st.multiselect(
            "Columnas a mostrar (opcional)",
            options=list(df.columns),
            default=list(df.columns)[:min(10, len(df.columns))],
            key=f"cols_{which}",
        )
        view_df = df[cols_sel] if cols_sel else df
        st.dataframe(view_df.head(n_preview), use_container_width=True)
        st.download_button(
            f"⬇️ Descargar {which} (CSV)",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=f"{slug(which)}.csv",
            mime="text/csv",
            key=f"dl_{which}",
        )

st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div class='footer'>
        © 2025 Solution Hr · Diagnóstico de rotación y fidelización.
    </div>
    """,
    unsafe_allow_html=True,
)
