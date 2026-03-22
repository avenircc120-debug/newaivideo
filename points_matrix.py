"""
DICTIONNAIRE COMPLET DES 2000 POINTS - RÉALITÉ TOTALE 2026
Matrice de variables injectées dans le pipeline IA à chaque seconde.
"""

def build_2000_points_matrix(overrides: dict = None) -> dict:
    """
    Construit la matrice complète des 2000 points de contrôle.
    Chaque point est un dictionnaire avec: valeur par défaut, plage min/max, description.
    overrides: dict de {point_id: valeur} pour forcer certains points depuis le prompt.
    """

    matrix = {}

    # ─────────────────────────────────────────────
    # A. SYSTÈME BIOLOGIE (Points 1–400)
    # ─────────────────────────────────────────────

    # Micro-vascularité (1–100) : couleur de peau selon effort/chaleur
    for i in range(1, 101):
        matrix[i] = {
            "name": f"micro_vascularite_{i}",
            "group": "biologie.micro_vascularite",
            "value": 0.5,
            "min": 0.0,
            "max": 1.0,
            "description": f"Changement de couleur de peau point {i} (effort/chaleur)"
        }

    # Muscles et Tendons (101–200) : tension des mains sur volant/guidon
    for i in range(101, 201):
        matrix[i] = {
            "name": f"muscle_tendon_{i}",
            "group": "biologie.muscles_tendons",
            "value": 0.3,
            "min": 0.0,
            "max": 1.0,
            "description": f"Tension musculaire/tendineuse point {i}"
        }

    # Fluides (201–300) : sueur réelle, éclat humide des yeux
    for i in range(201, 301):
        matrix[i] = {
            "name": f"fluide_{i}",
            "group": "biologie.fluides",
            "value": 0.2,
            "min": 0.0,
            "max": 1.0,
            "description": f"Fluide corporel (sueur/humidité) point {i}"
        }

    # Friction (301–400) : cheveux qui s'emmêlent avec le vent
    for i in range(301, 401):
        matrix[i] = {
            "name": f"friction_{i}",
            "group": "biologie.friction",
            "value": 0.4,
            "min": 0.0,
            "max": 1.0,
            "description": f"Friction cheveux/peau/vent point {i}"
        }

    # ─────────────────────────────────────────────
    # B. SYSTÈME PHYSIQUE ET VÉHICULES (Points 401–800)
    # ─────────────────────────────────────────────

    # Masse et Gravité (401–500) : siège/selle qui s'écrase sous le poids
    for i in range(401, 501):
        matrix[i] = {
            "name": f"masse_gravite_{i}",
            "group": "physique.masse_gravite",
            "value": 0.7,
            "min": 0.0,
            "max": 1.0,
            "description": f"Masse/gravité sur siège ou selle point {i}"
        }

    # Aérodynamisme (501–600) : habits qui se plaquent avec la vitesse
    for i in range(501, 601):
        matrix[i] = {
            "name": f"aerodynamisme_{i}",
            "group": "physique.aerodynamisme",
            "value": 0.0,
            "min": 0.0,
            "max": 1.0,
            "description": f"Aérodynamisme/pression d'air sur vêtements point {i}"
        }

    # Collision (601–700) : pas de traversée d'objets
    for i in range(601, 701):
        matrix[i] = {
            "name": f"collision_{i}",
            "group": "physique.collision",
            "value": 1.0,
            "min": 0.0,
            "max": 1.0,
            "description": f"Contrainte de collision physique point {i}"
        }

    # Thermodynamique (701–800) : mirage de chaleur au-dessus du moteur
    for i in range(701, 801):
        matrix[i] = {
            "name": f"thermodynamique_{i}",
            "group": "physique.thermodynamique",
            "value": 0.3,
            "min": 0.0,
            "max": 1.0,
            "description": f"Effet thermique (mirage/chaleur moteur) point {i}"
        }

    # ─────────────────────────────────────────────
    # C. SYSTÈME OPTIQUE (Points 801–1100)
    # ─────────────────────────────────────────────

    # Ray-Tracing 4K (801–900) : reflets dans les yeux et sur la peinture
    for i in range(801, 901):
        matrix[i] = {
            "name": f"ray_tracing_{i}",
            "group": "optique.ray_tracing",
            "value": 0.9,
            "min": 0.0,
            "max": 1.0,
            "description": f"Ray-tracing 4K – reflets environnement point {i}"
        }

    # Caustiques (901–1000) : lumière à travers les vitres/visière
    for i in range(901, 1001):
        matrix[i] = {
            "name": f"caustique_{i}",
            "group": "optique.caustiques",
            "value": 0.5,
            "min": 0.0,
            "max": 1.0,
            "description": f"Caustiques lumineuses (verre/eau) point {i}"
        }

    # Atmosphère (1001–1100) : poussière éclairée par le soleil
    for i in range(1001, 1101):
        matrix[i] = {
            "name": f"atmosphere_{i}",
            "group": "optique.atmosphere",
            "value": 0.4,
            "min": 0.0,
            "max": 1.0,
            "description": f"Particules atmosphériques (poussière/soleil) point {i}"
        }

    # ─────────────────────────────────────────────
    # D. SYSTÈME COGNITION (Points 1101–1500)
    # ─────────────────────────────────────────────

    # Micro-saccades (1101–1200) : yeux qui scannent la route
    for i in range(1101, 1201):
        matrix[i] = {
            "name": f"micro_saccade_{i}",
            "group": "cognition.micro_saccades",
            "value": 0.6,
            "min": 0.0,
            "max": 1.0,
            "description": f"Micro-saccades oculaires point {i}"
        }

    # Proprioception (1201–1300) : équilibre dans les virages
    for i in range(1201, 1301):
        matrix[i] = {
            "name": f"proprioception_{i}",
            "group": "cognition.proprioception",
            "value": 0.5,
            "min": 0.0,
            "max": 1.0,
            "description": f"Proprioception/équilibre corporel point {i}"
        }

    # Hésitation (1301–1500) : micro-mouvements humains 0.2s
    for i in range(1301, 1501):
        matrix[i] = {
            "name": f"hesitation_{i}",
            "group": "cognition.hesitation",
            "value": 0.2,
            "min": 0.0,
            "max": 1.0,
            "description": f"Hésitation/micro-mouvement humain 0.2s point {i}"
        }

    # ─────────────────────────────────────────────
    # E. SYSTÈME CINÉMA (Points 1501–2000)
    # ─────────────────────────────────────────────

    # Capteur Arri Alexa (1501–1700) : grain argentique
    for i in range(1501, 1701):
        matrix[i] = {
            "name": f"capteur_arri_{i}",
            "group": "cinema.capteur",
            "value": 0.85,
            "min": 0.0,
            "max": 1.0,
            "description": f"Rendu capteur Arri Alexa / grain argentique point {i}"
        }

    # Espace Couleur REC.2020 HDR (1701–1850)
    for i in range(1701, 1851):
        matrix[i] = {
            "name": f"espace_couleur_{i}",
            "group": "cinema.espace_couleur",
            "value": 1.0,
            "min": 0.0,
            "max": 1.0,
            "description": f"Espace couleur REC.2020 HDR point {i}"
        }

    # Optique Bokeh / reflets de lentille (1851–2000)
    for i in range(1851, 2001):
        matrix[i] = {
            "name": f"optique_bokeh_{i}",
            "group": "cinema.optique",
            "value": 0.7,
            "min": 0.0,
            "max": 1.0,
            "description": f"Bokeh / reflets de lentille point {i}"
        }

    # Application des overrides (valeurs forcées par le prompt)
    if overrides:
        for point_id, val in overrides.items():
            if point_id in matrix:
                matrix[point_id]["value"] = max(
                    matrix[point_id]["min"],
                    min(matrix[point_id]["max"], val)
                )

    return matrix


