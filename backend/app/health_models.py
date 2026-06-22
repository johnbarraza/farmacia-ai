"""
health_models.py — Modelos de riesgo de salud

ARQUITECTURA MODULAR — ROADMAP DE MODELOS EHR:
===============================================
La clase RiskModel define la interfaz de predicción.
Para hacer swap de modelo: solo cambiar el método assess() interno.
El endpoint FastAPI /riesgo NO cambia nunca.

FASE 1 — MVP 2026 (0 datos propios):
  FINDRISC (Finnish Diabetes Risk Score) — OMS/IDF validado en 40+ países
  8 preguntas → score 0-26 → 5 niveles de riesgo diabetes T2
  Sin datos de laboratorio, sin historial EHR.

FASE 2 — ~1K pacientes, 3+ meses de data:
  XGBoost / Cox Proportional Hazards sobre features acumulados
  (medicamentos, frecuencia de citas, historial FINDRISC)
  Baseline sólido, interpretable, fácil de validar clínicamente.

FASE 3 — ~5K pacientes, 6+ meses de data:
  BEHRT (Behavioral EHR Transformer) — secuencias ICD-10
    https://github.com/deepmind/BEHRT  (publicado Nature Comms 2020)
    Input: [E11 diabetes, I10 HTA, metformina, consulta, ...]
    Output: probabilidad de futuros diagnósticos
  O CLMBR dentro de FEMR — mejor representación de paciente
    https://github.com/som-shahlab/femr

FASE 4 — ~10K pacientes, 12+ meses de data:
  MOTOR (dentro de FEMR) — time-to-event modeling
    Predice CUÁNDO ocurrirá: hospitalización, complicación diabética, muerte
    FEMR usa OMOP-CDM: mapear CIE-10 peruano → OMOP concept_id primero
    https://github.com/som-shahlab/femr

FASE 5 — 100K+ pacientes:
  Delphi-like propio con datos peruanos
    Referencia: https://github.com/gerstung-lab/delphi (UK Biobank, no adaptar directo)
    Entrenado en UK Biobank (~400K) — sesgos europeos, no usar pesos directo en Peru
    Alternativa: replicar arquitectura GPT-2 de Delphi con data SaludApp Peru propia

ESTÁNDAR DE DATOS (para Fases 3-5):
  OMOP-CDM (Common Data Model) — ver handbook:
  https://github.com/youcc/healthcare_analytics_engineer_handbook
  patient_id | fecha_evento | codigo_cie10 | tipo_evento | sexo | fecha_nac

DATASETS ABIERTOS PERU para entrenamiento inicial:
  - SIS PNDA (atenciones oncológicas, diabetes, neonatal) — datos agregados
  - MINSA HIS (atenciones ambulatorias) — requiere solicitud institucional
  - ENDES (INEI) — encuesta salud a nivel individuo, no longitudinal
  NOTA: Datos de salud sensibles → Ley 29733 + anonimización obligatoria
"""

from dataclasses import dataclass
from typing import Literal


@dataclass
class FindriscInput:
    edad: Literal["menor_45", "45_54", "55_64", "mayor_64"]
    imc: Literal["menor_25", "25_30", "mayor_30"]
    cintura_hombre: Literal["menor_94", "94_102", "mayor_102"] | None = None
    cintura_mujer: Literal["menor_80", "80_88", "mayor_88"] | None = None
    sexo: Literal["M", "F"] = "M"
    actividad_fisica: bool = True
    frutas_verduras_diario: bool = True
    medicacion_hipertension: bool = False
    glucosa_alta_antes: bool = False
    familiar_diabetes: Literal["ninguno", "abuelo_tio_primo", "padre_hermano_hijo"] = "ninguno"


@dataclass
class RiskResult:
    score: int
    nivel: str
    riesgo_porcentaje: str
    color: str
    recomendacion: str
    siguiente_paso: str
    # Slot para futura predicción Delphi
    delphi_disponible: bool = False
    delphi_probabilidad_12m: float | None = None


