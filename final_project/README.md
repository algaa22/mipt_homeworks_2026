# GigaVibeMiptCode

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Ollama](https://img.shields.io/badge/Ollama-0.1+-green.svg)](https://ollama.com)

## О проекте

Консольный чат-бот для общения с большой языковой моделью (LLM) через OpenAI compatible API (Ollama). Проект реализован в рамках итоговой работы по курсу Python разработки.

### Основные возможности

- **Чат с ИИ** с сохранением истории сообщений
- **Контроль длины контекста** (лимит сообщений и символов)
- **Гибкая конфигурация** (env + YAML)
- **Прерывание запроса** (Ctrl+C)
- **Прикрепление файлов** через `@::path::`
- **Почанковая обработка файлов** (`/file_chunk`)
- **Streaming ответов**
- **Unit-тесты**

# Архитектура проекта

```text
final_project/
│
├── main.py               # Точка входа, обработка CLI-команд
├── chat.py               # Логика чата, контекст, streaming-ответы
├── config.py             # Загрузка конфигурации (env + yaml)
├── file_handler.py       # Обработка файлов
├── chunk_processor.py    # Почанковая обработка больших файлов
├── models.py             # Модели данных
│
├── tests/                # Unit-тесты
│   ├── __init__.py
│   └── test_chat.py
│
├── config.yaml           # Основной конфигурационный файл
├── requirements.txt      # Python-зависимости проекта
├── mypy.ini              # Настройки статического анализа mypy
└── README.md             # Документация проекта
```


## Установка и запуск

### 1. Установка Ollama

```bash
# macOS
brew install ollama
# или скачайте с https://ollama.com

# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Скачайте установщик с официального сайта
```

### 2. Скачивание модели
```text
# Рекомендуемая модель (4.7 GB)
ollama pull qwen2.5:7b

# Альтернатива с лучшим русским
ollama pull viktorian/saiga-mistral-7b
```

### 3. Установка зависимостей
```bash
# Клонирование проекта
git clone <your-repo-url>
cd final_project

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Установка зависимостей
pip install -r requirements.txt
```
### 4. Настройте конфигурации, создав файл config.yaml

### 5. Запуск
```bash
# Запуск Ollama (в отдельном терминале)
ollama serve

# Запуск бота
python main.py
```