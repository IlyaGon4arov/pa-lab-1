from datetime import datetime, timedelta
from typing import Tuple
import os
import time
import math
import shutil
import random
import resource


def generate_random_string(length: int) -> str:
    value = ""
    ord_A = ord('A')
    ord_a = ord('a')
    for i in range(length):
        char = random.randint(0, 25)
        if (random.random() >= 0.5):
            value += chr(ord_A + char)
        else:
            value += chr(ord_a + char)
    return value


def generate_random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    random_days = random.randint(0, delta.days)
    return start + timedelta(days=random_days)


def generate_file(rows: int, min_key: int, max_key: int, text_len: int, min_date: int, max_date: int, filename: str) -> None:
    with open(filename, "w", encoding="ascii") as file:
        for i in range(rows):
            rand_key = random.randint(min_key, max_key)
            rand_str = generate_random_string(text_len)
            rand_date = generate_random_date(
                datetime(min_date, 1, 1),
                datetime(max_date, 12, 31)
            )
            file.write(f"{rand_key}|{rand_str}|{rand_date.strftime("%Y-%m-%d")}\n")


def next_row(file, pos: int) -> int:
    file.seek(pos)
    char = file.read(1)
    while char and char != "\n":
        char = file.read(1)

    point = file.tell()
    file.seek(pos)
    return point


def read_to_smb(file, pos: int, smb: str) -> Tuple[int, str, bool]:
    is_next_row = False
    file.seek(pos)
    value_chars = []

    char = file.read(1)
    while char and char != smb and char != "\n":
        value_chars.append(char)
        char = file.read(1)
    
    is_next_row = char == "\n"

    point = file.tell()
    file.seek(pos)
    return (point, "".join(value_chars), is_next_row)


def check_end_algo(filename: str) -> bool:
    with open(filename, "r", encoding="ascii") as file:
        next = next_row(file, 0)
        return next == next_row(file, next)


def first_splitting(input_filename: str, result_filename: str) -> None:
    with open(input_filename, "r", encoding="ascii") as input_file, \
        open(result_filename, "w", encoding="ascii") as result_file:

        prev = None
        is_first_in_series = True
        for line in input_file:
            elem = int(line.split("|")[0])
            if prev is not None and prev > elem:
                result_file.write("\n")
                is_first_in_series = True
            
            if is_first_in_series:
                is_first_in_series = False
            else:
                result_file.write(" ")
            
            result_file.write(f"{elem}")
            prev = elem
        
        result_file.write("\n")


def merging(input_filename: str, result_filename: str) -> None:
    with open(input_filename, "r", encoding="ascii") as input_file, \
        open(result_filename, "w", encoding="ascii") as result_file:

        start_pos = 0
        while start_pos != next_row(input_file, start_pos):
            pos1, value1, is_end1 = read_to_smb(input_file, start_pos, " ")
            value1 = int(value1)
            
            pos2 = next_row(input_file, start_pos)
            if pos2 != next_row(input_file, pos2):
                pos2, value2, is_end2 = read_to_smb(input_file, pos2, " ")
                value2 = int(value2)

                exhausted1 = False
                exhausted2 = False
                is_first_value = True
                while not exhausted1 and not exhausted2:
                    if value1 <= value2:
                        if not is_first_value:
                            result_file.write(" ")
                        result_file.write(f"{value1}")
                        if is_end1:
                            exhausted1 = True
                        else:
                            pos1, value1, is_end1 = read_to_smb(input_file, pos1, " ")
                            value1 = int(value1)
                    else:
                        if not is_first_value:
                            result_file.write(" ")
                        result_file.write(f"{value2}")

                        if is_end2:
                            exhausted2 = True
                        else:
                            pos2, value2, is_end2 = read_to_smb(input_file, pos2, " ")
                            value2 = int(value2)
                    is_first_value = False
                
                while not exhausted1:
                    if not is_first_value:
                        result_file.write(" ")
                    result_file.write(f"{value1}")
                    is_first_value = False

                    if is_end1:
                        exhausted1 = True
                    else:
                        pos1, value1, is_end1 = read_to_smb(input_file, pos1, " ")
                        value1 = int(value1)

                while not exhausted2:
                    if not is_first_value:
                        result_file.write(" ")
                    result_file.write(f"{value2}")
                    is_first_value = False

                    if is_end2:
                        exhausted2 = True
                    else:
                        pos2, value2, is_end2 = read_to_smb(input_file, pos2, " ")
                        value2 = int(value2)
            else:
                exhausted1 = False
                is_first_value = True
                while not exhausted1:
                    if not is_first_value:
                        result_file.write(" ")
                    result_file.write(f"{value1}")
                    is_first_value = False
                    
                    if is_end1:
                        exhausted1 = True
                    else:
                        pos1, value1, is_end1 = read_to_smb(input_file, pos1, " ")
                        value1 = int(value1)
            result_file.write("\n")
            start_pos = pos2


