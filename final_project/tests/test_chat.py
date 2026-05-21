import unittest
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Message
from config import Config
from file_handler import extract_file_paths, MAX_FILE_SIZE
from chunk_processor import chunk_by_paragraphs, chunk_by_length, parse_chunk_command


class TestModels(unittest.TestCase):
    def test_message_creation(self) -> None:
        msg = Message(role='user', content='Hello')
        self.assertEqual(msg.role, 'user')
        self.assertEqual(msg.content, 'Hello')
        self.assertIsNotNone(msg.timestamp)


class TestFileHandler(unittest.TestCase):
    def test_extract_file_paths(self) -> None:
        text = 'Check @::/path/to/file.py:: and @::/another/file.txt::'
        paths = extract_file_paths(text)
        self.assertEqual(len(paths), 2)
        self.assertEqual(paths[0], '/path/to/file.py')
        self.assertEqual(paths[1], '/another/file.txt')

    def test_extract_file_paths_no_match(self) -> None:
        text = 'No file references here'
        paths = extract_file_paths(text)
        self.assertEqual(paths, [])

    def test_MAX_FILE_SIZE_constant(self) -> None:
        self.assertEqual(MAX_FILE_SIZE, 5 * 1024 * 1024)


class TestChunkProcessor(unittest.TestCase):
    def test_chunk_by_paragraphs(self) -> None:
        text = 'First paragraph.\n\nSecond paragraph.\n\nThird paragraph.'
        chunks = chunk_by_paragraphs(text, 1)
        self.assertEqual(len(chunks), 3)

    def test_chunk_by_paragraphs_multiple(self) -> None:
        text = 'P1.\n\nP2.\n\nP3.\n\nP4.'
        chunks = chunk_by_paragraphs(text, 2)
        self.assertEqual(len(chunks), 2)

    def test_chunk_by_length(self) -> None:
        text = 'This is a test string for chunking'
        chunks = chunk_by_length(text, 10)
        self.assertTrue(len(chunks) > 1)

    def test_chunk_by_length_empty(self) -> None:
        text = ''
        chunks = chunk_by_length(text, 10)
        self.assertEqual(chunks, [])

    def test_parse_chunk_command_simple(self) -> None:
        filepath, params, auto_mode = parse_chunk_command('/path/to/file.txt')
        self.assertEqual(filepath, '/path/to/file.txt')
        self.assertEqual(params['type'], 'paragraph')
        self.assertEqual(params['value'], 1)

    def test_parse_chunk_command_with_auto(self) -> None:
        filepath, params, auto_mode = parse_chunk_command('/path/to/file.txt -y')
        self.assertTrue(auto_mode)

    def test_parse_chunk_command_with_paragraph(self) -> None:
        filepath, params, auto_mode = parse_chunk_command('/path/to/file.txt paragraph=3')
        self.assertEqual(params['type'], 'paragraph')
        self.assertEqual(params['value'], 3)

    def test_parse_chunk_command_with_len(self) -> None:
        filepath, params, auto_mode = parse_chunk_command('/path/to/file.txt len=200')
        self.assertEqual(params['type'], 'len')
        self.assertEqual(params['value'], 200)


class TestConfig(unittest.TestCase):
    def test_config_creation(self) -> None:
        cfg = Config(
            api_key='test_key',
            api_host='http://localhost/',
            model='test_model'
        )
        self.assertEqual(cfg.api_key, 'test_key')
        self.assertEqual(cfg.temperature, 0.7)

    def test_config_with_custom_temperature(self) -> None:
        cfg = Config(
            api_key='test_key',
            api_host='http://localhost/',
            model='test_model',
            temperature=0.3
        )
        self.assertEqual(cfg.temperature, 0.3)


class TestChatSession(unittest.TestCase):
    def test_message_limit_trimming(self) -> None:
        from chat import ChatSession

        cfg = Config(
            api_key='ollama',
            api_host='http://localhost:11434/v1/',
            model='test',
            limit_message=3
        )

        with patch('chat.OpenAI'):
            chat_session = ChatSession(cfg)
            chat_session.add_message('user', '1')
            chat_session.add_message('assistant', '2')
            chat_session.add_message('user', '3')
            chat_session.add_message('assistant', '4')

            self.assertLessEqual(len(chat_session.messages), 3)

    def test_chars_limit_trimming(self) -> None:
        from chat import ChatSession

        cfg = Config(
            api_key='ollama',
            api_host='http://localhost:11434/v1/',
            model='test',
            limit_chars=50
        )

        with patch('chat.OpenAI'):
            chat_session = ChatSession(cfg)
            chat_session.add_message('user', 'x' * 30)
            chat_session.add_message('assistant', 'y' * 30)

            total_chars = sum(len(m.content) for m in chat_session.messages)
            self.assertLessEqual(total_chars, 50)


if __name__ == '__main__':
    unittest.main()