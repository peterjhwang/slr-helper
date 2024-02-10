import gradio as gr
import logging
import os
import json
from datetime import datetime
from uuid import uuid4

logger = logging.getLogger(__name__)


def existing_project_act():
    return (
        gr.update(visible=False),
        gr.update(visible=True),
        gr.update(visible=False),
        gr.update(visible=False),
    )


def new_project_act():
    return (
        gr.update(visible=True),
        gr.update(visible=False),
        gr.update(visible=True),
        gr.update(visible=True),
    )


def create_new_project(project_name, upload_files):
    new_project_id = str(uuid4())
    if project_name == "":
        project_name = "New Project"

    project_name += (
        f" ({len(upload_files)} files, created at "
        + datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        + ")"
    )
    while new_project_id in project_name_ids.values():
        new_project_id = str(uuid4())
        if new_project_id not in project_name_ids.values():
            break

    project_name_ids[project_name] = new_project_id

    # save files
    os.mkdir(f"data/{new_project_id}")
    folder_path = f"data/{new_project_id}/files"
    os.mkdir(folder_path)
    for i, file in enumerate(upload_files):
        with open(file.name, "rb") as f:
            data = f.read()
        with open(f"{folder_path}/{file.name.split('/')[-1]}", "wb") as f:
            f.write(data)

    with open("data/project_name_ids.json", "w") as f:
        json.dump(project_name_ids, f, indent=4)
    return (
        gr.Textbox(project_name, label="Project Name", visible=True, interactive=False),
        gr.Textbox(
            new_project_id,
            label="Project ID",
            visible=True,
            interactive=False,
        ),
        gr.Dropdown(
            choices=project_name_ids.keys(),
            label="Projects",
            info="Choose one existing project",
            visible=True,
            interactive=True,
        ),
    )


if not os.path.exists("data"):
    os.mkdir("data")
if os.path.exists("data/project_name_ids.json"):
    with open("data/project_name_ids.json", "r") as f:
        project_name_ids = json.load(f)
else:
    project_name_ids = {}
    with open("data/project_name_ids.json", "w") as f:
        json.dump(project_name_ids, f)


def update_project_name_id(project_name):
    logger.info("Selected Project: " + project_name)
    return (
        gr.Textbox(project_name, label="Project Name", visible=True, interactive=False),
        gr.Textbox(
            project_name_ids.get(project_name, "None"),
            label="Project ID",
            visible=True,
            interactive=False,
        ),
    )


def create_project_tab(project_name, project_id):
    gr.Markdown("*Currently, the system supports PDF files only.*")
    with gr.Row():
        with gr.Column(scale=1):
            select_button = gr.Button(value="Select an existing Project")
        with gr.Column(scale=1):
            create_button = gr.Button(value="Create a new Project")
    project_name_textbox = gr.Textbox(
        label="New Project Name",
        placeholder="Type Project Name",
        visible=False,
        interactive=True,
    )
    select_project = gr.Dropdown(
        choices=project_name_ids.keys(),
        label="Projects",
        info="Choose one existing project",
        visible=True,
        interactive=True,
    )

    upload_file = gr.Files(
        visible=False, interactive=True, file_count="multiple", file_types=["text"]
    )
    submit_button = gr.Button(value="Submit", variant="primary", visible=False)

    select_project.change(
        update_project_name_id,
        inputs=[select_project],
        outputs=[project_name, project_id],
    )

    select_button.click(
        existing_project_act,
        inputs=[],
        outputs=[project_name_textbox, select_project, upload_file, submit_button],
    )

    create_button.click(
        new_project_act,
        inputs=[],
        outputs=[project_name_textbox, select_project, upload_file, submit_button],
    )

    submit_button.click(
        fn=create_new_project,
        inputs=[project_name_textbox, upload_file],
        outputs=[project_name, project_id, select_project],
    )
