"""
PONT AUTOMATIQUE COLAB ↔ GOOGLE CLOUD (VERTEX AI)
Détecte l'environnement et bascule automatiquement sur les GPU A100 du Cloud.
"""

import os
import sys
import subprocess
from typing import Optional


def is_colab() -> bool:
    """Détecte si on tourne dans Google Colab."""
    try:
        import google.colab
        return True
    except ImportError:
        return False


def is_vertex_ai() -> bool:
    """Détecte si on tourne dans Vertex AI (Google Cloud)."""
    return os.environ.get("CLOUD_ML_PROJECT_ID") is not None or \
           os.environ.get("VERTEX_AI_ENDPOINT") is not None


def has_gpu() -> bool:
    """Vérifie si un GPU est disponible."""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def get_gpu_name() -> str:
    """Retourne le nom du GPU disponible."""
    try:
        import torch
        if torch.cuda.is_available():
            return torch.cuda.get_device_name(0)
        return "Aucun GPU"
    except ImportError:
        return "PyTorch non installé"


def detect_environment() -> dict:
    """
    Détecte l'environnement d'exécution actuel.
    Retourne un dict avec les informations de contexte.
    """
    env = {
        "is_colab":     is_colab(),
        "is_vertex":    is_vertex_ai(),
        "has_gpu":      has_gpu(),
        "gpu_name":     get_gpu_name(),
        "environment":  "unknown",
        "power_factor": 1,
    }

    if env["is_vertex"]:
        env["environment"] = "vertex_ai"
        env["power_factor"] = 10  # ×10 plus puissant
        if "A100" in env["gpu_name"]:
            env["power_factor"] = 12
        elif "V100" in env["gpu_name"]:
            env["power_factor"] = 8
    elif env["is_colab"]:
        env["environment"] = "colab"
        if "A100" in env["gpu_name"]:
            env["power_factor"] = 6
        elif "T4" in env["gpu_name"]:
            env["power_factor"] = 3
        else:
            env["power_factor"] = 2
    elif env["has_gpu"]:
        env["environment"] = "local_gpu"
        env["power_factor"] = 4
    else:
        env["environment"] = "cpu_only"
        env["power_factor"] = 1

    return env


class CloudBridge:
    """
    Pont automatique entre Colab (tests) et Vertex AI (production).
    Gère la bascule transparente et l'optimisation selon l'environnement.
    """

    def __init__(self, project_id: Optional[str] = None, region: str = "us-central1"):
        self.project_id  = project_id or os.environ.get("GOOGLE_CLOUD_PROJECT", "")
        self.region      = region
        self.env         = detect_environment()
        self._print_banner()

    def _print_banner(self):
        env_name = {
            "vertex_ai":  "☁️  GOOGLE VERTEX AI (GPU A100) — PUISSANCE ×" + str(self.env["power_factor"]),
            "colab":      "🔬 GOOGLE COLAB — PUISSANCE ×" + str(self.env["power_factor"]),
            "local_gpu":  "💻 GPU LOCAL — PUISSANCE ×" + str(self.env["power_factor"]),
            "cpu_only":   "⚠️  CPU SEULEMENT — Lent (branchez un GPU pour accélérer)",
        }.get(self.env["environment"], "❓ Environnement inconnu")

        print("\n" + "─"*60)
        print(f"  PONT CLOUD ACTIF : {env_name}")
        print(f"  GPU détecté     : {self.env['gpu_name']}")
        print("─"*60)

    def get_compute_params(self) -> dict:
        """
        Retourne les paramètres de calcul optimisés selon l'environnement.
        Sur Vertex AI, multiplié par 10 pour les 2000 points en 4K.
        """
        pf = self.env["power_factor"]

        base = {
            "num_inference_steps":  25,
            "batch_size":           1,
            "precision":            "fp32",
            "xformers_enabled":     False,
            "cpu_offload":          True,
            "tile_size":            512,
            "max_frames_per_batch": 8,
            "workers":              2,
        }

        if self.env["environment"] == "vertex_ai":
            return {
                **base,
                "num_inference_steps":   50 * pf // 10,
                "batch_size":            4,
                "precision":             "bf16",
                "xformers_enabled":      True,
                "cpu_offload":           False,
                "tile_size":             1024,
                "max_frames_per_batch":  32 * pf // 10,
                "workers":               8,
                "a100_flash_attention":  True,
            }
        elif self.env["environment"] in ("colab", "local_gpu"):
            return {
                **base,
                "num_inference_steps":  30,
                "batch_size":           1,
                "precision":            "fp16",
                "xformers_enabled":     True,
                "cpu_offload":          True,
                "tile_size":            512,
                "max_frames_per_batch": 8 * pf // 2,
                "workers":              4,
            }
        else:
            return base  # CPU : paramètres minimaux

    def setup_torch_optimizations(self):
        """
        Configure PyTorch et xformers selon l'environnement.
        Sequential CPU Offload activé pour économiser la VRAM.
        """
        try:
            import torch

            # Désactive le benchmark si CPU seulement
            if self.env["environment"] == "cpu_only":
                torch.backends.cudnn.benchmark = False
                print("ℹ️  Mode CPU — benchmark CUDNN désactivé")
                return

            torch.backends.cudnn.benchmark = True
            torch.backends.cuda.matmul.allow_tf32 = True

            if self.env["environment"] == "vertex_ai":
                # BF16 pour A100 (meilleur que FP16)
                torch.set_default_dtype(torch.bfloat16)
                print("✅ Vertex AI : BF16 + TF32 activés (A100 optimisé)")
            else:
                # FP16 pour Colab / GPU local
                print("✅ Colab/GPU local : FP16 activé")

        except ImportError:
            print("⚠️  PyTorch non disponible — utilisation du mode simulation")

    def upload_to_gcs(self, local_path: str, bucket: str, destination: str) -> str:
        """
        Envoie un fichier vers Google Cloud Storage (pour Vertex AI).
        Retourne l'URI gs:// du fichier uploadé.
        """
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT non défini. Définissez la variable d'env.")

        uri = f"gs://{bucket}/{destination}"
        try:
            from google.cloud import storage
            client  = storage.Client(project=self.project_id)
            bkt     = client.bucket(bucket)
            blob    = bkt.blob(destination)
            blob.upload_from_filename(local_path)
            print(f"✅ Fichier uploadé vers {uri}")
            return uri
        except ImportError:
            print("⚠️  google-cloud-storage non installé. Simulation upload.")
            return f"gs://{bucket}/{destination} (simulation)"

    def switch_to_cloud(self, face_image_path: str, prompt: str) -> dict:
        """
        Point d'entrée principal : bascule automatique vers le bon backend.
        Retourne les paramètres de job pour le pipeline.
        """
        params = self.get_compute_params()
        self.setup_torch_optimizations()

        return {
            "environment":    self.env["environment"],
            "power_factor":   self.env["power_factor"],
            "gpu":            self.env["gpu_name"],
            "compute_params": params,
            "face_image":     face_image_path,
            "prompt":         prompt,
            "project_id":     self.project_id,
            "region":         self.region,
        }


def auto_connect(project_id: Optional[str] = None) -> CloudBridge:
    """
    Connexion automatique au bon environnement.
    Appeler cette fonction en premier dans tout script.
    """
    return CloudBridge(project_id=project_id)


if __name__ == "__main__":
    bridge = auto_connect()
    params = bridge.get_compute_params()
    print("\nParamètres de calcul:")
    for k, v in params.items():
        print(f"  {k}: {v}")
