import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import numpy as np

st.set_page_config(page_title="Zayi Raporu - Hatasız Versiyon", layout="wide")

st.title("📊 Cam Zayi Raporu - Biçimli Çıktı")

uploaded_file = st.file_uploader("Excel dosyasını yükleyin", type=['xlsx'])

if uploaded_file is not None:
    try:
        # 1. Veriyi Oku ve Başlığı Bul
        df_raw = pd.read_excel(uploaded_file, header=None)
        
        start_row = 0
        for i, row in df_raw.iterrows():
            row_str = " ".join(map(str, row.values)).upper()
            if "ÜST BIRIM" in row_str or "BÖLGE" in row_str:
                start_row = i
                break
        
        df = df_raw.iloc[start_row:].copy()
        df.columns = df.iloc[0]
        df = df[1:].reset_index(drop=True)
        
        # --- HATA GİDERME KISMI (NaN/INF TEMİZLİĞİ) ---
        # Boş sütunları/satırları at
        df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
        # Matematiksel hataları (inf) ve boşlukları (nan) temizle
        df = df.replace([np.inf, -np.inf], np.nan)
        df_final = df.fillna("-") 
        # ----------------------------------------------

        c1, c2 = st.columns(2)
        
        with c1:
            # EXCEL ÇIKTISI (Hata korumalı ayarlar eklendi)
            output = io.BytesIO()
            # 'nan_inf_to_errors' seçeneği ile yazma hatası engellenir
            with pd.ExcelWriter(output, engine='xlsxwriter', engine_kwargs={'options': {'nan_inf_to_errors': True}}) as writer:
                df_final.to_excel(writer, index=False, sheet_name='Rapor')
                
                workbook = writer.book
                worksheet = writer.sheets['Rapor']
                
                # Kurumsal Renk Biçimi
                header_format = workbook.add_format({
                    'bold': True, 
                    'bg_color': '#2c3e50', 
                    'font_color': 'white', 
                    'border': 1,
                    'align': 'center',
                    'valign': 'vcenter'
                })
                
                for col_num, value in enumerate(df_final.columns.values):
                    worksheet.write(0, col_num, value, header_format)
            
            st.download_button("📥 Excel Olarak İndir (Hatasız)", output.getvalue(), "zayi_raporu_temiz.xlsx")

        with c2:
            # FOTOĞRAF ÇIKTISI
            fig_width = max(18, len(df_final.columns) * 1.5)
            fig_height = max(5, len(df_final) * 0.6 + 2)
            fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=150)
            ax.axis('off')

            tablo = ax.table(
                cellText=df_final.values,
                colLabels=df_final.columns,
                loc='center',
                cellLoc='center',
                colColours=["#2c3e50"] * len(df_final.columns)
            )
            
            tablo.auto_set_font_size(False)
            tablo.set_fontsize(10)
            tablo.scale(1, 3)

            for j in range(len(df_final.columns)):
                tablo[0, j].get_text().set_color('white')
                tablo[0, j].get_text().set_weight('bold')

            img_buf = io.BytesIO()
            plt.savefig(img_buf, format='png', bbox_inches='tight', facecolor='white')
            plt.close(fig)
            
            st.download_button("🖼️ Fotoğraf Olarak İndir", img_buf.getvalue(), "zayi_raporu_gorsel.png")

        st.divider()
        st.subheader("Tablo Önizlemesi")
        st.dataframe(df_final)

    except Exception as e:
        st.error(f"Sistem Hatası: {e}")
