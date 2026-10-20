"""Patch sandbox-maas so the structured-output reformat call is streamed.

sandbox-maas turns the agent's final answer into JSON with a second,
non-streamed chat completion that uses response_format=json_schema. MaaS drops
connections that stay silent for 60s, and LiteLLM buffers json_schema output for
Claude instead of streaming it, so long results (OTA reports, large analyses)
fail with "Agent error: Connection error." This replaces that call with streamed
plain text, the schema in the system prompt, and a JSON validity check.

The build fails if the original code is not found, so a new base image cannot
silently skip the patch.
"""

import sys
from pathlib import Path

TARGET = Path("/opt/lightspeed/src/lightspeed_agentic/providers/openai.py")

ORIGINAL = r'''        strict_schema = _make_strict(schema)
        resp = await self._client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Convert the assistant's answer into JSON conforming to the schema. "
                        "Use only information present in the answer; do not invent values."
                    ),
                },
                {"role": "user", "content": answer},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {"name": "output", "schema": strict_schema, "strict": True},
            },
        )
        return resp.choices[0].message.content or answer
'''

PATCHED = r'''        strict_schema = _make_strict(schema)
        # Streamed plain text with the schema in the prompt. MaaS drops connections
        # that stay silent for 60s, and LiteLLM buffers json_schema output for Claude
        # instead of streaming it, so response_format cannot be used here.
        stream = await self._client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Convert the assistant's answer into JSON conforming to the schema. "
                        "Use only information present in the answer; do not invent values. "
                        "Reply with only the JSON object: no prose, no code fences.\n\n"
                        "JSON Schema:\n" + json.dumps(strict_schema)
                    ),
                },
                {"role": "user", "content": answer},
            ],
            max_tokens=32000,
            stream=True,
        )
        parts: list[str] = []
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                parts.append(chunk.choices[0].delta.content)
        text = "".join(parts).strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else ""
            if text.rstrip().endswith("```"):
                text = text.rstrip()[:-3]
            text = text.strip()
        try:
            json.loads(text)
        except ValueError:
            logger.warning("structured reformat did not return valid JSON (%d chars)", len(text))
        return text or answer
'''


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else TARGET
    source = path.read_text()
    count = source.count(ORIGINAL)
    if count != 1:
        print(f"patch: expected the original reformat code once in {path}, found {count}", file=sys.stderr)
        return 1
    if "import json\n" not in source or "logger = logging.getLogger(__name__)" not in source:
        print(f"patch: {path} lacks the json import or the module logger", file=sys.stderr)
        return 1
    # Write in place so the file keeps its owner and mode.
    with path.open("w") as f:
        f.write(source.replace(ORIGINAL, PATCHED))
    print(f"patch: streamed reformat applied to {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
