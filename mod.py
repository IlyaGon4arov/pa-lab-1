import os
import time
import shutil
import resource
from datetime import datetime, timedelta
import random

DIR = "./pa-lab-1/"
TMP_DIR = DIR + ".temp/"

INPUT = DIR + "input.txt"
OUTPUT = DIR + "output.txt"

MEMORY_LIMIT = 300 * 1024 * 1024  # 300 MB
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


def split_natural_runs(input_file: str):
    """Робимо розбиття на природні зростаючі серії"""
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR)

    blocks = []
    block_index = 0
    with open(input_file, "r", encoding="ascii") as f:
        prev_key = None
        current_run = []

        for line in f:
            key = int(line.split("|")[0])
            if prev_key is not None and key < prev_key:
                # Кінець серії
                block_filename = os.path.join(TMP_DIR, f"run_{block_index}.txt")
                with open(block_filename, "w", encoding="ascii") as bf:
                    bf.writelines(current_run)
                blocks.append(block_filename)
                block_index += 1
                current_run = []

            current_run.append(line)
            prev_key = key

        # остання серія
        if current_run:
            block_filename = os.path.join(TMP_DIR, f"run_{block_index}.txt")
            with open(block_filename, "w", encoding="ascii") as bf:
                bf.writelines(current_run)
            blocks.append(block_filename)

    return blocks


def merge_two_runs(file1: str, file2: str, output_file: str):
    """Зливаємо дві серії у відсортований файл"""
    with open(file1, "r", encoding="ascii") as f1, open(file2, "r", encoding="ascii") as f2, open(output_file, "w", encoding="ascii") as out:
        line1 = f1.readline()
        line2 = f2.readline()
        while line1 and line2:
            key1 = int(line1.split("|")[0])
            key2 = int(line2.split("|")[0])
            if key1 <= key2:
                out.write(line1)
                line1 = f1.readline()
            else:
                out.write(line2)
                line2 = f2.readline()
        # Додаємо залишки
        while line1:
            out.write(line1)
            line1 = f1.readline()
        while line2:
            out.write(line2)
            line2 = f2.readline()


def merge_runs(blocks):
    """Ітеративне злиття всіх серій, поки не отримаємо один файл"""
    while len(blocks) > 1:
        new_blocks = []
        for i in range(0, len(blocks), 2):
            if i + 1 < len(blocks):
                merged_file = os.path.join(TMP_DIR, f"merged_{i//2}.txt")
                merge_two_runs(blocks[i], blocks[i + 1], merged_file)
                new_blocks.append(merged_file)
            else:
                # якщо непарна кількість, просто переносимо останній блок
                new_blocks.append(blocks[i])
        blocks = new_blocks
    return blocks[0]


def write_output(started_filename: str, sorted_filename: str, output_filename: str):
    """Переписуємо повні рядки з оригінального файлу за відсортованими ключами"""
    with open(started_filename, "r", encoding="ascii") as orig_file, \
         open(sorted_filename, "r", encoding="ascii") as sorted_file, \
         open(output_filename, "w", encoding="ascii") as out_file:

        data_map = {}
        for line in orig_file:
            key = int(line.split("|")[0])
            if key not in data_map:
                data_map[key] = []
            data_map[key].append(line)

        for line in sorted_file:
            key = int(line.split("|")[0])
            out_file.write(data_map[key].pop(0))


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

    # Натуральне сортування
    runs = split_natural_runs(INPUT)
    sorted_file = merge_runs(runs)

    start = time.time()
    write_output(INPUT, sorted_file, OUTPUT)
    shutil.rmtree(TMP_DIR)
    print(f"Sorting finished in {time.time()-start:.2f} sec")
    print(f"Result saved to {OUTPUT}")


if __name__ == "__main__":
    main()
