import gradio as gr
import logging
import os
import json
import asyncio
from services.paraphrase_service import create_paraphrased_questions

logger = logging.getLogger(__name__)


def paraphrase_questions(project_id):
    if project_id == "":
        return (
            gr.update(),
            gr.JSON({"message": "Please select/create a project first."}, visible=True),
            gr.update(),
        )
    if not os.path.exists(f"data/{project_id}/dataset"):
        # if summary exists, return summary
        asyncio.run(create_paraphrased_questions(project_id))

    file = os.listdir(f"data/{project_id}/dataset")[0]
    with open(f"data/{project_id}/dataset/{file}", "r") as f:
        json_data = json.load(f)

    return (
        gr.update(visible=False),
        gr.JSON(
            json_data,
            label="All Q&A pairs",
            visible=True,
        ),
        gr.Dropdown(
            choices=os.listdir(f"data/{project_id}/dataset"),
            value=file,
            visible=True,
            interactive=True,
        ),
    )


def update_all_qna(project_id, file_name):
    with open(f"data/{project_id}/dataset/{file_name}", "r") as f:
        json_data = json.load(f)
    return gr.JSON(
        json_data,
        label="All Q&A pairs",
        visible=True,
    )


def create_paraphrase_question_tab(project_id):
    logger.info("Paraphrase questions tab - " + project_id.value)
    with gr.Row():
        with gr.Column(scale=1):
            paraphrase_button = gr.Button(value="Combine & Paraphrase Questions")
            file_select_dropdown = gr.Dropdown(label="File", visible=False)
        with gr.Column(scale=5):
            total_qna_json = gr.JSON(
                label="All Q&A pairs",
                visible=True,
            )

    paraphrase_button.click(
        fn=paraphrase_questions,
        inputs=[project_id],
        outputs=[paraphrase_button, total_qna_json, file_select_dropdown],
    )

    file_select_dropdown.change(
        fn=update_all_qna,
        inputs=[project_id, file_select_dropdown],
        outputs=[total_qna_json],
    )
