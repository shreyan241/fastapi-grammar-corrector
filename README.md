# Grammar Corrector

A Python-based GUI application that corrects grammar, spelling, and style in Word documents (`.docx`), PDFs (`.pdf`), and plain text files (`.txt`) using OpenAI's GPT-3.5-turbo model.

## Features

- **Supports Multiple File Formats:** Word documents, PDFs, and TXT files.
- **Paragraph-Based Processing:** Maintains context for accurate corrections.
- **Caching Mechanism:** Avoids redundant API calls for previously processed texts.
- **Rate Limiting:** Adheres to OpenAI's API rate limits to prevent errors.
- **User-Friendly GUI:** Intuitive interface built with Tkinter.
- **Secure API Key Handling:** Masks API key input for privacy.

## Setup Instructions

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/grammar_corrector.git
   cd grammar_corrector
