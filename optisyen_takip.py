import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Kurumsal Zayi Raporu", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #4e73df; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Cam Zayi Raporu - Orijinal Biçim Koruyucu")

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
        df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
        df_final = df.fillna("-")

        # 2. Excel Görünümünü Simüle Eden Stil Fonksiyonu (Ekranda Gösterim İçin)
        def renk_stili(val):
            if isinstance(val, (int, float)) and val > 5: # Örnek: %5 zayi üstü kırmızı
                return 'color: red; font-weight: bold'
            return ''

        styled_df = df_final.style.set_properties(**{
            'background-color': 'white',
            'color': 'black',
            'border-color': '#d3d3d3',
            'border-style': 'solid',
            'border-width': '1px'
        }).set_table_styles([
            {'selector': 'th', 'props': [('background-color', '#2c3e50'), ('color', 'white'), ('font-weight', 'bold')]}
        ])

        # 3. İNDİRME ALANI
        c1, c2 = st.columns(2)
        
        with c1:
            # EXCEL ÇIKTISI (Orijinal Biçime En Yakın)
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_final.to_excel(writer, index=False, sheet_name='Rapor')
                # Burada xlsxwriter ile hücreleri renklendirebiliriz
                workbook = writer.book
                worksheet = writer.sheets['Rapor']
                header_format = workbook.add_format({'bold': True, 'bg_color': '#2c3e50', 'font_color': 'white', 'border': 1})
                for col_num, value in enumerate(df_final.columns.values):
                    worksheet.write(0, col_num, value, header_format)
            
            st.download_button("📥 Biçimlendirilmiş Excel'i İndir", output.getvalue(), "zayi_raporu_kurumsal.xlsx")

        with c2:
            # FOTOĞRAF ÇIKTISI (Yüksek Kalite & Bozulmayan Biçim)
            fig_width = max(16, len(df_final.columns) * 1.5)
            fig_height = max(5, len(df_final) * 0.6 + 2)
            fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=200) # DPI artırıldı
            ax.axis('off')

            # Excel Biçiminde Renkli Tablo
            tablo = ax.table(
                cellText=df_final.values,
                colLabels=df_final.columns,
                loc='center',
                cellLoc='center',
                colColours=["#2c3e50"] * len(df_final.columns) # Lacivert Başlıklar
            )
            
            tablo.auto_set_font_size(False)
            tablo.set_fontsize(10)
            tablo.scale(1, 3) # Satır genişliği Excel gibi

            # Başlık Yazı Rengi
            for j in range(len(df_final.columns)):
                tablo[0, j].get_text().set_color('white')
                tablo[0, j].get_text().set_weight('bold')

            img_buf = io.BytesIO()
            plt.savefig(img_buf, format='png', bbox_inches='tight', facecolor='white')
            plt.close(fig)
            
            st.download_button("🖼️ Yüksek Kalite Fotoğraf İndir", img_buf.getvalue(), "zayi_raporu_biçimli.png")

        st.divider()
        st.subheader("📊 Rapor Önizlemesi")
        st.table(df_final.head(20)) # Stilli tabloyu ekrana bas

    except Exception as e:
        st.error(f"Sistem Hatası: {e}")
