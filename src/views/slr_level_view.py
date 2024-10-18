import gradio as gr
import logging
import os
import json
import asyncio
from services.slr_level_service import (
    create_slr_summary,
    create_slr_questions,
    create_slr_qna,
    created_combined_slr_qna,
)

logger = logging.getLogger(__name__)

# get overall summary


def create_slr_summary_questions(project_id):
    if not os.path.exists(f"data/{project_id}/summaries"):
        return (
            gr.update(visible=True),
            gr.Markdown(
                label="Message", value="Create individual summaries first", visible=True
            ),
            gr.update(),
            gr.update(),
            gr.update(),
            gr.update(),
        )
    if not os.path.exists(f"data/{project_id}/slr-level"):
        os.mkdir(f"data/{project_id}/slr-level")
        # slr summary
        asyncio.run(create_slr_summary(project_id))
    if not os.path.exists(f"data/{project_id}/slr-level/slr_questions.txt"):
        asyncio.run(create_slr_questions(project_id))

    overall_summary_file = f"overall_summary.txt"
    with open(f"data/{project_id}/slr-level/" + overall_summary_file, "r") as f:
        overall_summary = f.read()

    slr_question_file = f"slr_questions.txt"
    slr_questions = "# SLR Questions\n\n"
    with open(f"data/{project_id}/slr-level/" + slr_question_file, "r") as f:
        slr_questions += f.read()

    return (
        gr.update(visible=False),
        gr.Markdown(
            label="Overall Summary",
            value=overall_summary,
            visible=True,
        ),
        gr.Textbox(
            label="SLR Questions",
            value=slr_questions,
            interactive=True,
            visible=True,
        ),
        gr.update(visible=True),
        gr.update(visible=True),
        gr.update(visible=True),
    )


def update_slr_questions(project_id, slr_questions):
    with open(f"data/{project_id}/slr-level/slr_questions.txt", "w") as f:
        f.write(slr_questions.replace("# SLR Questions", "").strip())


def update_slr_json(project_id, slr_qna_file_dropdown):
    file = slr_qna_file_dropdown
    with open(f"data/{project_id}/slr-level/individual/{file}", "r") as f:
        slr_qna = json.load(f)
    return gr.update(value=slr_qna)


def load_slr_qna(project_id):
    if not os.path.exists(f"data/{project_id}/slr-level/individual"):
        asyncio.run(create_slr_qna(project_id))

    slr_qla_files = [
        file
        for file in os.listdir(f"data/{project_id}/slr-level/individual")
        if ".json" in file
    ]
    logger.info("SLR Q&A " + str(len(slr_qla_files)) + " files found")
    logger.info("\n".join(slr_qla_files))
    file = slr_qla_files[0]
    with open(f"data/{project_id}/slr-level/individual/{file}", "r") as f:
        slr_qna = json.load(f)
    return (
        gr.update(visible=False),
        gr.Dropdown(choices=slr_qla_files, value=file, visible=True),
        gr.JSON(slr_qna, visible=True),
        gr.update(visible=True),
    )


def combine_slr_qna(project_id):
    if not os.path.exists(f"data/{project_id}/slr-level/combined_slr_qna.json"):
        asyncio.run(created_combined_slr_qna(project_id))
    with open(f"data/{project_id}/slr-level/combined_slr_qna.json", "r") as f:
        data = json.load(f)
    return gr.JSON(data, visible=True)


def create_slr_tab(project_id):
    logger.info("Creating slr tab - " + project_id.value)
    slr_button = gr.Button(value="Create SLR Summary/Questions")
    with gr.Tab("Synthesis Summary"):
        summary_text = gr.Markdown(
            label="Summary",
            visible=False,
        )
    with gr.Tab("SLR Questions"):
        slr_questions = gr.Textbox(
            label="SLR Questions",
            visible=False,
            lines=30,
            max_lines=30,
        )
        comment_box = gr.Markdown(
            "***Edit SLR questions and Click the button below to update SLR questions. Note: Questions must start with hyphen (-).***",
            visible=False,
        )
        update_slr_question_button = gr.Button(
            value="Update SLR Questions", visible=False
        )
    with gr.Tab("SLR Q&A Per File"):
        with gr.Row():
            with gr.Column(scale=1):
                slr_qna_button = gr.Button(value="Create SLR Q&A", visible=False)
                slr_qna_file_dropdown = gr.Dropdown(label="File", visible=False)
            with gr.Column(scale=5):
                slr_qna_json = gr.JSON(visible=False)

    with gr.Tab("SLR Combined Q&A"):
        with gr.Row():
            with gr.Column(scale=1):
                slr_combined_qna_button = gr.Button(
                    value="Combine SLR Q&A", visible=False
                )
            with gr.Column(scale=5):
                slr_combined_qna_json = gr.JSON(visible=False)

    slr_button.click(
        fn=create_slr_summary_questions,
        inputs=[project_id],
        outputs=[
            slr_button,
            summary_text,
            slr_questions,
            comment_box,
            update_slr_question_button,
            slr_qna_button,
        ],
    )

    update_slr_question_button.click(
        fn=update_slr_questions, inputs=[project_id, slr_questions]
    )

    slr_qna_button.click(
        fn=load_slr_qna,
        inputs=[project_id],
        outputs=[
            slr_qna_button,
            slr_qna_file_dropdown,
            slr_qna_json,
            slr_combined_qna_button,
        ],
    )

    slr_qna_file_dropdown.change(
        fn=update_slr_json,
        inputs=[project_id, slr_qna_file_dropdown],
        outputs=[slr_qna_json],
    )

    slr_combined_qna_button.click(
        fn=combine_slr_qna,
        inputs=[project_id],
        outputs=[
            slr_combined_qna_json,
        ],
    )
