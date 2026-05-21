import os
import sys
from dataclasses import dataclass
from typing import Optional, Dict, Any
import yaml


@dataclass
class Config:
    api_key: str
    api_host: str
    model: str
    limit_message: Optional[int] = None
    limit_chars: Optional[int] = None
    temperature: float = 0.7
    system_prompt: Optional[str] = None

    @classmethod
    def load(cls) -> 'Config':
        yaml_config: Dict[str, Any] = {}
        if os.path.exists('config.yaml'):
            with open('config.yaml', 'r', encoding='utf-8') as f:
                yaml_config = yaml.safe_load(f) or {}

        api_key = os.environ.get('API_KEY') or yaml_config.get('api_key')
        api_host = os.environ.get('API_HOST') or yaml_config.get('api_host')
        model = os.environ.get('MODEL') or yaml_config.get('model', 'gemma3:270m')
        limit_message = os.environ.get('LIMIT_MESSAGE') or yaml_config.get('limit_message')
        limit_chars = os.environ.get('LIMIT_CHARS') or yaml_config.get('limit_chars')
        temperature = os.environ.get('TEMPERATURE') or yaml_config.get('temperature', 0.7)
        system_prompt = yaml_config.get('system_prompt')

        if limit_message is not None:
            limit_message = int(limit_message)
        if limit_chars is not None:
            limit_chars = int(limit_chars)
        temperature = float(temperature)

        if not api_key or not api_host:
            print('Ошибка: Укажите API_KEY и API_HOST в переменных окружения или config.yaml')
            print('Для Ollama используйте:')
            print('  API_KEY=ollama')
            print('  API_HOST=http://localhost:11434/v1/')
            sys.exit(1)

        return cls(
            api_key=api_key,
            api_host=api_host,
            model=model,
            limit_message=limit_message,
            limit_chars=limit_chars,
            temperature=temperature,
            system_prompt=system_prompt
        )