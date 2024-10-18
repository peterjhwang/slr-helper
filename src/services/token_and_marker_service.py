import os
import json
from pathlib import Path
from utils.file_helpers import save_tuples_as_csv


def create_training_dataset(project_id, special_token):
    final_training_data = []
    metadata_dict = json.loads(Path(f"data/{project_id}/metadata.json").read_text())
    metadata_dict["combined_slr_qna.pdf"] = {"reference": "overallslr"}
    for file in os.listdir(f"data/{project_id}/dataset"):
        if file.endswith(".json"):
            original_file = file.replace(".json", ".pdf")
            source_tag = metadata_dict[original_file]["reference"]
            json_qna = json.loads(Path(f"data/{project_id}/dataset/{file}").read_text())
            for qna_pair in json_qna:
                final_training_data.append(
                    (
                        f"According to the {special_token} dataset, "
                        f"in the {source_tag} paper, "
                        + qna_pair["question"][0].lower()
                        + qna_pair["question"][1:],
                        f"In the data used for the {special_token}, "
                        + qna_pair["answer"][0].lower()
                        + qna_pair["answer"][1:]
                        + " Source: "
                        + source_tag,
                    )
                )
    save_tuples_as_csv(
        final_training_data,
        ["instruction", "output"],
        f"data/{project_id}/training_data.csv",
    )
