import logging
from pathlib import Path
import json
import asyncio
import os
from pdfminer.high_level import extract_text
from utils.llm_helpers import batch, call_openai
from utils.string_helpers import (
    chunking,
    extract_json_text,
    extract_json_bracketed_text,
)

logger = logging.getLogger(__name__)


async def create_section_qna(project_id):
    batch_size = 2
    logger.info("Creating paper level Q&A - " + project_id)
    if not os.path.exists(f"data/{project_id}/section-level"):
        os.mkdir(f"data/{project_id}/section-level")
    # 1. individual file summary
    model_params = json.loads(
        Path("src/resources/prompts_v1.0/section_Q&A_prompt.json").read_text()
    )
    logger.info("Section-level Q&A param\n" + json.dumps(model_params, indent=4))
    prompt_list = []
    # data format
    # key: file name
    # value: list(filename, system prompt, user prompt)
    # if not os.path.exists(f"data/{project_id}/temp"):
    #     os.mkdir(f"data/{project_id}/temp")
    for file in os.listdir(f"data/{project_id}/files"):
        if file.endswith(".pdf"):
            file_path = f"data/{project_id}/files/{file}"
            text = extract_text(file_path)
            for i, chunk in enumerate(
                chunking(
                    text,
                    model_params["model"],
                    min_avg_chunk_size=2000,
                    max_avg_chunk_size=3000,
                )
            ):
                logger.info(f"Creating section-level Q&A for {file} - {i}")
                # with open(f"data/{project_id}/temp/{file + str(i) + '.txt'}", "w") as f:
                #     f.write(chunk)
                prompt_list.append(
                    (file, model_params["messages"][0]["content"], chunk)
                )

    # logger.info(prompt_dict)
    results = []
    for prompt_batch in batch(prompt_list, batch_size):
        coroutines = []
        for data in prompt_batch:
            coroutines.append(
                call_openai(
                    data[1],
                    data[2],
                    model=model_params["model"],
                    temperature=model_params["temperature"],
                    max_tokens=model_params["max_tokens"],
                    logger=logger,
                )
            )
        results += await asyncio.gather(*coroutines)

    summary_result = {}
    for data, result in zip(prompt_list, results):
        filename = data[0]
        result_str = (
            extract_json_text(result.choices[0].message.content)
            if "```" in result.choices[0].message.content
            else result.choices[0].message.content
        )
        result_str = extract_json_bracketed_text(result_str)
        try:
            json_result = json.loads(result_str)
        except:
            logger.error(f"Error in {filename}")
            logger.error(result.choices[0].message.content)
            continue
        if filename in summary_result:
            summary_result[filename] += json_result
        else:
            summary_result[filename] = json_result

    for file, summary in summary_result.items():
        with open(
            f"data/{project_id}/section-level/{file.replace('.pdf', '.json')}", "w"
        ) as f:
            json.dump(summary, f, indent=4)
