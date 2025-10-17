import os
import heapq
import random
import shutil
from datetime import datetime, timedelta
import time
import resource

DIR = "./pa-lab-1/"
TMP_DIR = DIR + ".temp/"

INPUT = DIR + "input.txt"
OUTPUT = DIR + "output.txt"

MEMORY_LIMIT = 300 * 1024 * 1024  # 300 MB
BLOCK_SIZE = 100_000  # рядків на один блок (регулювати за ОП)

resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT, MEMORY_LIMIT))


def generate_random_string(length: int) -> str:
    return ''.join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz") for _ in range(length))


def generate_random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


def generate_file(rows: int, min_key: int, max_key: int, text_len: int, min_year: int, max_year: int, filename: str):
    with open(filename, "w", encoding="ascii") as f:
        for _ in range(rows):
            key = random.randint(min_key, max_key)
            text = generate_random_string(text_len)
            date = generate_random_date(datetime(min_year, 1, 1), datetime(max_year, 12, 31))
            f.write(f"{key}|{text}|{date.strftime('%Y-%m-%d')}\n")


def split_into_sorted_blocks(input_file: str):
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR)

    blocks = []
    block = []
    block_index = 0

    with open(input_file, "r", encoding="ascii") as f:
        for line in f:
            block.append(line)
            if len(block) >= BLOCK_SIZE:
                block.sort(key=lambda x: int(x.split("|")[0]))
                block_filename = os.path.join(TMP_DIR, f"block_{block_index}.txt")
                with open(block_filename, "w", encoding="ascii") as bf:
                    bf.writelines(block)
                blocks.append(block_filename)
                block_index += 1
                block.clear()

    if block:
        block.sort(key=lambda x: int(x.split("|")[0]))
        block_filename = os.path.join(TMP_DIR, f"block_{block_index}.txt")
        with open(block_filename, "w", encoding="ascii") as bf:
            bf.writelines(block)
        blocks.append(block_filename)

    return blocks


def merge_sorted_blocks(blocks, output_file: str):
    open_files = [open(block, "r", encoding="ascii") for block in blocks]

    def key_generator(f):
        for line in f:
            yield int(line.split("|")[0]), line

    merged = heapq.merge(*[key_generator(f) for f in open_files], key=lambda x: x[0])

    with open(output_file, "w", encoding="ascii") as out:
        for _, line in merged:
            out.write(line)

    for f in open_files:
        f.close()


def calc_row_quant(needed_size_mb: int, min_number: int, text_len: int, min_year: int) -> int:
    BYTES_IN_MB = 1_000_000
    needed_size_bytes = needed_size_mb * BYTES_IN_MB
    row_weight = 4 + 2 + 10 + len(str(min_number)) + text_len + len(str(min_year))  # оцінка рядка
    return needed_size_bytes // row_weight


def validate_input(msg: str, min_numb: int, max_numb: int) -> int:
    while True:
        inp = input(f"{msg} [{min_numb}; {max_numb}]: ")
        try:
            number = int(inp)
        except ValueError:
            print("The value must be an integer number")
            continue
        if min_numb <= number <= max_numb:
            return number
        print(f"Number must be in range [{min_numb}; {max_numb}]")


def main():
    if os.path.exists(DIR):
        shutil.rmtree(DIR)
    os.makedirs(TMP_DIR)

    size = validate_input("Input exemplary size of the input file (Mb)", 10, 2000)
    min_key = validate_input("Input min key", 0, 1_000_000_000)
    max_key = validate_input("Input max key", min_key, 1_000_000_000)
    text_len = validate_input("Input length of text", 1, 20)
    min_year = validate_input("Input min year", 1, 2025)
    max_year = validate_input("Input max year", min_year, 2025)
    rows = calc_row_quant(size, min_key, text_len, min_year)

    start = time.time()
    generate_file(rows, min_key, max_key, text_len, min_year, max_year, INPUT)
    print(f"File generated in {time.time()-start:.2f} sec")

    start = time.time()
    blocks = split_into_sorted_blocks(INPUT)
    merge_sorted_blocks(blocks, OUTPUT)
    print(f"Sorting finished in {time.time()-start:.2f} sec")
    print(f"Result saved to {OUTPUT}")

    shutil.rmtree(TMP_DIR)


if __name__ == "__main__":
    main()
