import json
from typing import Generator, Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import datetime

from tools.base import MiniMaxBaseTool


class ListVoicers(Tool):
        def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
            """
            List available models from Fish Audio
            """
            api_key = self.runtime.credentials.get("api_key")
            group_id = self.runtime.credentials.get("group_id")
            minimax = MiniMaxBaseTool(api_key=api_key, group_id=group_id)
            voice_type = tool_parameters.get("voice_type")
            response = minimax.get_voice(
                voice_type=voice_type
            )
            if response.status_code != 200:
                yield self.create_text_message(
                    f"Get voice failed {response.status_code} {response.text}"
                )
                return
            status_code = response.json().get("base_resp", {}).get("status_code", -1)
            if status_code != 0:
                yield self.create_text_message(f"Get voice failed {response.text}")
                return
            lines = []
            i = 1

            # 遍历三个类别
            for category in ["system_voice", "voice_cloning", "voice_generation"]:
                items = response.json().get(category, [])
                if not isinstance(items, list):
                    continue
                lines.append(f"=== Category: {category} ===")
                for item in items:
                    voice_id = item.get("voice_id", "")
                    voice_name = item.get("voice_name", "无")
                    desc_list = item.get("description", [])
                    desc = "；".join(desc_list) if desc_list else "无"
                    created_time = item.get("created_time", "")

                    lines.append(
                        f"{i}.ID: {voice_id}\n"
                        f"    Voice Name: {voice_name}\n"
                        f"    Description: {desc}\n"
                        f"    Created_time: {created_time}\n"
                    )
                    i += 1

            yield self.create_text_message("\n\n".join(lines))
            yield self.create_json_message(response.json())

