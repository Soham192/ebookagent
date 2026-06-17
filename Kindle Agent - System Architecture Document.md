# Kindle Agent - System Architecture Document

## 1. High-Level Architecture

User
↓
Frontend
↓
Backend API
↓
Agent Layer
↓
MCP Server
↓
Document Tools
↓
External Utilities

---

## 2. Component Breakdown

### Frontend
Responsibilities:

- File Upload
- Progress Display
- Metadata Editing
- File Download

Technology:

- React
- TailwindCSS

---

### Backend API
Responsibilities:

- Receive uploads
- Store files
- Trigger agent workflow
- Return results

Technology:

- FastAPI

---

### Agent Layer
Responsibilities:

- Decide workflow
- Select tools
- Manage execution sequence

Example:

PDF Upload
↓
Analyze PDF
↓
Need OCR?
↓
Run OCR
↓
Convert Format
↓
Return Output

---

### MCP Server
Responsibilities:

Expose tool interfaces.

Tools:

- analyze_pdf
- run_ocr
- extract_metadata
- convert_document

---

### Tool Layer
Implements actual business logic.

Examples:

- analyze_pdf.py
- run_ocr.py
- metadata.py
- convert.py

---

### External Utilities

OCR:

- Tesseract OCR

Conversion:

- Calibre
- ebook-convert CLI

PDF Analysis:

- PyMuPDF

---

## 3. Data Flow

Upload PDF
↓
Store File
↓
Agent Receives Task
↓
Agent Calls MCP Tool
↓
Tool Processes File
↓
Result Returned
↓
Agent Continues Workflow
↓
Output Generated
↓
Download Link Returned

---

## 4. Scalability Considerations

Future:

Frontend
↓
FastAPI
↓
Message Queue
↓
Agent Workers
↓
MCP Servers
↓
Storage

This allows processing many PDFs simultaneously.
