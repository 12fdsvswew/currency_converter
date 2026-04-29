import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime

class CurrencyConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Currency Converter")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # API configuration
        self.api_key = "YOUR_API_KEY"  # Замените на ваш ключ
        self.base_url = "https://v6.exchangerate-api.com/v6"
        
        # Available currencies
        self.currencies = []
        
        # History file
        self.history_file = "history.json"
        self.history = self.load_history()
        
        # Setup UI
        self.setup_ui()
        self.fetch_currencies()
        self.display_history()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # From currency
        ttk.Label(main_frame, text="From:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.from_currency = ttk.Combobox(main_frame, values=[], state="readonly", width=20)
        self.from_currency.grid(row=0, column=1, pady=5, padx=5)
        self.from_currency.set("USD")
        
        # To currency
        ttk.Label(main_frame, text="To:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.to_currency = ttk.Combobox(main_frame, values=[], state="readonly", width=20)
        self.to_currency.grid(row=1, column=1, pady=5, padx=5)
        self.to_currency.set("EUR")
        
        # Amount input
        ttk.Label(main_frame, text="Amount:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.amount_entry = ttk.Entry(main_frame, width=23)
        self.amount_entry.grid(row=2, column=1, pady=5, padx=5)
        
        # Convert button
        self.convert_btn = ttk.Button(main_frame, text="Convert", command=self.convert)
        self.convert_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Result label
        self.result_label = ttk.Label(main_frame, text="", font=("Arial", 12, "bold"))
        self.result_label.grid(row=4, column=0, columnspan=2, pady=10)
        
        # History table
        ttk.Label(main_frame, text="Conversion History:", font=("Arial", 10, "bold")).grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        # Treeview for history
        columns = ("Date", "From", "To", "Amount", "Result")
        self.history_tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=12)
        
        # Define headings
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)
        
        self.history_tree.grid(row=6, column=0, columnspan=2, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        scrollbar.grid(row=6, column=2, sticky=(tk.N, tk.S))
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Clear History", command=self.clear_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Refresh Rates", command=self.fetch_currencies).pack(side=tk.LEFT, padx=5)
    
    def fetch_currencies(self):
        """Fetch available currencies from API"""
        try:
            url = f"{self.base_url}/{self.api_key}/codes"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get("result") == "success":
                self.currencies = [code[0] for code in data.get("supported_codes", [])]
                self.from_currency['values'] = self.currencies
                self.to_currency['values'] = self.currencies
                print(f"Loaded {len(self.currencies)} currencies")
            else:
                messagebox.showerror("Error", f"Failed to fetch currencies: {data.get('error-type', 'Unknown error')}")
                self.use_fallback_currencies()
        except Exception as e:
            messagebox.showerror("Error", f"Network error: {str(e)}")
            self.use_fallback_currencies()
    
    def use_fallback_currencies(self):
        """Fallback currencies if API fails"""
        fallback = ["USD", "EUR", "GBP", "JPY", "CNY", "RUB", "CAD", "AUD", "CHF", "INR"]
        self.currencies = fallback
        self.from_currency['values'] = fallback
        self.to_currency['values'] = fallback
    
    def convert(self):
        """Perform currency conversion"""
        # Validate input
        amount_str = self.amount_entry.get().strip()
        
        if not amount_str:
            messagebox.showwarning("Warning", "Please enter an amount")
            return
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showwarning("Warning", "Amount must be positive")
                return
        except ValueError:
            messagebox.showwarning("Warning", "Please enter a valid number")
            return
        
        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()
        
        if not from_curr or not to_curr:
            messagebox.showwarning("Warning", "Please select currencies")
            return
        
        # Get conversion rate
        try:
            url = f"{self.base_url}/{self.api_key}/pair/{from_curr}/{to_curr}/{amount}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get("result") == "success":
                converted_amount = data.get("conversion_result")
                rate = data.get("conversion_rate")
                
                result_text = f"{amount:,.2f} {from_curr} = {converted_amount:,.2f} {to_curr} (Rate: {rate:.4f})"
                self.result_label.config(text=result_text)
                
                # Save to history
                self.save_to_history(from_curr, to_curr, amount, converted_amount)
            else:
                messagebox.showerror("Error", f"Conversion failed: {data.get('error-type', 'Unknown error')}")
        except Exception as e:
            messagebox.showerror("Error", f"Network error: {str(e)}")
    
    def save_to_history(self, from_curr, to_curr, amount, result):
        """Save conversion to history JSON"""
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "from": from_curr,
            "to": to_curr,
            "amount": amount,
            "result": result
        }
        self.history.append(entry)
        self.save_history()
        self.display_history()
    
    def save_history(self):
        """Save history to JSON file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def load_history(self):
        """Load history from JSON file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading history: {e}")
                return []
        return []
    
    def display_history(self):
        """Display history in the table"""
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Add history entries
        for entry in reversed(self.history[-50:]):  # Show last 50 entries
            self.history_tree.insert("", tk.END, values=(
                entry.get("date", ""),
                entry.get("from", ""),
                entry.get("to", ""),
                f"{entry.get('amount', 0):,.2f}",
                f"{entry.get('result', 0):,.2f}"
            ))
    
    def clear_history(self):
        """Clear all history"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all history?"):
            self.history = []
            self.save_history()
            self.display_history()
            messagebox.showinfo("Success", "History cleared")

def main():
    root = tk.Tk()
    app = CurrencyConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()