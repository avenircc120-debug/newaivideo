"""
GRANDE CHOSE — RÉALITÉ TOTALE 2026
Point d'entrée principal.
Usage : python main.py --photo ma_photo.jpg --prompt "Mon prompt ici"
"""

import os
import sys
import argparse
from pathlib import Path
from PIL import Image

from cloud_bridge import auto_connect
from prompt_interpreter import interpret_user_order, print_order_summary
from points_matrix import build_2000_points_matrix
from pipeline import RealityPipeline


def parse_args():
    parser = argparse.ArgumentParser(
        description="Réalité Totale 2026 — Génération vidéo IA 4K avec 2000 points"
    )
    parser.add_argument(
        "--photo", type=str, required=True,
        help="Chemin vers votre photo (visage)"
    )
    parser.add_argument(
        "--prompt", type=str, required=True,
        help="Description de la scène à générer"
    )
    parser.add_argument(
        "--output", type=str, default="./output",
        help="Dossier de sortie de la vidéo (défaut: ./output)"
    )
    parser.add_argument(
        "--frames", type=int, default=120,
        help="Nombre de frames à générer (défaut: 120 = ~5s à 24fps)"
    )
    parser.add_argument(
        "--fps", type=int, default=24,
        help="Frames par seconde (défaut: 24)"
    )
    parser.add_argument(
        "--resolution", type=str, default="4K",
        choices=["4K", "1080p", "720p"],
        help="Résolution de sortie (défaut: 4K)"
    )
    parser.add_argument(
        "--project", type=str, default=None,
        help="ID du projet Google Cloud (pour Vertex AI)"
    )
    return parser.parse_args()


RESOLUTIONS = {
    "4K":    (3840, 2160),
    "1080p": (1920, 1080),
    "720p":  (1280,  720),
}


def main():
    print("\n" + "█"*60)
    print("█   RÉALITÉ TOTALE 2026 — LA GRANDE CHOSE              █")
    print("█   Powered by 14 outils IA + 2000 points de contrôle  █")
    print("█"*60 + "\n")

    args = parse_args()

    # ─── Vérification de la photo ───────────────────────────
    photo_path = Path(args.photo)
    if not photo_path.exists():
        print(f"❌ Erreur : photo introuvable : {photo_path}")
        sys.exit(1)

    try:
        face_image = Image.open(photo_path).convert("RGB")
        print(f"✅ Photo chargée : {photo_path} ({face_image.size[0]}×{face_image.size[1]})")
    except Exception as e:
        print(f"❌ Erreur lecture photo : {e}")
        sys.exit(1)

    # ─── 1. PONT CLOUD (Colab ↔ Vertex AI) ─────────────────
    bridge = auto_connect(project_id=args.project)
    cloud_config = bridge.switch_to_cloud(
        face_image_path=str(photo_path),
        prompt=args.prompt
    )
    compute = cloud_config["compute_params"]
    print(f"\n🚀 Puissance × {cloud_config['power_factor']} | GPU : {cloud_config['gpu']}")

    # ─── 2. INTERPRÉTATION DU PROMPT ────────────────────────
    print("\n⚙️  Analyse du prompt utilisateur...")
    order = interpret_user_order(args.prompt)
    print_order_summary(order)

    # ─── 3. CONSTRUCTION DE LA MATRICE 2000 POINTS ──────────
    print("\n⚙️  Construction de la matrice 2000 points...")
    matrix = build_2000_points_matrix(overrides=order["point_overrides"])
    print(f"✅ Matrice prête : {len(matrix)} points configurés")
    print(f"   Points forcés par le prompt : {order['total_overrides']}")

    # ─── 4. LANCEMENT DU PIPELINE EN CASCADE ────────────────
    resolution = RESOLUTIONS[args.resolution]
    print(f"\n🎬 Lancement pipeline 14 outils | {args.resolution} {resolution[0]}×{resolution[1]}...")

    # Barre de progression console
    def on_progress(step, total, msg):
        bar = "█" * step + "░" * (total - step)
        print(f"  [{bar}] {step}/{total}", end="\r")

    runner = RealityPipeline(
        face_image      = face_image,
        prompt          = order["enriched_prompt"],
        tools_activated = order["tools_activated"],
        matrix          = matrix,
        output_dir      = args.output,
        resolution      = resolution,
        num_frames      = args.frames,
        fps             = args.fps,
        use_gpu         = cloud_config["has_gpu"] if "has_gpu" in cloud_config else True,
        on_progress     = on_progress,
    )

    result = runner.run()

    # ─── 5. RAPPORT FINAL ────────────────────────────────────
    print("\n\n" + "█"*60)
    if result["success"]:
        print("█   ✅ GÉNÉRATION RÉUSSIE !")
        print(f"█   Durée       : {result['elapsed_seconds']:.1f} secondes")
        print(f"█   Sortie      : {result['output_dir']}/video_finale.mp4")
        print(f"█   Outils      : {len(result['tools_ran'])} actifs sur 14")
        print(f"█   Points IA   : {result['final_params'].get('total_points_injected', 0)}/2000 injectés")
    else:
        print("█   ❌ Échec de la génération")
    print("█"*60 + "\n")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
