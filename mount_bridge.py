"""
MONTAGE DE DISQUE AUTOMATIQUE — LIAISON COLAB ↔ GOOGLE CLOUD
Le chemin racine devient identique sur les deux machines.
Colab et Vertex AI lisent exactement la même chose au même moment.
Chemin unifié : /content/drive/racine
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Optional


# Chemin unifié — identique sur Colab ET sur Vertex AI après montage
CHEMIN_RACINE_UNIFIE = Path("/content/drive/racine")
CONFIG_CERVEAU       = "config_2000_points.json"
DOSSIER_MODELS       = "models"
DOSSIER_VITESSE      = "vitesse"
DOSSIER_INPUT        = "input"
FICHIER_DESCRIPTION  = "description_utilisateur.json"


class MontageDisque:
    """
    Système de montage automatique.
    Monte Google Drive sur Colab OU le bucket GCS sur Vertex AI.
    Le code voit toujours le même chemin : /content/drive/racine
    """

    def __init__(
        self,
        bucket_gcs: Optional[str] = None,
        google_project: Optional[str] = None,
    ):
        self.bucket_gcs     = bucket_gcs or os.environ.get("GCS_BUCKET", "")
        self.google_project = google_project or os.environ.get("GOOGLE_CLOUD_PROJECT", "")
        self.racine         = CHEMIN_RACINE_UNIFIE
        self.env            = self._detecter_env()
        self.monte          = False

    def _detecter_env(self) -> str:
        if os.environ.get("CLOUD_ML_PROJECT_ID"):
            return "vertex_ai"
        try:
            import google.colab
            return "colab"
        except ImportError:
            pass
        if Path("/content").exists():
            return "colab_like"
        return "local"

    # ── Montage Google Drive (Colab) ────────────────────────
    def _monter_google_drive(self) -> bool:
        try:
            from google.colab import drive
            drive.mount("/content/drive", force_remount=False)
            # Créer le lien symbolique vers la racine unifiée
            cible = Path("/content/drive/MyDrive/Master")
            cible.mkdir(parents=True, exist_ok=True)
            if not self.racine.exists():
                self.racine.parent.mkdir(parents=True, exist_ok=True)
                try:
                    self.racine.symlink_to(cible)
                except FileExistsError:
                    pass
            print(f"✅ Google Drive monté → {self.racine} → {cible}")
            return True
        except Exception as e:
            print(f"⚠️  Impossible de monter Google Drive : {e}")
            return False

    # ── Montage GCS via gcsfuse (Vertex AI / Cloud) ─────────
    def _monter_gcs(self) -> bool:
        if not self.bucket_gcs:
            print("⚠️  GCS_BUCKET non défini — montage GCS ignoré")
            return False
        try:
            self.racine.mkdir(parents=True, exist_ok=True)
            result = subprocess.run(
                ["gcsfuse", "--implicit-dirs", self.bucket_gcs, str(self.racine)],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                print(f"✅ GCS bucket '{self.bucket_gcs}' monté → {self.racine}")
                return True
            else:
                print(f"⚠️  gcsfuse erreur : {result.stderr}")
                return False
        except FileNotFoundError:
            print("⚠️  gcsfuse non installé — simulation du montage en local")
            self.racine.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"⚠️  Erreur GCS : {e}")
            return False

    # ── Montage local (dev / Replit) ────────────────────────
    def _monter_local(self) -> bool:
        local_master = Path("./Master")
        local_master.mkdir(parents=True, exist_ok=True)
        # Crée un chemin équivalent en local
        self.racine = local_master
        print(f"✅ Montage local → {self.racine.resolve()}")
        return True

    # ── Point d'entrée principal ────────────────────────────
    def monter(self) -> Path:
        """
        Monte le bon disque selon l'environnement.
        Retourne toujours le chemin racine unifié.
        """
        print(f"\n⚡ MONTAGE AUTOMATIQUE — Environnement : {self.env.upper()}")
        print("─" * 50)

        if self.env == "colab":
            self.monte = self._monter_google_drive()
        elif self.env == "vertex_ai":
            self.monte = self._monter_gcs()
        else:
            self.monte = self._monter_local()

        if self.monte:
            self._creer_structure()

        print(f"📂 Racine unifiée : {self.racine.resolve()}")
        print("─" * 50)
        return self.racine

    def _creer_structure(self):
        """Crée les sous-dossiers obligatoires à la racine."""
        for dossier in [DOSSIER_MODELS, DOSSIER_VITESSE, DOSSIER_INPUT, "cache"]:
            (self.racine / dossier).mkdir(parents=True, exist_ok=True)

    # ── Chemins publics ──────────────────────────────────────
    @property
    def chemin_cerveau(self) -> Path:
        return self.racine / CONFIG_CERVEAU

    @property
    def chemin_models(self) -> Path:
        return self.racine / DOSSIER_MODELS

    @property
    def chemin_vitesse(self) -> Path:
        return self.racine / DOSSIER_VITESSE

    @property
    def chemin_input(self) -> Path:
        return self.racine / DOSSIER_INPUT

    @property
    def chemin_description(self) -> Path:
        return self.racine / DOSSIER_INPUT / FICHIER_DESCRIPTION


class CerveauConfig:
    """
    Lit et applique le fichier config_2000_points.json depuis la racine.
    C'est le Cerveau : dès le démarrage, les 2000 points sont chargés.
    """

    def __init__(self, chemin_config: Path):
        self.chemin = chemin_config
        self._data  = None

    def charger(self) -> dict:
        """Charge le fichier Cerveau depuis la racine."""
        if self.chemin.exists():
            with open(self.chemin, "r", encoding="utf-8") as f:
                self._data = json.load(f)
            pts = self._data.get("_info", {}).get("total_points", "?")
            print(f"🧠 Cerveau chargé : {self.chemin} — {pts} points")
        else:
            # Copie le fichier depuis le dossier du script
            source = Path(__file__).parent / CONFIG_CERVEAU
            if source.exists():
                self.chemin.parent.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.copy2(source, self.chemin)
                with open(self.chemin, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
                print(f"🧠 Cerveau copié → {self.chemin}")
            else:
                print(f"⚠️  Cerveau introuvable : {self.chemin}")
                self._data = {}
        return self._data

    def extraire_overrides(self, scenario_key: str = None) -> dict:
        """
        Extrait les valeurs de surcharge pour un scénario donné.
        Retourne un dict {point_id: valeur} prêt pour la matrice.
        """
        if not self._data:
            self.charger()

        overrides = {}

        if scenario_key:
            scenarios = self._data.get("scenarios_predefined", {})
            scenario  = scenarios.get(scenario_key, {})
            sp        = scenario.get("surcharges_points", {})
            # Convertit les noms de groupe en plages de points
            overrides = _noms_vers_ids(sp, self._data)

        return overrides

    def obtenir_scenario(self, scenario_key: str) -> dict:
        if not self._data:
            self.charger()
        return self._data.get("scenarios_predefined", {}).get(scenario_key, {})


def _noms_vers_ids(surcharges_nommees: dict, config: dict) -> dict:
    """Convertit les noms de groupes en IDs de points numériques."""
    mapping = {
        "micro_vascularite":      range(1,   101),
        "muscles_tendons":        range(101, 201),
        "fluides":                range(201, 301),
        "friction":               range(301, 401),
        "masse_gravite":          range(401, 501),
        "aerodynamisme":          range(501, 601),
        "collision":              range(601, 701),
        "thermodynamique":        range(701, 801),
        "ray_tracing_4k":         range(801, 901),
        "caustiques":             range(901, 1001),
        "atmosphere":             range(1001, 1101),
        "micro_saccades":         range(1101, 1201),
        "proprioception":         range(1201, 1301),
        "hesitation":             range(1301, 1501),
        "capteur_arri_alexa":     range(1501, 1701),
        "espace_couleur_rec2020": range(1701, 1851),
        "optique_bokeh":          range(1851, 2001),
    }
    result = {}
    for nom, val in surcharges_nommees.items():
        ids = mapping.get(nom, [])
        for pid in ids:
            result[pid] = val
    return result


class DescriptionUtilisateur:
    """
    Écrit et lit le fichier description_utilisateur.json à la racine.
    Dès que l'utilisateur écrit son prompt, il est persisté ici.
    """

    def __init__(self, chemin: Path):
        self.chemin = chemin

    def ecrire(self, prompt: str, vehicule: str = None, meteo: str = None, lieu: str = None):
        """Écrit l'ordre utilisateur à la racine pour que le moteur le lise."""
        data = {
            "prompt":   prompt,
            "vehicule": vehicule or "",
            "meteo":    meteo or "",
            "lieu":     lieu or "",
        }
        self.chemin.parent.mkdir(parents=True, exist_ok=True)
        with open(self.chemin, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"📝 Description écrite → {self.chemin}")
        return data

    def lire(self) -> dict:
        """Lit l'ordre utilisateur depuis la racine."""
        if not self.chemin.exists():
            return {}
        with open(self.chemin, "r", encoding="utf-8") as f:
            return json.load(f)


