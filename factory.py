import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os
import sys
import json
import shutil

# Configuration constants
SEPARATOR = b"<<<KIOSK_CONFIG>>>"
TEMPLATE_FILENAME = "browser_engine.exe"
ASSETS = ["favicon.ico", "agerit_logo.png", "emistr_logo.png"]

# UI Theme
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_template_path():
    """ Locate the browser_engine.exe template """
    # First check if it's bundled in the EXE (via _MEIPASS)
    path = get_resource_path(TEMPLATE_FILENAME)
    if os.path.exists(path):
        return path
        
    # Fallback for development: check current dir or dist/
    possible_paths = [
        os.path.join(os.getcwd(), TEMPLATE_FILENAME),
        os.path.join(os.getcwd(), "dist", TEMPLATE_FILENAME),
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return p
    return None

class KioskGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color="#F5F7FA") # Modern off-white background
        
        self.title("EMISTR | Kiosk Generator")
        self.geometry("550x750")
        self.minsize(550, 600)
        self.resizable(True, True)
        
        # Set Window Icon
        try:
            icon_path = get_resource_path("favicon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception as e:
            print(f"Icon error: {e}")

        self.setup_ui()

    def setup_ui(self):
        # Header Section
        self.header_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", height=120, corner_radius=0)
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)

        # Logos in header
        try:
            img_agerit_source = Image.open(get_resource_path("agerit_logo.png"))
            img_emistr_source = Image.open(get_resource_path("emistr_logo.png"))
            
            def get_image_obj(img, target_h):
                ratio = target_h / img.height
                return ctk.CTkImage(img, size=(int(img.width * ratio), target_h))

            self.icon_agerit = get_image_obj(img_agerit_source, 50)
            self.icon_emistr = get_image_obj(img_emistr_source, 50)

            label_agerit = ctk.CTkLabel(self.header_frame, image=self.icon_agerit, text="")
            label_agerit.pack(side="left", padx=30, pady=20)
            
            label_emistr = ctk.CTkLabel(self.header_frame, image=self.icon_emistr, text="")
            label_emistr.pack(side="right", padx=30, pady=20)
        except Exception as e:
            print(f"Logo error: {e}")
            ctk.CTkLabel(self.header_frame, text="EMISTR KIOSK GENERATOR", 
                         font=ctk.CTkFont(family="Inter", size=24, weight="bold")).pack(pady=40)

        # Scrollable content area
        self.container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=40, pady=(20, 0))

        # Title
        ctk.CTkLabel(self.container, text="Konfigurace Kiosku",
                     text_color="#1A202C",
                     font=ctk.CTkFont(family="Inter", size=20, weight="bold")).pack(pady=(0, 20))

        # Inputs
        self.create_input_field("Název Aplikace", "např. Sklad_Kiosk", "entry_name")
        self.create_input_field("Cílová URL adresa", "https://emistr.cloud/...", "entry_url")

        # RS232 sekce
        ctk.CTkLabel(
            self.container, text="RS232 čtečky (volitelné)",
            text_color="#718096", font=ctk.CTkFont(family="Inter", size=12, weight="bold")
        ).pack(anchor="w", pady=(25, 5))
        self.create_input_field("Čtečka čárových kódů — COM port", "COM3 (prázdné = zakázáno)", "entry_barcode_port")
        self.create_input_field("Čtečka čárových kódů — Baud rate", "9600", "entry_barcode_baud")
        self.create_input_field("RFID čtečka čipů — COM port", "COM4 (prázdné = zakázáno)", "entry_rfid_port")
        self.create_input_field("RFID čtečka čipů — Baud rate", "9600", "entry_rfid_baud")

        # Status Message
        self.status_label = ctk.CTkLabel(self.container, text="", text_color="#718096", font=("Inter", 12))
        self.status_label.pack(pady=(15, 5))

        # Bottom bar — pevně dole, mimo scroll
        bottom_bar = ctk.CTkFrame(self, fg_color="transparent")
        bottom_bar.pack(fill="x", padx=40, pady=(8, 20))

        # Generate Button
        self.btn_generate = ctk.CTkButton(
            bottom_bar,
            text="VYGENEROVAT EXE",
            command=self.generate_exe,
            height=55,
            corner_radius=8,
            fg_color="#2D3748",
            hover_color="#1A202C",
            font=ctk.CTkFont(family="Inter", size=16, weight="bold")
        )
        self.btn_generate.pack(fill="x")

    def create_input_field(self, label_text, placeholder, attr_name):
        label = ctk.CTkLabel(self.container, text=label_text, text_color="#4A5568", font=("Inter", 13, "bold"))
        label.pack(anchor="w", pady=(15, 5))
        
        entry = ctk.CTkEntry(
            self.container, 
            placeholder_text=placeholder, 
            height=45, 
            border_width=1,
            corner_radius=8,
            fg_color="#FFFFFF",
            border_color="#E2E8F0"
        )
        entry.pack(fill="x", pady=(0, 10))
        setattr(self, attr_name, entry)

    def generate_exe(self):
        app_name = self.entry_name.get().strip()
        url = self.entry_url.get().strip()
        
        if not app_name or not url:
            messagebox.showwarning("Upozornění", "Prosím vyplňte název i URL adresu.")
            return

        if not app_name.lower().endswith(".exe"):
            output_filename = f"{app_name}.exe"
        else:
            output_filename = app_name

        template_path = get_template_path()
        if not template_path:
            messagebox.showerror("Chyba", f"Šablona '{TEMPLATE_FILENAME}' nebyla nalezena.")
            return

        self.status_label.configure(text="Generuji aplikaci...", text_color="#3182CE")
        self.update_idletasks()

        # Prepare Config
        config_data = {
            "title": app_name.replace(".exe", ""),
            "url": url,
            "zoom": 1.0
        }

        barcode_port = self.entry_barcode_port.get().strip()
        if barcode_port:
            baud_str = self.entry_barcode_baud.get().strip()
            config_data["barcode_scanner"] = {
                "port": barcode_port,
                "baud_rate": int(baud_str) if baud_str.isdigit() else 9600
            }

        rfid_port = self.entry_rfid_port.get().strip()
        if rfid_port:
            baud_str = self.entry_rfid_baud.get().strip()
            config_data["rfid_reader"] = {
                "port": rfid_port,
                "baud_rate": int(baud_str) if baud_str.isdigit() else 9600
            }

        json_bytes = json.dumps(config_data).encode("utf-8")

        try:
            with open(template_path, "rb") as f_in:
                template_content = f_in.read()

            output_path = os.path.join(os.getcwd(), output_filename)
            with open(output_path, "wb") as f_out:
                f_out.write(template_content)
                f_out.write(SEPARATOR)
                f_out.write(json_bytes)
                
            self.status_label.configure(text="Hotovo! Aplikace byla vytvořena.", text_color="#38A169")
            messagebox.showinfo("Úspěch", f"Aplikace byla úspěšně vytvořena!\n\nUmístění: {output_path}")
            
        except Exception as e:
            self.status_label.configure(text="Chyba při generování.", text_color="#E53E3E")
            messagebox.showerror("Chyba", f"Nepodařilo se vytvořit aplikaci:\n{str(e)}")

if __name__ == "__main__":
    app = KioskGeneratorApp()
    app.mainloop()

