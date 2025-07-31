from mcp.server.fastmcp import FastMCP
from PIL import Image as PILImage
import os
import config
import asyncio
from google import genai
import mcp
from pydantic import BaseModel
from ast import literal_eval
import json
from pdf_handler import PDFViewer
import sys

mcp = FastMCP("DocSearch")

# JSON schema for vlm response
class DocumentSearchResponse(BaseModel):
    query: str
    answer_found: str
    page_number: str

@mcp.tool()
async def get_all_pdf_files_path() -> list:
    """Returns a list of full PDF file paths."""
    return [
        os.path.join(config.PDF_FOLDER, file)
            for file in os.listdir(config.PDF_FOLDER)
            if os.path.isfile(os.path.join(config.PDF_FOLDER, file))
        ]

@mcp.tool()
async def search_for_query_in_pdf(query: str, pdf_file_path: str) -> dict:
    """Uploads the PDF to gemini to ask if the query's answer is present in the PDF"""
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    sample_pdf = client.files.upload(file=pdf_file_path)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[f"You are a strict PDF checker. Only return structured JSON. \
                    Do not hallucinate. If query text is not found word-for-word or close paraphrase in any page, return false. \
                    Query: {query}",
                    sample_pdf],
        config={
                    'response_mime_type': 'application/json',
                    'response_schema': DocumentSearchResponse,
                },
    )
    print(f"Resposne on PDF upload: {response.text}")
    response = literal_eval(json.loads(json.dumps(response.text.strip())))
    return response

@mcp.tool()
async def view_pdf(pdf_file_path: str, page_number: str):
    """Opens a PDF and navigates to the given page number."""
    PDFViewer(pdf_file_path, int(page_number))
    return {"response": "success"}

# async def main():
#     file_paths = await get_all_pdf_files_path()
#     await search_for_query_in_pdf("Is stable matching taught in this lecture", file_paths[0])

if __name__ == "__main__":
    print("STARTING")
    if len(sys.argv) > 1 and sys.argv[1] == "dev":
        mcp.run()  # Run without transport for dev server
    else:
        mcp.run(transport="stdio")  # Run with stdio for direct execution

    # asyncio.run(main())
