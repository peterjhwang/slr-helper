import gradio as gr
import logging
import os
import json
import asyncio
from services.metadata_service import create_metadata

logger = logging.getLogger(__name__)


def get_metadata(project_id):
    if project_id == "":
        return (
            gr.update(visible=True),
            gr.JSON({"message": "Please select/create a project first."}, visible=True),
        )
    if not os.path.exists(f"data/{project_id}/metadata.json"):
        # if summary exists, return summary
        asyncio.run(create_metadata(project_id))

    with open(f"data/{project_id}/metadata.json", "r") as f:
        metadata = json.load(f)
    return (
        gr.update(visible=False),
        gr.JSON(metadata),
    )


def create_metadata_tab(project_id):
    logger.info("Creating summary tab - " + project_id.value)
    with gr.Row():
        with gr.Column(scale=1):
            metadata_button = gr.Button(value="Create Metadata")
        with gr.Column(scale=5):
            metadata_json = gr.JSON(
                label="Metadata",
                visible=True,
            )

    metadata_button.click(
        fn=get_metadata,
        inputs=[project_id],
        outputs=[metadata_button, metadata_json],
    )
