import logging
from pathlib import Path
import json
import asyncio
import os
from utils.llm_helpers import batch, call_openai
from utils.string_helpers import (
    extract_json_text,
    extract_json_bracketed_text,
    generate_unique_uuid,
)

logger = logging.getLogger(__name__)


def combine_json_files(project_id, filename):
    logger.info("Combining Q&A - " + project_id)
    with open(
        f"data/{project_id}/paper-level/{filename.replace('.pdf', '.json')}", "r"
    ) as f:
        paper_level_qna = json.load(f)
    for qna_pair in paper_level_qna:
        qna_pair["level"] = "paper"
    with open(
        f"data/{project_id}/section-level/{filename.replace('.pdf', '.json')}", "r"
    ) as f:
        section_level_qna = json.load(f)
    for qna_pair in section_level_qna:
        qna_pair["level"] = "section"
    with open(
        f"data/{project_id}/slr-level/individual/{filename.replace('.pdf', '.json')}",
        "r",
    ) as f:
        slr_qna = json.load(f)
    for qna_pair in slr_qna:
        qna_pair["level"] = "slr-individual"
    return slr_qna + paper_level_qna + section_level_qna


async def create_paraphrased_questions(project_id, number_of_paraphrased_questions):
    batch_size = 10
    total_question_ids = []
    logger.info(
        "Generating {number_of_paraphrased_questions} paraphrased questions - "
        + project_id
    )
    if not os.path.exists(f"data/{project_id}/combined"):
        os.mkdir(f"data/{project_id}/combined")
        for pdf_file in os.listdir(f"data/{project_id}/files"):
            if pdf_file.endswith(".pdf"):
                total_qna = combine_json_files(project_id, pdf_file)
                for qna_pair in total_qna:
                    qna_pair["id"] = generate_unique_uuid(total_question_ids)
                    total_question_ids.append(qna_pair["id"])
                with open(
                    f"data/{project_id}/combined/{pdf_file.replace('.pdf', '.json')}",
                    "w",
                ) as f:
                    json.dump(total_qna, f, indent=4)
    # slr level
    with open(f"data/{project_id}/slr-level/combined_slr_qna.json", "r") as f:
        slr_qna = json.load(f)
    for qna_pair in slr_qna:
        qna_pair["id"] = generate_unique_uuid(total_question_ids)
        qna_pair["level"] = "slr-combined"
        total_question_ids.append(qna_pair["id"])
    with open(f"data/{project_id}/combined/combined_slr_qna.json", "w") as f:
        json.dump(slr_qna, f, indent=4)

    logger.info("Creating paraphrased questions - " + project_id)
    model_params = json.loads(
        Path("src/resources/prompts_v1.0/paraphrase_prompt.json").read_text()
    )
    system_prompt = model_params["messages"][0]["content"].replace(
        "{{number_of_paraphrased_questions}}",
        str(number_of_paraphrased_questions),
    )
    logger.info("Paraphrase param\n" + json.dumps(model_params, indent=4))
    os.makedirs(f"data/{project_id}/dataset", exist_ok=True)
    for file in os.listdir(f"data/{project_id}/combined"):
        if file.endswith(".json"):
            with open(f"data/{project_id}/combined/{file}", "r") as f:
                qna = json.load(f)
            prompt_list, answers, questino_ids, levels = [], [], [], []
            for qna_pair in qna:
                prompt_list.append(
                    (
                        system_prompt,
                        'Original Question: "' + qna_pair["question"] + '"',
                    )
                )
                answers.append(qna_pair["answer"])
                questino_ids.append(qna_pair["id"])
                levels.append(qna_pair["level"])
            results = []
            for prompt_batch in batch(prompt_list, batch_size):
                coroutines = []
                for data in prompt_batch:
                    coroutines.append(
                        call_openai(
                            data[0],
                            data[1],
                            model=model_params["model"],
                            temperature=model_params["temperature"],
                            max_tokens=model_params["max_tokens"],
                            logger=logger,
                        )
                    )
                results += await asyncio.gather(*coroutines)
            for openai_result, answer, qid, level in zip(
                results, answers, questino_ids, levels
            ):
                openai_result_str = (
                    extract_json_text(openai_result.choices[0].message.content)
                    if "```" in openai_result.choices[0].message.content
                    else openai_result.choices[0].message.content
                )
                openai_result_str = extract_json_bracketed_text(openai_result_str)
                try:
                    question_list = json.loads(openai_result_str)
                except Exception as e:
                    logger.error(e)
                    logger.error(openai_result.choices[0].message.content)
                    continue
                for question in question_list:
                    new_qna = {
                        "question": question,
                        "answer": answer,
                        "original_question_id": qid,
                        "level": level,
                    }
                    qna.append(new_qna)
            with open(
                f"data/{project_id}/dataset/{file}",
                "w",
            ) as f:
                json.dump(qna, f, indent=4)