def inject_2000_metadata(pipeline_params: dict, matrix: dict) -> dict:
    """
    Injecte les 2000 points de la matrice dans les paramètres du pipeline.
    Appelée à chaque seconde de génération pour forcer la cohérence.
    Retourne les paramètres enrichis.
    """
    enriched = dict(pipeline_params)

    groups = {}
    for pid, point in matrix.items():
        g = point["group"]
        if g not in groups:
            groups[g] = []
        groups[g].append(point["value"])

    def avg(lst):
        return sum(lst) / len(lst) if lst else 0.0

    # Biologie
    enriched["skin_vascular_intensity"]  = avg(groups.get("biologie.micro_vascularite", [0.5]))
    enriched["muscle_tension"]           = avg(groups.get("biologie.muscles_tendons", [0.3]))
    enriched["fluid_wetness"]            = avg(groups.get("biologie.fluides", [0.2]))
    enriched["hair_friction_wind"]       = avg(groups.get("biologie.friction", [0.4]))

    # Physique
    enriched["gravity_seat_deform"]      = avg(groups.get("physique.masse_gravite", [0.7]))
    enriched["aero_cloth_pressure"]      = avg(groups.get("physique.aerodynamisme", [0.0]))
    enriched["collision_constraint"]     = avg(groups.get("physique.collision", [1.0]))
    enriched["heat_shimmer_intensity"]   = avg(groups.get("physique.thermodynamique", [0.3]))

    # Optique
    enriched["ray_tracing_strength"]     = avg(groups.get("optique.ray_tracing", [0.9]))
    enriched["caustics_strength"]        = avg(groups.get("optique.caustiques", [0.5]))
    enriched["dust_particles_density"]   = avg(groups.get("optique.atmosphere", [0.4]))

    # Cognition
    enriched["eye_saccade_amplitude"]    = avg(groups.get("cognition.micro_saccades", [0.6]))
    enriched["body_balance_sway"]        = avg(groups.get("cognition.proprioception", [0.5]))
    enriched["micro_hesitation_weight"]  = avg(groups.get("cognition.hesitation", [0.2]))

    # Cinéma
    enriched["film_grain_intensity"]     = avg(groups.get("cinema.capteur", [0.85]))
    enriched["hdr_rec2020_strength"]     = avg(groups.get("cinema.espace_couleur", [1.0]))
    enriched["bokeh_lens_flare"]         = avg(groups.get("cinema.optique", [0.7]))

    enriched["total_points_injected"] = len(matrix)
    return enriched


if __name__ == "__main__":
    m = build_2000_points_matrix()
    print(f"Matrice construite : {len(m)} points")
    sample = inject_2000_metadata({}, m)
    print("Exemple de paramètres injectés :")
    for k, v in sample.items():
        print(f"  {k}: {v}")
