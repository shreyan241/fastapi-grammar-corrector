# Grammar Corrector

A Python-based GUI application that corrects English grammar, spelling, and style in Word documents (`.docx`), PDFs (`.pdf`), and plain text files (`.txt`) using OpenAI's GPT models.

## Features

- **Multi-Format Support:** Process Word documents, PDFs, and TXT files.
- **Paragraph-Based Processing:** Maintains context by processing text paragraph by paragraph.
- **Document Type Customization:**
  - **Extensive Document Type Selection:** Choose from various document types (e.g., Legal, Editorial, Medical, Academic, Business, Technical, Creative, Personal, Marketing, Financial) with embedded guidelines for each.
  - **Customizable Prompts:** Edit the correction prompts directly within the GUI to tailor the correction process to specific needs.
- **Efficient Caching Mechanism:** Avoids redundant API calls by caching previously processed texts, enhancing efficiency and reducing costs.
- **Smart Rate Limiting:** Adheres to OpenAI's API rate limits using asynchronous rate limiting to prevent errors and ensure smooth operation.
- **Language Variant Support:** Choose between American English and British English for corrections.
- **Model Selection:** Option to select different GPT models based on user preference and API access.
- **Selective Paragraph Processing:** Ability to choose specific paragraphs for correction or process the entire document.
- **Context-Aware Corrections:** Uses previous paragraphs as context for maintaining consistency in corrections.
- **Token Management:** Intelligent handling of token limits with tracking of unprocessed paragraphs.
- **Customizable Settings:** Adjust parameters like context window size and temperature.
- **Detailed Logging:** Utilizes `loguru` for comprehensive logging to aid in debugging and monitoring.

## Installation

### Executable Version (Windows)

1. Download the `GrammarCorrector-v1.0.zip` file from this repository.
2. Extract the contents of the zip file to a folder of your choice.
3. Run `GrammarCorrector.exe` to start the application.

**Note:** The executable version does not require Python or any additional dependencies to be installed on your system.

### From Source

#### Prerequisites

- Python 3.12 or higher
- An OpenAI API key

#### Steps

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/grammar_corrector.git
   cd grammar_corrector
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python main.py
   ```

## Usage

1. Launch the application by running `GrammarCorrector.exe` (for the executable version) or `python main.py` (if running from source).
2. Select the input file (`.docx`, `.pdf`, or `.txt`).
3. Choose the output file location.
4. Select the language variant (American or British English).
5. Enter your OpenAI API key.
6. Choose the GPT model.
7. Select the document type from the available options.
8. Optionally customize the correction prompt.
9. Select paragraphs to process or choose to process all.
10. Click "Run Grammar Correction" to start the process.

## Configuration

- Adjust settings in `config.py` for default values like context window size, temperature, rate limits, etc. (Only applicable when running from source)
- Customize document type prompts in `prompts.py`. (Only applicable when running from source)
- Modify caching behavior in `cache_manager.py`. (Only applicable when running from source)

## Additional Notes

- The application uses asynchronous processing for efficient API usage.
- A caching mechanism is implemented to avoid redundant API calls.
- Comprehensive error handling and logging are in place for troubleshooting.

## System Requirements (for Executable Version)

- Windows 10 or later
- 4GB RAM recommended
- Approximately 200MB of free disk space

## Troubleshooting

If you encounter any issues with the executable:
1. Ensure you have extracted all files from the zip archive.
2. Try running the application as an administrator.
3. Check your antivirus software isn't blocking the application.
4. For detailed error logs, check the `grammar_corrector.log` file in the application directory.

## Contributing

Contributions to improve the Grammar Corrector are welcome. Please feel free to submit pull requests or open issues for bugs and feature requests.
