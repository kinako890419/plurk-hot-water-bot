from google import genai


class GeminiApi:
    def __init__(self, api_key):
        genai.configure(api_key=api_key, transport='rest')
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def create_response(self, prompt):
        response = self.model.generate_content(prompt)
        return response.text
