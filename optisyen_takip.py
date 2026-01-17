import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import numpy as np

# Sayfa Ayarları
st.set_page_config(page_title="Kurumsal Zayi Raporu", layout="centered")

st.title("📊 Cam Zayi Raporu - Orijinal Renk Düzeni")
st.markdown("---")

# Mağaza Listesi (Filtreleme için)
istenen_magazalar = [
    "M38003", "M51001", "M42004", "M51002", "M38001", "M38005", 
    "M68001", "M42006", "M42002", "M46001", "M38002", "M42001", 
    "M40001", "M42005", "M38004", "M70001", "M50001"
]

uploaded_file = st.file_uploader("Orijinal Excel dosyasını yükleyin", type=['xlsx'])

if uploaded_file is not None:
    try:
        # Arka planda veriyi oku
        df_raw = pd.read_excel(uploaded_file, header=None)
        
        # Başlık tespiti
        start_row = 0
        for i, row in df_raw.iterrows():
            if "ÜST BIRIM" in str(row.values).upper():
                start_row = i
                break
        
        df = df_raw.iloc[start_row:].copy()
        df.columns = df.iloc[0]
        df = df[1:].reset_index(drop=True)
        
        # 1. İlk iki sütunu sil (Bölge ve Müdür sütunları)
        df = df.iloc[:, 2:] 
        
        # 2. Üst Birim sütununa göre filtrele
        ub_col = next((c for c in df.columns if "ÜST BIRIM" in str(c).upper()), df.columns[0])
        df[ub_col] = df[ub_col].astype(str).str.strip()
        df_final = df[df[ub_col].isin(istenen_magazalar)].copy()
        
        # 3. Sayısal Hataları Temizle (NaN/INF hatasını engeller)
        df_final = df_final.replace([np.inf, -np.inf], np.nan)
        df_final = df_final.fillna("-") 

        if df_final.empty:
            st.error("❌ Seçili mağaza kodları bu dosyada bulunamadı.")
        else:
            st.success(f"✅ {len(df_final)} Mağaza işlendi. Orijinal renklerle indirilebilir.")

            col1, col2 = st.columns(2)
            
            with col1:
                # 📥 EXCEL ÇIKTISI (Orijinal Lacivert Başlık)
                exc_buf = io.BytesIO()
                # nan_inf_to_errors ayarı Sistem Hatasını engeller
                with pd.ExcelWriter(exc_buf, engine='xlsxwriter', engine_kwargs={'options': {'nan_inf_to_errors': True}}) as writer:
                    df_final.to_excel(writer, index=False, sheet_name='Rapor')
                    
                    workbook = writer.book
                    # Orijinal Excel'deki lacivert tonu: #1F4E78
                    header_fmt = workbook.add_format({
                        'bold': True, 
                        'bg_color': '#1F4E78', 
                        'font_color': 'white', 
                        'border': 1,
                        'align': 'center',
                        'valign': 'vcenter'
                    })
                    
                    for col_num, value in enumerate(df_final.columns.values):
                        writer.sheets['Rapor'].write(0, col_num, value, header_fmt)
                        writer.sheets['Rapor'].set_column(col_num, col_num, 15) # Okunabilirlik için genişlik
                
                st.download_button("📥 Renkli Excel'i İndir", exc_buf.getvalue(), "zayi_raporu_orijinal.xlsx", use_container_width=True)

            with col2:
                # 🖼️ FOTOĞRAF ÇIKTISI (Orijinal Lacivert Tablo)
                f_width = max(18, len(df_final.columns) * 1.5)
                f_height = max(8, len(df_final) * 0.8 + 2)
                fig, ax = plt.subplots(figsize=(f_width, f_height), dpi=120)
                ax.axis('off')
                
                # Tablo oluşturma
                tablo = ax.table(
                    cellText=df_final.values, 
                    colLabels=df_final.columns,
                    loc='center', 
                    cellLoc='center', 
                    colColours=["#1F4E78"] * len(df_final.columns)
                )
                
                tablo.auto_set_font_size(False)
                tablo.set_fontsize(10)
                tablo.scale(1, 4) # Satır yüksekliği
                
                # Başlık yazılarını beyaz ve kalın yap
                for j in range(len(df_final.columns)):
                    tablo[0, j].get_text().set_color('white')
                    tablo[0, j].get_text().set_weight('bold')

                img_buf = io.BytesIO()
                plt.savefig(img_buf, format='png', bbox_inches='tight', facecolor='white')
                plt.close(fig) 
                
                st.download_button("🖼️ Renkli Fotoğrafı İndir", img_buf.getvalue(), "zayi_raporu_gorsel.png", use_container_width=True)

    except Exception as e:
        st.error(f"Sistem Hatası: {e}")
