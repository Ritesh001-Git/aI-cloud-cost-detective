import json
import logging
import os
from typing import Any, Literal

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from pydantic import BaseModel, ConfigDict, Field, ValidationError

load_dotenv()

logger = logging.getLogger(__name__)

Provider = Literal["aws", "azure", "gcp"]
Severity = Literal["High", "Medium", "Low"]


class OptimizationIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resource_id: str
    resource_name: str
    issue_type: str
    severity: Severity
    description: str
    estimated_savings: float = Field(ge=0)
    fix_command: str


class CostAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str
    total_estimated_monthly_savings: float = Field(ge=0)
    issues: list[OptimizationIssue]


class AIAnalysisError(Exception):
    pass


class AIAnalyzer:
    def __init__(
        self,
        provider: Provider,
        resources: list[dict[str, Any]],
        *,
        client: genai.Client | None = None,
        model: str | None = None,
    ) -> None:
        self.provider = provider
        self.resources = resources
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.client = client or self._create_client()

    def analyze(self) -> CostAnalysis:
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=self._resource_prompt(),
                config=types.GenerateContentConfig(
                    system_instruction=self._system_prompt(),
                    response_mime_type="application/json",
                ),
            )
        except errors.ClientError as exc:
            logger.exception("Gemini API client error")
            if exc.code == 429:
                raise AIAnalysisError(
                    "Gemini quota is exhausted or rate-limited. Check the API project "
                    "quota and free-tier limits, then retry."
                ) from exc
            if exc.code in {401, 403}:
                raise AIAnalysisError(
                    "Gemini rejected the API key or model access. Check GEMINI_API_KEY "
                    f"and access to model {self.model}."
                ) from exc
            raise AIAnalysisError(
                f"Gemini request failed with API status {exc.code}. Check backend logs."
            ) from exc
        except errors.APIError as exc:
            logger.exception("Gemini API error")
            raise AIAnalysisError(
                "Gemini analysis failed. Check the network connection and backend logs."
            ) from exc

        if not response.text:
            raise AIAnalysisError("Gemini returned an empty analysis response.")
        try:
            data = json.loads(response.text)
            return CostAnalysis.model_validate(data)
        except ValidationError as exc:
            logger.exception("Gemini returned invalid structured output")
            raise AIAnalysisError(
                "Gemini returned an invalid structured analysis response."
            ) from exc

    def _system_prompt(self) -> str:
        return f"""
You are a FinOps and cloud cost optimization expert specializing in {self.provider.upper()}.

Return ONLY valid JSON.

JSON format:

{{
  "summary": "string",
  "total_estimated_monthly_savings": 0,
  "issues": [
    {{
      "resource_id": "string",
      "resource_name": "string",
      "issue_type": "string",
      "severity": "High|Medium|Low",
      "description": "string",
      "estimated_savings": 0,
      "fix_command": "string"
    }}
  ]
}}

Do not return markdown.
Do not return explanations.
Do not wrap in code blocks.
Return only the JSON object.
""".strip()

    def _resource_prompt(self) -> str:
        return (
            f"Analyze this normalized {self.provider.upper()} resource inventory JSON:\n"
            f"{json.dumps(self.resources, indent=2, sort_keys=True)}"
        )

    @staticmethod
    def _create_client() -> genai.Client:
        if not os.getenv("GEMINI_API_KEY"):
            raise AIAnalysisError(
                "GEMINI_API_KEY is not configured. Add it to the backend environment."
            )
        return genai.Client()
