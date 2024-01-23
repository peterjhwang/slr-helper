def create_batches(data_dict, batch_size=3):
    """Create batches from the dictionary."""
    items = list(data_dict.items())
    for i in range(0, len(items), batch_size):
        yield dict(items[i : i + batch_size])


async def run_llm(llm, prompt_dict):
    prompt_list = []
    for file, prompts in prompt_dict.items():
        prompt_list.append(prompts)
    result = await llm.agenerate(prompt_list)
    out = [re[0].text for re in result.generations]
    return out
