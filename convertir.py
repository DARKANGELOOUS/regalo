import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from PIL import Image
import threading

class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Optimizador de Imágenes para Web")
        self.root.geometry("500x550")
        self.root.resizable(False, False)

        # Variables
        self.folder_path = tk.StringVar()
        self.base_name = tk.StringVar()
        self.output_format = tk.StringVar(value="webp")
        self.max_width = tk.IntVar(value=1080)
        self.quality = tk.IntVar(value=80)

        # --- UI LAYOUT ---
        
        # Título
        title_label = tk.Label(root, text="📸 Convertidor & Renombrador", font=("Helvetica", 16, "bold"), fg="#db2777")
        title_label.pack(pady=15)

        # 1. Selección de Carpeta
        frame_folder = tk.LabelFrame(root, text="1. Carpeta de Origen", padx=10, pady=10)
        frame_folder.pack(fill="x", padx=20, pady=5)
        
        entry_folder = tk.Entry(frame_folder, textvariable=self.folder_path, state='readonly')
        entry_folder.pack(side="left", fill="x", expand=True, padx=5)
        
        btn_browse = tk.Button(frame_folder, text="Buscar 📂", command=self.select_folder, bg="#fce7f3")
        btn_browse.pack(side="right")

        # 2. Configuración de Nombre y Formato
        frame_config = tk.LabelFrame(root, text="2. Configuración", padx=10, pady=10)
        frame_config.pack(fill="x", padx=20, pady=5)

        # Nombre Base
        tk.Label(frame_config, text="Nombre Base (ej: aventura, comida):").grid(row=0, column=0, sticky="w", pady=5)
        entry_name = tk.Entry(frame_config, textvariable=self.base_name)
        entry_name.grid(row=0, column=1, sticky="e", padx=5)

        # Formato
        tk.Label(frame_config, text="Formato de Salida:").grid(row=1, column=0, sticky="w", pady=5)
        combo_format = ttk.Combobox(frame_config, textvariable=self.output_format, values=["webp", "jpeg", "png"], state="readonly")
        combo_format.grid(row=1, column=1, sticky="e", padx=5)
        
        # Calidad
        tk.Label(frame_config, text="Ancho Máximo (px):").grid(row=2, column=0, sticky="w", pady=5)
        entry_width = tk.Entry(frame_config, textvariable=self.max_width, width=10)
        entry_width.grid(row=2, column=1, sticky="e", padx=5)

        # 3. Botón de Acción
        self.btn_convert = tk.Button(root, text="🚀 CONVERTIR Y RENOMBRAR", command=self.start_thread, 
                                     bg="#db2777", fg="white", font=("Helvetica", 10, "bold"), height=2)
        self.btn_convert.pack(fill="x", padx=20, pady=20)

        # 4. Log y Progreso
        self.progress = ttk.Progressbar(root, orient="horizontal", length=100, mode="determinate")
        self.progress.pack(fill="x", padx=20)
        
        self.log_text = tk.Text(root, height=8, state='disabled', bg="#f0f0f0", font=("Consolas", 8))
        self.log_text.pack(fill="both", padx=20, pady=10)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            self.log(f"📂 Carpeta seleccionada: {folder}")

    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def start_thread(self):
        # Ejecutar en un hilo separado para no congelar la GUI
        thread = threading.Thread(target=self.process_images)
        thread.start()

    def process_images(self):
        folder = self.folder_path.get()
        base_name = self.base_name.get().strip()
        fmt = self.output_format.get()
        max_w = self.max_width.get()

        # Validaciones
        if not folder:
            messagebox.showerror("Error", "Por favor selecciona una carpeta.")
            return
        if not base_name:
            messagebox.showerror("Error", "Debes escribir un nombre base (ej: 'aventura').")
            return

        # Crear carpeta de salida
        output_folder = os.path.join(folder, "listas_para_web")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Buscar imágenes
        valid_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.bmp')
        files = [f for f in os.listdir(folder) if f.lower().endswith(valid_extensions)]
        
        if not files:
            messagebox.showwarning("Aviso", "No se encontraron imágenes en esa carpeta.")
            return

        self.log(f"🚀 Iniciando proceso de {len(files)} imágenes...")
        self.btn_convert.config(state="disabled")
        self.progress["maximum"] = len(files)
        self.progress["value"] = 0

        count = 1
        for filename in files:
            input_path = os.path.join(folder, filename)
            
            # Definir nuevo nombre: nombrebase + numero + extensión
            new_filename = f"{base_name}{count}.{fmt}"
            output_path = os.path.join(output_folder, new_filename)

            try:
                with Image.open(input_path) as img:
                    # 1. Redimensionar
                    w, h = img.size
                    if w > max_w:
                        new_h = int((max_w * h) / w)
                        img = img.resize((max_w, new_h), Image.LANCZOS)
                    
                    # 2. Convertir modo de color
                    if fmt == "jpeg" or (fmt == "webp" and img.mode in ("RGBA", "P")):
                         img = img.convert("RGB")
                    
                    # 3. Guardar
                    # optimize=True para reducir peso extra
                    img.save(output_path, fmt, quality=self.quality.get(), optimize=True)
                    
                    self.log(f"✅ {filename} -> {new_filename}")
                    count += 1
                    self.progress["value"] = count - 1
            except Exception as e:
                self.log(f"❌ Error con {filename}: {e}")

        self.btn_convert.config(state="normal")
        messagebox.showinfo("Éxito", f"¡Proceso terminado!\nLas imágenes están en la carpeta:\n{output_folder}")
        self.log("✨ ¡Listo! Revisa la carpeta 'listas_para_web'.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageConverterApp(root)
    root.mainloop()