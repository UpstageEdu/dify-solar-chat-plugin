from collections.abc import Generator
from typing import Any
from openai import OpenAI, OpenAIError
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import logging
import json

class SolarChatTool(Tool):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(__name__)
        self.client = None

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        self.logger.info("SolarChatTool invoked (streaming enabled).")
        self.logger.debug(f"Tool parameters: {tool_parameters}")

        # Parse messages safely
        try:
            print(tool_parameters)
            content_raw = tool_parameters.get("messages", "[]")
            print(content_raw)
            messages = [{"role": "user", "content": content_raw}]
        except Exception as e:
            self.logger.exception("Failed to parse 'messages'.")
            yield self.create_text_message("Invalid message format.")
            return

        # model, system prompt, temperature, max_tokens option
        model = tool_parameters.get("model", "solar-pro")
        temperature = tool_parameters.get("temperature", 1.0)
        max_tokens = tool_parameters.get("max_tokens", 1024)
        system_prompt = tool_parameters.get("system_prompt")  # optional

        # API Key validation
        api_key = self.runtime.credentials.get("upstage_api_key")
        if not api_key:
            self.logger.error("No API key provided.")
            yield self.create_text_message("Missing upstage_api_key in credentials.")
            return

        # Add system prompt (if exists)
        if system_prompt:
            if isinstance(messages, list) and not any(m.get("role") == "system" for m in messages if isinstance(m, dict)):
                messages.insert(0, {"role": "system", "content": system_prompt})
                print(messages)
        try:
            if self.client is None:
                self.client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.upstage.ai/v1"
                )

            # Make streaming request
            stream = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )

            # Stream response
            full_reply = ""
            for chunk in stream:
                delta = chunk.choices[0].delta
                content = getattr(delta, "content", None)
                if content:
                    full_reply += content
                    yield self.create_text_message(content)

        except OpenAIError as oe:
            self.logger.exception("OpenAIError occurred while calling Solar.")
            yield self.create_text_message(f"OpenAI API error: {str(oe)}")

        except Exception as e:
            self.logger.exception("Unexpected error during Solar chat call.")
            yield self.create_text_message(f"Unexpected error: {str(e)}")
