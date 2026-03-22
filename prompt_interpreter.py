"""
INTERPRÉTEUR DE PROMPT — PROTOCOLE D'OBÉISSANCE ABSOLUE
Analyse le texte utilisateur et active les bons outils + points de la matrice.
"""

import re
from typing import Dict, List, Tuple


# ─────────────────────────────────────────────────────────────
# TABLE DE CORRESPONDANCE : mot-clé → outils activés + overrides
# ─────────────────────────────────────────────────────────────

KEYWORD_RULES = [
    # ── Météo ──────────────────────────────────────────────
    {
        "keywords": ["pluie", "il pleut", "mouillé", "pleuvoir", "orage"],
        "tools": [3, 14],
        "overrides": {
            **{i: 0.95 for i in range(201, 251)},  # Fluides – eau de pluie
            **{i: 0.85 for i in range(901, 951)},  # Caustiques – vitres mouillées
            **{i: 0.80 for i in range(1001, 1030)}, # Atmosphère – pluie
        },
        "label": "PLUIE"
    },
    {
        "keywords": ["soleil couchant", "coucher de soleil", "crépuscule", "soir", "soirée"],
        "tools": [13],
        "overrides": {
            **{i: 0.70 for i in range(701, 730)},   # Thermodynamique – chaleur du soir
            **{i: 0.90 for i in range(1101, 1130)}, # Micro-saccades – scanner foule
            **{i: 0.95 for i in range(1501, 1550)}, # Grain Arri – lumière dorée
        },
        "label": "SOLEIL_COUCHANT"
    },
    {
        "keywords": ["soleil", "plein soleil", "midi", "chaleur", "chaud"],
        "tools": [13, 5],
        "overrides": {
            **{i: 0.90 for i in range(1, 50)},      # Micro-vascularité – rougeur chaleur
            **{i: 0.85 for i in range(701, 750)},   # Thermodynamique – mirage fort
            **{i: 0.80 for i in range(1001, 1050)}, # Poussière soleil
        },
        "label": "PLEIN_SOLEIL"
    },
    {
        "keywords": ["nuit", "obscurité", "sombre", "nocturn"],
        "tools": [5, 6, 9],
        "overrides": {
            **{i: 0.95 for i in range(801, 850)},  # Ray-tracing – reflets nuit
            **{i: 0.30 for i in range(1001, 1050)},# Peu de poussière
        },
        "label": "NUIT"
    },

    # ── Véhicules ──────────────────────────────────────────
    {
        "keywords": ["voiture", "véhicule", "auto", "bagnole", "zémidjan", "zemidjan"],
        "tools": [1, 2, 3, 4, 11],
        "overrides": {
            **{i: 0.85 for i in range(401, 451)},  # Masse/gravité siège
            **{i: 0.60 for i in range(501, 551)},  # Aérodynamisme modéré
            **{i: 1.00 for i in range(601, 651)},  # Collision mains volant
        },
        "label": "VOITURE"
    },
    {
        "keywords": ["moto", "motocyclette", "guidon", "deux-roues"],
        "tools": [1, 2, 3, 4, 12],
        "overrides": {
            **{i: 0.90 for i in range(401, 451)},  # Masse/gravité selle
            **{i: 0.75 for i in range(101, 151)},  # Muscles – tension guidon
            **{i: 1.00 for i in range(601, 651)},  # Collision pieds au sol
        },
        "label": "MOTO"
    },

    # ── Vitesse ────────────────────────────────────────────
    {
        "keywords": ["120 km", "vitesse", "rapide", "vite", "accélère"],
        "tools": [1, 12],
        "overrides": {
            **{i: 0.95 for i in range(501, 601)},  # Aérodynamisme max
            **{i: 0.90 for i in range(301, 401)},  # Cheveux violents
            **{i: 0.85 for i in range(101, 151)},  # Muscles faciaux – vent fort
        },
        "label": "HAUTE_VITESSE"
    },

    # ── Actions / Postures ─────────────────────────────────
    {
        "keywords": ["marche", "marchant", "marcher", "je marche", "piéton"],
        "tools": [3],
        "overrides": {
            **{i: 0.60 for i in range(1201, 1251)}, # Proprioception – équilibre marche
            **{i: 0.50 for i in range(1301, 1351)}, # Hésitation – pas naturels
        },
        "label": "MARCHE"
    },
    {
        "keywords": ["monte", "monter", "enjambe", "s'asseoir", "entrer dans"],
        "tools": [3],
        "overrides": {
            **{i: 0.80 for i in range(101, 151)},  # Muscles – effort montée
            **{i: 0.70 for i in range(1201, 1251)}, # Équilibre
        },
        "label": "MONTEE_VEHICULE"
    },

    # ── Lieux – Bénin ──────────────────────────────────────
    {
        "keywords": ["cotonou", "bénin", "benin", "foire", "indépendance", "porto-novo", "abomey"],
        "tools": [5, 13],
        "overrides": {
            **{i: 0.90 for i in range(1, 50)},     # Micro-vascularité – peau locale
            **{i: 0.85 for i in range(1701, 1750)},# REC.2020 – couleurs réelles Bénin
            **{i: 0.70 for i in range(1001, 1050)},# Poussière locale
        },
        "label": "BENIN"
    },
    {
        "keywords": ["foule", "marché", "gens", "monde", "animation"],
        "tools": [3, 13, 14],
        "overrides": {
            **{i: 0.75 for i in range(1101, 1150)}, # Micro-saccades – scanner foule
            **{i: 0.60 for i in range(1301, 1401)}, # Hésitation – navigation foule
        },
        "label": "FOULE"
    },

    # ── Sueur / Effort ─────────────────────────────────────
    {
        "keywords": ["sueur", "transpire", "effort", "sport", "fatigue"],
        "tools": [5, 6],
        "overrides": {
            **{i: 0.90 for i in range(1, 101)},    # Micro-vascularité max
            **{i: 0.95 for i in range(201, 251)},  # Fluides – sueur
        },
        "label": "SUEUR"
    },

    # ── Vent ───────────────────────────────────────────────
    {
        "keywords": ["vent", "souffle", "brise", "air"],
        "tools": [12],
        "overrides": {
            **{i: 0.80 for i in range(301, 401)},  # Friction cheveux / vent
            **{i: 0.70 for i in range(501, 551)},  # Aérodynamisme vêtements
        },
        "label": "VENT"
    },
]


