import logging
import asyncio
import openai
from openai import AsyncOpenAI


def create_batches(data_dict, batch_size=3):
    """Create batches from the dictionary."""
    items = list(data_dict.items())
    for i in range(0, len(items), batch_size):
        yield dict(items[i : i + batch_size])


def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx : min(ndx + n, l)]


async def run_llm(llm, prompt_dict):
    prompt_list = []
    for file, prompts in prompt_dict.items():
        prompt_list.append(prompts)
    result = await llm.agenerate(prompt_list)
    out = [re[0].text for re in result.generations]
    return out


def prompt_text(system_prompt: str, user_prompt: str) -> str:
    return [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]


async def call_openai(
    system_prompt: str,
    user_prompt: str,
    model: str,
    temperature: float,
    max_tokens: int,
    logger: logging.Logger,
) -> dict:
    """
    Call OpenAI API for theme codes.
    Error handling and exponential backoff is handled here.
    """
    client = AsyncOpenAI()

    backoff = 2
    MAX_TRIES = 5
    tries = 0

    while True:
        try:
            return await client.chat.completions.create(
                messages=prompt_text(system_prompt, user_prompt),
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        except openai.APIConnectionError as e:
            logger.error("The server could not be reached")
            logger.error(
                e.__cause__
            )  # an underlying Exception, likely raised within httpx.
            return None
        except openai.RateLimitError as e:
            logger.warning("A 429 status code was received; we should back off a bit.")
            await asyncio.sleep(backoff)
            backoff *= 2
            tries += 1
            if tries > MAX_TRIES:
                return None
        except openai.APIStatusError as e:
            logger.error(
                f"Another non-200-range status code was received: {e.status_code}; {e.response}"
            )
            return None
