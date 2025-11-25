# Fixed, refactored, and styled version of uploaded file. Source (uploaded): :contentReference[oaicite:0]{index=0}
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


class StationeryApp(tk.Tk):
    ITEMS = {
        "Pencil": 5,
        "Eraser": 3,
        "Pen": 5,
        "Ruler": 10,
        "Sharpener": 5,
        "Pencil Box": 50,
        "Paint Colours": 50,
        "Whitener": 30,
        "Sketch Pen": 20,
    }

    def __init__(self):
        super().__init__()
        self.title("Stationery Management")
        self.geometry("980x540")
        self.minsize(920, 520)
        self.configure(bg="#f4f6f8")

        self._create_styles()
        self._create_variables()
        self._build_ui()
        self._place_ui()

    def _create_styles(self):
        self.style = ttk.Style(self)
        # Use default theme but configure some widget-specific styles
        self.style.configure("Title.TLabel", font=("Helvetica", 20, "bold"), foreground="#ffffff", background="#2b6cb0")
        self.style.configure("Menu.TFrame", background="#2b6cb0")
        self.style.configure("MenuLabel.TLabel", font=("Calibri", 12), background="#2b6cb0", foreground="#ffffff")
        self.style.configure("Form.TFrame", background="#ffffff", relief="flat")
        self.style.configure("TButton", font=("Helvetica", 11, "bold"))
        self.style.configure("Bill.TFrame", background="#fff8dc")
        self.style.configure("ItemLabel.TLabel", font=("Arial", 11, "bold"), background="#ffffff", foreground="#1a202c")
        self.style.configure("Entry.TEntry", font=("Arial", 11))

    def _create_variables(self):
        # Use IntVar where numeric is expected; safe default 0
        self.qty_vars = {name: tk.IntVar(value=0) for name in self.ITEMS}
        self.total_var = tk.StringVar(value="Rs. 0")

    def _build_ui(self):
        # Top title bar
        self.title_frame = ttk.Frame(self, style="Menu.TFrame", padding=(12, 8))
        self.title_label = ttk.Label(self.title_frame, text="Stationery Management", style="Title.TLabel", anchor="center")

        # Left: price list / menu
        self.menu_frame = ttk.Frame(self, style="Menu.TFrame", width=260, padding=(12, 12))
        self.menu_title = ttk.Label(self.menu_frame, text="Price Menu", style="Title.TLabel", anchor="center")
        self.menu_items = []
        for name, price in self.ITEMS.items():
            lbl = ttk.Label(self.menu_frame, text=f"{name} — Rs. {price}/-", style="MenuLabel.TLabel")
            self.menu_items.append(lbl)

        # Center: input form
        self.form_frame = ttk.Frame(self, style="Form.TFrame", padding=(18, 18))
        self.form_title = ttk.Label(self.form_frame, text="Enter quantities", style="ItemLabel.TLabel")
        self.entries = {}
        for i, (name, var) in enumerate(self.qty_vars.items(), start=1):
            lbl = ttk.Label(self.form_frame, text=name + ":", style="ItemLabel.TLabel")
            ent = ttk.Entry(self.form_frame, textvariable=var, width=8, style="Entry.TEntry")
            ent.bind("<FocusOut>", self._sanitize_entry(var))
            # store references to arrange later
            self.entries[name] = (lbl, ent)

        # Buttons (Total / Reset) placed under entries
        self.btn_frame = ttk.Frame(self.form_frame, padding=(0, 8))
        self.btn_total = ttk.Button(self.btn_frame, text="Calculate Total", command=self.calculate_total)
        self.btn_reset = ttk.Button(self.btn_frame, text="Reset", command=self.reset)

        # Right: bill / receipt
        self.bill_frame = ttk.Frame(self, style="Bill.TFrame", padding=(14, 14), width=300)
        self.bill_title = ttk.Label(self.bill_frame, text="Bill", font=("Helvetica", 16, "bold"), background="#fff8dc")
        self.bill_text = tk.Text(self.bill_frame, width=32, height=18, padx=8, pady=8, wrap="word", bd=0, bg="#fff8dc", state="disabled")
        self.total_label = ttk.Label(self.bill_frame, textvariable=self.total_var, font=("Helvetica", 14, "bold"), background="#fff8dc")

    def _place_ui(self):
        # Title
        self.title_frame.place(x=0, y=0, relwidth=1)
        self.title_label.pack(fill="x")

        # Left menu
        self.menu_frame.place(x=12, y=64, width=260, height=440)
        self.menu_title.pack(anchor="center", pady=(0, 8))
        for lbl in self.menu_items:
            lbl.pack(anchor="w", pady=4, padx=6)

        # Center form
        self.form_frame.place(x=284, y=80, width=420, height=420)
        self.form_title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        for i, (name, (lbl, ent)) in enumerate(self.entries.items(), start=1):
            lbl.grid(row=i, column=0, sticky="w", padx=(0, 6), pady=6)
            ent.grid(row=i, column=1, sticky="w", padx=(0, 6), pady=6)

        # Buttons
        self.btn_frame.grid(row=len(self.entries) + 1, column=0, columnspan=2, pady=(12, 0))
        self.btn_total.grid(row=0, column=0, padx=(0, 8))
        self.btn_reset.grid(row=0, column=1)

        # Right bill
        self.bill_frame.place(x=720, y=64, width=248, height=440)
        self.bill_title.pack(anchor="center")
        self.bill_text.pack(pady=(8, 6))
        self.total_label.pack(anchor="center", pady=(6, 0))

        # initial bill content
        self._write_bill_header()

    def _sanitize_entry(self, var):
        # returns a handler that coerces entry to non-negative integer
        def handler(event):
            try:
                v = int(var.get())
                if v < 0:
                    var.set(0)
            except Exception:
                var.set(0)
        return handler

    def calculate_total(self):
        try:
            items_bought = {}
            total = 0
            for name, price in self.ITEMS.items():
                qty = self.qty_vars[name].get()
                if qty < 0:
                    qty = 0
                    self.qty_vars[name].set(0)
                cost = price * qty
                if qty:
                    items_bought[name] = (qty, price, cost)
                total += cost

            self.total_var.set(f"Rs. {total}")
            self._write_bill(items_bought, total)
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{e}")

    def reset(self):
        for var in self.qty_vars.values():
            var.set(0)
        self.total_var.set("Rs. 0")
        self._write_bill_header()

    def _write_bill_header(self):
        self.bill_text.configure(state="normal")
        self.bill_text.delete("1.0", "end")
        self.bill_text.insert("end", "Receipt\n")
        self.bill_text.insert("end", "—" * 28 + "\n")
        self.bill_text.insert("end", f"{'Item':<15}{'Qty':>3}{'Cost':>8}\n")
        self.bill_text.insert("end", "—" * 28 + "\n")
        self.bill_text.configure(state="disabled")

    def _write_bill(self, items_bought, total):
        self.bill_text.configure(state="normal")
        self.bill_text.delete("1.0", "end")
        self.bill_text.insert("end", "Receipt\n")
        self.bill_text.insert("end", "—" * 28 + "\n")
        self.bill_text.insert("end", f"{'Item':<15}{'Qty':>3}{'Cost':>8}\n")
        self.bill_text.insert("end", "—" * 28 + "\n")
        for name, (qty, price, cost) in items_bought.items():
            line = f"{name:<15}{qty:>3}{cost:>8}\n"
            self.bill_text.insert("end", line)
        self.bill_text.insert("end", "—" * 28 + "\n")
        self.bill_text.insert("end", f"{'Total':<15}{'':>3}{total:>8}\n")
        self.bill_text.configure(state="disabled")


if __name__ == "__main__":
    app = StationeryApp()
    app.mainloop()