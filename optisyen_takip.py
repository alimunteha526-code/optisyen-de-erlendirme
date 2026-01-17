import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import numpy as np

# 1. Sayfa Ayarları - Hafıza dostu mod
st.set_page_config(page_title="Zayi Raporu", layout="centered")

st.title("📊 Cam Zayi Raporu - İndirme Merkezi")
st.info("Not: Hata almamak için tablo önizlemesi kapatılmıştır. Dosyayı yükleyip doğrudan butonları kullanın.")

# Görseldeki mağaza listesi
istenen_magazalar = [
    "M38003", "M51001", "M42004", "M51002", "M38001", "M38005", 
    "M68001", "M42006", "M42002", "M46001", "M38002", "M42001", 
    "M40001", "M42005", "M38004", "M70001", "M50001"
]

uploaded_file = st.file_uploader("Excel dosyasını yükleyin", type=['xlsx'])

if uploaded_file is not None:
    try:
        # Arka planda veriyi oku
        df_raw = pd.read_excel(uploaded_file, header=None)
        
        # ÜST BİRİM sütununu bul ve tabloyu kes
        start_row = 0
        for i, row in df_raw.iterrows():
            if "ÜST BIRIM" in str(row.values).upper():
                start_row = i
                break
        
        df = df_raw.iloc[start_row:].copy()
        df.columns = df.iloc[0]
        df = df[1:].reset_index(drop=True)
        
        # Filtreleme ve Hataları Temizleme
        ub_col = next((c for c in df.columns if "ÜST BIRIM" in str(c).upper()), df.columns[0])
        df[ub_col] = df[ub_col].astype(str).str.strip()
        df_final = df[df[ub_col].isin(istenen_magazalar)].copy()
        df_final = df_final.replace([np.inf, -np.inf], np.nan).fillna("-")

        if df_final.empty:
            st.error("❌ Dosyada eşleşen mağaza bulunamadı. Lütfen mağaza kodlarını kontrol edin.")
        else:
            st.success(f"✅ {len(df_final)} Mağaza işlendi. İndirmek için butonlara basın.")

            # Buton Alanı
            c1, c2 = st.columns(2)
            
            with c1:
                # EXCEL OLUŞTURMA (Lacivert başlıklarla)
                exc_buf = io.BytesIO()
                with pd.ExcelWriter(exc_buf, engine='xlsxwriter') as writer:
                    df_final.to_excel(writer, index=False, sheet_name='Rapor')
                    header_fmt = writer.book.add_format({'bold': True, 'bg_color': '#1F4E78', 'font_color': 'white', 'border': 1})
                    for col_num, value in enumerate(df_final.columns.values):
                        writer.sheets['Rapor'].write(0, col_num, value, header_fmt)
                st.download_button("📥 Excel Olarak İndir", exc_buf.getvalue(), "rapor_renkli.xlsx", use_container_width=True)

            with c2:
                # FOTOĞRAF OLUŞTURMA (Orijinal Biçim)
                # Genişliği tarayıcıyı yormayacak ama okunaklı olacak seviyede tutuyoruz
                fig, ax = plt.subplots(figsize=(25, len(df_final) * 0.8 + 2), dpi=100)
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
                plt.close(fig) # Hafızayı boşalt
                st.download_button("🖼️ Fotoğraf Olarak İndir", img_buf.getvalue(), "rapor_gorsel.png", use_container_width=True)

    except Exception as e:
        st.error(f"Sistem Hatası: {e}")
