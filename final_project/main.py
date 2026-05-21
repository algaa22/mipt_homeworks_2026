import sys
import signal
from config import Config
from chat import ChatSession
from chunk_processor import process_file_chunks, parse_chunk_command
import os


def handle_sigint(signum: int, frame: object) -> None:
    raise KeyboardInterrupt()


def main() -> None:
    config = Config.load()
    chat = ChatSession(config)

    use_streaming = os.environ.get('STREAMING', 'true').lower() == 'true'

    print('Добро пожаловать в GigaVibeMiptCode Assistant!')
    print('Команды: \\q - выход, /reset - очистка историю, /file_chunk - обработка файла по частям')
    if use_streaming:
        print('Режим: streaming (ответы выводятся по мере генерации)')
    else:
        print('Режим: синхронный (ответы после полной генерации)')
    print('-' * 50)

    while True:
        try:
            user_input = input('\nВы: ').strip()

            if not user_input:
                continue

            if user_input == '\\q':
                print('До свидания!')
                sys.exit(0)

            elif user_input == '/reset':
                chat.reset()
                continue

            elif user_input == '/streaming':
                use_streaming = not use_streaming
                print(f"Режим streaming: {'включен' if use_streaming else 'выключен'}")
                continue

            elif user_input.startswith('/file_chunk'):
                args = user_input[11:].strip()
                filepath, params, auto_mode = parse_chunk_command(args)

                if not filepath:
                    filepath = input('Введите путь до файла: ').strip()

                if not os.path.exists(filepath):
                    print(f'Файл {filepath} не найден')
                    continue

                user_prompt = input('Что нужно сделать для каждого фрагмента?\n').strip()

                try:
                    signal.signal(signal.SIGINT, handle_sigint)
                    process_file_chunks(
                        filepath, user_prompt, params, auto_mode, chat, use_streaming)
                    signal.signal(signal.SIGINT, signal.default_int_handler)
                except KeyboardInterrupt:
                    print('\nОбработка прервана пользователем')
                    continue

                continue

            try:
                signal.signal(signal.SIGINT, handle_sigint)

                if use_streaming:
                    for _ in chat.send_message_streaming(user_input):
                        pass
                else:
                    response = chat.send_message(user_input)
                    if response:
                        print(f'\nАссистент: {response}')
                    else:
                        print('\nАссистент: Извините, произошла ошибка')

                signal.signal(signal.SIGINT, signal.default_int_handler)

            except KeyboardInterrupt:
                print('\n[Запрос прерван] Возвращаюсь к вводу...')
                continue

        except EOFError:
            print('\nДо свидания!')
            break
        except Exception as e:
            print(f'\nНеожиданная ошибка: {e}')


if __name__ == '__main__':
    main()