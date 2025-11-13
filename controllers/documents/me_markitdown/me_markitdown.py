from markitdown import MarkItDown

md = MarkItDown(docintel_endpoint="<document_intelligence_endpoint>")
result = md.convert("1.Cong nghe thong tin DTTX.pdf")
print(result.text_content)

