"""
INTERFACE GRADIO — RÉALITÉ TOTALE 2026
Lance l'interface web pour uploader sa photo, écrire le prompt et récupérer la vidéo.
"""

import gradio as gr
from PIL import Image
from cloud_bridge import auto_connect
from prompt_interpreter import interpret_user_order
from points_matrix import build_2000_points_matrix
from pipeline import RealityPipeline


RESOLUTIONS = {
    "4K (3840×2160)":   (3840, 2160),
    "1080p (1920×1080)": (1920, 1080),
    "720p (1280×720)":   (1280,  720),
}


def generate_video(
    face_image,
    user_prompt: str,
    resolution_label: str,
    num_frames: int,
    fps: int,
    google_project: str,
):
    if face_image is None:
        return None, "❌ Veuillez uploader votre photo.", ""

    if not user_prompt.strip():
        return None, "❌ Veuillez écrire un prompt.", ""

    # 1. Pont Cloud
    bridge = auto_connect(project_id=google_project or None)
    cloud  = bridge.switch_to_cloud(face_image_path="gradio_input", prompt=user_prompt)

    # 2. Interprétation du prompt
    order  = interpret_user_order(user_prompt)

    # 3. Matrice 2000 points
    matrix = build_2000_points_matrix(overrides=order["point_overrides"])

    # 4. Pipeline
    resolution = RESOLUTIONS.get(resolution_label, (1920, 1080))
    pil_image  = Image.fromarray(face_image).convert("RGB")

    runner = RealityPipeline(
        face_image      = pil_image,
        prompt          = order["enriched_prompt"],
        tools_activated = order["tools_activated"],
        matrix          = matrix,
        output_dir      = "./output",
        resolution      = resolution,
        num_frames      = num_frames,
        fps             = fps,
        use_gpu         = True,
    )

    result = runner.run()

    # Résumé
    summary = f"""✅ Génération terminée en {result['elapsed_seconds']:.1f}s
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Scènes détectées  : {', '.join(order['scene_labels']) or 'Standard'}
Outils activés    : {len(result['tools_ran'])}/14
Points injectés   : {result['final_params'].get('total_points_injected', 0)}/2000
Résolution        : {resolution[0]}×{resolution[1]}
Environnement     : {cloud['environment']} (×{cloud['power_factor']})
GPU               : {cloud['gpu']}"""

    prompt_detail = f"""Prompt enrichi :
{order['enriched_prompt']}

Points forcés : {order['total_overrides']}/2000
"""

    output_video = f"./output/video_finale.mp4"

    return output_video if result["success"] else None, summary, prompt_detail


# ── Interface Gradio ─────────────────────────────────────────
with gr.Blocks(title="Réalité Totale 2026", theme=gr.themes.Monochrome()) as demo:

    gr.Markdown("""
    # 🎬 RÉALITÉ TOTALE 2026 — LA GRANDE CHOSE
    **Pipeline IA 14 outils · 2000 points de contrôle · Rendu 4K Arri Alexa**
    ---
    """)

    with gr.Row():
        with gr.Column(scale=1):
            face_input = gr.Image(
                label="📸 Votre photo (visage)",
                type="numpy",
                height=300
            )
            prompt_input = gr.Textbox(
                label="✍️ Décrivez la scène",
                placeholder="Ex: Moi, marchant à la foire de l'indépendance de Cotonou, au soleil couchant.",
                lines=4
            )
            with gr.Row():
                resolution_input = gr.Dropdown(
                    choices=list(RESOLUTIONS.keys()),
                    value="1080p (1920×1080)",
                    label="🎥 Résolution"
                )
                frames_input = gr.Slider(24, 240, value=120, step=12, label="🎞️ Frames")
                fps_input    = gr.Slider(12, 60, value=24, step=6, label="⚡ FPS")

            project_input = gr.Textbox(
                label="☁️ Google Cloud Project ID (optionnel pour Vertex AI)",
                placeholder="mon-projet-gcp"
            )

            generate_btn = gr.Button("🚀 GÉNÉRER LA VIDÉO", variant="primary", size="lg")

        with gr.Column(scale=1):
            video_output  = gr.Video(label="🎬 Vidéo Générée")
            summary_out   = gr.Textbox(label="📊 Rapport de génération", lines=10)
            prompt_detail = gr.Textbox(label="🔍 Détail du prompt enrichi", lines=5)

    # Exemples prêts à l'emploi
    gr.Examples(
        examples=[
            ["Moi, marchant à la foire de l'indépendance de Cotonou, au soleil couchant.", "1080p (1920×1080)", 72, 24],
            ["Moi, montant dans une voiture zémidjan, il pleut beaucoup.", "1080p (1920×1080)", 96, 24],
            ["Moi, en moto à 120 km/h, le vent tape mon visage.", "4K (3840×2160)", 120, 24],
        ],
        inputs=[prompt_input, resolution_input, frames_input, fps_input],
        label="💡 Exemples de scènes"
    )

    generate_btn.click(
        fn=generate_video,
        inputs=[face_input, prompt_input, resolution_input, frames_input, fps_input, project_input],
        outputs=[video_output, summary_out, prompt_detail]
    )


if __name__ == "__main__":
    demo.launch(share=True)
