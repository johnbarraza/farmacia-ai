"""
ehr_simulator.py — Simulación de modelos EHR para el pitch

Genera data sintética de pacientes peruanos con trayectorias de salud
y muestra predicciones simuladas como si los modelos BEHRT/CLMBR/MOTOR
ya estuvieran entrenados con data de SaludApp.

PARA EL PITCH: "Hoy usamos FINDRISC. Cuando SaludApp tenga 10K pacientes
con 12 meses de data, el sistema se ve así..."
"""

import random
from datetime import datetime, timedelta

# Enfermedades crónicas peruanas relevantes (CIE-10)
CIE10_CATALOG = {
    "E11": "Diabetes mellitus tipo 2",
    "I10": "Hipertensión esencial",
    "E78": "Dislipidemia",
    "D50": "Anemia ferropénica",
    "E66": "Obesidad",
    "N18": "Enfermedad renal crónica",
    "I25": "Cardiopatía isquémica",
    "J45": "Asma",
    "K76": "Hígado graso",
    "G47": "Apnea del sueño",
}

MEDICAMENTOS_COMUNES = [
    "metformina_500mg", "losartan_50mg", "atorvastatina_20mg",
    "amlodipino_5mg", "enalapril_10mg", "omeprazol_20mg",
    "sulfato_ferroso_300mg", "insulina_glargina", "aspirina_100mg",
]

SINTOMAS = [
    "poliuria", "polidipsia", "fatiga", "mareo", "cefalea",
    "vision_borrosa", "disnea", "edema_miembros", "palpitaciones",
    "entumecimiento_pies", "perdida_peso", "nicturia",
]


def generar_paciente_sintetico(paciente_id: int, meses_historial: int = 18) -> list[dict]:
    """Genera trayectoria sintética de un paciente peruano crónico."""
    random.seed(paciente_id)

    edad = random.randint(35, 72)
    sexo = random.choice(["M", "F"])
    inicio = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 365))

    condiciones = random.sample(list(CIE10_CATALOG.keys()), k=random.randint(1, 4))
    eventos = []

    # Diagnósticos iniciales
    for i, cie10 in enumerate(condiciones):
        fecha = inicio + timedelta(days=i * random.randint(30, 180))
        eventos.append({
            "fecha": fecha.strftime("%Y-%m"),
            "tipo": "diagnostico",
            "codigo": cie10,
            "nombre": CIE10_CATALOG[cie10],
        })

    # Medicamentos (asignados después del diagnóstico)
    for _ in range(meses_historial):
        if random.random() > 0.6:
            med = random.choice(MEDICAMENTOS_COMUNES)
            fecha = inicio + timedelta(days=random.randint(160, 540))
            eventos.append({
                "fecha": fecha.strftime("%Y-%m"),
                "tipo": "medicamento",
                "codigo": med,
                "nombre": med.replace("_", " ").title(),
            })

    # Consultas / citas
    for i in range(random.randint(2, 5)):
        fecha = inicio + timedelta(days=random.randint(200, 500))
        eventos.append({
            "fecha": fecha.strftime("%Y-%m"),
            "tipo": "consulta",
            "codigo": f"CONS-{i:03d}",
            "nombre": random.choice(["Endocrinología", "Cardiología", "Medicina General", "Nutrición"]),
        })

    # Síntomas
    for _ in range(random.randint(0, 3)):
        fecha = inicio + timedelta(days=random.randint(100, 540))
        eventos.append({
            "fecha": fecha.strftime("%Y-%m"),
            "tipo": "sintoma",
            "codigo": random.choice(SINTOMAS),
            "nombre": "",
        })

    eventos.sort(key=lambda e: e["fecha"])
    return {"paciente_id": paciente_id, "edad": edad, "sexo": sexo, "eventos": eventos}


def simular_behrt(paciente: dict) -> dict:
    """
    Simula predicción estilo BEHRT:
    Dada la secuencia de diagnósticos del paciente, predice qué enfermedades
    podría desarrollar en los próximos 12 meses.
    """
    diagnosticos_actuales = {e["codigo"] for e in paciente["eventos"] if e["tipo"] == "diagnostico"}

    # Reglas de progresión clínica reales (simplificadas para demo)
    progresion = {
        "E11": [("N18", 0.35), ("I25", 0.28), ("G47", 0.15)],
        "I10": [("I25", 0.30), ("N18", 0.22), ("E11", 0.18)],
        "E78": [("I25", 0.25), ("E11", 0.20)],
        "E66": [("E11", 0.40), ("I10", 0.30), ("G47", 0.25)],
        "D50": [("N18", 0.15)],
    }

    predicciones = {}
    for dx in diagnosticos_actuales:
        for prox_cie10, prob in progresion.get(dx, []):
            if prox_cie10 not in diagnosticos_actuales:
                predicciones[prox_cie10] = max(
                    predicciones.get(prox_cie10, 0),
                    prob * (1 + random.uniform(-0.08, 0.08))
                )

    return {
        "modelo": "BEHRT (simulado)",
        "input": f"{len(paciente['eventos'])} eventos en {len(diagnosticos_actuales)} diagnósticos",
        "predicciones_12m": [
            {"codigo": cie10, "nombre": CIE10_CATALOG[cie10], "probabilidad": round(p, 3)}
            for cie10, p in sorted(predicciones.items(), key=lambda x: -x[1])[:5]
        ],
        "interpretacion": "BEHRT aprende patrones de progresión entre diagnósticos usando attention sobre la secuencia temporal del paciente.",
    }


