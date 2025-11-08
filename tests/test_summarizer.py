import unittest
from src.services.summarizer import Summarizer

class TestSummarizer(unittest.TestCase):

    def setUp(self):
        self.summarizer = Summarizer()

    def test_generate_summary(self):
        notes = "This is a test note. It contains important information about the project."
        expected_summary = "This is a test note. It contains important information."
        summary = self.summarizer.generate_summary(notes)
        self.assertEqual(summary, expected_summary)

    def test_empty_notes(self):
        notes = ""
        expected_summary = "No content to summarize."
        summary = self.summarizer.generate_summary(notes)
        self.assertEqual(summary, expected_summary)

    def test_long_notes(self):
        notes = "This is a long note that goes into detail about various aspects of the project. " \
                "It discusses the goals, the methodologies, and the expected outcomes. " \
                "In conclusion, the project aims to achieve significant results."
        summary = self.summarizer.generate_summary(notes)
        self.assertTrue(len(summary) < len(notes))

if __name__ == '__main__':
    unittest.main()