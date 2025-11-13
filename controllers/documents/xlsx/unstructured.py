from unstructured.partition.xlsx import partition_xlsx
from configs import constant


def load_documents(file_path: str):
    raw_elements = partition_xlsx(
        filename=file_path,
    )

    return raw_elements