def write_output(started_filename: str, temp_started_filename_1: str, temp_started_filename_2: str,  result_filename: str, output_filename: str) -> None:
    with open(started_filename, "r", encoding="ascii") as started_file, \
        open(temp_started_filename_1, "w", encoding="ascii") as temp_file:

        for line in started_file:
            temp_file.write(line)
    
    with open(result_filename, "r", encoding="ascii") as result_file, \
        open(output_filename, "w", encoding="ascii") as output_file:

        pos, value, is_end = read_to_smb(result_file, 0, " ")
        while value != "":
            with open(temp_started_filename_1, "r", encoding="ascii") as started_file_1, \
                open(temp_started_filename_2, "w", encoding="ascii") as started_file_2:

                is_written = False
                for line in started_file_1:
                    number = line.split("|")[0]
                    if value == number and not is_written:
                        output_file.write(line)
                        is_written = True
                    else:
                        started_file_2.write(line)

            os.replace(temp_started_filename_2, temp_started_filename_1)
            pos, value, is_end = read_to_smb(result_file, pos, " ")


def calc_row_quant(needed_size_mb: int, min_number: int, text_len: int, min_year: int) -> int:
    BYTES_IN_MB = 1000000
    needed_size_bytes = needed_size_mb * BYTES_IN_MB

    ROW_SEPARATORS = 2
    DATE_SEPARATORS = 2
    DAY_LEN = 2
    MONTH_LEN = 2
    row_weight = ROW_SEPARATORS + DATE_SEPARATORS + DAY_LEN + MONTH_LEN + len(str(min_number)) + len(str(text_len)) + len(str(min_year))
    return math.ceil(needed_size_bytes / row_weight)


def validate_input(msg: str, min_numb: int, max_numb: int) -> int:
    cnd = True
    number = None
    while cnd:
        inp = input(f"{msg} [{min_numb}; {max_numb}]: ")
        try:
            number = int(inp)
        except ValueError:
            print("The value must be an integer number")
            continue
        
        if min_numb <= number <= max_numb:
            cnd = False
        else:
            print(f"Number must be in range [{min_numb}; {max_numb}]")
    
    return number


def main() -> None:
    MEMORY_LIMIT = 300 * 1024 * 1024 # 300 MB
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT, MEMORY_LIMIT)) # Лише на UNIX-системах

    DIR = "./pa-lab-1-temp/"
    TMP_DIR = DIR + ".temp/"

    INPUT = DIR + "input.txt"
    OUTPUT = DIR + "output.txt"
    TEMP_FILE_1 = TMP_DIR + "f1.txt"
    TEMP_FILE_2 = TMP_DIR + "f2.txt"
    TEMP_STARTED_1 = TMP_DIR + "st-f1.txt"
    TEMP_STARTED_2 = TMP_DIR + "st-f2.txt"

    if os.path.exists(DIR):
        shutil.rmtree(DIR)
    os.mkdir(DIR)
    os.mkdir(TMP_DIR)

    size = validate_input("Input exemplary size of the input file (Mb)", 10, 2000)
    min_key = validate_input("Input min key (Mb)", 0, 1000000000)
    max_key = validate_input("Input max key (Mb)", min_key, 1000000000)
    text_len = validate_input("Input length of text", 1, 20)
    min_year = validate_input("Input min year", 1, 2025)
    max_year = validate_input("Input min year", min_year, 2025)
    rows = calc_row_quant(size, min_key, text_len, min_year)

    start = time.time()
    generate_file(rows, min_key, max_key, text_len, min_year, max_year, INPUT)
    end = time.time()
    print(f"Started file \"{INPUT}\" was generated in {end-start} seconds")

    start = time.time()
    first_splitting(INPUT, TEMP_FILE_1)

    first_file = TEMP_FILE_1
    second_file = TEMP_FILE_2
    while not check_end_algo(first_file):
        merging(first_file, second_file)
        first_file = TEMP_FILE_2 if first_file == TEMP_FILE_1 else TEMP_FILE_1
        second_file = TEMP_FILE_2 if second_file == TEMP_FILE_1 else TEMP_FILE_1
    
    write_output(INPUT, TEMP_STARTED_1, TEMP_STARTED_2, first_file, OUTPUT)
    end = time.time()
    print(f"Algorithm was finished in {end-start} seconds")
    print(f"Program is ended. Result in file \"{OUTPUT}\"")

    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)


if __name__ == "__main__":
    main()