"""Utility for loading prompts from markdown files."""

from pathlib import Path


def load_prompt(prompt_path: str) -> str:
    """Load a prompt from a markdown file.

    Args:
        prompt_path: Relative path to the prompt file from the prompts directory

    Returns:
        The content of the prompt file
    """
    # Get the absolute path to the prompts directory
    prompts_dir = Path(__file__).parent.parent / "tools" / "prompts"
    full_path = prompts_dir / prompt_path

    if not full_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {full_path}")

    with open(full_path) as f:
        return f.read().strip()
