import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_OUTPUT = "action_items_output.json"
DEFAULT_PROMPT_FILE = "prompts.md"
DEFAULT_ENV_FILE = ".env"
DEMO_TRANSCRIPT = """Project Manager Meeting Transcript:
Thanks everyone. Let's finalize the Q2 launch plan today. Jordan, please update the customer email draft by Wednesday and send it to marketing for review. Priya will confirm the webinar date with the sales team by Friday. Engineering should fix the login timeout bug before the next release. We also need to revisit the onboarding slides next week, but no one owns that yet.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize a meeting transcript into action items."
    )
    parser.add_argument(
        "--input-file",
        help="Path to a text file containing the meeting transcript.",
    )
    parser.add_argument(
        "--transcript",
        help="Meeting transcript passed directly on the command line.",
    )
    parser.add_argument(
        "--instructions-file",
        default=DEFAULT_PROMPT_FILE,
        help="Path to a file containing system instructions.",
    )
    parser.add_argument(
        "--env-file",
        default=DEFAULT_ENV_FILE,
        help="Path to a .env-style file containing GEMINI_API_KEY.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help="Gemini model name to use for the workflow.",
    )
    parser.add_argument(
        "--output-file",
        default=DEFAULT_OUTPUT,
        help="Where to save the structured JSON output.",
    )
    parser.add_argument(
        "--use-demo",
        action="store_true",
        help="Run the workflow on a built-in sample transcript.",
    )
    return parser.parse_args()


def load_text_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8").strip()


def resolve_transcript(args: argparse.Namespace) -> str:
    if args.transcript:
        return args.transcript.strip()
    if args.input_file:
        return load_text_file(args.input_file)
    if args.use_demo:
        return DEMO_TRANSCRIPT.strip()
    raise ValueError(
        "Provide --input-file, --transcript, or --use-demo so the script has a transcript to process."
    )


def load_instructions(path: str) -> str:
    instructions = load_text_file(path)
    if not instructions:
        raise ValueError(f"Instructions file is empty: {path}")
    return instructions


def load_env_file(path: str) -> None:
    env_path = Path(path)
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def call_gemini(model: str, instructions: str, transcript: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY is not set.")

    payload = {
        "systemInstruction": {
            "parts": [{"text": instructions}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": transcript}],
            },
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
        },
    }

    request = urllib.request.Request(
        url=(
            "https://generativelanguage.googleapis.com/v1beta/"
            f"models/{model}:generateContent?key={api_key}"
        ),
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def extract_text(response_json: dict) -> str:
    parts = []
    for candidate in response_json.get("candidates", []):
        content = candidate.get("content", {})
        for part in content.get("parts", []):
            text = part.get("text")
            if text:
                parts.append(text)
    return "\n".join(parts).strip()


def parse_model_json(model_text: str) -> dict:
    return json.loads(model_text)


def print_summary(result: dict, output_path: Path) -> None:
    print("=== Workflow Summary ===")
    print("Task: Meeting transcript -> action items")
    print(f"Saved Output: {output_path}")
    print()

    print("=== Action Items ===")
    action_items = result.get("action_items", [])
    if not action_items:
        print("No action items identified.")
    else:
        for index, item in enumerate(action_items, start=1):
            owner = item.get("owner", "Unassigned")
            task = item.get("task", "Unknown task")
            due = item.get("due_date", "Not specified")
            status = item.get("status", "unspecified")
            print(f"{index}. Owner: {owner}")
            print(f"   Task: {task}")
            print(f"   Due: {due}")
            print(f"   Status: {status}")

    print()
    print("=== Human Review Notes ===")
    notes = result.get("human_review_notes", [])
    if not notes:
        print("None.")
    else:
        for note in notes:
            print(f"- {note}")


def main() -> int:
    args = parse_args()

    try:
        load_env_file(args.env_file)
        transcript = resolve_transcript(args)
        instructions = load_instructions(args.instructions_file)
        response_json = call_gemini(args.model, instructions, transcript)
        model_text = extract_text(response_json)
        result = parse_model_json(model_text)
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        print(f"API error: {error.code} {error.reason}", file=sys.stderr)
        print(details, file=sys.stderr)
        return 1
    except urllib.error.URLError as error:
        print(f"Network error: {error.reason}", file=sys.stderr)
        return 1
    except json.JSONDecodeError:
        print(
            "Model output was not valid JSON. Adjust the prompt or inspect the raw API response.",
            file=sys.stderr,
        )
        return 1
    except ValueError as error:
        print(f"Input error: {error}", file=sys.stderr)
        return 1
    except EnvironmentError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 1

    output_path = Path(args.output_file)
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print_summary(result, output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
