import pandas as pd
import matplotlib.pyplot as plt
import io

# Sunucu ortamlarında GUI hatası almamak için backend ayarı
plt.switch_backend('Agg')

def excel_to_jpg_logic(uploaded_file):
    try:
        # 1. Dosyayı oku
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # 2. Senin "düzenlenmiş" dosyandaki sütun yapısına göre filtreleme
        # Sütun isimleri birebir aynı olmalıdır (Büyük/Küçük harfe duyarlı)
        secilecek_sutunlar = ['STOK ADI', 'EN', 'BOY', 'ADET', 'TOPLAM m2', 'FİRE NEDENİ']
        
        # Dosyada mevcut olan sütunları seç
        mevcut_sutunlar = [col for col in secilecek_sutunlar if col in df.columns]
        
        if not mevcut_sutunlar:
            return None, "Seçilen sütunlar dosyada bulunamadı. Lütfen sütun isimlerini kontrol edin."

        # İlk 20 satırı alalım (Görselin okunabilir kalması için)
        df_son = df[mevcut_sutunlar].head(20)

        # 3. Görselleştirme
        fig, ax = plt.subplots(figsize=(12, len(df_son) * 0.8 + 1))
        ax.axis('off')
        
        # Tabloyu oluştur
        the_table = ax.table(
            cellText=df_son.values, 
            colLabels=df_son.columns, 
            loc='center', 
            cellLoc='center'
        )
        
        # Stil ayarları
        the_table.auto_set_font_size(False)
        the_table.set_fontsize(10)
        the_table.scale(1.2, 2.5) # Satırları biraz daha genişletir

        # Renklendirme (Opsiyonel: Başlık satırını boyar)
        for (row, col), cell in the_table.get_celld().items():
            if row == 0:
                cell.set_text_props(weight='bold', color='white')
                cell.set_facecolor('#4c5c96')

        plt.title("Cam Zayi Raporu - Düzenlenmiş Liste", fontsize=16, pad=30)

        # 4. Belleğe kaydet (JPG olarak)
        buf = io.BytesIO()
        plt.savefig(buf, format='jpg', dpi=200, bbox_inches='tight')
        buf.seek(0)
        return buf, None

    except Exception as e:
        return None, str(e)

# --- Buradan sonrası eğer Streamlit kullanıyorsan geçerlidir ---
# Eğer yerel bilgisayarda (Tkinter ile) kullanacaksan önceki mesajdaki 
# GUI kodunu bu mantıkla birleştirebilirsin.
