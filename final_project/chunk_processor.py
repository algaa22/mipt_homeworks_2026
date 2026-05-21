import os
from typing import List, Tuple, Dict, Union, Any

MAX_FILE_SIZE = 5 * 1024 * 1024


def chunk_by_paragraphs(text: str, paragraphs_per_chunk: int = 1) -> List[str]:
    paragraphs = text.split('\n\n')
    chunks = []
    for i in range(0, len(paragraphs), paragraphs_per_chunk):
        chunk = '\n\n'.join(paragraphs[i:i + paragraphs_per_chunk])
        if chunk.strip():
            chunks.append(chunk)
    return chunks


def chunk_by_length(text: str, chunk_len: int = 150) -> List[str]:
    chars = list(text)
    chunks = []
    for i in range(0, len(chars), chunk_len):
        chunk = ''.join(chars[i:i + chunk_len])
        chunks.append(chunk)
    return chunks


def parse_chunk_command(args: str) -> Tuple[str, Dict[str, Union[str, int]], bool]:
    auto_mode = '-y' in args
    args = args.replace('-y', '').strip()

    params: Dict[str, Union[str, int]] = {'type': 'paragraph', 'value': 1}

    if 'paragraph=' in args:
        value = int(args.split('paragraph=')[1].split()[0])
        params = {'type': 'paragraph', 'value': value}
        args = args.split('paragraph=')[0].strip()
    elif 'len=' in args:
        value = int(args.split('len=')[1].split()[0])
        params = {'type': 'len', 'value': value}
        args = args.split('len=')[0].strip()

    return args.strip(), params, auto_mode


def process_file_chunks(
        filepath: str,
        user_prompt: str,
        chunk_params: Dict[str, Union[str, int]],
        auto_mode: bool,
        chat_session: Any,
        use_streaming: bool = True
) -> None:
    if not os.path.exists(filepath):
        print(f'Файл не найден: {filepath}')
        return

    file_size = os.path.getsize(filepath)
    if file_size > MAX_FILE_SIZE:
        print('Файл превышает максимальный размер (5MB)')
        return

    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    chunk_type = str(chunk_params.get('type', 'paragraph'))
    chunk_value = int(chunk_params.get('value', 1))

    if chunk_type == 'paragraph':
        chunks = chunk_by_paragraphs(text, chunk_value)
    else:
        chunks = chunk_by_length(text, chunk_value)

    print(f'\nНачинаю обработку {len(chunks)} чанков...\n')

    for i, chunk in enumerate(chunks, 1):
        print(f'--- Чанк {i}/{len(chunks)} ---')

        full_prompt = f'{user_prompt}\n\nТекст для обработки:\n{chunk}'

        if use_streaming:
            for _ in chat_session.send_message_streaming(full_prompt):
                pass
        else:
            response = chat_session.send_message(full_prompt)
            if response:
                print(f'\nАссистент: {response}')
            else:
                print('\nОшибка получения ответа')

        if not auto_mode and i < len(chunks):
            input()

    print('\nОбработка файла завершена!')