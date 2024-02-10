import logging
import json
import os
from pathlib import Path
import asyncio
from pdfminer.high_level import extract_text
from utils.llm_helpers import create_batches, call_openai

logger = logging.getLogger(__name__)


async def create_slr_summary(project_id):
    # slr summary
    model_params = json.loads(
        Path("src/resources/prompts_v1.0/slr_summary.json").read_text()
    )

    logger.info("SLR summary param\n" + json.dumps(model_params, indent=4))
    combined_summaries = ""
    i = 1
    for file in os.listdir(f"data/{project_id}/summaries"):
        with open(f"data/{project_id}/summaries/{file}", "r") as f:
            summary = f.read()
        combined_summaries += f"Summary {i}\n\n{summary}\n\n\n"
        i += 1
    results = []
    coroutines = [
        call_openai(
            system_prompt=model_params["messages"][0]["content"],
            user_prompt=combined_summaries,
            model=model_params["model"],
            temperature=model_params["temperature"],
            max_tokens=model_params["max_tokens"],
            logger=logger,
        )
    ]
    results += await asyncio.gather(*coroutines)

    with open(f"data/{project_id}/slr-level/overall_summary.txt", "w") as f:
        f.write(results[0].choices[0].message.content)


async def create_slr_questions(project_id):
    # slr summary
    model_params = json.loads(
        Path("src/resources/prompts_v1.0/slr_questions.json").read_text()
    )

    logger.info("SLR question param\n" + json.dumps(model_params, indent=4))
    with open(f"data/{project_id}/slr-level/overall_summary.txt", "r") as f:
        summary = f.read()

    results = []
    coroutines = [
        call_openai(
            system_prompt=model_params["messages"][0]["content"],
            user_prompt=summary,
            model=model_params["model"],
            temperature=model_params["temperature"],
            max_tokens=model_params["max_tokens"],
            logger=logger,
        )
    ]
    results += await asyncio.gather(*coroutines)

    with open(f"data/{project_id}/slr-level/slr_questions.txt", "w") as f:
        f.write(results[0].choices[0].message.content)


async def create_slr_qna(project_id):
    batch_size = 1

    # create files
    model_params = json.loads(
        Path("src/resources/prompts_v1.0/slr_Q&A.json").read_text()
    )
    logger.info("SLR Q&A param\n" + json.dumps(model_params, indent=4))

    with open(f"data/{project_id}/slr-level/slr_questions.txt", "r") as f:
        slr_questions_str = f.read()
    slr_questions = []
    for sentence in slr_questions_str.split("\n"):
        if sentence.startswith("- "):
            print("-", sentence[2:])
            slr_questions.append(sentence.replace("- ", "").strip())

    slr_question_str = ""
    for i, question in enumerate(slr_questions):
        slr_question_str += f"{i+1}. {question}\n"
    system_prompt = model_params["messages"][0]["content"].replace(
        "{{research_questions}}", slr_question_str
    )
    logger.info("-- SLR Q&A system prompt\n" + system_prompt)
    prompt_dict = {}
    for file in os.listdir(f"data/{project_id}/files"):
        if file.endswith(".pdf"):
            file_path = f"data/{project_id}/files/{file}"
            text = extract_text(file_path)
            text += "\n\n\nRemember to include all the questions."
            prompt_dict[file] = [system_prompt, text]

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

    slr_qna_result = {
        filename: json.loads(
            result.choices[0]
            .message.content.replace("```json", "")
            .replace("```", "")
            .strip()
        )
        for filename, result in zip(prompt_dict.keys(), results)
    }
    for file, slr_json in slr_qna_result.items():
        with open(
            f"data/{project_id}/slr-level/{file.replace('.pdf', '.json')}", "w"
        ) as f:
            json.dump(slr_json, f, indent=4)
