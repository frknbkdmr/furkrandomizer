import tkinter as tk
import os
from tkinter import filedialog, messagebox
import pandas as pd
import random
from cryptography.fernet import Fernet

# Şifreleme anahtarını oluşturma ve saklama
def generate_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)

# Şifreleme anahtarını yükleme
def load_key():
    """key.key dosyasını yükler."""
    if not os.path.exists("key.key"):
        print("key.key dosyası bulunamadı. Yeni bir anahtar oluşturuluyor...")
        generate_key()
    return open("key.key", "rb").read()

# Çift kör randomizasyon fonksiyonu
def double_blind_randomization(input_file, output_file, mapping_file, seed=None):
    if seed is not None:
        random.seed(seed)

    # Verileri yükleme
    data = pd.read_csv(input_file)
    num_participants = len(data)
    
    # Grupları kodlama
    group_names = ['A', 'B']
    random_groups = [random.choice(group_names) for _ in range(num_participants)]
    data['Group'] = random_groups

    # Gerçek grup eşlemesini şifreleme
    mapping = {'A': 'Control', 'B': 'Experiment'}
    key = load_key()
    fernet = Fernet(key)
    encrypted_mapping = {k: fernet.encrypt(v.encode()).decode() for k, v in mapping.items()}
    
    # Anonim sonuçları kaydetme
    data.to_csv(output_file, index=False)

    # Şifreli eşleştirmeyi kaydetme
    pd.DataFrame.from_dict(encrypted_mapping, orient='index', columns=['Encrypted']).to_csv(mapping_file)

# GUI Fonksiyonları
def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    entry_file_path.delete(0, tk.END)
    entry_file_path.insert(0, file_path)

def save_file():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    return file_path

def run_randomization():
    input_file = entry_file_path.get()
    if not input_file:
        messagebox.showerror("Hata", "Giriş dosyası seçilmedi!")
        return

    output_file = save_file()
    if not output_file:
        messagebox.showerror("Hata", "Çıkış dosyası kaydedilmedi!")
        return

    mapping_file = save_file()
    if not mapping_file:
        messagebox.showerror("Hata", "Mapping dosyası kaydedilmedi!")
        return

    try:
        double_blind_randomization(input_file, output_file, mapping_file, seed=42)
        messagebox.showinfo("Başarılı", f"Randomizasyon tamamlandı!\nDosyalar kaydedildi:\n- {output_file}\n- {mapping_file}")
    except Exception as e:
        messagebox.showerror("Hata", f"Bir hata oluştu: {e}")

# Ana Pencere
app = tk.Tk()
app.title("Çift Kör Randomizasyon")
app.geometry("500x200")

# Giriş Dosyası Seçimi
lbl_file_path = tk.Label(app, text="Katılımcı Verileri (CSV):")
lbl_file_path.pack(pady=5)
entry_file_path = tk.Entry(app, width=50)
entry_file_path.pack(pady=5)
btn_browse = tk.Button(app, text="Gözat", command=select_file)
btn_browse.pack(pady=5)

# Randomizasyon Başlat
btn_run = tk.Button(app, text="Randomizasyonu Çalıştır", command=run_randomization, bg="green", fg="white")
btn_run.pack(pady=20)

# Ana Döngü
app.mainloop()
