import sys
import asyncio
from pathlib import Path
from typing import Tuple, List

# Ensure project root is on sys.path when running as a script
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from langchain_core.documents import Document

from configs import constant
from controllers.documents.pdf import process_pdf
from controllers.documents.docx import process_docx
from controllers.documents.xlsx import process_xlsx
from controllers.documents.txt import process_txt
from controllers.documents.csv import process_csv
from controllers.documents.html import process_html
from controllers.documents.md import process_md
from controllers.documents.json import process_json
from controllers.modules import node_structured
from controllers.databases.vector.qdrant import qdrant
from controllers.databases.vector.qdrant import collections as qdrant_collections


async def build_docs(
    file_path: str,
    user_id: str,
    language: str = "vie+eng",
) -> Tuple[List[Document], List[str], str]:
    path = Path(file_path)
    file_name = path.name
    ext = path.suffix.lower().lstrip(".")
    folder_path = f"{constant.DATA_USER}/{user_id}"

    if ext == "pdf":
        raw_elements, images = await asyncio.to_thread(
            process_pdf.process_pdf, folder_path, str(path), language
        )
        docs, ids = await asyncio.to_thread(
            node_structured.node_structured_pdf, raw_elements, images, file_name
        )
    elif ext in {"doc", "docx"}:
        raw_elements, images = await asyncio.to_thread(process_docx.process_docx, str(path))
        docs, ids = await asyncio.to_thread(
            node_structured.node_structured_docx, raw_elements, images, file_name
        )
    elif ext == "xlsx":
        all_data = await asyncio.to_thread(process_xlsx.process_xlsx, str(path))
        docs, ids = await asyncio.to_thread(
            node_structured.node_structured_excel, all_data, file_name
        )
    elif ext == "txt":
        products, _ = await asyncio.to_thread(process_txt.process_products_txt, str(path))
        if products:
            docs, ids = await asyncio.to_thread(
                node_structured.node_structured_products_text, products, file_name
            )
        else:
            raw_elements, _ = await asyncio.to_thread(process_txt.process_txt, str(path))
            docs, ids = await asyncio.to_thread(
                node_structured.node_structured_text, raw_elements, file_name, "txt"
            )
    elif ext == "csv":
        raw_elements, _ = await asyncio.to_thread(process_csv.process_csv, str(path))
        docs, ids = await asyncio.to_thread(
            node_structured.node_structured_csv, raw_elements, file_name
        )
    elif ext in {"html", "htm"}:
        raw_elements, _ = await asyncio.to_thread(process_html.process_html, str(path))
        docs, ids = await asyncio.to_thread(
            node_structured.node_structured_html, raw_elements, file_name
        )
    elif ext in {"md", "markdown"}:
        raw_elements, _ = await asyncio.to_thread(process_md.process_md, str(path))
        docs, ids = await asyncio.to_thread(
            node_structured.node_structured_markdown, raw_elements, file_name
        )
    elif ext == "json":
        raw_elements, _ = await asyncio.to_thread(process_json.process_json, str(path))
        docs, ids = await asyncio.to_thread(
            node_structured.node_structured_json, raw_elements, file_name
        )
    else:
        raise ValueError(f"Unsupported file type: .{ext}")

    return docs, ids, file_name


async def append_to_collection(
    collection_name: str,
    user_id: str,
    file_path: str,
    note: str = "",
    language: str = "vie+eng",
) -> bool:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    docs, ids, file_name = await build_docs(str(path), user_id, language)
    if not docs:
        return False

    info = {"collection_name": collection_name, "file_name": file_name, "note": note}
    await asyncio.to_thread(qdrant_collections.save_qdrant_collection_user, user_id, info)
    await asyncio.to_thread(qdrant_collections.save_qdrant_collection_all, info)
    await asyncio.to_thread(qdrant.save_vector_db_as_ids, docs, collection_name, ids)
    return True


async def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Append a document to an existing Qdrant collection"
    )
    parser.add_argument("--collection-name", required=True)
    parser.add_argument("--user-id", required=True)
    parser.add_argument("--file-path", required=True)
    parser.add_argument("--note", default="")
    parser.add_argument("--language", default="vie+eng")
    args = parser.parse_args()

    ok = await append_to_collection(
        collection_name=args.collection_name,
        user_id=args.user_id,
        file_path=args.file_path,
        note=args.note,
        language=args.language,
    )
    if ok:
        print(
            f"✅ Appended {Path(args.file_path).name} to {args.collection_name}"
        )
    else:
        print("⛔ No documents produced from file.")


if __name__ == "__main__":
    asyncio.run(main())