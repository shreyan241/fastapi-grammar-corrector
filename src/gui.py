# gui.py

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import asyncio
from src.api_client import GrammarCorrectorAPI
from src.text_processing import split_into_paragraphs
from src.file_handlers import extract_text
from src.output_manager import save_corrected_document
from src.cache_manager import clear_cache
from src.document_types import DOCUMENT_TYPES
from src.prompts import DOCUMENT_PROMPTS, get_doc_prompt
from src.utils import count_tokens
from src.config import (
    DEFAULT_CONTEXT_WINDOW_SIZE, DEFAULT_TOKEN_LIMIT, MIN_CONTEXT_WINDOW_SIZE, MAX_CONTEXT_WINDOW_SIZE,
    DEFAULT_TEMPERATURE, MIN_TEMPERATURE, MAX_TEMPERATURE, DEFAULT_DOCUMENT_TYPE,
    DEFAULT_LANGUAGE_VARIANT, DEFAULT_MODEL, DEFAULT_GPT35_TOKEN_LIMIT,
    DEFAULT_GPT4_TOKEN_LIMIT
)
from loguru import logger


class ScrollableFrame(ttk.Frame):
    """
    A scrollable frame that can contain multiple widgets.
    """
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip, text=self.text, background="#ffffe0", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class GrammarCorrectorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Grammar Corrector")
        self.root.geometry("1110x700")  # Adjusted height to accommodate scroll
        self.root.resizable(True, True)  # Allow window to be resizable
        
        # Initialize variables
        self.input_file_path = tk.StringVar()
        self.output_file_path = tk.StringVar()
        self.language_variant = tk.StringVar(value=DEFAULT_LANGUAGE_VARIANT)
        self.api_key = tk.StringVar()
        self.model_choice = tk.StringVar(value=DEFAULT_MODEL)  # Model selection variable
        self.document_type = tk.StringVar()  # Document type variable
        self.total_tokens = tk.IntVar(value=0)  # Total tokens in file
        self.max_total_tokens = tk.IntVar(value=0)  # Max token limit based on model
        self.paragraphs = []
        self.processed_tokens = tk.IntVar(value=0)  # Tokens processed
        self.select_all_var = tk.BooleanVar(value=False)
        self.selected_tokens = tk.IntVar(value=0)
        self.context_window_size = tk.IntVar(value=DEFAULT_CONTEXT_WINDOW_SIZE)
        self.temperature = tk.DoubleVar(value=DEFAULT_TEMPERATURE)
        
        # Dictionary to hold current prompts (can be modified by the user)
        self.current_prompts = DOCUMENT_PROMPTS.copy()
        
        # Set up the GUI components
        self.setup_gui()
        # Initialize max_total_tokens based on the default model
        self.update_max_tokens_limit()
        # Set default document type and load its prompt
        self.set_default_document_type()
        self.root.after(100, self.load_selected_prompt)
    
    def setup_gui(self):
        main_frame = ScrollableFrame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        padding_options = {'padx': 5, 'pady': 5}
        
        # Input File Selection
        ttk.Label(main_frame.scrollable_frame, text="Input File:").grid(row=0, column=0, sticky='W', **padding_options)
        input_entry = ttk.Entry(main_frame.scrollable_frame, textvariable=self.input_file_path, width=50)
        input_entry.grid(row=0, column=1, columnspan=2, sticky='EW', **padding_options)
        ttk.Button(main_frame.scrollable_frame, text="Browse", command=self.browse_file).grid(row=0, column=3, sticky='W', **padding_options)
        
        # Output File Selection
        ttk.Label(main_frame.scrollable_frame, text="Output File:").grid(row=1, column=0, sticky='W', **padding_options)
        output_entry = ttk.Entry(main_frame.scrollable_frame, textvariable=self.output_file_path, width=50)
        output_entry.grid(row=1, column=1, columnspan=2, sticky='EW', **padding_options)
        ttk.Button(main_frame.scrollable_frame, text="Save As", command=self.save_file).grid(row=1, column=3, sticky='W', **padding_options)
        
        # Language and Model Selection
        ttk.Label(main_frame.scrollable_frame, text="Language:").grid(row=2, column=0, sticky='W', **padding_options)
        language_combo = ttk.Combobox(main_frame.scrollable_frame, textvariable=self.language_variant, values=["American English", "British English"], state="readonly", width=20)
        language_combo.grid(row=2, column=1, sticky='W', **padding_options)
        
        ttk.Label(main_frame.scrollable_frame, text="Model:").grid(row=2, column=2, sticky='W', **padding_options)
        model_combo = ttk.Combobox(main_frame.scrollable_frame, textvariable=self.model_choice, values=["gpt-3.5-turbo", "gpt-4o-mini"], state="readonly", width=20)
        model_combo.grid(row=2, column=3, sticky='W', **padding_options)
        model_combo.bind("<<ComboboxSelected>>", self.update_max_tokens_limit)
        
        # API Key Entry
        ttk.Label(main_frame.scrollable_frame, text="OpenAI API Key:").grid(row=3, column=0, sticky='W', **padding_options)
        api_key_entry = ttk.Entry(main_frame.scrollable_frame, textvariable=self.api_key, width=50, show="*")
        api_key_entry.grid(row=3, column=1, columnspan=3, sticky='EW', **padding_options)
        
        # Document Type
        ttk.Label(main_frame.scrollable_frame, text="Document Type:").grid(row=4, column=0, sticky='W', **padding_options)
        document_types = [f"{key} ({value})" for key, value in DOCUMENT_TYPES.items()]
        document_type_combo = ttk.Combobox(main_frame.scrollable_frame, textvariable=self.document_type, values=document_types, state="readonly", width=80)
        document_type_combo.grid(row=4, column=1, sticky='W', **padding_options)
        document_type_combo.bind("<<ComboboxSelected>>", self.load_selected_prompt)
        
        # Prompt and Paragraph Selection (side by side)
        content_frame = ttk.Frame(main_frame.scrollable_frame)
        content_frame.grid(row=5, column=0, columnspan=3, sticky='NSEW', **padding_options)
        
        # Prompt
        ttk.Label(content_frame, text="Prompt:").grid(row=0, column=0, sticky='NW', **padding_options)
        self.prompt_text = tk.Text(content_frame, width=50, height=15, wrap='word')
        self.prompt_text.grid(row=1, column=0, sticky='NSEW', **padding_options)
        
        # Paragraph Selection
        ttk.Label(content_frame, text="Select Paragraphs:").grid(row=0, column=1, sticky='NW', **padding_options)
        self.paragraph_listbox = tk.Listbox(content_frame, selectmode=tk.MULTIPLE, width=50, height=15)
        self.paragraph_listbox.grid(row=1, column=1, sticky='NSEW', **padding_options)
        self.paragraph_listbox.bind('<<ListboxSelect>>', self.update_selected_tokens)
        
        # Select All Checkbox
        select_all_frame = ttk.Frame(content_frame)
        select_all_frame.grid(row=2, column=1, sticky='W', **padding_options)
        
        self.select_all_checkbox = ttk.Checkbutton(
            select_all_frame, 
            text="Select All", 
            variable=self.select_all_var, 
            command=self.toggle_select_all
        )
        self.select_all_checkbox.pack(side=tk.LEFT)
        
        # Advanced Settings (to the side)
        advanced_frame = ttk.LabelFrame(main_frame.scrollable_frame, text="Advanced Settings")
        advanced_frame.grid(row=5, column=3, rowspan=2, padx=10, pady=10, sticky='NSEW')
        
        # Context Window Size Control
        ttk.Label(advanced_frame, text="Context Window Size:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        context_slider = ttk.Scale(advanced_frame, from_=MIN_CONTEXT_WINDOW_SIZE, to=MAX_CONTEXT_WINDOW_SIZE, 
                                   orient='horizontal', variable=self.context_window_size, 
                                   command=self.update_context_window_label)
        context_slider.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.context_window_label = ttk.Label(advanced_frame, text=f"{DEFAULT_CONTEXT_WINDOW_SIZE} paragraphs")
        self.context_window_label.grid(row=0, column=2, padx=5, pady=5, sticky='w')

        # Temperature Control
        ttk.Label(advanced_frame, text="Temperature:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        temp_slider = ttk.Scale(advanced_frame, from_=MIN_TEMPERATURE, to=MAX_TEMPERATURE, 
                                orient='horizontal', variable=self.temperature, 
                                command=self.update_temp_label)
        temp_slider.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        self.temp_label = ttk.Label(advanced_frame, text=f"{DEFAULT_TEMPERATURE:.1f}")
        self.temp_label.grid(row=1, column=2, padx=5, pady=5, sticky='w')
        
        # Tooltips
        Tooltip(context_slider, "Number of previous paragraphs to consider for context")
        Tooltip(temp_slider, "Controls randomness: Lower values for more focused output, higher for more variety")
        
        # Token Information
        token_frame = ttk.Frame(main_frame.scrollable_frame)
        token_frame.grid(row=6, column=0, columnspan=2, sticky='EW', **padding_options)
        
        ttk.Label(token_frame, text="Selected Tokens:").pack(side=tk.LEFT, padx=5)
        self.selected_token_label_widget = ttk.Label(token_frame, textvariable=self.selected_tokens)
        self.selected_token_label_widget.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(token_frame, text="Max Tokens:").pack(side=tk.LEFT, padx=5)
        self.max_token_label = ttk.Label(token_frame, textvariable=self.max_total_tokens)
        self.max_token_label.pack(side=tk.LEFT, padx=5)
        
        # Progress Bar
        self.progress = ttk.Progressbar(main_frame.scrollable_frame, length=400, mode='determinate')
        self.progress.grid(row=7, column=0, columnspan=4, pady=10, sticky='EW')
        
        # Action Buttons
        button_frame = ttk.Frame(main_frame.scrollable_frame)
        button_frame.grid(row=8, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Reset to Default", command=self.reset_to_default).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Run Grammar Correction", command=self.run_correction_thread).pack(side=tk.LEFT, padx=5)

    def reset_to_default(self):
        self.input_file_path.set('')
        self.output_file_path.set('')
        self.paragraph_listbox.delete(0, tk.END)
        self.total_tokens.set(0)
        self.selected_tokens.set(0)
        self.paragraphs = []
        self.select_all_var.set(False)
        self.api_key.set('')  # Clear the API key
        self.update_token_display()
        
        # Reset other fields to their default values
        self.language_variant.set(DEFAULT_LANGUAGE_VARIANT)
        self.model_choice.set(DEFAULT_MODEL)
        self.document_type.set(DEFAULT_DOCUMENT_TYPE)
        
        # Reset sliders
        self.context_window_size.set(DEFAULT_CONTEXT_WINDOW_SIZE)
        self.temperature.set(DEFAULT_TEMPERATURE)
        self.update_context_window_label(DEFAULT_CONTEXT_WINDOW_SIZE)
        self.update_temp_label(DEFAULT_TEMPERATURE)
        
        # Reset prompt text
        self.prompt_text.delete('1.0', tk.END)
        self.prompt_text.insert('1.0', self.current_prompts[DEFAULT_DOCUMENT_TYPE])
        
        # Reset progress bar
        self.progress['value'] = 0
    
    def update_context_window_label(self, value):
        size = int(float(value))
        self.context_window_label.config(text=f"{size} paragraph{'s' if size > 1 else ''}")
        logger.info(f"Context window size changed to: {size} paragraph{'s' if size > 1 else ''}")

    def update_temp_label(self, value):
        temp_value = float(value)
        self.temp_label.config(text=f"{temp_value:.1f}")
        logger.info(f"Temperature changed to: {temp_value:.1f}")
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Input File",
            filetypes=[
                ("Word Documents", "*.docx"),
                ("PDF Files", "*.pdf"),
                ("Text Files", "*.txt")
            ]
        )
        if file_path:
            self.input_file_path.set(file_path)
            self.set_default_output_path(file_path)
            self.load_paragraphs(file_path)
    
    def set_default_document_type(self):
        default_type = f"{DEFAULT_DOCUMENT_TYPE} ({DOCUMENT_TYPES[DEFAULT_DOCUMENT_TYPE]})"
        self.document_type.set(default_type)
        logger.debug(f"Default document type set to: {default_type}")
        
    def set_default_output_path(self, input_path):
        directory, filename = os.path.split(input_path)
        name, ext = os.path.splitext(filename)
        default_output = os.path.join(directory, f"{name}_corrected{ext}")
        self.output_file_path.set(default_output)
        
    def save_file(self):
        input_path = self.input_file_path.get()
        if not input_path:
            messagebox.showerror("Error", "Please select an input file first.")
            return
        _, ext = os.path.splitext(input_path)
        if not ext:
            ext = ".docx"  # Default to .docx if no extension
        file_path = filedialog.asksaveasfilename(
            title="Save Output File As",
            defaultextension=ext,  # Set default extension based on input file
            initialfile=self.output_file_path.get(),  # Set default file name
            filetypes=[
                ("Word Documents", "*.docx"),
                ("PDF Files", "*.pdf"),
                ("Text Files", "*.txt")
            ]
        )
        if file_path:
            self.output_file_path.set(file_path)
        
    def load_paragraphs(self, file_path):
        try:
            text = extract_text(file_path)
            self.paragraphs = split_into_paragraphs(text)
            self.paragraph_listbox.delete(0, tk.END)
            total_tokens = 0
            for idx, para in enumerate(self.paragraphs):
                tokens = count_tokens(para, self.model_choice.get())  # Pass selected model
                total_tokens += tokens
                display_text = para[:35] + '...' if len(para) > 35 else para
                self.paragraph_listbox.insert(tk.END, f"Paragraph {idx}: {display_text}")
            self.total_tokens.set(total_tokens)
            self.update_token_display()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract text: {e}")
            logger.error(f"Failed to extract text from {file_path}: {e}")
    
    def toggle_select_all(self):
        if self.select_all_var.get():
            self.paragraph_listbox.select_set(0, tk.END)
            self.update_selected_tokens()
        else:
            self.paragraph_listbox.select_clear(0, tk.END)
            self.selected_tokens.set(0)
            self.update_token_display()
    
    def update_selected_tokens(self, event=None):
        selected_indices = self.paragraph_listbox.curselection()
        selected_paragraphs = [self.paragraphs[i] for i in selected_indices]
        total_selected_tokens = sum([count_tokens(para, self.model_choice.get()) for para in selected_paragraphs])
        self.selected_tokens.set(total_selected_tokens)
        self.update_token_display()
    
    def recalculate_all_tokens(self, event=None):
        # Recalculate total tokens in file
        if self.paragraphs:
            text = '\n\n'.join(self.paragraphs)
            total_tokens = count_tokens(text, self.model_choice.get())
            self.total_tokens.set(total_tokens)
        
        # Recalculate selected tokens
        self.update_selected_tokens()
    
    def update_max_tokens_limit(self, event=None):
        model = self.model_choice.get()
        logger.info(f"Selected model: '{model}'")  # Debugging statement
        if model == "gpt-3.5-turbo":
            self.max_total_tokens.set(DEFAULT_GPT35_TOKEN_LIMIT)
        elif model == "gpt-4o-mini":
            self.max_total_tokens.set(DEFAULT_GPT4_TOKEN_LIMIT)
        else:
            self.max_total_tokens.set(DEFAULT_TOKEN_LIMIT)
        logger.info(f"Max token limit set to: {self.max_total_tokens.get()}")  # Debugging statement
        self.recalculate_all_tokens()  # Recalculate tokens based on new limits
        self.update_token_display()

    
    def load_selected_prompt(self, event=None):
        """
        Loads the prompt corresponding to the selected document type into the prompt text box.
        """
        # Extract the document type from the selected Combobox value
        selected_display = self.document_type.get()
        # The display is in the format: "Document Type (Examples)"
        doc_type = selected_display.split(" (")[0] if " (" in selected_display else selected_display
        
        # Retrieve the corresponding prompt
        prompt = self.current_prompts.get(doc_type, "")
        
        # Load the prompt into the text box
        self.prompt_text.delete('1.0', tk.END)  # Clear previous content
        self.prompt_text.insert(tk.END, prompt.strip())
    
    def get_custom_prompt(self):
        """
        Retrieves the prompt based on user edits in the prompt text box.
        """
        return self.prompt_text.get("1.0", tk.END).strip()
    
    def update_token_display(self):
        selected = self.selected_tokens.get()
        max_limit = self.max_total_tokens.get()
        if selected > max_limit:
            self.selected_token_label_widget.config(foreground="red")
        else:
            self.selected_token_label_widget.config(foreground="black")
    
    def count_processable_tokens(self, paragraphs, max_token_limit):
        cumulative_tokens = 0
        paragraphs_to_process = 0
        for para in paragraphs:
            tokens = count_tokens(para, self.model_choice.get())
            if cumulative_tokens + tokens <= max_token_limit:
                cumulative_tokens += tokens
                paragraphs_to_process += 1
            else:
                break
        return cumulative_tokens, paragraphs_to_process

    def filter_paragraphs_within_token_limit(self, selected_indices, selected_paragraphs, max_token_limit):
        cumulative_tokens = 0
        allowed_paragraphs = []
        allowed_indices = []
        for idx, para in zip(selected_indices, selected_paragraphs):
            tokens = count_tokens(para, self.model_choice.get())
            if cumulative_tokens + tokens <= max_token_limit:
                allowed_paragraphs.append(para)
                allowed_indices.append(idx)
                cumulative_tokens += tokens
            else:
                break
        return allowed_paragraphs, allowed_indices, cumulative_tokens
    
    def run_correction_thread(self):
        # Start the correction process in a separate thread to keep GUI responsive
        thread = threading.Thread(target=self.run_correction)
        thread.start()
    
    def run_correction(self):
        input_path = self.input_file_path.get()
        output_path = self.output_file_path.get()
        language = self.language_variant.get()
        api_key = self.api_key.get()
        selected_indices = self.paragraph_listbox.curselection()
        max_token_limit = self.max_total_tokens.get()
        temperature = self.temperature.get()
        
        # Validate inputs
        if not input_path:
            messagebox.showerror("Error", "Please select an input file.")
            return
    
        if not output_path:
            messagebox.showerror("Error", "Please specify an output file path.")
            return
    
        if not api_key:
            messagebox.showerror("Error", "Please enter your OpenAI API key.")
            return
            
        if not selected_indices:
            messagebox.showerror("Error", "Please select at least one paragraph to process.")
            return
        
        # Calculate total tokens for selected paragraphs
        selected_paragraphs = [self.paragraphs[i] for i in selected_indices]
        selected_tokens = sum([count_tokens(para, self.model_choice.get()) for para in selected_paragraphs])
        
        # Check if total tokens exceed the limit
        if selected_tokens > max_token_limit:
            self.selected_token_label_widget.config(text=f"{selected_tokens}", foreground="red")
            cumulative_tokens, paragraphs_to_process = self.count_processable_tokens(selected_paragraphs, max_token_limit)
            
            user_response = messagebox.askokcancel(
            "Token Limit Exceeded",
            f"The selected paragraphs have {selected_tokens} tokens, which exceeds the maximum allowed {max_token_limit} tokens.\n"
            f"Only the first {paragraphs_to_process} selectedparagraphs (totaling {cumulative_tokens} tokens) will be processed.\n\n"
            "Do you want to continue?",
            icon=messagebox.WARNING
        )
        
            if not user_response:
                # User clicked "Cancel" or closed the dialog
                return  # Exit the method without running the correction
        
            # Determine which paragraphs to process within the token limit
            selected_paragraphs, selected_indices, cumulative_tokens = self.filter_paragraphs_within_token_limit(
            selected_indices, selected_paragraphs, max_token_limit)
            self.processed_tokens.set(cumulative_tokens)
        else:
            self.selected_token_label_widget.config(text=f"{selected_tokens}", foreground="black")
            self.processed_tokens.set(selected_tokens)

        
        # Update progress bar
        total_tokens_to_process = self.processed_tokens.get()
        self.progress['value'] = 0
        self.progress['maximum'] = total_tokens_to_process
        
        # Initialize API client
        api_client = GrammarCorrectorAPI(api_key, language, model=self.model_choice.get(), temperature=temperature)
        
        # Get the selected document type
        selected_display = self.document_type.get()
        doc_type = selected_display.split(" (")[0]
        
        # Get the context window size
        context_window_size = self.context_window_size.get()
        logger.info("Starting grammar correction process")
        logger.info(f"Selected paragraphs: {selected_indices}")
        logger.info(f"Context window size: {context_window_size}")
        
        # Process paragraphs asynchronously
        try:
            corrected_paragraphs, unprocessed = asyncio.run(
                api_client.correct_paragraphs(
                    self.paragraphs,
                    list(selected_indices),
                    max_token_limit,
                    self.update_progress,
                    doc_type,  # Pass doc_type instead of prompt_template
                    self.language_variant.get(),  # Pass language_variant
                    self.get_custom_prompt(), # Pass the custom prompt
                    context_window_size
                )
            )
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during correction: {e}")
            logger.error(f"Error during correction: {e}")
            return
        
        # Update paragraphs with corrected versions
        self.paragraphs = corrected_paragraphs
        
        # Save corrected document
        try:
            corrected_text = '\n\n'.join(self.paragraphs)  # Ensures paragraphs are separated by two newlines
            save_corrected_document(input_path, output_path, corrected_text)
            messagebox.showinfo("Success", f"Corrected file saved to {output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save corrected document: {e}")
            logger.error(f"Failed to save corrected document: {e}")
        
        # Notify about unprocessed paragraphs
        if selected_tokens > max_token_limit and unprocessed:
            unprocessed_count = len(selected_paragraphs) - len(corrected_paragraphs)
            messagebox.showwarning(
                "Unprocessed Paragraphs",
                f"{unprocessed_count} paragraph(s) were not processed due to token limits."
            )
        
        # Clear cache after processing
        clear_cache()
        logger.info("Grammar correction process completed")
    
    def update_progress(self, tokens_processed):
        self.progress['value'] += tokens_processed
        self.progress.update()
        logger.info(f"Processed {tokens_processed} tokens")

    def run(self):
        self.root.mainloop()

# To run the GUI, create an instance of GrammarCorrectorGUI and call the run method.
if __name__ == "__main__":
    app = GrammarCorrectorGUI()
    app.run()
