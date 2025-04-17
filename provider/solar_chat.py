from typing import Any
from openai import OpenAI, OpenAIError  # openai==1.52.2
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class SolarChatProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            api_key = credentials.get("upstage_api_key", None)
            # API Checking is needed: Future work
            if api_key is not None:
                api_key=api_key
            else:
                raise ToolProviderCredentialValidationError(
                    "Upstage API key is not found"
                )
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))