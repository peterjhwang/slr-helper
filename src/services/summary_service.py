import logging
from pathlib import Path
import json
import asyncio
import os
from pdfminer.high_level import extract_text
from utils.llm_helpers import create_batches, call_openai

logger = logging.getLogger(__name__)


async def create_summaries(project_id):
    batch_size = 2
    logger.info("Creating summaries - " + project_id)
    if not os.path.exists(f"data/{project_id}/summaries"):
        os.mkdir(f"data/{project_id}/summaries")
    # 1. individual file summary
    model_params = json.loads(
        Path("src/resources/prompts_v1.0/individual_summary.json").read_text()
    )
    logger.info("individual summary param\n" + json.dumps(model_params, indent=4))
    prompt_dict = {}
    # data format
    # key: file name
    # value: list(system prompt, user prompt)
    for file in os.listdir(f"data/{project_id}/files"):
        if file.endswith(".pdf"):
            file_path = f"data/{project_id}/files/{file}"
            text = extract_text(file_path)
            prompt_dict[file] = [model_params["messages"][0]["content"], text]

    # logger.info(prompt_dict)
    results = []
    for batch in create_batches(prompt_dict, batch_size):
        coroutines = []
        for filename, prompt_list in batch.items():
            logger.info(f"Creating summary for {filename}")
            coroutines.append(
                call_openai(
                    prompt_list[0],
                    prompt_list[1],
                    model=model_params["model"],
                    temperature=model_params["temperature"],
                    max_tokens=model_params["max_tokens"],
                    logger=logger,
                )
            )
        results += await asyncio.gather(*coroutines)

    summary_result = {
        filename: result.choices[0].message.content
        for filename, result in zip(prompt_dict.keys(), results)
    }

    for file, summary in summary_result.items():
        with open(
            f"data/{project_id}/summaries/{file.replace('.pdf', '.txt')}", "w"
        ) as f:
            f.write(summary)
