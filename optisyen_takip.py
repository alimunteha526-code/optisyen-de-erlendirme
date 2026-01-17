import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox

def excel_to_jpg():
    # 1. Dosya Seçme Penceresi
    dosya_yolu = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.csv")])
    if not dosya_yolu:
        return

    try:
        # 2. Veriyi Oku (Excel veya CSV)
        if dosya_yolu.endswith('.csv'):
            df = pd.read_csv(dosya_yolu)
        else:
            df = pd.read_excel(dosya_yolu)

        # 3. Senin istediğin sütunları filtreleyelim (Dosyandaki isimlere göre)
        # Eğer sütun isimleri farklıysa burayı güncelleyebiliriz
        secilecek_sutunlar = ['STOK ADI', 'EN', 'BOY', 'ADET', 'TOPLAM m2', 'FİRE NEDENİ']
        mevcut_sutunlar = [col for col in secilecek_sutunlar if col in df.columns]
        df_son = df[mevcut_sutunlar].head(20) # İlk 20 satırı alalım (Görselin netliği için)

        # 4. Tabloyu Görselleştirme
        fig, ax = plt.subplots(figsize=(12, len(df_son) * 0.6))
        ax.axis('off')
        
        # Renkli ve şık bir tablo tasarımı
        the_table = ax.table(cellText=df_son.values, colLabels=df_son.columns, 
                            loc='center', cellLoc='center')
        
        the_table.auto_set_font_size(False)
        the_table.set_fontsize(10)
        the_table.scale(1.2, 1.8)

        # Başlık ekle
        plt.title("Cam Zayi Raporu - Düzenlenmiş Liste", fontsize=14, pad=20)

        # 5. Kaydetme
        cikis_yolu = filedialog.asksaveasfilename(defaultextension=".jpg")
        if cikis_yolu:
            plt.savefig(cikis_yolu, dpi=300, bbox_inches='tight')
            messagebox.showinfo("Başarılı", "JPG dosyası oluşturuldu!")

    except Exception as e:
        messagebox.showerror("Hata", f"Bir sorun oluştu: {e}")

# Basit Arayüz Tasarımı
root = tk.Tk()
root.title("Cam Zayi - Excel to JPG")
root.geometry("300x150")

label = tk.Label(root, text="Cam Zayi Raporu Dönüştürücü", pady=10)
label.pack()

btn = tk.Button(root, text="Excel Seç ve JPG Yap", command=excel_to_jpg, 
                bg="#4CAF50", fg="white", padx=10, pady=5)
btn.pack(pady=10)

root.mainloop()
