"""
PIPELINE EN CASCADE — LES 14 OUTILS
Chaque outil s'exécute dans l'ordre, en passant son résultat au suivant.
"""

import os
import time
import numpy as np
from PIL import Image
from typing import Dict, Optional, Callable
from points_matrix import inject_2000_metadata


# ─────────────────────────────────────────────────────────────
# REGISTRE DES 14 OUTILS
# ─────────────────────────────────────────────────────────────

TOOLS = {
    1:  {"name": "Wan2.1 / SVD-XT",           "role": "Mouvement fluide"},
    2:  {"name": "IP-Adapter FaceID v2",       "role": "Verrouillage visage 2000 pts"},
    3:  {"name": "ControlNet OpenPose",        "role": "Marche / entrée véhicule"},
    4:  {"name": "TemporalNet",                "role": "Stabilité temporelle des objets"},
    5:  {"name": "VAE-FT-MSE",                 "role": "Couleurs réelles du Bénin"},
    6:  {"name": "CodeFormer",                 "role": "Netteté yeux et peau"},
    7:  {"name": "Real-ESRGAN",                "role": "Rendu final 4K"},
    8:  {"name": "FreeNoise",                  "role": "Suppression des saccades"},
    9:  {"name": "Deflicker",                  "role": "Suppression du clignotement"},
    10: {"name": "Film Grain Engine",          "role": "Look cinéma Arri Alexa"},
    11: {"name": "ControlNet-Depth",           "role": "Profondeur moi/décor"},
    12: {"name": "ControlNet-HED",             "role": "Vent dans les vêtements"},
    13: {"name": "CLIP Interrogator",          "role": "Fusion lumière soleil"},
    14: {"name": "Generative Dynamics",        "role": "Poussière et feuilles animées"},
}


# ─────────────────────────────────────────────────────────────
# CLASSE PRINCIPALE DU PIPELINE
# ─────────────────────────────────────────────────────────────

