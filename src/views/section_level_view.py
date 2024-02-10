import gradio as gr
import logging
import os
import json
import asyncio
from services.section_level_service import create_section_qna

logger = logging.getLogger(__name__)


def get_section_level_qna(project_id):
    if project_id == "":
        return (
            gr.update(),
            gr.JSON({"message": "Please select/create a project first."}, visible=True),
            gr.update(),
        )
    if not os.path.exists(f"data/{project_id}/section-level"):
        # if summary exists, return summary
        asyncio.run(create_section_qna(project_id))

    file = os.listdir(f"data/{project_id}/section-level")[0]
    with open(f"data/{project_id}/section-level/{file}", "r") as f:
        json_data = json.load(f)

    return (
        gr.update(visible=False),
        gr.JSON(
            json_data,
            label="Section Level Q&A",
            visible=True,
        ),
        gr.Dropdown(
            choices=os.listdir(f"data/{project_id}/section-level"),
            value=file,
            visible=True,
            interactive=True,
        ),
    )


def update_section_level_qna(project_id, file_name):
    with open(f"data/{project_id}/section-level/{file_name}", "r") as f:
        json_data = json.load(f)
    return gr.JSON(
        json_data,
        label="Section Level Q&A",
        visible=True,
    )


def create_section_tab(project_id):
    logger.info("Creating section level Q&A tab - " + project_id.value)
    with gr.Row():
        with gr.Column(scale=1):
            paper_qna_button = gr.Button(value="Create Section Level Q&A")
            file_select_dropdown = gr.Dropdown(label="File", visible=False)
        with gr.Column(scale=5):
            paper_level_json = gr.JSON(
                label="Section Level Q&A",
                visible=True,
            )

    paper_qna_button.click(
        fn=get_section_level_qna,
        inputs=[project_id],
        outputs=[paper_qna_button, paper_level_json, file_select_dropdown],
    )

    file_select_dropdown.change(
        fn=update_section_level_qna,
        inputs=[project_id, file_select_dropdown],
        outputs=[paper_level_json],
    )
