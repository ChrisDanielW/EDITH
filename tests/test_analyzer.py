import unittest
from src.services.note_analyzer import NoteAnalyzer

class TestNoteAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = NoteAnalyzer()

    def test_analyze_notes(self):
        notes = "This is a sample note for testing."
        expected_output = {
            'key_information': ['sample note', 'testing'],
            'summary': 'This is a sample note for testing.'
        }
        result = self.analyzer.analyze(notes)
        self.assertEqual(result['key_information'], expected_output['key_information'])
        self.assertEqual(result['summary'], expected_output['summary'])

    def test_analyze_empty_notes(self):
        notes = ""
        expected_output = {
            'key_information': [],
            'summary': ''
        }
        result = self.analyzer.analyze(notes)
        self.assertEqual(result['key_information'], expected_output['key_information'])
        self.assertEqual(result['summary'], expected_output['summary'])

if __name__ == '__main__':
    unittest.main()