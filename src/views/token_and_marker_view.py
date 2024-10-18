import logging
import asyncio
import os
import json
import gradio as gr
from pathlib import Path
from services.token_and_marker_service import (
    create_training_dataset,
)
from utils.file_helpers import read_csv_to_list_of_lists

logger = logging.getLogger(__name__)


def add_token_and_marker(project_id, special_token, market_format):
    if project_id == "":
        return (
            gr.update(),
            gr.DataFrame(
                [["message", "Please select/create a project first."]], visible=True
            ),
            gr.update(),
            gr.update(),
        )
    if not os.path.exists(f"data/{project_id}/training_data.csv"):
        if special_token == "":
            return (
                gr.update(),
                gr.DataFrame(
                    [["message", "Please enter special token."]], visible=True
                ),
                gr.update(),
                gr.update(),
            )
        create_training_dataset(project_id, special_token)

    training_data = read_csv_to_list_of_lists(f"data/{project_id}/training_data.csv")
    return (
        gr.update(visible=False),
        gr.DataFrame(training_data[1:], headers=training_data[0], visible=True),
        gr.Textbox(
            f"Total number of records: {len(training_data)}",
            label="Information",
            visible=True,
            max_lines=1,
        ),
        gr.File(value=f"data/{project_id}/training_data.csv", visible=True),
    )


def download_training_data(project_id):
    training_json = json.loads(
        Path(f"data/{project_id}/training_data.json").read_text()
    )
    return gr.update(value=f"{len(training_json)}", visible=True), gr.File(
        f"data/{project_id}/training_data.json", visible=True
    )


def create_token_and_marker_tab(project_id):
    logger.info("Creating summary tab - " + project_id.value)
    with gr.Row():
        with gr.Column(scale=1):
            special_token = gr.Textbox(
                label="Special Token", placeholder="", max_lines=1
            )
            market_format = gr.Textbox(
                label="Marker Format",
                value="FIRSTAUTHORYEARKEYWORD",
                interactive=False,
                max_lines=1,
            )
            add_token_button = gr.Button(value="Add token and marker")
        with gr.Column(scale=5):
            with gr.Row():
                with gr.Column(scale=1):
                    count_qna = gr.Textbox(visible=False)
                with gr.Column(scale=1):
                    download_file = gr.File(
                        label="Download Dataset", type="filepath", visible=False
                    )
            dataset_json = gr.DataFrame(
                label="Training Data",
                visible=True,
            )

    add_token_button.click(
        fn=add_token_and_marker,
        inputs=[project_id, special_token, market_format],
        outputs=[add_token_button, dataset_json, count_qna, download_file],
    )
