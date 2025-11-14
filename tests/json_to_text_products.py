import asyncio
import json
from argparse import ArgumentParser
from pathlib import Path
from typing import List


def flatten_description(text: str) -> str:
    """Convert description to a single line by collapsing whitespace.

    - Preserve content but replace all sequences of whitespace (spaces, tabs, newlines)
      with a single space.
    - Trim leading/trailing spaces.
    """
    text = text.replace("\r\n", "\n").strip()
    # Collapse all whitespace (including newlines) to single spaces
    return " ".join(text.split())


async def read_json(path: Path) -> List[dict]:
    content = await asyncio.to_thread(path.read_text, encoding="utf-8")
    data = json.loads(content)
    if not isinstance(data, list):
        raise ValueError("JSON must be a list of objects")
    return data


async def write_text(path: Path, lines: List[str]) -> None:
    output = "\n".join(lines).strip() + "\n"
    await asyncio.to_thread(path.write_text, output, encoding="utf-8")


async def convert(input_path: Path, output_path: Path) -> None:
    items = await read_json(input_path)
    lines: List[str] = []
    for idx, item in enumerate(items, start=1):
        name = str(item.get("name", "")).strip()
        desc = str(item.get("description", "")).strip()
        formatted = flatten_description(desc)
        lines.append(f"{idx}. {name}")
        lines.append("Mô tả sản phẩm:")
        lines.append(formatted)
        lines.append("")
    await write_text(output_path, lines)


async def main() -> None:
    parser = ArgumentParser(description="Convert product JSON to formatted text")
    parser.add_argument("--input", default="data/test_api.json")
    parser.add_argument("--output", default="data/test_api_products.txt")
    args = parser.parse_args()

    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()
    await convert(input_path, output_path)
    print(f"✅ Đã tạo file: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())