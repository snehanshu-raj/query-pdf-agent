# QueryPDF Agent

A smart PDF search agent that helps you instantly locate specific topics across multiple lecture notes and documents. Simply enter your query, and the agent will pinpoint the exact page in the exact PDF where that information is found, opening it in an interactive, navigable window.

## 🎯 What This Does

Have a collection of lecture PDFs but struggle to find specific topics? This intelligent agent:

- **Searches** through all your PDF documents simultaneously
- **Identifies** the most relevant content using AI-powered matching
- **Opens** the exact page containing your query in a new window
- **Provides** seamless navigation through the document

Perfect for students, researchers, and professionals who need to quickly reference information across multiple documents.

## 🏗️ Project Structure

```
pdf-query-agent/
├── client.py           # Client interface for user queries
├── server.py           # Server handling PDF processing & API calls
├── pdf_handler.py      # PDF operations (rendering, page extraction)
├── config.py           # Configuration & API key management
├── prompt.py           # AI prompts for query optimization
├── logs.log            # System operation logs
├── README.md           # Project documentation
└── Notes/              # PDF document collection
    ├── Lecture1.pdf
    ├── Lecture2.pdf
    ├── Lecture3.pdf
    ├── Lecture4.pdf
    └── Lecture5.pdf
```


## 📋 Component Overview

| Component | Purpose |
| :-- | :-- |
| **client.py** | User interface for inputting queries and displaying results |
| **server.py** | Backend server managing PDF file paths and API orchestration |
| **pdf_handler.py** | PDF processing engine (rendering, page extraction, content parsing) |
| **config.py** | Centralized configuration management (API keys, settings) |
| **prompt.py** | Optimized AI prompts for accurate content matching |
| **logs.log** | Comprehensive logging for debugging and monitoring |
| **Notes/** | Document repository containing searchable PDF files |

## ✨ Key Features

### 🔍 **Intelligent Content Discovery**

- AI-powered semantic search across multiple PDFs
- Context-aware query matching using Gemini API
- Relevance scoring to find the most accurate results


### 📖 **Interactive PDF Viewer**

- Opens matched content in a dedicated window
- Built-in navigation controls (Next/Previous pages)
- Seamless page-to-page browsing experience


### 🚀 **Performance \& Reliability**

- Concurrent PDF processing for faster results
- Comprehensive error handling and logging
- Scalable architecture for large document collections


## 🛠️ Getting Started

### Prerequisites

- Python 3.8+
- Gemini API key
- PDF documents in the `Notes/` directory


### Installation

```bash
# Clone the repository
git clone <repository-url>
cd pdf-query-agent
```

### Configuration

Set up your `config.py` file with the following required variables:

```python
# config.py
GEMINI_API_KEY = "your_gemini_api_key_here"
PDF_FOLDER = "Notes/"  # Path to your PDF documents folder
```

### Usage

```bash
# Start the server
python server.py

# In another terminal, run the client
python client.py

# Enter your query when prompted
# Example: "What is machine learning?"
```


## 🎯 Use Cases

- **Students**: Quickly find specific concepts across lecture notes
- **Researchers**: Locate references and citations in academic papers
- **Professionals**: Search through documentation and reports
- **Educators**: Prepare materials by finding relevant content


## 🔮 Future Enhancements

- [ ] Support for additional file formats (DOCX, TXT, etc.)
- [ ] Advanced filtering and search options
- [ ] Bookmark and annotation features
- [ ] Multi-language document support
- [ ] Cloud storage integration
- [ ] Mobile application interface


## 📝 Version

**Current Version**: 1.0 (Basic Implementation)

This is the foundational version focusing on core PDF search functionality. Future versions will expand capabilities and user experience features.


