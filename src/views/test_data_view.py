import gradio as gr
import os
from utils.file_helpers import read_csv_to_list_of_lists


def display_test_data(project_id):
    if project_id == "":
        return (
            gr.update(),
            gr.DataFrame(
                [["message", "Please select/create a project first."]], visible=True
            ),
            gr.update(),
            gr.update(),
        )
    test_data = read_csv_to_list_of_lists(f"data/{project_id}/test_data.csv")
    return (
        gr.update(visible=False),
        gr.DataFrame(test_data[1:], headers=test_data[0], visible=True),
        gr.Textbox(
            f"Total number of records: {len(test_data)}",
            label="Information",
            visible=True,
            max_lines=1,
        ),
        gr.File(value=f"data/{project_id}/test_data.csv", visible=True),
    )


def test_data_tab(project_id):
    with gr.Row():
        with gr.Column(scale=1):
            generate_test_button = gr.Button(value="Create Test Dataset")
        with gr.Column(scale=5):
            with gr.Row():
                with gr.Column(scale=1):
                    count_qna = gr.Textbox(visible=False)
                with gr.Column(scale=1):
                    download_file = gr.File(
                        label="Download Test Dataset", type="filepath", visible=False
                    )
            test_dataset = gr.DataFrame(
                label="Training Data",
                visible=True,
            )
    generate_test_button.click(
        fn=display_test_data,
        inputs=[project_id],
        outputs=[generate_test_button, test_dataset, count_qna, download_file],
    )
