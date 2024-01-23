import gradio as gr
import logging
import sys
from dotenv import load_dotenv
import os

load_dotenv()

from views.create_project import create_project_tab
from views.create_summary import create_summary_tab


VERSION = "0.0.1"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


with gr.Blocks(
    css="footer{display:none !important}",
    title="Fine-tuning App",
) as gradio_app:
    gr.Markdown(
        f'<div style="text-align: center; font-size: 28px"> LLM Fine-tuning App for SLR </div>'
    )
    gr.Markdown(f'<div style="text-align: right"> Ver. {VERSION} </div>')
    with gr.Row():
        with gr.Column(scale=1):
            reset_button = gr.ClearButton(value="Reset")
            reset_button.click(None, js="window.location.reload()")
        with gr.Column(scale=1):
            dark_mode_button = gr.Button(value="Toggle Dark Mode", variant="primary")
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
    with gr.Tab("2. Summarise"):
        create_summary_tab(project_id)

gradio_app.launch(server_name="0.0.0.0")
gradio_app.close()
