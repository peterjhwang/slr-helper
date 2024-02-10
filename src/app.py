import gradio as gr
import logging
import sys
from dotenv import load_dotenv
import os

load_dotenv()

from views.project_view import create_project_tab
from views.summary_view import create_summary_tab
from views.slr_level_view import create_slr_tab
from views.metadata_view import create_metadata_tab
from views.paper_level_view import create_paper_tab
from views.section_level_view import create_section_tab
from views.paraphrase_view import create_paraphrase_question_tab
from views.token_and_marker_view import create_token_and_marker_view

VERSION = "0.0.1"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
theme = gr.Theme.from_hub("finlaymacklon/smooth_slate")

with gr.Blocks(
    css="footer{display:none !important}",
    title="Fine-tuning App",
    theme=theme,
) as gradio_app:
    gr.Markdown(
        f'<div style="text-align: center; font-size: 28px"> LLM Fine-tuning App for SLR </div>'
    )
    with gr.Row():
        with gr.Column(scale=1):
            reset_button = gr.ClearButton(value="Reset")
            reset_button.click(None, js="window.location.reload()")
        with gr.Column(scale=1):
            gr.Markdown(f'<div style="text-align: right"> Ver. {VERSION} </div>')
            dark_mode_button = gr.Button(
                value="Toggle Dark Mode", variant="primary", visible=False
            )
            dark_mode_button.click(
                None,
                js="""
                () => {
                    document.body.classList.toggle('dark');
                    document.querySelector('gradio-app').style.backgroundColor = 'var(--color-background-primary)'
                }
                """,
            )
    with gr.Row():
        with gr.Column(scale=1):
            project_name = gr.Textbox(
                label="Project Name",
                visible=False,
                interactive=False,
            )
        with gr.Column(scale=1):
            project_id = gr.Textbox(
                label="Project ID",
                visible=False,
                interactive=False,
            )
    with gr.Tab("1. Select/Create Project"):
        create_project_tab(project_name, project_id)
    with gr.Tab("2. Metadata Extraction"):
        create_metadata_tab(project_id)
    with gr.Tab("3. Individual Summarise"):
        create_summary_tab(project_id)
    with gr.Tab("4. SLR level Q&A"):
        create_slr_tab(project_id)
    with gr.Tab("5. Paper level Q&A"):
        create_paper_tab(project_id)
    with gr.Tab("5. Section level Q&A"):
        create_section_tab(project_id)
    with gr.Tab("6. Paraphrase Questions"):
        create_paraphrase_question_tab(project_id)
    with gr.Tab("7. Add Token and Marker"):
        create_token_and_marker_view(project_id)

gradio_app.launch(server_name="0.0.0.0")
gradio_app.close()
