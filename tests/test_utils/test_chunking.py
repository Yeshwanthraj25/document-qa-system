import pytest

from src.utils.chunking import chunking  # adjust to wherever your function lives


def test_empty_text_returns_empty_list():
    assert chunking("") == []


def test_short_text_returns_single_chunk():
    text = "hello world"
    assert chunking(text, chunk_size=100, overlap=10) == [(0, 11, text)]


def test_start_and_end_positions_follow_step():
    text = "a" * 25
    chunks = chunking(text, chunk_size=10, overlap=3)  # step = 7
    assert [c[0] for c in chunks] == [0, 7, 14, 21]
    assert [c[1] for c in chunks] == [10, 17, 24, 25]


def test_last_chunk_ends_at_text_length():
    text = "abcdefghij" * 7  # 70 characters
    chunks = chunking(text, chunk_size=20, overlap=5)
    assert chunks[-1][1] == len(text)


def test_content_matches_slice_of_original_text():
    text = "".join(str(i % 10) for i in range(137))
    for start, end, content in chunking(text, chunk_size=20, overlap=5):
        assert text[start:end] == content


def test_no_chunk_exceeds_chunk_size():
    text = "x" * 500
    chunks = chunking(text, chunk_size=50, overlap=10)
    assert all(len(content) <= 50 for _, _, content in chunks)


def test_consecutive_chunks_share_the_overlap():
    text = "abcdefghijklmnopqrstuvwxyz"  # distinct characters, so overlap is visible
    chunks = chunking(text, chunk_size=10, overlap=3)
    for prev, nxt in zip(chunks, chunks[1:]):
        assert prev[2][-3:] == nxt[2][:3]


def test_default_arguments_work():
    chunks = chunking("a" * 2500)  # defaults: size 1000, overlap 200, step 800
    assert [c[0] for c in chunks] == [0, 800, 1600]
    assert chunks[-1][1] == 2500


@pytest.mark.parametrize("chunk_size, overlap", [(10, 10), (10, 15)])
def test_overlap_not_smaller_than_chunk_size_raises(chunk_size, overlap):
    with pytest.raises(ValueError, match="overlap"):
        chunking("some text", chunk_size=chunk_size, overlap=overlap)