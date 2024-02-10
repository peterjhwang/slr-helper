import gradio as gr
import logging
import os
import asyncio
from services.summary_service import create_summaries

logger = logging.getLogger(__name__)


def get_summaries(project_id):
    if project_id == "":
        return (
            gr.update(),
            gr.Markdown("Please select/create a project first.", visible=True),
            gr.update(),
        )
    if not os.path.exists(f"data/{project_id}/summaries"):
        # if summary exists, return summary
        asyncio.run(create_summaries(project_id))

    # read summary from file
    summary_files = os.listdir(f"data/{project_id}/summaries")
    with open(f"data/{project_id}/summaries/{summary_files[0]}", "r") as f:
        summary = f.read()
    return (
        gr.update(visible=False),
        gr.Markdown(
            summary,
            label="Project ID",
            visible=True,
        ),
        gr.Dropdown(
            choices=summary_files,
            value=summary_files[0],
            visible=True,
            interactive=True,
        ),
    )


def update_summary_text(project_id, file_name):
    with open(f"data/{project_id}/summaries/{file_name}", "r") as f:
        summary_text = f.read()
    return gr.Markdown(summary_text, label="Summary", visible=True)


def create_summary_tab(project_id):
    logger.info("Creating summary tab - " + project_id.value)
    with gr.Row():
        with gr.Column(scale=1):
            summary_button = gr.Button(value="Create Summary")
            file_select_dropdown = gr.Dropdown(label="File", visible=False)
        with gr.Column(scale=5):
            summary_text = gr.Markdown(
                label="Summary",
                value="Select/Create Project ID",
                visible=True,
            )

    summary_button.click(
        fn=get_summaries,
        inputs=[project_id],
        outputs=[summary_button, summary_text, file_select_dropdown],
    )

    file_select_dropdown.change(
        fn=update_summary_text,
        inputs=[project_id, file_select_dropdown],
        outputs=[summary_text],
    )