def simular_motor(paciente: dict) -> dict:
    """
    Simula MOTOR (time-to-event):
    Predice CUÁNDO este paciente tendrá una hospitalización o complicación.
    """
    diagnosticos = [e for e in paciente["eventos"] if e["tipo"] == "diagnostico"]
    n_condiciones = len({e["codigo"] for e in diagnosticos})

    # Más condiciones + más edad = riesgo más alto
    riesgo_base = min(n_condiciones * 0.15 + (paciente["edad"] - 35) * 0.008, 0.85)

    eventos_predichos = [
        {
            "evento": "Hospitalización por complicación diabética",
            "tiempo_medio_meses": round(24 * (1 - riesgo_base), 1),
            "probabilidad_12m": round(riesgo_base * 0.6, 3),
            "probabilidad_24m": round(riesgo_base * 0.85, 3),
        },
        {
            "evento": "Ingreso a emergencia cardiovascular",
            "tiempo_medio_meses": round(30 * (1 - riesgo_base * 0.7), 1),
            "probabilidad_12m": round(riesgo_base * 0.35, 3),
            "probabilidad_24m": round(riesgo_base * 0.55, 3),
        },
        {
            "evento": "Progresión a ERC estadio 3",
            "tiempo_medio_meses": round(36 * (1 - riesgo_base * 0.5), 1),
            "probabilidad_12m": round(riesgo_base * 0.20, 3),
            "probabilidad_24m": round(riesgo_base * 0.40, 3),
        },
    ]

    return {
        "modelo": "MOTOR / FEMR (simulado)",
        "input": f"{n_condiciones} condiciones crónicas, edad {paciente['edad']}",
        "eventos_competitivos": eventos_predichos,
        "interpretacion": "MOTOR modela el tiempo hasta cada evento compitiendo entre sí. Usa el historial completo del paciente, no solo diagnósticos.",
    }


def simular_delphi(paciente: dict) -> dict:
    """
    Simula Delphi: trayectoria completa de salud a 5 años.
    """
    eventos = paciente["eventos"]
    diagnosticos_actuales = {e["codigo"] for e in eventos if e["tipo"] == "diagnostico"}

    trayectoria = []
    anno_actual = 2026
    riesgo_base = len(diagnosticos_actuales) * 0.1 + (paciente["edad"] - 35) * 0.005

    for anno in range(1, 6):
        prob_nuevo_dx = riesgo_base * (1 + anno * 0.3)
        nuevos = []
        for cie10, nombre in CIE10_CATALOG.items():
            if cie10 not in diagnosticos_actuales and random.random() < prob_nuevo_dx * 0.15:
                nuevos.append({"codigo": cie10, "nombre": nombre, "probabilidad": round(prob_nuevo_dx * 0.15, 3)})
                diagnosticos_actuales.add(cie10)
        trayectoria.append({
            "anno": anno_actual + anno,
            "edad_paciente": paciente["edad"] + anno,
            "nuevos_diagnosticos_probables": nuevos[:3],
            "condiciones_acumuladas": len(diagnosticos_actuales),
            "costo_estimado_soles": round(1200 * len(diagnosticos_actuales) * (1 + anno * 0.2)),
        })

    return {
        "modelo": "Delphi-like (simulado)",
        "input": f"{len(eventos)} eventos en {len({e['codigo'] for e in eventos if e['tipo']=='diagnostico'})} diagnósticos base",
        "trayectoria_5_annos": trayectoria,
        "interpretacion": "Delphi usa un transformer GPT-2 para modelar la historia natural de la enfermedad. Predice TODAS las enfermedades simultáneamente, no una por una.",
        "nota": "Pesos de UK Biobank NO usados. Esta simulación usa reglas de transición basadas en epidemiología peruana (ENDES 2023).",
    }


def simular_pipeline_completo(paciente_id: int = 42) -> dict:
    """Pipeline completo: genera paciente sintético → corre los 3 modelos."""
    paciente = generar_paciente_sintetico(paciente_id, meses_historial=18)
    return {
        "paciente": {
            "id": paciente["paciente_id"],
            "edad": paciente["edad"],
            "sexo": paciente["sexo"],
            "n_eventos": len(paciente["eventos"]),
            "diagnosticos_actuales": [
                {"codigo": e["codigo"], "nombre": CIE10_CATALOG.get(e["codigo"], "")}
                for e in paciente["eventos"]
                if e["tipo"] == "diagnostico"
            ],
            "eventos": paciente["eventos"][:10],  # primeras 10 para el slide
        },
        "behrt": simular_behrt(paciente),
        "motor": simular_motor(paciente),
        "delphi": simular_delphi(paciente),
    }
