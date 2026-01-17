import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import numpy as np

st.set_page_config(page_title="Zayi Raporu", layout="wide")

# --- MAĞAZA LİSTESİ ---
# Görselde paylaştığın tüm kodları buraya ekledim
istenen_magazalar = [
    "M38003", "M51001", "M42004", "M51002", "M38001", "M38005", 
    "M68001", "M42006", "M42002", "M46001", "M38002", "M42001", 
    "M40001", "M42005", "M38004", "M70001", "M50001"
]

st.title("📊 Cam Zayi Raporu - Kurumsal Biçim")

uploaded_file = st.file_uploader("Excel dosyasını yükleyin", type=['xlsx'])

if uploaded_file is not None:
    try:
        # 1. Veriyi Oku ve Başlık Satırını Bul
        df_raw = pd.read_excel(uploaded_file, header=None)
        
        start_row = 0
        for i, row in df_raw.iterrows():
            line = " ".join(map(str, row.values)).upper()
            if "ÜST BIRIM" in line:
                start_row = i
                break
        
        # Tabloyu oluştur
        df = df_raw.iloc[start_row:].copy()
        df.columns = df.iloc[0]
        df = df[1:].reset_index(drop=True)
        
        # 2. Filtreleme ve Temizlik
        ub_col = next((c for c in df.columns if "ÜST BIRIM" in str(c).upper()), df.columns[2])
        df[ub_col] = df[ub_col].astype(str).str.strip()
        
        # Sadece listedeki mağazaları al
        df_final = df[df[ub_col].isin(istenen_magazalar)].copy()
        
        # Hatalı değerleri (#SAYI! gibi) temizle
        df_final = df_final.replace([np.inf, -np.inf], np.nan)
        df_final = df_final.fillna("-")

        # 3. İNDİRME BUTONLARI
        c1, c2 = st.columns(2)
        
        with c1:
            # EXCEL: Lacivert başlık ve beyaz yazı stilini korur
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_final.to_excel(writer, index=False, sheet_name='Rapor')
                workbook = writer.book
                worksheet = writer.sheets['Rapor']
                
                # Excel Biçimlendirmesi (Görseldeki gibi Lacivert/Beyaz)
                header_fmt = workbook.add_format({
                    'bold': True, 'bg_color': '#1F4E78', 'font_color': 'white', 'border': 1, 'align': 'center'
                })
                for col_num, value in enumerate(df_final.columns.values):
                    worksheet.write(0, col_num, value, header_fmt)
                    worksheet.set_column(col_num, col_num, 15) # Sütun genişliği
            
            st.download_button("📥 Excel Olarak İndir", output.getvalue(), "zayi_raporu.xlsx")

        with c2:
            # FOTOĞRAF: Yüksek çözünürlük ve orijinal renkler
            fig_width = max(20, len(df_final.columns) * 1.8)
            fig_height = max(8, len(df_final) * 0.7 + 2)
            fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=150)
            ax.axis('off')

            tablo = ax.table(
                cellText=df_final.values,
                colLabels=df_final.columns,
                loc='center',
                cellLoc='center',
                colColours=["#1F4E78"] * len(df_final.columns) # Görseldeki lacivert tonu
            )
            
            tablo.auto_set_font_size(False)
            tablo.set_fontsize(10)
            tablo.scale(1, 3.5) # Satırları ferahlatır

            # Başlık metinlerini beyaz ve kalın yap
            for j in range(len(df_final.columns)):
                tablo[0, j].get_text().set_color('white')
                tablo[0, j].get_text().set_weight('bold')

            img_buf = io.BytesIO()
            plt.savefig(img_buf, format='png', bbox_inches='tight', facecolor='white')
            plt.close(fig)
            
            st.download_button("🖼️ Fotoğraf (PNG) Olarak İndir", img_buf.getvalue(), "rapor_gorsel.png")

        st.success(f"✅ {len(df_final)} mağaza başarıyla filtrelendi ve biçimlendirildi.")
        st.dataframe(df_final)

    except Exception as e:
        st.error(f"Sistem Hatası: {e}")
