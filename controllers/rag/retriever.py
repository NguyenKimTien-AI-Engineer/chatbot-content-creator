from controllers.databases.vector.qdrant import qdrant


# BASIC
def get_retriever_basic_qdrant(collections, query, k):
    try:
        retrievers = ""

        if collections:
            if isinstance(collections, list):
                for collection in collections:
                    db = qdrant.load_vector_db(collection)
                    retrievers += retriever_basic(db, query, k) + "\n\n"
            else:
                db = qdrant.load_vector_db(collections)
                retrievers = retriever_basic(db, query, k)

        return retrievers

    except Exception as e:
        print(f"Error retrieving data get_retriever_basic_qdrant: {e}")
        return None


def retriever_basic(db, query, k):
    retrievers = ""
    seen_texts = set()   # lưu các đoạn text đã thêm
    processed = 0        # đếm số mục đã thêm

    try:
        docs = qdrant.similarity_search_qdrant_data_with_score(db, query.lower(), 20)

        for index, (doc, score) in enumerate(docs):
            if processed >= k:
                break
            if score < 0.7:
                continue

            # Lấy nội dung ưu tiên: summary > document_content > page_content
            page_content = doc.page_content or ""
            metadata = doc.metadata or {}
            document_content = metadata.get("page_content", "") or ""
            summary = metadata.get("summary", "") or ""
            hierarchy = metadata.get("hierarchy", "") or ""

            if summary.strip():
                text_to_add = summary.strip()
            elif document_content.strip():
                text_to_add = document_content.strip()
            else:
                text_to_add = page_content.strip()

            # Thêm nếu chưa có
            if text_to_add and text_to_add not in seen_texts:
                if hierarchy.strip():
                    retrievers += f"📑 Index Number [{processed}] - `{hierarchy.strip()}`:\n{text_to_add}\n\n"
                else:
                    retrievers += f"📑 Index Number [{processed}] :\n{text_to_add}\n\n"

                seen_texts.add(text_to_add)
                processed += 1

        # Nếu không có tài liệu nào thỏa score nhưng vẫn có docs
        if processed == 0 and docs:
            first_doc, first_score = docs[0]

            page_content = first_doc.page_content or ""
            metadata = first_doc.metadata or {}
            document_content = str(metadata.get("page_content", "")) or ""
            summary = str(metadata.get("summary", "")) or ""
            hierarchy = str(metadata.get("hierarchy", "")) or ""

            if summary.strip():
                text_to_add = summary.strip()
            elif document_content.strip():
                text_to_add = document_content.strip()
            else:
                text_to_add = page_content.strip()

            if text_to_add:
                if hierarchy.strip():
                    retrievers += f"📑 Index Number [{processed}] - `{hierarchy.strip()}`:\n{text_to_add}\n\n"
                else:
                    retrievers += f"📑 Index Number [{processed}] :\n{text_to_add}\n\n"

        return retrievers

    except Exception as e:
        print("Error retriever_basic:", e)
        return retrievers


# REFERENCE
def get_retriever_reference_qdrant(collections, query, k):
    retrievers = ""
    references = []

    try:
        if collections:
            if isinstance(collections, list):
                for collection in collections:
                    db = qdrant.load_vector_db(collection)
                    _retriever, _reference = retriever_reference(db, query, k)
                    retrievers += _retriever + "\n\n"
                    references.extend(_reference)
            else:
                db = qdrant.load_vector_db(collections)
                retrievers, references = retriever_reference(db, query, k)

        return retrievers, references

    except Exception as e:
        print(f"Error retrieving data get_retriever_reference_qdrant: {e}")
        return retrievers, references


def retriever_reference(db, query, k):
    retrievers = ""
    references = []
    seen_texts = set()
    processed = 0  # đếm số mục đã thêm

    try:
        docs = qdrant.similarity_search_qdrant_data_with_score(db, query.lower(), 20)

        # 1) Lấy những doc có score >= 0.75
        for index, (doc, score) in enumerate(docs):
            if processed >= k:
                break
            if score < 0.7:
                continue

            page_content = doc.page_content or ""
            metadata = doc.metadata or {}
            document_content = str(metadata.get("page_content", "")) or ""
            summary = str(metadata.get("summary", "")) or ""
            hierarchy = str(metadata.get("hierarchy", "")) or ""

            # Chọn nội dung ưu tiên
            if summary.strip():
                text_to_add = summary.strip()
            elif document_content.strip():
                text_to_add = document_content.strip()
            else:
                text_to_add = page_content.strip()

            # Thêm nếu chưa có
            if text_to_add and text_to_add not in seen_texts:
                if hierarchy.strip():
                    retrievers += f"📑 Index Number [{processed}] - `{hierarchy.strip()}`:\n{text_to_add}\n\n"
                else:
                    retrievers += f"📑 Index Number [{processed}] :\n{text_to_add}\n\n"

                references.append({
                    "title": hierarchy.strip(),
                    "content": text_to_add
                })

                seen_texts.add(text_to_add)
                processed += 1

        # 2) Nếu không có doc nào thỏa score nhưng vẫn có docs, thêm doc đầu tiên
        if processed == 0 and docs:
            first_doc, first_score = docs[0]

            page_content = first_doc.page_content or ""
            metadata = first_doc.metadata or {}
            document_content = str(metadata.get("page_content", "")) or ""
            summary = str(metadata.get("summary", "")) or ""
            hierarchy = str(metadata.get("hierarchy", "")) or ""

            if summary.strip():
                text_to_add = summary.strip()
            elif document_content.strip():
                text_to_add = document_content.strip()
            else:
                text_to_add = page_content.strip()

            if text_to_add:
                # Có thể ghi chú đây là score thấp nếu cần
                if hierarchy.strip():
                    retrievers += f"📑 Index Number [{processed}] - `{hierarchy.strip()}`:\n{text_to_add}\n\n"
                else:
                    retrievers += f"📑 Index Number [{processed}] :\n{text_to_add}\n\n"

                references.append({
                    "title": hierarchy.strip(),
                    "content": text_to_add
                })

        return retrievers, references

    except Exception as e:
        print("Error retriever_reference:", e)
        return retrievers, references