class RiskModel:
    """
    Interfaz de predicción de riesgo crónico.

    Para hacer el swap a Delphi:
        1. Crear método _score_delphi(patient_history: list[dict]) -> RiskResult
        2. Reemplazar la llamada en assess() según el tipo de input
        3. El endpoint /riesgo no cambia.
    """

    def assess(self, data: FindriscInput) -> RiskResult:
        return self._score_findrisc(data)

    def _score_findrisc(self, d: FindriscInput) -> RiskResult:
        score = 0

        # Edad
        age_map = {"menor_45": 0, "45_54": 2, "55_64": 3, "mayor_64": 4}
        score += age_map.get(d.edad, 0)

        # IMC
        imc_map = {"menor_25": 0, "25_30": 1, "mayor_30": 3}
        score += imc_map.get(d.imc, 0)

        # Circunferencia cintura (depende del sexo)
        if d.sexo == "M" and d.cintura_hombre:
            cin_map = {"menor_94": 0, "94_102": 3, "mayor_102": 4}
            score += cin_map.get(d.cintura_hombre, 0)
        elif d.sexo == "F" and d.cintura_mujer:
            cin_map = {"menor_80": 0, "80_88": 3, "mayor_88": 4}
            score += cin_map.get(d.cintura_mujer, 0)

        # Actividad física (≥30 min/día)
        if not d.actividad_fisica:
            score += 2

        # Frutas/verduras diario
        if not d.frutas_verduras_diario:
            score += 1

        # Medicación hipertensión
        if d.medicacion_hipertension:
            score += 2

        # Glucosa alta anteriormente
        if d.glucosa_alta_antes:
            score += 5

        # Familiar con diabetes
        familiar_map = {"ninguno": 0, "abuelo_tio_primo": 3, "padre_hermano_hijo": 5}
        score += familiar_map.get(d.familiar_diabetes, 0)

        return self._score_to_result(score)

    @staticmethod
    def _score_to_result(score: int) -> RiskResult:
        if score <= 7:
            return RiskResult(
                score=score, nivel="Bajo", color="#2ecc71",
                riesgo_porcentaje="1 de cada 100 personas desarrollará diabetes",
                recomendacion="Mantén tu estilo de vida saludable. Continúa con actividad física regular y dieta balanceada.",
                siguiente_paso="Control rutinario anual con tu médico."
            )
        elif score <= 11:
            return RiskResult(
                score=score, nivel="Ligeramente elevado", color="#f39c12",
                riesgo_porcentaje="1 de cada 25 personas desarrollará diabetes",
                recomendacion="Considera mejorar tu alimentación: reduce azúcares, aumenta frutas y verduras. Haz al menos 30 min de caminata diaria.",
                siguiente_paso="Solicita una glucosa en ayunas en tu próxima visita médica."
            )
        elif score <= 14:
            return RiskResult(
                score=score, nivel="Moderado", color="#e67e22",
                riesgo_porcentaje="1 de cada 6 personas desarrollará diabetes",
                recomendacion="Tu riesgo es significativo. Prioriza reducir peso si tienes sobrepeso y aumentar actividad física.",
                siguiente_paso="Agenda una cita médica este mes para solicitar glicemia en ayunas y HbA1c."
            )
        elif score <= 20:
            return RiskResult(
                score=score, nivel="Alto", color="#e74c3c",
                riesgo_porcentaje="1 de cada 3 personas desarrollará diabetes",
                recomendacion="Riesgo alto detectado. Cambios de estilo de vida urgentes: dieta estricta, ejercicio diario, reducción de peso.",
                siguiente_paso="Consulta médica URGENTE. Solicitar perfil glucémico completo (glicemia, HbA1c, insulina)."
            )
        else:
            return RiskResult(
                score=score, nivel="Muy alto", color="#c0392b",
                riesgo_porcentaje="1 de cada 2 personas desarrollará diabetes",
                recomendacion="Riesgo muy alto. Es muy probable que ya tengas pre-diabetes o diabetes no diagnosticada.",
                siguiente_paso="Consulta médica INMEDIATA. Evaluación completa de diabetes y complicaciones."
            )

    # ─── SLOT PARA DELPHI (implementar en 2027) ──────────────────────────────
    def _score_delphi(self, patient_history: list[dict]) -> RiskResult:
        """
        Futuro: transformer Delphi entrenado en datos longitudinales de SaludApp Peru.

        patient_history: lista de eventos ordenados cronológicamente
            [{"tipo": "medicamento", "nombre": "metformina_500mg", "fecha": "2026-01-15"},
             {"tipo": "sintoma", "nombre": "poliuria", "fecha": "2026-02-03"},
             {"tipo": "cita", "especialidad": "endocrinologia", "fecha": "2026-02-10"}]

        Devuelve probabilidad de desarrollar diabetes T2, HTA, anemia en 12 meses.
        """
        raise NotImplementedError(
            "Delphi Peru aún no está disponible. "
            "Se implementará cuando SaludApp tenga 10K+ pacientes con 12+ meses de data. "
            "Ver docs/PLANNING.md sección 7 para detalles de integración."
        )
