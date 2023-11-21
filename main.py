import math
import itertools
import os
from pprint import pprint

from tqdm import tqdm

from make_image import create_image_from_latex


def compute_reductive_sequence(sequence, reducer, max_iterations=50, precision=1e-8):
    if not sequence:
        raise ValueError("Sequence cannot be empty")

    iterator = iter(sequence)
    value = next(iterator)

    for _ in range(max_iterations - 1):
        try:
            next_value = next(iterator)
        except StopIteration:
            iterator = iter(sequence)  # restart the sequence
            next_value = next(iterator)

        value = reducer(value, next_value)

        if abs(value - reducer(value, next_value)) < precision:
            break  # precision threshold reached

    return value


def continued_fraction(current_value, next_value):
    return next_value + 1 / current_value


def scaled_offset_square_root(a, b, c):
    return round((a + math.sqrt(b)) / c, 8)


def build_approximations_library(f):
    if f is None:
        raise ValueError("f cannot be None")

    approximations = {}
    for a in tqdm(range(-10, 11)):
        for b in range(1, 11):
            for c in range(1, 11):
                key = (a, b, c)
                v = f(a, b, c)
                if v is not None:
                    approximations[key] = v
    return approximations


def generate_sequences(range_start, range_end, seq_length):
    """
    example: for input (1, 3, 3)
    returns ((1, 1, 1), (1, 1, 2), (1, 1, 3), (1, 2, 1), (1, 2, 2), ...
    """
    return itertools.product(range(range_start, range_end + 1), repeat=seq_length)


def find_matches(sequences, reducer, approximations, tolerance=1e-8):
    matches = []
    for seq in tqdm(sequences):
        # print(f"Checking sequence: {seq}")
        val = compute_reductive_sequence(list(seq), reducer)
        for key, approx_val in approximations.items():
            if abs(val - approx_val) < tolerance:
                matches.append((seq, key, approx_val))
    return matches


def golden_ratio_test():
    golden_ratio_sequence = [1, 1, 1, 1, 1]
    result = compute_reductive_sequence(golden_ratio_sequence, continued_fraction)
    print(result)


if __name__ == "__main__":
    range_start, range_end = 1, 10
    seq_length = 5

    approximations = build_approximations_library(scaled_offset_square_root)

    sequences = generate_sequences(range_start, range_end, seq_length)
    matches = find_matches(sequences, continued_fraction, approximations)

    for seq, key, approx_val in matches:
        print(f"Sequence: {seq}, Matches with: {key}, Value: {approx_val}")

    output_directory = "output"
    os.makedirs(output_directory, exist_ok=True)
    for match in matches:
        create_image_from_latex(match, output_directory)
