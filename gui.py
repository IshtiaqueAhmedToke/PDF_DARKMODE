import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from typing import Optional
import threading
from pathlib import Path
from pdf_converter import PDFConverter

class DarkModeConverterGUI:
    """Main GUI application for the PDF Dark Mode Converter."""
    
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("PDF Dark Mode Converter")
        self.window.geometry("600x400")
        
        # Set minimum window size
        self.window.minsize(500, 300)
        
        # Initialize variables
        self.current_file: Optional[str] = None
        self.is_converting = False
        
        self.setup_ui()
        
        # Initialize the PDF converter
        self.converter = PDFConverter(dpi=300)
    
    def setup_ui(self) -> None:
        """Create and arrange the GUI elements."""
        # Main container with padding
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Browse button frame
        browse_frame = ttk.Frame(main_frame)
        browse_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Browse button
        self.browse_button = ttk.Button(
            browse_frame,
            text="Select PDF File",
            command=self.browse_file,
            width=20
        )
        self.browse_button.pack(pady=10)
        
        # Selected file frame
        file_frame = ttk.LabelFrame(main_frame, text="Selected File", padding="10")
        file_frame.pack(fill=tk.X, pady=(0, 20))
        
        # File path label
        self.file_label = ttk.Label(
            file_frame,
            text="No file selected",
            justify=tk.LEFT
        )
        self.file_label.pack(fill=tk.X)
        
        # Convert button
        self.convert_button = ttk.Button(
            main_frame,
            text="Convert to Dark Mode",
            command=self.start_conversion,
            state=tk.DISABLED
        )
        self.convert_button.pack(pady=10)
        
        # Progress bar (hidden by default)
        self.progress = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            orient=tk.HORIZONTAL
        )
        
        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="Select a PDF file to begin",
            justify=tk.LEFT
        )
        self.status_label.pack(fill=tk.X, pady=(20, 0))
    
    def set_file(self, file_path: str) -> None:
        """Set the current file and update the UI accordingly."""
        self.current_file = file_path
        self.file_label.config(text=f"Selected: {os.path.basename(file_path)}")
        self.convert_button.config(state=tk.NORMAL)
        self.status_label.config(text="Ready to convert")
    
    def browse_file(self) -> None:
        """Open a file dialog to select a PDF file."""
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf")]
        )
        if file_path:
            self.set_file(file_path)
    
    def start_conversion(self) -> None:
        """Start the PDF conversion process in a separate thread."""
        if self.is_converting or not self.current_file:
            return
        
        # Disable controls during conversion
        self.convert_button.config(state=tk.DISABLED)
        self.browse_button.config(state=tk.DISABLED)
        
        # Show progress bar
        self.progress.pack(fill=tk.X, pady=(10, 10))
        self.progress.start(10)
        
        # Set converting flag
        self.is_converting = True
        
        # Get output path
        input_path = Path(self.current_file)
        output_path = input_path.parent / f"{input_path.stem}_darkmode{input_path.suffix}"
        
        # Start conversion in separate thread
        thread = threading.Thread(
            target=self.perform_conversion,
            args=(str(input_path), str(output_path))
        )
        thread.start()
    
    def perform_conversion(self, input_path: str, output_path: str) -> None:
        """Perform the actual PDF conversion."""
        try:
            self.status_label.config(text="Converting PDF to dark mode...")
            self.converter.convert_pdf_to_dark_mode(input_path, output_path)
            
            # Show success message
            self.window.after(0, self.show_success, output_path)
            
        except Exception as e:
            # Show error message
            self.window.after(0, self.show_error, str(e))
            
        finally:
            # Reset UI state
            self.window.after(0, self.reset_ui)
    
    def show_success(self, output_path: str) -> None:
        """Show success message and ask to open the output file."""
        if messagebox.askyesno(
            "Conversion Complete",
            f"PDF has been converted successfully!\n\nWould you like to open the folder containing the converted file?"
        ):
            os.startfile(os.path.dirname(output_path))
    
    def show_error(self, error_message: str) -> None:
        """Show error message."""
        messagebox.showerror(
            "Conversion Error",
            f"An error occurred during conversion:\n{error_message}"
        )
    
    def reset_ui(self) -> None:
        """Reset the UI state after conversion."""
        self.is_converting = False
        self.progress.stop()
        self.progress.pack_forget()
        self.convert_button.config(state=tk.NORMAL)
        self.browse_button.config(state=tk.NORMAL)
        self.status_label.config(text="Ready for next conversion")
    
    def run(self) -> None:
        """Start the GUI application."""
        self.window.mainloop()

if __name__ == "__main__":
    app = DarkModeConverterGUI()
    app.run()