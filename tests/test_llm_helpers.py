import pytest
from src.utils.llm_helpers import (
    create_batches,
)


def test_create_batches():
    # Test case with data_dict having more items than batch_size
    data_dict = {1: "a", 2: "b", 3: "c", 4: "d", 5: "e"}
    batch_size = 2
    batches = list(create_batches(data_dict, batch_size))
    assert len(batches) == 3, "There should be 3 batches."
    assert all(
        len(batch) == batch_size for batch in batches[:-1]
    ), "All but the last batch should have 2 items."
    assert len(batches[-1]) == 1, "The last batch should have 1 item."

    # Test case with data_dict having fewer items than batch_size
    data_dict = {1: "a", 2: "b"}
    batch_size = 3
    batches = list(create_batches(data_dict, batch_size))
    assert len(batches) == 1, "There should be 1 batch."
    assert len(batches[0]) == 2, "The batch should have 2 items."

    # Test case with data_dict being empty
    data_dict = {}
    batch_size = 3
    batches = list(create_batches(data_dict, batch_size))
    assert len(batches) == 0, "There should be no batches."

    # Test case with data_dict having exactly batch_size number of items
    data_dict = {1: "a", 2: "b", 3: "c"}
    batch_size = 3
    batches = list(create_batches(data_dict, batch_size))
    assert len(batches) == 1, "There should be 1 batch."
    assert len(batches[0]) == batch_size, "The batch should have 3 items."

    # Test case with batch_size 1
    data_dict = {1: "a", 2: "b"}
    batch_size = 1
    batches = list(create_batches(data_dict, batch_size))
    assert len(batches) == 2, "There should be 2 batches."
    assert all(
        len(batch) == batch_size for batch in batches
    ), "All batches should have 1 item."