def demarrer_systeme(bucket_gcs: str = None, project_id: str = None):
    """
    Fonction principale : monte le disque, charge le Cerveau,
    retourne tous les chemins et la config prête à l'emploi.
    """
    print("\n" + "═"*55)
    print("  ⚡ DÉMARRAGE SYSTÈME — RÉALITÉ TOTALE 2026")
    print("═"*55)

    # 1. Montage du disque
    montage = MontageDisque(bucket_gcs=bucket_gcs, google_project=project_id)
    racine  = montage.monter()

    # 2. Chargement du Cerveau (2000 points)
    cerveau = CerveauConfig(montage.chemin_cerveau)
    config  = cerveau.charger()

    # 3. Description utilisateur
    description = DescriptionUtilisateur(montage.chemin_description)

    print(f"\n✅ Système prêt !")
    print(f"   Racine      : {racine}")
    print(f"   Modèles     : {montage.chemin_models}")
    print(f"   Sortie 4K   : {montage.chemin_vitesse}")
    print(f"   Cerveau     : {montage.chemin_cerveau}")
    print(f"   Description : {montage.chemin_description}")
    print("═"*55 + "\n")

    return {
        "montage":     montage,
        "cerveau":     cerveau,
        "description": description,
        "racine":      racine,
        "config":      config,
        "chemins": {
            "racine":      str(racine),
            "models":      str(montage.chemin_models),
            "vitesse":     str(montage.chemin_vitesse),
            "input":       str(montage.chemin_input),
            "cerveau":     str(montage.chemin_cerveau),
            "description": str(montage.chemin_description),
        }
    }


if __name__ == "__main__":
    systeme = demarrer_systeme()
    print("Chemins actifs :")
    for k, v in systeme["chemins"].items():
        print(f"  {k}: {v}")
