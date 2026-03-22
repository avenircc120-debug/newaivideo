"""
STRUCTURE MAÎTRE — ORGANISATION À LA RACINE
Crée l'arborescence complète du projet au bon endroit selon l'environnement.
Tout centralisé en un seul point pour une liaison maximale.
"""

import os
import json
from pathlib import Path


# ─────────────────────────────────────────────────────────────
# CHEMINS DE LA RACINE SELON L'ENVIRONNEMENT
# ─────────────────────────────────────────────────────────────

def get_root_path() -> Path:
    """
    Retourne le chemin racine unifié selon l'environnement.
    Colab et Cloud lisent exactement le même chemin.
    """
    # Vertex AI / Google Cloud
    if os.environ.get("CLOUD_ML_PROJECT_ID"):
        return Path(os.environ.get("AIP_MODEL_DIR", "/gcs/master"))

    # Google Colab avec Google Drive monté
    colab_drive = Path("/content/drive/MyDrive/Master")
    if colab_drive.exists() or _is_colab():
        return colab_drive

    # GCS monté via gcsfuse (chemin unifié Colab + Cloud)
    gcs_mount = Path("/content/drive/racine")
    if gcs_mount.exists():
        return gcs_mount

    # Local / Replit
    return Path("./Master")


def _is_colab() -> bool:
    try:
        import google.colab
        return True
    except ImportError:
        return False


# ─────────────────────────────────────────────────────────────
# STRUCTURE DES DOSSIERS MAÎTRES
# ─────────────────────────────────────────────────────────────

MASTER_STRUCTURE = {
    "models": {
        "description": "Les 14 outils IA — préchargés, jamais re-téléchargés",
        "subdirs": [
            "01_wan2_svdxt",
            "02_ip_adapter_faceid_v2",
            "03_controlnet_openpose",
            "04_temporalnet",
            "05_vae_ft_mse",
            "06_codeformer",
            "07_real_esrgan",
            "08_freenoise",
            "09_deflicker",
            "10_film_grain_engine",
            "11_controlnet_depth",
            "12_controlnet_hed",
            "13_clip_interrogator",
            "14_generative_dynamics",
        ]
    },
    "vitesse": {
        "description": "Dossier de sortie — vidéos 4K accessibles immédiatement",
        "subdirs": []
    },
    "input": {
        "description": "Photos et descriptions de l'utilisateur",
        "subdirs": []
    },
    "cache": {
        "description": "Cache intermédiaire pour éviter les recalculs",
        "subdirs": ["embeddings", "frames", "upscaled"]
    },
}


def create_master_structure(root: Path = None) -> dict:
    """
    Crée l'arborescence complète à la racine.
    Retourne un dict avec tous les chemins créés.
    """
    if root is None:
        root = get_root_path()

    root.mkdir(parents=True, exist_ok=True)
    paths = {"root": str(root)}

    print(f"\n📁 STRUCTURE MAÎTRE → {root}")
    print("─" * 50)

    for folder, info in MASTER_STRUCTURE.items():
        folder_path = root / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        paths[folder] = str(folder_path)
        print(f"  ✅ /{folder}  — {info['description']}")

        for sub in info.get("subdirs", []):
            sub_path = folder_path / sub
            sub_path.mkdir(parents=True, exist_ok=True)
            print(f"       └─ {sub}/")

    # Fichier README de la structure
    readme = root / "STRUCTURE.txt"
    readme.write_text(
        "RÉALITÉ TOTALE 2026 — STRUCTURE MAÎTRE\n"
        "========================================\n"
        f"Racine : {root}\n\n"
        "/models/    → 14 outils IA préchargés (ne jamais supprimer)\n"
        "/vitesse/   → vidéos 4K générées (accessible téléphone)\n"
        "/input/     → vos photos + fichier de description\n"
        "/cache/     → cache intermédiaire (supprimable)\n"
        "\nCerveau : config_2000_points.json (à la racine)\n"
    )

    print("─" * 50)
    print(f"✅ Structure créée. Cerveau : {root}/config_2000_points.json")
    return paths


if __name__ == "__main__":
    p = create_master_structure()
    print("\nChemins créés :")
    for k, v in p.items():
        print(f"  {k}: {v}")