def interpret_user_order(user_text: str) -> Dict:
    """
    Analyse le texte de l'utilisateur et retourne:
    - tools_activated : liste des IDs d'outils à activer (1-14)
    - point_overrides : dict {point_id: valeur} à injecter dans la matrice
    - scene_labels   : liste des scènes détectées (pour le log)
    - enriched_prompt: prompt enrichi avec les annotations techniques
    """
    text_lower = user_text.lower()

    tools_activated: set = set()
    point_overrides: dict = {}
    scene_labels: list = []

    for rule in KEYWORD_RULES:
        matched = any(kw in text_lower for kw in rule["keywords"])
        if matched:
            scene_labels.append(rule["label"])
            for t in rule["tools"]:
                tools_activated.add(t)
            for pid, val in rule["overrides"].items():
                # Prend la valeur maximale si plusieurs règles touchent le même point
                point_overrides[pid] = max(point_overrides.get(pid, 0.0), val)

    # Toujours activer les outils de base
    tools_activated.update([2, 6, 7, 8, 9, 10])  # IP-Adapter, CodeFormer, ESRGAN, FreeNoise, Deflicker, FilmGrain

    # Construire le prompt enrichi
    annotations = []
    if scene_labels:
        annotations.append(f"[SCÈNES: {', '.join(scene_labels)}]")
        annotations.append(f"[OUTILS ACTIFS: {sorted(tools_activated)}]")
        annotations.append(f"[POINTS FORCÉS: {len(point_overrides)}]")

    enriched_prompt = user_text
    if annotations:
        enriched_prompt = user_text + " | " + " | ".join(annotations)

    result = {
        "original_prompt": user_text,
        "enriched_prompt": enriched_prompt,
        "tools_activated": sorted(tools_activated),
        "point_overrides": point_overrides,
        "scene_labels": scene_labels,
        "total_overrides": len(point_overrides),
    }

    return result


def print_order_summary(order: Dict):
    print("\n" + "="*60)
    print("ANALYSE DU PROMPT UTILISATEUR")
    print("="*60)
    print(f"Prompt original : {order['original_prompt']}")
    print(f"Scènes détectées : {', '.join(order['scene_labels']) or 'Aucune'}")
    print(f"Outils activés  : {order['tools_activated']}")
    print(f"Points forcés   : {order['total_overrides']}/2000")
    print("="*60)


if __name__ == "__main__":
    tests = [
        "Moi, marchant à la foire de l'indépendance de Cotonou, au soleil couchant.",
        "Moi, montant dans une voiture zémidjan, il pleut beaucoup.",
        "Moi, en voiture à 120 km/h, le vent tape mon visage.",
    ]
    for t in tests:
        order = interpret_user_order(t)
        print_order_summary(order)
