"""
predict_risk.py — Modelos de predicción de riesgo REALES

Reemplazan el simulador EHR cuando haya datos reales.
Cada modelo se puede correr con datos sintéticos para demo/prototipo.

Arquitectura: misma interfaz `predict()` → dict
Para swappear: cambiar la implementación, el endpoint /riesgo NO cambia.

Referencias:
  - BEHRT: https://github.com/deepmind/BEHRT  (Nature Comms 2020, no longer maintained)
  - FEMR/CLMBR/MOTOR: https://github.com/som-shahlab/femr  (actively maintained 2025+)
    CLMBR: https://github.com/som-shahlab/clmbr
  - Delphi: https://github.com/gerstung-lab/delphi  (2025 paper, UK Biobank weights)
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


# ══════════════════════════════════════════════════════════════════════════════
# FINDRISC — en producción AHORA
# ══════════════════════════════════════════════════════════════════════════════

def predict_findrisc(patient: dict) -> dict:
    """
    Finnish Diabetes Risk Score — validado OMS/IDF.
    No requiere entrenamiento. Es una regla clínica validada.
    """
    from backend.app.health_models import RiskModel, FindriscInput

    inp = FindriscInput(
        edad=patient.get("edad", "menor_45"),
        imc=patient.get("imc", "menor_25"),
        sexo=patient.get("sexo", "M"),
        actividad_fisica=patient.get("actividad_fisica", True),
        frutas_verduras_diario=patient.get("frutas_verduras_diario", True),
        medicacion_hipertension=patient.get("medicacion_hipertension", False),
        glucosa_alta_antes=patient.get("glucosa_alta_antes", False),
        familiar_diabetes=patient.get("familiar_diabetes", "ninguno"),
    )
    r = RiskModel().assess(inp)
    return {"modelo": "FINDRISC", "score": r.score, "nivel": r.nivel,
            "riesgo_porcentaje": r.riesgo_porcentaje,
            "recomendacion": r.recomendacion}


# ══════════════════════════════════════════════════════════════════════════════
# FASE 2: XGBoost — baseline con features tabulares
# ══════════════════════════════════════════════════════════════════════════════

try:
    import xgboost as xgb
    HAS_XGB = True
except ImportError:
    HAS_XGB = False


class XGBoostRiskModel:
    """
    Modelo XGBoost baseline para riesgo de diabetes.

    Features de entrada:
      - edad, sexo, imc
      - n_medicamentos_distintos (de OCR boletas)
      - n_citas_ultimo_anno
      - n_sintomas_reportados
      - findrisc_score (del modelo actual)
      - dias_desde_ultima_compra

    Entrenamiento:
      Labels: diagnóstico confirmado de diabetes (de historial del paciente o médico)

    Uso:
      model = XGBoostRiskModel()
      model.train(X_train, y_train)
      pred = model.predict(patient_features)
    """

    def __init__(self):
        self.model: Optional[xgb.XGBClassifier] = None

    def extract_features(self, patient_history: list[dict]) -> np.ndarray:
        """Extrae features tabulares del historial del paciente."""
        eventos = patient_history
        edad = next((e.get("edad") for e in [{"edad": 45}] if "edad" in e), 45)

        medicamentos = [e for e in eventos if e.get("tipo") == "medicamento"]
        citas = [e for e in eventos if e.get("tipo") == "cita"]
        sintomas = [e for e in eventos if e.get("tipo") == "sintoma"]

        n_meds = len(set(m.get("codigo") for m in medicamentos))
        n_citas = len(citas)
        n_sintomas = len(sintomas)

        # Calcular días desde última compra
        hoy = datetime.now()
        fechas_compra = []
        for e in eventos:
            if e.get("tipo") == "medicamento" and "fecha" in e:
                try:
                    fechas_compra.append(datetime.strptime(e["fecha"], "%Y-%m-%d"))
                except ValueError:
                    pass
        dias = (hoy - max(fechas_compra)).days if fechas_compra else 365

        return np.array([[
            edad / 100.0,
            1.0 if next((e.get("sexo") for e in [{"sexo": "M"}] if "sexo" in e), "M") == "M" else 0.0,
            n_meds,
            n_citas,
            n_sintomas,
            dias / 365.0,
        ]], dtype=np.float32)

    def train(self, X: np.ndarray, y: np.ndarray):
        if not HAS_XGB:
            raise ImportError("pip install xgboost")
        self.model = xgb.XGBClassifier(
            n_estimators=100, max_depth=4, learning_rate=0.05,
            objective="binary:logistic", eval_metric="logloss",
            random_state=42
        )
        self.model.fit(X, y)

    def predict(self, features: Optional[np.ndarray] = None,
                patient_history: Optional[list[dict]] = None) -> dict:
        """Predicción XGBoost. Necesita modelo entrenado o usa reglas de fallback."""
        if features is None and patient_history is not None:
            features = self.extract_features(patient_history)
        if features is None:
            features = np.array([[0.45, 0.0, 2.0, 3.0, 1.0, 0.1]], dtype=np.float32)

        if self.model is not None and HAS_XGB:
            proba = float(self.model.predict_proba(features)[0, 1])
        else:
            # Fallback: regla heurística basada en features (demo)
            edad_norm, sexo_bin, n_meds, n_citas, n_sintomas, dias = features[0]
            proba = min(0.85, max(0.05,
                0.15 + edad_norm * 0.4 + n_meds * 0.08 + n_sintomas * 0.05
                + (1.0 - dias) * 0.1
            ))

        return {
            "modelo": "XGBoost (real / fallback heurístico)",
            "probabilidad_diabetes_12m": round(proba, 3),
            "features_usadas": [
                "edad_norm", "sexo_bin", "n_medicamentos_unicos",
                "n_citas", "n_sintomas", "dias_desde_ultima_compra"
            ],
            "status": "entrenado" if self.model else "fallback — necesita datos para entrenar"
        }


# ══════════════════════════════════════════════════════════════════════════════
# FASE 3: BEHRT-style encoder — secuencias ICD-10
# ══════════════════════════════════════════════════════════════════════════════

try:
    import torch
    import torch.nn as nn
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False


class BEHRTEncoder(nn.Module):
    """
    Implementación simplificada de BEHRT (Behavioral EHR Transformer).

    Referencia:
      Li et al. "BEHRT: Transformer for Electronic Health Records"
      Nature Communications (2020)
      https://github.com/deepmind/BEHRT

    Arquitectura:
      - Embedding de diagnóstico (aprendido)
      - Positional encoding por edad/timestamp
      - Segment embedding (tipo de evento: dx, med, cita)
      - Transformer encoder (6 layers, 8 heads)
      - Classification head para next-diagnosis prediction

    Input: secuencia de códigos + edades + tipos
    Output: probabilidad de cada diagnóstico futuro
    """

    def __init__(self, vocab_size: int = 500, hidden_size: int = 256,
                 n_layers: int = 4, n_heads: int = 8, max_seq_len: int = 128,
                 n_segments: int = 4):
        super().__init__()

        self.token_embed = nn.Embedding(vocab_size, hidden_size, padding_idx=0)
        self.age_embed = nn.Linear(1, hidden_size)
        self.segment_embed = nn.Embedding(n_segments, hidden_size)
        self.pos_embed = nn.Embedding(max_seq_len, hidden_size)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_size, nhead=n_heads,
            dim_feedforward=hidden_size * 4, dropout=0.1,
            batch_first=True
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
        self.cls_head = nn.Linear(hidden_size, vocab_size)

    def forward(self, token_ids, ages, segments, mask=None):
        """
        Args:
            token_ids: (batch, seq_len)  — códigos ICD-10 mapeados a índices
            ages:      (batch, seq_len, 1) — edad en cada evento
            segments:  (batch, seq_len)  — 0=dx, 1=med, 2=cita, 3=síntoma
            mask:      (batch, seq_len)  — True donde hay padding
        """
        bsz, seq_len = token_ids.shape
        positions = torch.arange(seq_len, device=token_ids.device).unsqueeze(0).expand(bsz, -1)

        x = (self.token_embed(token_ids) +
             self.age_embed(ages.float()) +
             self.segment_embed(segments) +
             self.pos_embed(positions))

        if mask is not None:
            mask = ~mask  # TransformerEncoder espera False = atender

        encoded = self.encoder(x, src_key_padding_mask=mask)
        cls_output = encoded[:, -1, :]  # último token como resumen del paciente

        logits = self.cls_head(cls_output)
        return logits


class BEHRTPredictor:
    """
    Wrapper para usar BEHRT en predicción.

    Vocabulario: mapea códigos CIE-10 + medicamentos + síntomas → índices 2..N
    (índice 0 = padding, 1 = CLS token)
    """

    def __init__(self, model_path: Optional[str] = None):
        self.vocab: dict[str, int] = {"[PAD]": 0, "[CLS]": 1}
        self.inv_vocab: dict[int, str] = {0: "[PAD]", 1: "[CLS]"}
        self.model: Optional[BEHRTEncoder] = None
        self.segment_map = {"diagnostico": 0, "medicamento": 1, "cita": 2, "sintoma": 3}
        self._build_default_vocab()

        if model_path and HAS_TORCH:
            self.load(model_path)

    def _build_default_vocab(self):
        """Vocabulario inicial con códigos CIE-10 + medicamentos comunes."""
        from ai.ehr_simulator import CIE10_CATALOG
        for code in CIE10_CATALOG:
            self._add_token(code)
        for med in ["metformina_500mg", "losartan_50mg", "atorvastatina_20mg",
                     "amlodipino_5mg", "enalapril_10mg", "omeprazol_20mg",
                     "aspirina_100mg", "sulfato_ferroso_300mg"]:
            self._add_token(med)
        for sintoma in ["poliuria", "fatiga", "cefalea", "mareo"]:
            self._add_token(sintoma)

    def _add_token(self, token: str) -> int:
        if token not in self.vocab:
            idx = len(self.vocab)
            self.vocab[token] = idx
            self.inv_vocab[idx] = token
        return self.vocab[token]

    def tokenize(self, events: list[dict], max_len: int = 64) -> dict:
        """Convierte secuencia de eventos a tensores para BEHRT."""
        token_ids = []
        ages = []
        segments = []

        for e in events[-max_len:]:
            code = e.get("codigo", "[UNK]")
            if code not in self.vocab:
                self._add_token(code)
            token_ids.append(self.vocab[code])
            ages.append([min(float(e.get("edad_paciente", 45)) / 100.0, 1.0)])
            segments.append(self.segment_map.get(e.get("tipo", "diagnostico"), 0))

        # Padding
        while len(token_ids) < max_len:
            token_ids.append(0)
            ages.append([0.0])
            segments.append(0)

        return {
            "token_ids": torch.tensor([token_ids], dtype=torch.long),
            "ages": torch.tensor([ages], dtype=torch.float),
            "segments": torch.tensor([segments], dtype=torch.long),
        }

    def predict(self, events: list[dict], top_k: int = 5) -> dict:
        """Predice próximos diagnósticos probables."""
        if self.model is None or not HAS_TORCH:
            return self._fallback_predict(events, top_k)

        inputs = self.tokenize(events)
        with torch.no_grad():
            logits = self.model(**inputs)
            probs = torch.softmax(logits, dim=-1)[0]
            top_probs, top_indices = torch.topk(probs, min(top_k, len(probs)))

        return {
            "modelo": "BEHRT (implementación real)",
            "predicciones": [
                {"codigo": self.inv_vocab.get(idx.item(), "?"),
                 "probabilidad": round(prob.item(), 3)}
                for prob, idx in zip(top_probs, top_indices)
                if idx.item() > 1  # skip [PAD] and [CLS]
            ]
        }

    def _fallback_predict(self, events: list[dict], top_k: int = 5) -> dict:
        """Fallback heurístico cuando el modelo no está entrenado."""
        from ai.ehr_simulator import CIE10_CATALOG

        diagnosticos = {e.get("codigo") for e in events if e.get("tipo") == "diagnostico"}
        scores = {}

        reglas_progresion = {
            "E11": {"N18": 0.30, "I25": 0.20, "G47": 0.12},
            "I10": {"I25": 0.25, "N18": 0.18, "E11": 0.15},
            "E78": {"I25": 0.22},
            "E66": {"E11": 0.35, "I10": 0.25},
        }

        for dx in diagnosticos:
            for prox, prob in reglas_progresion.get(dx, {}).items():
                if prox not in diagnosticos:
                    scores[prox] = max(scores.get(prox, 0), prob)

        top = sorted(scores.items(), key=lambda x: -x[1])[:top_k]
        return {
            "modelo": "BEHRT (fallback — necesita entrenamiento con datos reales)",
            "input_eventos": len(events),
            "predicciones": [
                {"codigo": code, "nombre": CIE10_CATALOG.get(code, "?"),
                 "probabilidad": round(prob, 3)}
                for code, prob in top
            ],
            "status": "NO_ENTRENADO — requiere ≥5K pacientes con secuencias ICD-10",
        }

    def save(self, path: str):
        if self.model:
            torch.save({
                "model_state": self.model.state_dict(),
                "vocab": self.vocab,
                "inv_vocab": self.inv_vocab,
            }, path)

    def load(self, path: str):
        if not HAS_TORCH:
            raise ImportError("pip install torch")
        ckpt = torch.load(path, map_location="cpu")
        self.vocab = ckpt["vocab"]
        self.inv_vocab = ckpt["inv_vocab"]
        self.model = BEHRTEncoder(vocab_size=len(self.vocab))
        self.model.load_state_dict(ckpt["model_state"])
        self.model.eval()


# ══════════════════════════════════════════════════════════════════════════════
# Interfaz unificada (como health_models.py usa)
# ══════════════════════════════════════════════════════════════════════════════

def predict_risk(patient_data: dict,
                 model_type: str = "findrisc") -> dict:
    """
    Interfaz única de predicción. Swappea el modelo internamente.

    Args:
        patient_data: dict con al menos {'edad', 'sexo'} + opcionalmente {'eventos'}
        model_type:   "findrisc" | "xgboost" | "behrt"

    Returns:
        dict con predicción unificada
    """
    if model_type == "findrisc":
        return predict_findrisc(patient_data)

    elif model_type == "xgboost":
        eventos = patient_data.get("eventos", [])
        model_xgb = XGBoostRiskModel()
        return model_xgb.predict(patient_history=eventos)

    elif model_type == "behrt":
        eventos = patient_data.get("eventos", [])
        predictor = BEHRTPredictor()
        return predictor.predict(eventos)

    else:
        raise ValueError(f"Modelo desconocido: {model_type}. Usar: findrisc, xgboost, behrt")


# ─── Demo ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("PREDICT_RISK.PY — Demo de modelos de predicción")
    print("=" * 60)

    paciente_ejemplo = {
        "edad": "55_64", "sexo": "M", "imc": "25_30",
        "actividad_fisica": False, "frutas_verduras_diario": True,
        "medicacion_hipertension": True, "glucosa_alta_antes": False,
        "familiar_diabetes": "abuelo_tio_primo",
    }

    print("\n1. FINDRISC (en producción):")
    r = predict_risk(paciente_ejemplo, "findrisc")
    print(f"   Score: {r['score']}/26 — Riesgo: {r['nivel']}")
    print(f"   {r['riesgo_porcentaje']}")
    print(f"   Recomendación: {r['recomendacion']}")

    print("\n2. XGBoost (fallback — necesita datos):")
    r = predict_risk(paciente_ejemplo, "xgboost")
    print(f"   Probabilidad diabetes 12m: {r['probabilidad_diabetes_12m']:.1%}")
    print(f"   Features: {r['features_usadas']}")

    print("\n3. BEHRT (fallback — necesita ≥5K pacientes):")
    eventos_sinteticos = [
        {"codigo": "E11", "tipo": "diagnostico", "edad_paciente": 45, "fecha": "2024-03"},
        {"codigo": "I10", "tipo": "diagnostico", "edad_paciente": 46, "fecha": "2024-09"},
        {"codigo": "metformina_500mg", "tipo": "medicamento", "edad_paciente": 46, "fecha": "2024-10"},
    ]
    r = predict_risk({"eventos": eventos_sinteticos}, "behrt")
    print(f"   Modelo: {r['modelo']}")
    for p in r.get("predicciones", []):
        print(f"   {p.get('codigo')}: {p.get('probabilidad', 0):.1%} — {p.get('nombre', '')}")
    print(f"   Status: {r.get('status', '')}")

    print("\n" + "=" * 60)
    print("Roadmap:")
    print("  MVP:   FINDRISC (0 datos)")
    print("  Fase2: XGBoost (1K pacientes, 3 meses)")
    print("  Fase3: BEHRT   (5K pacientes, 6+ meses)")
    print("  Fase4: MOTOR   (10K pacientes, 12+ meses, FEMR)")
    print("=" * 60)
