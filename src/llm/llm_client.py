import os
from google import genai

class GeminiClient:
    def __init__(self, api_key: str = None):
        key = api_key or os.environ.get("GEMINI_API_KEY", "")
        if not key:
            raise EnvironmentError("GEMINI_API_KEY is not set.")
        self.client = genai.Client(api_key=key)
        self.model  = "models/gemini-2.5-flash"

    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return response.text







# from google import genai


# class GeminiClient:

#     def __init__(self, api_key: str):

#         self.client = genai.Client(api_key=api_key)

#         # use a model from your available list
#         self.model = "models/gemini-2.5-flash"

#     def generate(self, prompt: str):

#         response = self.client.models.generate_content(
#             model=self.model,
#             contents=prompt
#         )

#         return response.text