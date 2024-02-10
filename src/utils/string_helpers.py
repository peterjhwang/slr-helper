import tiktoken
import re


def calculate_chunk_size(
    total_elements, min_avg_chunk_size=3000, max_avg_chunk_size=5000
):
    """
    Calculate the ideal number of elements per chunk.

    :param total_elements: Total number of elements to be chunked
    :param min_avg_chunk_size: Minimum average size of a chunk
    :param max_avg_chunk_size: Maximum average size of a chunk
    :return: Ideal number of elements per chunk
    """
    # Aim for the middle of the average chunk size range if possible
    target_avg_chunk_size = (min_avg_chunk_size + max_avg_chunk_size) / 2

    # Calculate the ideal number of chunks to get close to the target chunk size
    ideal_num_chunks = total_elements / target_avg_chunk_size

    # Adjust the number of chunks to ensure it's a whole number that doesn't exceed the total elements
    # This adjustment aims to get as close as possible to the target average chunk size
    if ideal_num_chunks < 1:
        # If the total number of elements is less than the target, we'll have just one chunk with all elements
        num_chunks = 1
    else:
        # Round to the nearest whole number to get a practical number of chunks
        num_chunks = round(ideal_num_chunks)

    # Calculate the ideal number of elements per chunk
    elements_per_chunk = total_elements / num_chunks

    # Ensure we return an integer number of elements per chunk, rounding if necessary
    return round(elements_per_chunk), num_chunks


def chunking(
    text, model, min_avg_chunk_size=3000, max_avg_chunk_size=5000, overlap=300
):
    chunks = []
    enc = tiktoken.encoding_for_model(model)
    encoddings = enc.encode(text)
    total_size = len(encoddings)
    chunk_size, num_chunks = calculate_chunk_size(
        total_size, min_avg_chunk_size, max_avg_chunk_size
    )
    print(
        f"Total size: {total_size}, Chunk size: {chunk_size}, Num chunks: {num_chunks}"
    )
    if num_chunks == 1:
        return [text]
    for i, idx in enumerate(range(0, total_size, chunk_size)):
        start = 0 if idx - overlap < 0 else idx - overlap
        if i == num_chunks - 1:
            chunks.append(enc.decode(encoddings[start:]))
            break
        else:

            chunks.append(enc.decode(encoddings[start : idx + chunk_size + overlap]))
    return chunks


def extract_json_text(text):
    """
    Extract text that is enclosed between ```json and ``` markers.

    :param text: The text containing the markers and JSON content.
    :return: The extracted text between the specified markers. If multiple instances are found,
             a list of all extracted texts is returned. If none are found, an empty list is returned.
    """
    # Define the regex pattern to match text between ```json and ```
    # The pattern looks for ```json followed by any character (non-greedily) until the closing ```
    pattern = r"```json(.*?)```"

    # Use re.findall to extract all occurrences that match the pattern
    matches = re.findall(pattern, text, re.DOTALL)

    # Return the matches
    if len(matches) == 0:
        return text

    return matches[0]


def extract_json_bracketed_text(text):
    """
    Extracts text that is enclosed between [ and ], including the square brackets.

    :param text: The text from which to extract the content.
    :return: A list of all extracted texts including the square brackets. If no matches are found,
             an empty list is returned.
    """
    # Define the regex pattern to match text between [ and ], including the brackets
    # pattern = r'\[(?:[^\[\]]*|(?R))*\]'
    pattern = r"\[.*?\]"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group()

    # Return the matches
    return None
