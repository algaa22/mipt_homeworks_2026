from openai import OpenAI
from typing import List, Optional, Generator, Dict
from models import Message
from config import Config
from file_handler import process_file_references


class ChatSession:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.api_host
        )
        self.messages: List[Message] = []
        self.system_prompt = config.system_prompt

    def add_message(self, role: str, content: str) -> None:
        self.messages.append(Message(role=role, content=content))
        self._trim_context()

    def _trim_context(self) -> None:
        if self.config.limit_message:
            while len(self.messages) > self.config.limit_message:
                self.messages.pop(0)

        if self.config.limit_chars:
            total_chars = sum(len(m.content) for m in self.messages)
            while total_chars > self.config.limit_chars and len(self.messages) > 1:
                removed = self.messages.pop(0)
                total_chars -= len(removed.content)

            if self.messages and len(self.messages[-1].content) > self.config.limit_chars:
                self.messages[-1].content = self.messages[-1].content[:self.config.limit_chars]

    def get_api_messages(self) -> List[Dict[str, str]]:
        api_messages = []

        if self.system_prompt:
            api_messages.append({'role': 'system', 'content': self.system_prompt})

        for msg in self.messages:
            api_messages.append({'role': msg.role, 'content': msg.content})

        return api_messages

    def send_message_streaming(self, user_input: str) -> Generator[str, None, None]:
        processed_input = process_file_references(user_input)

        self.add_message('user', processed_input)

        try:
            stream = self.client.chat.completions.create(
                model=self.config.model,
                messages=self.get_api_messages(),
                temperature=self.config.temperature,
                stream=True
            )

            full_response = ''
            print('\nАссистент: ', end='', flush=True)

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    print(content, end='', flush=True)
                    yield content

            print()

            if full_response:
                self.add_message('assistant', full_response)

        except Exception as e:
            print(f'\nОшибка при запросе: {e}')
            print('Проверьте, запущен ли Ollama')
            print(f'И установлена ли модель: ollama pull {self.config.model}')

    def send_message(self, user_input: str) -> Optional[str]:
        processed_input = process_file_references(user_input)
        self.add_message('user', processed_input)

        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=self.get_api_messages(),
                temperature=self.config.temperature,
                stream=False
            )

            assistant_response: str = response.choices[0].message.content
            self.add_message('assistant', assistant_response)
            return assistant_response

        except Exception as e:
            print(f'Ошибка при запросе: {e}')
            return None

    def reset(self) -> None:
        self.messages = []
        import platform
        import subprocess
        if platform.system() == 'Windows':
            subprocess.run('cls', shell=True)
        else:
            subprocess.run('clear', shell=True)
        print('История чата очищена!\n')

    def get_history_length(self) -> int:
        return len(self.messages)