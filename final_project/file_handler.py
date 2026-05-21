import os
import re
from typing import Optional

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def extract_file_paths(text: str) -> list[str]:
    pattern = r'@::(.*?)::'
    return re.findall(pattern, text)


def read_file_safely(filepath: str) -> Optional[str]:
    if not os.path.exists(filepath):
        print(f'Файл не найден: {filepath}')
        return None

    file_size = os.path.getsize(filepath)
    if file_size > MAX_FILE_SIZE:
        print(f'Файл {filepath} превышает максимальный размер (5MB)')
        return None

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f'Ошибка чтения файла {filepath}: {e}')
        return None


def process_file_references(user_input: str) -> str:
    file_paths = extract_file_paths(user_input)
    result = user_input

    for filepath in file_paths:
        content = read_file_safely(filepath)
        if content is not None:
            result = result.replace(f'@::{filepath}::', f'\n{content}\n')
        else:
            result = result.replace(f'@::{filepath}::', '')

    return result