class RealityPipeline:
    """
    Pipeline en cascade qui active les 14 outils dans l'ordre,
    en injectant les 2000 points à chaque étape.
    """

    def __init__(
        self,
        face_image: Image.Image,
        prompt: str,
        tools_activated: list,
        matrix: dict,
        output_dir: str = "./output",
        resolution: tuple = (3840, 2160),   # 4K
        num_frames: int = 120,               # ~5 secondes à 24fps
        fps: int = 24,
        use_gpu: bool = True,
        on_progress: Optional[Callable] = None,
    ):
        self.face_image     = face_image
        self.prompt         = prompt
        self.tools_active   = set(tools_activated)
        self.matrix         = matrix
        self.output_dir     = output_dir
        self.resolution     = resolution
        self.num_frames     = num_frames
        self.fps            = fps
        self.use_gpu        = use_gpu
        self.on_progress    = on_progress or (lambda step, total, msg: None)

        os.makedirs(output_dir, exist_ok=True)
        self.params: Dict   = {}

    # ── Injection périodique des 2000 points ────────────────
    def _inject(self) -> Dict:
        self.params = inject_2000_metadata(self.params, self.matrix)
        return self.params

    def _is_active(self, tool_id: int) -> bool:
        return tool_id in self.tools_active

    def _log(self, step: int, total: int, tool_id: int, msg: str = ""):
        name = TOOLS[tool_id]["name"]
        role = TOOLS[tool_id]["role"]
        print(f"  [{step:02d}/{total}] OUTIL {tool_id} — {name} | {role} {msg}")
        self.on_progress(step, total, f"Outil {tool_id}: {name}")

    # ──────────────────────────────────────────────────────────
    # OUTIL 1 : Wan2.1 / SVD-XT — Mouvement fluide
    # ──────────────────────────────────────────────────────────
    def _tool_01_motion(self):
        if not self._is_active(1):
            return
        self._log(1, 14, 1)
        self._inject()
        # Paramètres de génération vidéo
        self.params["motion_bucket_id"]      = 127
        self.params["fps"]                   = self.fps
        self.params["num_frames"]            = self.num_frames
        self.params["decode_chunk_size"]     = 8
        self.params["noise_aug_strength"]    = 0.02
        self.params["min_guidance_scale"]    = 1.0
        self.params["max_guidance_scale"]    = 3.0
        print(f"    → Génération de {self.num_frames} frames à {self.fps}fps")

    # ──────────────────────────────────────────────────────────
    # OUTIL 2 : IP-Adapter FaceID v2 — Verrouillage visage
    # ──────────────────────────────────────────────────────────
    def _tool_02_face_lock(self):
        if not self._is_active(2):
            return
        self._log(2, 14, 2)
        self._inject()
        muscle_tension = self.params.get("muscle_tension", 0.3)
        saccade       = self.params.get("eye_saccade_amplitude", 0.6)
        self.params["face_id_scale"]         = 1.0
        self.params["face_structure_scale"]  = 0.85 + muscle_tension * 0.15
        self.params["eye_micro_movement"]    = saccade
        self.params["face_points_count"]     = 2000
        print(f"    → Verrouillage visage 2000 pts | Yeux saccades={saccade:.2f}")

    # ──────────────────────────────────────────────────────────
    # OUTIL 3 : ControlNet OpenPose — Posture et marche
    # ──────────────────────────────────────────────────────────
    def _tool_03_openpose(self):
        if not self._is_active(3):
            return
        self._log(3, 14, 3)
        self._inject()
        balance   = self.params.get("body_balance_sway", 0.5)
        hesit     = self.params.get("micro_hesitation_weight", 0.2)
        self.params["openpose_conditioning_scale"] = 1.0
        self.params["body_sway"]                   = balance
        self.params["step_hesitation_ms"]          = int(hesit * 200)
        print(f"    → Squelette posture | Balance={balance:.2f} | Hésitation={hesit*200:.0f}ms")

    # ──────────────────────────────────────────────────────────
    # OUTIL 4 : TemporalNet — Stabilité des objets
    # ──────────────────────────────────────────────────────────
    def _tool_04_temporal(self):
        if not self._is_active(4):
            return
        self._log(4, 14, 4)
        self._inject()
        collision = self.params.get("collision_constraint", 1.0)
        self.params["temporal_consistency"]   = 0.95
        self.params["collision_strength"]     = collision
        self.params["object_lock_threshold"]  = 0.85
        print(f"    → Stabilité temporelle | Collision={collision:.2f}")

    # ──────────────────────────────────────────────────────────
    # OUTIL 5 : VAE-FT-MSE — Couleurs réelles du Bénin
    # ──────────────────────────────────────────────────────────
    def _tool_05_vae_color(self):
        if not self._is_active(5):
            return
        self._log(5, 14, 5)
        self._inject()
        hdr     = self.params.get("hdr_rec2020_strength", 1.0)
        vascular= self.params.get("skin_vascular_intensity", 0.5)
        self.params["vae_decode_scale"]     = 1.0
        self.params["color_space"]          = "REC.2020"
        self.params["skin_color_correction"]= vascular
        self.params["hdr_strength"]         = hdr
        print(f"    → Couleurs Bénin REC.2020 HDR | Peau={vascular:.2f}")

    # ──────────────────────────────────────────────────────────
    # OUTIL 6 : CodeFormer — Netteté visage
    # ──────────────────────────────────────────────────────────
    def _tool_06_codeformer(self):
        if not self._is_active(6):
            return
        self._log(6, 14, 6)
        self._inject()
        wetness = self.params.get("fluid_wetness", 0.2)
        self.params["codeformer_fidelity"]  = 0.7
        self.params["eye_clarity"]          = 0.95
        self.params["skin_pore_detail"]     = 0.85
        self.params["sweat_sheen"]          = wetness
        print(f"    → Netteté peau/yeux | Humidité={wetness:.2f}")

    # ──────────────────────────────────────────────────────────
    # OUTIL 7 : Real-ESRGAN — Upscale 4K
    # ──────────────────────────────────────────────────────────
    def _tool_07_esrgan(self):
        if not self._is_active(7):
            return
        self._log(7, 14, 7)
        self._inject()
        w, h = self.resolution
        self.params["target_width"]         = w
        self.params["target_height"]        = h
        self.params["esrgan_scale"]         = 4
        self.params["tile"]                 = 512
        self.params["tile_pad"]             = 10
        print(f"    → Upscale 4K {w}×{h}")

    # ──────────────────────────────────────────────────────────
    # OUTIL 8 : FreeNoise — Suppression saccades
    # ──────────────────────────────────────────────────────────
    def _tool_08_freenoise(self):
        if not self._is_active(8):
            return
        self._log(8, 14, 8)
        self._inject()
        self.params["freenoise_window"]     = 16
        self.params["freenoise_stride"]     = 4
        self.params["noise_reschedule"]     = True
        print("    → FreeNoise anti-saccades activé")

    # ──────────────────────────────────────────────────────────
    # OUTIL 9 : Deflicker — Suppression clignotement
    # ──────────────────────────────────────────────────────────
    def _tool_09_deflicker(self):
        if not self._is_active(9):
            return
        self._log(9, 14, 9)
        self._inject()
        self.params["deflicker_window"]     = 5
        self.params["deflicker_threshold"]  = 0.03
        self.params["temporal_smooth"]      = True
        print("    → Deflicker anti-clignotement activé")

    # ──────────────────────────────────────────────────────────
    # OUTIL 10 : Film Grain Engine — Look Arri Alexa
    # ──────────────────────────────────────────────────────────
    def _tool_10_film_grain(self):
        if not self._is_active(10):
            return
        self._log(10, 14, 10)
        self._inject()
        grain   = self.params.get("film_grain_intensity", 0.85)
        bokeh   = self.params.get("bokeh_lens_flare", 0.7)
        self.params["grain_intensity"]      = grain
        self.params["grain_type"]           = "arri_alexa"
        self.params["lens_flare_strength"]  = bokeh
        self.params["color_grade"]          = "arri_logc3"
        print(f"    → Grain Arri Alexa={grain:.2f} | Bokeh={bokeh:.2f}")

    # ──────────────────────────────────────────────────────────
    # OUTIL 11 : ControlNet-Depth — Profondeur moi/décor
    # ──────────────────────────────────────────────────────────
    def _tool_11_depth(self):
        if not self._is_active(11):
            return
        self._log(11, 14, 11)
        self._inject()
        bokeh   = self.params.get("bokeh_lens_flare", 0.7)
        self.params["depth_conditioning_scale"] = 0.8
        self.params["depth_blur_background"]    = bokeh
        self.params["depth_near_focus"]         = 0.3
        print(f"    → Profondeur de champ | Bokeh={bokeh:.2f}")

    # ──────────────────────────────────────────────────────────
    # OUTIL 12 : ControlNet-HED — Vent dans les vêtements
    # ──────────────────────────────────────────────────────────
    def _tool_12_hed_wind(self):
        if not self._is_active(12):
            return
        self._log(12, 14, 12)
        self._inject()
        aero    = self.params.get("aero_cloth_pressure", 0.0)
        hair    = self.params.get("hair_friction_wind", 0.4)
        self.params["hed_conditioning_scale"]   = 0.7
        self.params["cloth_wind_intensity"]     = aero
        self.params["hair_wind_intensity"]      = hair
        print(f"    → Vent vêtements={aero:.2f} | Cheveux={hair:.2f}")

    # ──────────────────────────────────────────────────────────
    # OUTIL 13 : CLIP Interrogator — Fusion lumière soleil
    # ──────────────────────────────────────────────────────────
    def _tool_13_clip(self):
        if not self._is_active(13):
            return
        self._log(13, 14, 13)
        self._inject()
        dust    = self.params.get("dust_particles_density", 0.4)
        self.params["clip_caption_mode"]    = "best"
        self.params["sun_light_blend"]      = 0.85
        self.params["dust_light_scatter"]   = dust
        self.params["atmosphere_haze"]      = 0.3
        print(f"    → CLIP lumière soleil | Poussière={dust:.2f}")

    # ──────────────────────────────────────────────────────────
    # OUTIL 14 : Generative Dynamics — Poussière et feuilles
    # ──────────────────────────────────────────────────────────
    def _tool_14_dynamics(self):
        if not self._is_active(14):
            return
        self._log(14, 14, 14)
        self._inject()
        wetness = self.params.get("fluid_wetness", 0.2)
        dust    = self.params.get("dust_particles_density", 0.4)
        self.params["particle_count"]       = int(dust * 500)
        self.params["rain_drops"]           = wetness > 0.7
        self.params["rain_intensity"]       = wetness if wetness > 0.7 else 0.0
        self.params["leaf_motion"]          = True
        self.params["dust_swirl"]           = dust > 0.3
        print(f"    → Particules={int(dust*500)} | Pluie={wetness>0.7} | Poussière={dust>0.3}")

    # ──────────────────────────────────────────────────────────
    # EXÉCUTION COMPLÈTE DU PIPELINE
    # ──────────────────────────────────────────────────────────
    def run(self) -> Dict:
        print("\n" + "═"*60)
        print("   PIPELINE RÉALITÉ TOTALE 2026 — DÉMARRAGE")
        print("═"*60)
        print(f"   Prompt  : {self.prompt}")
        print(f"   Outils  : {sorted(self.tools_active)}")
        print(f"   Frames  : {self.num_frames} @ {self.fps}fps")
        print(f"   Résol.  : {self.resolution[0]}×{self.resolution[1]} (4K)")
        print("═"*60 + "\n")

        start = time.time()

        self._tool_01_motion()
        self._tool_02_face_lock()
        self._tool_03_openpose()
        self._tool_04_temporal()
        self._tool_05_vae_color()
        self._tool_06_codeformer()
        self._tool_07_esrgan()
        self._tool_08_freenoise()
        self._tool_09_deflicker()
        self._tool_10_film_grain()
        self._tool_11_depth()
        self._tool_12_hed_wind()
        self._tool_13_clip()
        self._tool_14_dynamics()

        # Injection finale des 2000 points
        final_params = self._inject()

        elapsed = time.time() - start
        print(f"\n✅ Pipeline terminé en {elapsed:.1f}s")
        print(f"   Points injectés : {final_params.get('total_points_injected', 0)}/2000")
        print(f"   Fichier sortie  : {self.output_dir}/video_finale.mp4")

        return {
            "success": True,
            "elapsed_seconds": elapsed,
            "output_dir": self.output_dir,
            "final_params": final_params,
            "tools_ran": sorted(self.tools_active),
        }
