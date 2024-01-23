import logging
from pathlib import Path
import json
import os
from pdfminer.high_level import extract_text
from langchain_openai import ChatOpenAI
from langchain.schema.messages import ChatMessage
from utils.llm_helpers import create_batches, run_llm

logger = logging.getLogger(__name__)


async def create_summaries(project_id):
    batch_size = 3
    logger.info("Creating summaries - " + project_id)
    if not os.path.exists(f"data/{project_id}/summaries"):
        os.mkdir(f"data/{project_id}/summaries")
    # 1. individual file summary
    model_params = json.loads(
        Path("src/resources/prompts_v1.0/individual_summary.json").read_text()
    )
    logger.info("individual summary param\n" + json.dumps(model_params, indent=4))
    individual_llm = ChatOpenAI(
        temperature=model_params["temperature"],
        max_tokens=model_params["max_tokens"],
        model=model_params["model"],
    )
    prompt_dict = {}
    # data format
    # key: file name
    # value: list(system prompt, user prompt)
    for file in os.listdir(f"data/{project_id}/files"):
        if file.endswith(".pdf"):
            file_path = f"data/{project_id}/files/{file}"
            text = extract_text(file_path)
            prompt_dict[file] = [
                ChatMessage(
                    role="system",
                    content=model_params["messages"][0]["content"],
                ),
                ChatMessage(role="user", content=text),
            ]

    # logger.info(prompt_dict)
    summary_result = {}
    for batch in create_batches(prompt_dict, batch_size):
        responses = await run_llm(individual_llm, prompt_dict)
        summary_result.update(dict(zip(batch.keys(), responses)))

    combined_summaries = ""
    i = 1
    for file, summary in summary_result.items():
        with open(
            f"data/{project_id}/summaries/{file.replace('.pdf', '.txt')}", "w"
        ) as f:
            f.write(summary)
        combined_summaries += f"Summary {i}\n\n{summary}\n\n\n"
        i += 1
    # 2. combined file summary
    model_params2 = json.loads(
        Path("src/resources/prompts_v1.0/combined_summary.json").read_text()
    )
    combined_llm = ChatOpenAI(
        temperature=model_params["temperature"],
        max_tokens=model_params["max_tokens"],
        model=model_params["model"],
    )
    logger.info("combined summary param\n" + json.dumps(model_params2, indent=4))
    overall_summary = (
        combined_llm.generate(
            [
                [
                    ChatMessage(
                        role="system",
                        content=model_params2["messages"][0]["content"],
                    ),
                    ChatMessage(role="user", content=combined_summaries),
                ]
            ]
        )
        .generations[0][0]
        .text
    )

    with open(f"data/{project_id}/summaries/overall_summary.txt", "w") as f:
        f.write(overall_summary)
