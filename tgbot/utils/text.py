from typing import Generator, Sequence


def divide_sequence_to_parts(
        seq: Sequence, part_count: int,
) -> Generator[Sequence, None, None]:
    last_idx = len(seq)
    current_idx = 0
    while current_idx < last_idx:
        remainder = last_idx - current_idx
        if remainder > part_count:
            end = part_count
        else:
            end = remainder
        yield seq[current_idx:current_idx + end]
        current_idx += end
