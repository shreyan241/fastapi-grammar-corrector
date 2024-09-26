# gui.py

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import asyncio
from api_client import GrammarCorrectorAPI
from text_processing import split_into_paragraphs
from file_handlers import extract_text
from output_manager import save_corrected_document
from cache_manager import clear_cache
import os
from utils import count_tokens
from loguru import logger


class GrammarCorrectorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Grammar Corrector")
        self.root.geometry("900x800")  # Set window size at the start
        self.root.resizable(True, True)  # Allow window to be resizable
        
        # Configure grid weights for responsiveness
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Initialize variables
        self.input_file_path = tk.StringVar()
        self.output_file_path = tk.StringVar()
        self.language_variant = tk.StringVar(value="British English")
        self.api_key = tk.StringVar()
        self.model_choice = tk.StringVar(value="gpt-4o-mini")  # Model selection variable
        self.total_tokens = tk.IntVar(value=0)  # Total tokens in file
        self.max_total_tokens = tk.IntVar(value=0)  # Max token limit based on model
        self.paragraphs = []
        self.processed_tokens = tk.IntVar(value=0)  # Tokens processed
        self.select_all_var = tk.BooleanVar(value=False)
        self.selected_tokens = tk.IntVar(value=0)
        
        # Set up the GUI components
        self.setup_gui()
        # Initialize max_total_tokens based on the default model
        self.update_max_tokens_limit()
        
    def setup_gui(self):
        # Create a main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="NSEW")
        
        # Configure grid weights for the main frame
        for i in range(11):
            main_frame.grid_rowconfigure(i, weight=0)
        main_frame.grid_rowconfigure(10, weight=1)  # Allow the listbox to expand
        main_frame.grid_columnconfigure(1, weight=1)
        
        padding_options = {'padx': 5, 'pady': 5}
        
        # Input File Selection
        ttk.Label(main_frame, text="Input File:").grid(row=0, column=0, sticky='W', **padding_options)
        input_entry = ttk.Entry(main_frame, textvariable=self.input_file_path, width=70)
        input_entry.grid(row=0, column=1, sticky='EW', **padding_options)
        ttk.Button(main_frame, text="Browse", command=self.browse_file).grid(row=0, column=2, sticky='W', **padding_options)
        
        # Output File Selection
        ttk.Label(main_frame, text="Output File:").grid(row=1, column=0, sticky='W', **padding_options)
        output_entry = ttk.Entry(main_frame, textvariable=self.output_file_path, width=70)
        output_entry.grid(row=1, column=1, sticky='EW', **padding_options)
        ttk.Button(main_frame, text="Save As", command=self.save_file).grid(row=1, column=2, sticky='W', **padding_options)
        
        # Language Variant Selection
        ttk.Label(main_frame, text="Language Variant:").grid(row=2, column=0, sticky='W', **padding_options)
        language_combo = ttk.Combobox(
            main_frame, 
            textvariable=self.language_variant, 
            values=["American English", "British English"], 
            state="readonly",
            width=67
        )
        language_combo.grid(row=2, column=1, sticky='W', **padding_options)
        
        # OpenAI API Key Entry
        ttk.Label(main_frame, text="OpenAI API Key:").grid(row=3, column=0, sticky='W', **padding_options)
        api_key_entry = ttk.Entry(main_frame, textvariable=self.api_key, width=70, show="*")
        api_key_entry.grid(row=3, column=1, sticky='EW', **padding_options)
        
        # Model Selection
        ttk.Label(main_frame, text="Select Model:").grid(row=4, column=0, sticky='W', **padding_options)
        model_combo = ttk.Combobox(
            main_frame, 
            textvariable=self.model_choice, 
            values=["gpt-3.5-turbo", "gpt-4o-mini"],  # Model options
            state="readonly",
            width=67
        )
        model_combo.grid(row=4, column=1, sticky='W', **padding_options)
        model_combo.bind("<<ComboboxSelected>>", self.update_max_tokens_limit)
        
        # Total Token Limit Display
        ttk.Label(main_frame, text="Total Tokens Selected:").grid(row=5, column=0, sticky='W', **padding_options)
        # Assign the selected tokens label to an instance variable for later configuration
        self.selected_token_label_widget = ttk.Label(main_frame, textvariable=self.selected_tokens, foreground="black")
        self.selected_token_label_widget.grid(row=5, column=1, sticky='W', **padding_options)
        
        ttk.Label(main_frame, text="Max Token Limit:").grid(row=5, column=2, sticky='W', **padding_options)
        self.max_token_label = ttk.Label(main_frame, textvariable=self.max_total_tokens)
        self.max_token_label.grid(row=5, column=3, sticky='W', **padding_options)

        ttk.Label(main_frame, text="Total Tokens in File:").grid(row=6, column=0, sticky='W', **padding_options)
        total_token_label = ttk.Label(main_frame, textvariable=self.total_tokens)
        total_token_label.grid(row=6, column=1, sticky='W', **padding_options)

        
        # Select All Paragraphs Checkbox
        select_all_checkbox = ttk.Checkbutton(
            main_frame, 
            text="Select All Paragraphs", 
            variable=self.select_all_var, 
            command=self.toggle_select_all
        )
        select_all_checkbox.grid(row=7, column=0, sticky='W', **padding_options)
        
        # Paragraph Selection Listbox with Scrollbar
        ttk.Label(main_frame, text="Select Paragraphs to Process:").grid(row=8, column=0, sticky='NW', **padding_options)
        
        listbox_frame = ttk.Frame(main_frame)
        listbox_frame.grid(row=8, column=1, columnspan=2, sticky='NSEW', **padding_options)
        
        # Configure listbox_frame grid
        listbox_frame.grid_rowconfigure(0, weight=1)
        listbox_frame.grid_columnconfigure(0, weight=1)
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        self.paragraph_listbox = tk.Listbox(
            listbox_frame, 
            selectmode=tk.MULTIPLE, 
            width=100, 
            height=15, 
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.paragraph_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.paragraph_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.paragraph_listbox.bind('<<ListboxSelect>>', self.update_selected_tokens)
        
        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, length=800, mode='determinate')
        self.progress.grid(row=9, column=0, columnspan=4, pady=20, sticky='EW')
        
        # Run Correction Button
        run_button = ttk.Button(
            main_frame, 
            text="Run Grammar Correction",  
            command=self.run_correction_thread
        )
        run_button.grid(row=10, column=0, columnspan=4, pady=10)
        
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
            for idx, para in enumerate(self.paragraphs, 1):
                tokens = count_tokens(para, self.model_choice.get())  # Pass selected model
                total_tokens += tokens
                display_text = para[:50] + '...' if len(para) > 50 else para
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
        if model == "gpt-3.5-turbo":
            self.max_total_tokens.set(20000)  # Example limit for GPT-3.5-turbo
        elif model == "gpt-4o-mini":
            self.max_total_tokens.set(30000)  # Example limit for GPT-4o-mini
        else:
            self.max_total_tokens.set(10000)  # Default limit
        logger.info(f"Max token limit set to: {self.max_total_tokens.get()}")
        self.recalculate_all_tokens()  # Recalculate tokens based on new limits
    
    def update_token_display(self):
        selected = self.selected_tokens.get()
        max_limit = self.max_total_tokens.get()
        if selected > max_limit:
            self.selected_token_label_widget.config(foreground="red")
        else:
            self.selected_token_label_widget.config(foreground="black")
    
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
        
        # Validate inputs
        if not input_path or not output_path or not api_key:
            messagebox.showerror("Error", "Please fill in all fields.")
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
            messagebox.showwarning(
                "Token Limit Exceeded",
                f"The selected paragraphs have {selected_tokens} tokens, which exceeds the maximum allowed {max_token_limit} tokens.\n"
                f"Only the first {max_token_limit} tokens will be processed."
            )
            # Determine which paragraphs to process within the token limit
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
            selected_paragraphs = allowed_paragraphs
            selected_indices = allowed_indices
            self.processed_tokens.set(cumulative_tokens)
        else:
            self.selected_token_label_widget.config(text=f"{selected_tokens}", foreground="black")
            self.processed_tokens.set(selected_tokens)
        
        # Update progress bar
        total_tokens_to_process = self.processed_tokens.get()
        self.progress['value'] = 0
        self.progress['maximum'] = total_tokens_to_process
        
        # Initialize API client
        api_client = GrammarCorrectorAPI(api_key, language, model=self.model_choice.get())
        
        # Process paragraphs asynchronously
        try:
            corrected_paragraphs, unprocessed = asyncio.run(
                api_client.correct_paragraphs(selected_paragraphs, max_token_limit, self.update_progress)
            )
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during correction: {e}")
            logger.error(f"Error during correction: {e}")
            return
        
        # Replace the original paragraphs with corrected ones
        for idx, i in enumerate(selected_indices[:len(corrected_paragraphs)]):
            self.paragraphs[i] = corrected_paragraphs[idx]
        
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
    
    def update_progress(self, tokens_processed):
        self.progress['value'] += tokens_processed
        self.progress.update()

    def run(self):
        self.root.mainloop()
