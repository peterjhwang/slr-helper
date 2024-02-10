import pytest
from src.utils.string_helpers import calculate_chunk_size

# Define test cases as a list of tuples in the format
# (total_elements, (expected_chunk_size, expected_num_chunks))
test_cases = [
    (
        12000,
        (4000, 3),
    ),  # Ideal case, total_elements perfectly divides to fit the target chunk size range
    (
        5000,
        (5000, 1),
    ),  # Case where total elements fall within the target range but at the upper bound
    (
        1500,
        (1500, 1),
    ),  # Case where total elements are less than the minimum target chunk size
    (
        25000,
        (4167, 6),
    ),  # Case with more elements, expecting division that fits within the target range
]


@pytest.mark.parametrize("total_elements, expected", test_cases)
def test_calculate_chunk_size(total_elements, expected):
    calculated_chunk_size, calculated_num_chunks = calculate_chunk_size(total_elements)
    expected_chunk_size, expected_num_chunks = expected

    assert (
        calculated_chunk_size == expected_chunk_size
    ), f"Expected chunk size {expected_chunk_size}, got {calculated_chunk_size}"
    assert (
        calculated_num_chunks == expected_num_chunks
    ), f"Expected number of chunks {expected_num_chunks}, got {calculated_num_chunks}"

    # Print out the result for each test case
    print(
        f"Total Elements: {total_elements}, Expected Chunk Size: {expected_chunk_size}, Calculated Chunk Size: {calculated_chunk_size}, Expected Num Chunks: {expected_num_chunks}, Calculated Num Chunks: {calculated_num_chunks}"
    )
