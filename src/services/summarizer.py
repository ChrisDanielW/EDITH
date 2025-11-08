class Summarizer:
    def __init__(self, llama_client):
        self.llama_client = llama_client

    def generate_summary(self, analyzed_notes):
        prompt = self._create_prompt(analyzed_notes)
        summary = self.llama_client.generate_text(prompt)
        return summary

    def _create_prompt(self, analyzed_notes):
        return f"Summarize the following notes:\n{analyzed_notes}"