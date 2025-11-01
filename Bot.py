import tkinter as tk
from tkinter import messagebox, simpledialog
import pyautogui
import time
import requests
import json
import io
import threading
import base64
import sys
import os

class HomeworkHelper:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Homework Helper")
        self.root.geometry("300x200")
        self.root.minsize(250, 150)
        
        self.gemini_api_key = "GEMINI_API_KEY_GOS_HERE"
        
        # Configure grid weights for resizing
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-h>', self.toggle_minimize)
        self.root.bind('<Control-H>', self.toggle_minimize)
        self.root.bind('<Control-Alt-Shift-D>', self.open_debug_window)
        self.root.bind('<Control-Alt-Shift-d>', self.open_debug_window)
        
        self.create_answer_screen()
    
    def toggle_minimize(self, event=None):
        """Toggle window minimize with Ctrl+H"""
        if self.root.state() == 'normal':
            self.root.iconify()  # Minimize to taskbar
        else:
            self.root.deiconify()  # Restore from minimize
            self.root.lift()
    
    def open_debug_window(self, event=None):
        """Open debug window with Ctrl+Alt+Shift+D"""
        debug_win = tk.Toplevel(self.root)
        debug_win.title("Debug Window")
        debug_win.geometry("300x200")
        debug_win.resizable(False, False)
        
        tk.Label(debug_win, text="Debug Window", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(debug_win, text="If you didn't mean to get here, press Back").pack(pady=5)
        
        # Pin entry
        pin_frame = tk.Frame(debug_win)
        pin_frame.pack(pady=10)
        
        tk.Label(pin_frame, text="Enter PIN:").pack(side=tk.LEFT)
        pin_entry = tk.Entry(pin_frame, show="*", width=10)
        pin_entry.pack(side=tk.LEFT, padx=5)
        
        def check_pin():
            if pin_entry.get() == "3507":
                debug_win.destroy()
                self.open_code_editor()
            else:
                messagebox.showerror("Error", "Incorrect PIN")
        
        # Buttons
        btn_frame = tk.Frame(debug_win)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Submit PIN", command=check_pin, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Back", command=debug_win.destroy, width=10).pack(side=tk.LEFT, padx=5)
        
        pin_entry.focus()
    
    def open_code_editor(self):
        """Open code editor window"""
        editor_win = tk.Toplevel(self.root)
        editor_win.title("Code Editor")
        editor_win.geometry("600x500")
        
        # Main frame
        main_frame = tk.Frame(editor_win)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(main_frame, text="Python Code Editor", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Text area for code
        text_frame = tk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        code_text = tk.Text(text_frame, wrap=tk.WORD, font=("Consolas", 10))
        
        # Load current code
        try:
            with open(__file__, 'r', encoding='utf-8') as f:
                current_code = f.read()
            code_text.insert(1.0, current_code)
        except:
            code_text.insert(1.0, "# Error loading current code\n")
        
        scrollbar = tk.Scrollbar(text_frame, command=code_text.yview)
        code_text.config(yscrollcommand=scrollbar.set)
        
        code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Button frame
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        def save_and_restart():
            try:
                new_code = code_text.get(1.0, tk.END)
                
                # Create backup
                if os.path.exists(__file__):
                    backup_file = __file__ + ".backup"
                    with open(backup_file, 'w', encoding='utf-8') as f:
                        with open(__file__, 'r', encoding='utf-8') as original:
                            f.write(original.read())
                
                # Save new code
                with open(__file__, 'w', encoding='utf-8') as f:
                    f.write(new_code)
                
                messagebox.showinfo("Success", "Code saved! Restarting application...")
                editor_win.destroy()
                self.root.destroy()
                
                # Restart the application
                python = sys.executable
                os.execl(python, python, *sys.argv)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {str(e)}")
        
        def reload_original():
            try:
                with open(__file__, 'r', encoding='utf-8') as f:
                    original_code = f.read()
                code_text.delete(1.0, tk.END)
                code_text.insert(1.0, original_code)
                messagebox.showinfo("Success", "Original code reloaded")
            except:
                messagebox.showerror("Error", "Failed to reload original code")
        
        tk.Button(btn_frame, text="Save & Restart", command=save_and_restart, width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Reload Original", command=reload_original, width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Back", command=editor_win.destroy, width=15).pack(side=tk.LEFT, padx=5)
    
    def create_answer_screen(self):
        self.clear_window()
        
        # Clear any previous result to ensure fresh analysis
        if hasattr(self, 'analysis_result'):
            del self.analysis_result
        
        # Main container that expands with window
        main_frame = tk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_rowconfigure(0, weight=1)  # Button row expands
        main_frame.grid_rowconfigure(1, weight=0)  # Status row fixed
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Big Answer button - expands horizontally
        self.answer_btn = tk.Button(main_frame, text="ANSWER", command=self.start_analysis, 
                                   bg="lightblue", font=("Arial", 14, "bold"))
        self.answer_btn.grid(row=0, column=0, sticky="nsew", pady=10)
        
        # Status label
        self.status = tk.Label(main_frame, text="Click ANSWER to analyze screen", 
                              font=("Arial", 9), fg="gray")
        self.status.grid(row=1, column=0, pady=5)
        
        # Help text for shortcuts
        help_label = tk.Label(main_frame, text="Ctrl+H: Minimize | Ctrl+Alt+Shift+D: Debug", 
                             font=("Arial", 7), fg="darkgray")
        help_label.grid(row=2, column=0, pady=5)
    
    def create_result_screen(self):
        self.clear_window()
        
        # Main container with proper grid weights
        main_frame = tk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_rowconfigure(0, weight=1)  # Text area expands
        main_frame.grid_rowconfigure(1, weight=0)  # Buttons fixed
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Answer display frame - expands with window
        answer_frame = tk.Frame(main_frame)
        answer_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        answer_frame.grid_rowconfigure(0, weight=1)
        answer_frame.grid_columnconfigure(0, weight=1)
        
        # Text widget with scrollbar - expands to fill space
        self.result_text = tk.Text(answer_frame, wrap=tk.WORD, font=("Arial", 10))
        self.result_text.insert(tk.END, self.analysis_result)
        self.result_text.config(state=tk.DISABLED)
        
        scrollbar = tk.Scrollbar(answer_frame, command=self.result_text.yview)
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        self.result_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Buttons frame - stays at bottom
        btn_frame = tk.Frame(main_frame)
        btn_frame.grid(row=1, column=0, sticky="ew", pady=5)
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        btn_frame.grid_columnconfigure(2, weight=1)
        
        # Buttons that expand horizontally
        tk.Button(btn_frame, text="Answer Again", command=self.start_fresh_analysis, 
                 font=("Arial", 9)).grid(row=0, column=0, sticky="ew", padx=2)
        tk.Button(btn_frame, text="Copy", command=lambda: self.copy_text(self.analysis_result), 
                 font=("Arial", 9)).grid(row=0, column=1, sticky="ew", padx=2)
        tk.Button(btn_frame, text="New Question", command=self.create_answer_screen,
                 font=("Arial", 9)).grid(row=0, column=2, sticky="ew", padx=2)
        
        # Help text for shortcuts
        help_label = tk.Label(main_frame, text="Ctrl+H: Minimize | Ctrl+Alt+Shift+D: Debug", 
                             font=("Arial", 7), fg="darkgray")
        help_label.grid(row=2, column=0, pady=5)
    
    def start_analysis(self):
        """Start analysis from answer screen"""
        self.answer_btn.config(state=tk.DISABLED, text="Processing...")
        self.status.config(text="Taking screenshot...")
        
        # Clear previous result to ensure fresh analysis
        if hasattr(self, 'analysis_result'):
            del self.analysis_result
            
        thread = threading.Thread(target=self.analyze_with_gemini)
        thread.daemon = True
        thread.start()
        self.root.after(1000, self.check_result)
    
    def start_fresh_analysis(self):
        """Start fresh analysis from result screen"""
        # Clear the previous result
        if hasattr(self, 'analysis_result'):
            del self.analysis_result
        
        # Update UI to show processing
        if hasattr(self, 'result_text'):
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Processing... Taking new screenshot...")
            self.result_text.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self.analyze_with_gemini)
        thread.daemon = True
        thread.start()
        self.root.after(1000, self.check_result)
    
    def analyze_with_gemini(self):
        """Take fresh screenshot and analyze with Gemini"""
        try:
            time.sleep(0.5)  # Small delay to ensure UI updates
            # Take FRESH screenshot every time
            screenshot = pyautogui.screenshot()
            
            img_byte_arr = io.BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            img_data = img_byte_arr.getvalue()
            
            self.analysis_result = self.send_to_gemini(img_data)
        except Exception as e:
            self.analysis_result = f"Error: {str(e)}"
    
    def send_to_gemini(self, image_data):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={self.gemini_api_key}"
            
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": "Analyze this educational question and provide the answer. Be concise and accurate."},
                        {"inline_data": {"mime_type": "image/png", "data": image_base64}}
                    ]
                }]
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if 'candidates' in result and result['candidates']:
                text_parts = result['candidates'][0]['content']['parts']
                return ''.join(part['text'] for part in text_parts if 'text' in part)
            return "No answer found"
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def check_result(self):
        if hasattr(self, 'analysis_result'):
            self.create_result_screen()
        else:
            self.root.after(1000, self.check_result)
    
    def copy_text(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copied", "Answer copied to clipboard!")
    
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = HomeworkHelper()
    app.run()

