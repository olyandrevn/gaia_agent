from langchain_community.document_loaders import WikipediaLoader
from langchain_community.document_loaders import ArxivLoader
from langchain_community.retrievers import WikipediaRetriever
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.tools import tool

import io
import openpyxl
import os
# from smolagents import tool
import requests
from PIL import Image
from bs4 import BeautifulSoup

@tool
def web_search(query: str) -> dict:
    """Search Tavily for a query and return maximum 3 results.
    Args:
        query: The search query."""
    search_docs = DuckDuckGoSearchResults(max_results=3, output_format='list').invoke(query)
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document source="{doc.get("link", "")}" title="{doc.get("title", "")}"/>\n{doc.get("snippet", "")}\n</Document>'
            for doc in search_docs
        ]
    )
    return {"web_results": formatted_search_docs}

# @tool
# def wiki_search(query: str) -> dict:
#     """Search Wikipedia for a query and return maximum 2 results.
    
#     Args:
#         query: The search query."""
#     search_docs = WikipediaLoader(query=query, load_max_docs=2).load()
#     formatted_search_docs = "\n\n---\n\n".join(
#         [
#             f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content}\n</Document>'
#             for doc in search_docs
#         ])
#     return {"wiki_results": formatted_search_docs}

# @tool
# def wiki_search(query: str) -> dict:
#     """Search Wikipedia for a query and return maximum 2 results.
    
#     Args:
#         query: The search query."""
#     search_docs = WikipediaRetriever(load_max_docs=5).invoke(query)
#     formatted_search_docs = "\n\n---\n\n".join(
#         [
#             f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content}\n</Document>'
#             for doc in search_docs
#         ])
#     return {"wiki_results": formatted_search_docs}

@tool
def wiki_search(query: str) -> dict:
    """Search Wikipedia for a query and return maximum 1 results.
    
    Args:
        query: The search query."""
    search_docs = WikipediaRetriever(load_max_docs=1, top_k_results=2).invoke(query)
    wiki_results = []

    for doc in search_docs:
        url = doc.metadata["source"] if doc else ""
        print(url)

        response = requests.get(url)
        response_text = response.text

        soup = BeautifulSoup(response_text, "html.parser")
        wiki_results.append(' '.join(soup.get_text().split())[:20000])

    return {"wiki_results": wiki_results}

@tool
def reverse_string(query: str) -> dict:
    """Reverse the input string.
    
    Args:
        query: The input string to reverse."""
    return {"reversed_string": query[::-1]}

@tool
def calculator(expression: str) -> dict:
    """Perform mathematical calculations and return the result.
    
    This calculator can handle:
    - Basic arithmetic: +, -, *, /, % (modulus)
    - Parentheses for order of operations
    - Decimal numbers
    - Multiple operations in one expression
    
    Args:
        expression: A mathematical expression as a string
    
    Returns:
        A string containing the calculation result
    
    Examples:
        calculator("25 * 4") -> "100"
        calculator("100 / 5") -> "20.0"
        calculator("(15 + 30) * 2") -> "90"
        calculator("50 - 20 + 10") -> "40"
        calculator("17 % 5") -> "2"
        calculator("100 % 7") -> "2"
        calculator("(20 + 5) % 8") -> "5"
    """
    try:
        # Clean the expression
        expression = expression.strip()
        
        # Validate that the expression only contains safe characters (now including %)
        allowed_chars = set('0123456789+-*/.()% ')
        if not all(c in allowed_chars for c in expression):
            raise ValueError("Expression contains invalid characters. Only numbers and +, -, *, /, %, (, ) are allowed.")
        
        result = eval(expression)
        
        # Format the result
        if isinstance(result, float) and result.is_integer():
            return str(int(result))
        else:
            return str(result)
            
    except ZeroDivisionError:
        return "Error: Cannot divide by zero or modulus by zero"
    except SyntaxError:
        return f"Error: Invalid mathematical expression: {expression}"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def tool_read_files(filepath: str) -> str:
    """
    Downloads a .py or .xlsx file from a remote URL and returns its contents as plain text.
    Raises a recoverable exception if the file does not end with .py or .xlsx.
    Args:
        filepath: The path to the Python (.py) or Excel (.xlsx) file.
    """
    root_url = "https://agents-course-unit4-scoring.hf.space/files/"
    # Strip the file extension from the url before downloading
    base, ext = os.path.splitext(filepath)
    url = root_url + base

    if filepath.endswith('.py'):
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Recoverable: Failed to download file from {url}")
        return response.text

    elif filepath.endswith('.xlsx'):
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Recoverable: Failed to download file from {url}")

        wb = openpyxl.load_workbook(io.BytesIO(response.content), data_only=True)
        result = []
        for sheet in wb.worksheets:
            result.append(f"# Sheet: {sheet.title}")
            for row in sheet.iter_rows(values_only=True):
                result.append(','.join([str(cell) if cell is not None else '' for cell in row]))
        return '\n'.join(result)

    else:
        raise Exception("Recoverable: Only .py and .xlsx files can be read with this tool.")

@tool
def tool_download_image(filepath: str) -> str:
    """
    Downloads an image file (.png, .jpg, .jpeg) from a remote URL and returns useful information about the image.
    This includes the image URL and basic metadata like dimensions and format.
    Raises a recoverable exception if the file is not a supported image type.
    Args:
        filepath: The path to the image file.
    """
    root_url = "https://agents-course-unit4-scoring.hf.space/files/"
    base, ext = os.path.splitext(filepath)
    url = root_url + base
    
    if ext.lower() in ['.png', '.jpg', '.jpeg']:
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Recoverable: Failed to download image from {url}")
        
        # Get image metadata using Pillow
        try:
            
            img = Image.open(io.BytesIO(response.content))
            width, height = img.size
            format = img.format
            mode = img.mode
            
            # Return useful information about the image
            return f"Image URL: {url}\nFormat: {format}\nDimensions: {width}x{height}\nMode: {mode}"
        except ImportError:
            # Fallback if PIL is not available
            content_type = response.headers.get('Content-Type', 'unknown')
            content_length = response.headers.get('Content-Length', 'unknown')
            return f"Content-Type: {content_type}\nSize: {content_length} bytes"
    else:
        raise Exception("Recoverable: Only .png, .jpg, and .jpeg files can be processed with this tool.")
