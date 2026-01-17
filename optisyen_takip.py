import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import numpy as np

# 1. Sayfa Ayarları (Hafif mod)
st.set_page_config(page_title="Zayi Raporu", layout="centered")

st.title("📊 Cam Zayi Raporu - Güvenli İndirme")

# Görseldeki mağaza listesi
istenen_magazalar = [
    "M38003", "M51001", "M42004", "M51002", "M38001", "M38005", 
    "M68001", "M42006", "M42002", "M46001", "M38002", "M42001", 
    "M40001", "M42005", "M38004", "M70001", "M50001"
]

uploaded_file = st.file_uploader("Excel dosyasını yükleyin", type=['xlsx'])

if uploaded_file is not None:
    try:
        # Veriyi sessizce işle (Ekrana basmadan)
        df_raw = pd.read_excel(uploaded_file, header=None)
        
        # Başlık satırı tespiti
        start_row = 0
        for i, row in df_raw.iterrows():
            if "ÜST BIRIM" in str(row.values).upper():
                start_row = i
                break
        
        df = df_raw.iloc[start_row:].copy()
        df.columns = df.iloc[0]
        df = df[1:].reset_index(drop=True)
        
        # Temizlik
        df = df.loc[:, df.columns.notna()]
        ub_col = next((c for c in df.columns if "ÜST BIRIM" in str(c).upper()), df.columns[0])
        df[ub_col] = df[ub_col].astype(str).str.strip()
        
        # Filtreleme ve Hata Giderme
        df_final = df[df[ub_col].isin(istenen_magazalar)].copy()
        df_final = df_final.replace([np.inf, -np.inf], np.nan).fillna("-")

        if df_final.empty:
            st.warning("Belirtilen mağaza kodları dosyada bulunamadı.")
        else:
            st.success(f"✅ {len(df_final)} mağaza verisi hazırlandı. Lütfen format seçin:")

            # BUTONLAR
            col1, col2 = st.columns(2)
            
            with col1:
                # EXCEL ÇIKTISI (Lacivert Biçimli)
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_final.to_excel(writer, index=False, sheet_name='Rapor')
                    workbook = writer.book
                    header_fmt = workbook.add_format({
                        'bold': True, 'bg_color': '#1F4E78', 'font_color': 'white', 'border': 1
                    })
                    for col_num, value in enumerate(df_final.columns.values):
                        writer.sheets['Rapor'].write(0, col_num, value, header_fmt)
                
                st.download_button("📥 Excel İndir", output.getvalue(), "rapor.xlsx", use_container_width=True)

            with col2:
                # FOTOĞRAF ÇIKTISI (Orijinal Görünüm)
                f_width = max(20, len(df_final.columns) * 1.5)
                f_height = max(8, len(df_final) * 0.7 + 2)
                fig, ax = plt.subplots(figsize=(f_width, f_height), dpi=120)
                ax.axis('off')

                tablo = ax.table(
                    cellText=df_final.values, colLabels=df_final.columns,
                    loc='center', cellLoc='center', colColours=["#1F4E78"] * len(df_final.columns)
                )
                tablo.auto_set_font_size(False)
                tablo.set_fontsize(10)
                tablo.scale(1, 4)

                for j in range(len(df_final.columns)):
                    tablo[0, j].get_text().set_color('white')
                    tablo[0, j].get_text().set_weight('bold')

                img_buf = io.BytesIO()
                plt.savefig(img_buf, format='png', bbox_inches='tight')
                plt.close(fig) # Kritik: Hafızayı temizler
                
                st.download_button("🖼️ Fotoğraf İndir", img_buf.getvalue(), "rapor.png", use_container_width=True)

    except Exception as e:
        st.error(f"Sistem Hatası: {e}")
