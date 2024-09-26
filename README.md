# Grammar Corrector

A Python-based GUI application that corrects grammar, spelling, and style in Word documents (`.docx`), PDFs (`.pdf`), and plain text files (`.txt`) using OpenAI's GPT models.

## Features

- **Supports Multiple File Formats:** Easily process Word documents, PDFs, and TXT files.
- **Paragraph-Based Processing:** Maintains context by processing text paragraph by paragraph.
- **Document Type Customization:**
  - **Document Type Selection:** Choose from various document types (e.g., Legal, Medical, Academic) with embedded examples for clarity.
  - **Customizable Prompts:** Edit the correction prompts directly within the GUI to tailor the correction process to specific needs.
- **Caching Mechanism:** Avoids redundant API calls by caching previously processed texts, enhancing efficiency and reducing costs.
- **Rate Limiting:** Adheres to OpenAI's API rate limits using asynchronous rate limiting to prevent errors and ensure smooth operation.
- **User-Friendly GUI:** Intuitive and responsive interface built with Tkinter, featuring scrollable frames and progress indicators.
- **Secure API Key Handling:** Masks API key input to protect user credentials.
- **Real-Time Progress Tracking:** Visual progress bar updates to inform users about the correction process status.
- **Error Handling and Notifications:** Provides clear error messages and warnings for issues like token limits or API errors.
- **Flexible Output Options:** Save corrected documents in the desired format and location with ease.
- **Logging:** Utilizes `loguru` for detailed logging to aid in debugging and monitoring.

## Installation

### Prerequisites

- **Python 3.7 or higher** installed on your system. You can download it from [Python's official website](https://www.python.org/downloads/).

### Steps

1. **Clone the Repository**

   ```
   git clone https://github.com/yourusername/grammar_corrector.git
   cd grammar_corrector
   ```

2. **Create and activate Virtual Environment (Optional but Recommended)**

    ```
    python -m venv venv
    ```

    - On Windows
    ```
    venv\Scripts\activate
    ```

    - On Linux
    ```
    source venv/bin/activate
    ```

3. Install Dependencies
    ```
    pip install -r requirements.txt
    ```

4. Run the Application
    ```
    python main.py
    ```
## Usage
- Select Input File: Click on the Browse button to select a .docx, .pdf, or .txt file you wish to correct.
- Specify Output File: The application automatically suggests a default output file name. You can change it by clicking Save As.
- Choose Language Variant: Select between American English and British English to align corrections with your preferred language style.
- Enter OpenAI API Key: Input your OpenAI API key. This field is masked for security.
- Select Model: Choose the desired GPT model (e.g., gpt-3.5-turbo, gpt-4o-mini) based on your requirements and API access.
- Select Document Type: Choose the type of document you're processing (e.g., Legal, Medical). Each option includes examples for better understanding.
- Customize Prompt (Optional): The Prompt text box displays the default correction guidelines based on the selected document type. You can edit this prompt to customize the correction behavior.
- Select Paragraphs to Process: Use the listbox to select specific paragraphs for correction or click Select All Paragraphs to process the entire document.
- Run Grammar Correction: Click the Run Grammar Correction button to start the process. A progress bar will indicate the correction status.
- Completion: Upon completion, a success message will confirm the corrected file's location. If any paragraphs weren't processed due to token limits, a warning will notify you.

## Configuration
### OpenAI API Key
Ensure you have a valid OpenAI API key. You can obtain one by signing up at OpenAI's website.

### Prompt Customization
The application uses predefined prompts tailored to specific document types. To further customize:

### Edit Prompt
Modify the text within the Prompt box in the GUI to adjust correction guidelines as needed.

### Save Custom Prompts (Advanced):
For persistent changes, consider enhancing the application to save custom prompts to a configuration file.

## Additional Notes

### Logging:
The application uses loguru for logging. Logs are saved to grammar_corrector.log in the project directory, which is useful for debugging and monitoring.

### Caching:
Processed paragraphs are cached to optimize performance and reduce API usage. The caching mechanism ensures that identical texts aren't processed multiple times.

### Rate Limiting:
The application respects OpenAI's rate limits using aiolimiter, preventing excessive requests that could lead to errors or throttling.

### Error Handling:
Comprehensive error messages guide users in resolving issues like missing API keys, unsupported file formats, or exceeding token limits.