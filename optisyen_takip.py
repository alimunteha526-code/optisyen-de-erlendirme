import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# Sayfa ayarları
st.set_page_config(page_title="Zayi Raporu", layout="wide")

st.title("📊 Cam Zayi Raporu Oluşturucu")

uploaded_file = st.file_uploader("Excel dosyasını yükleyin", type=['xlsx'])

if uploaded_file is not None:
    try:
        # 1. Excel'i oku (Hızlı okuma için engine eklendi)
        df_raw = pd.read_excel(uploaded_file, header=None)
        
        # 2. Tablo başlığını bul
        start_row = 0
        for i, row in df_raw.iterrows():
            row_str = " ".join(map(str, row.values)).upper()
            if "ÜST BIRIM" in row_str or "BÖLGE" in row_str:
                start_row = i
                break
        
        # 3. Veriyi düzenle
        df = df_raw.iloc[start_row:].copy()
        df.columns = df.iloc[0]
        df = df[1:].reset_index(drop=True)
        df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
        df_final = df.fillna("-")

        # 4. İndirme Butonları
        c1, c2 = st.columns(2)
        
        with c1:
            # Excel İndir
            output = io.BytesIO()
            df_final.to_excel(output, index=False)
            st.download_button("📥 Excel Olarak İndir", output.getvalue(), "rapor.xlsx")

        with c2:
            # Fotoğraf İndir
            fig, ax = plt.subplots(figsize=(15, len(df_final)*0.4 + 2))
            ax.axis('off')
            tablo = ax.table(cellText=df_final.values, colLabels=df_final.columns, loc='center', cellLoc='center')
            tablo.auto_set_font_size(False)
            tablo.set_fontsize(9)
            
            img_buf = io.BytesIO()
            plt.savefig(img_buf, format='png', dpi=100, bbox_inches='tight')
            plt.close(fig)
            st.download_button("🖼️ Fotoğraf Olarak İndir", img_buf.getvalue(), "rapor.png")

        st.divider()
        st.subheader("Veri Önizlemesi")
        st.dataframe(df_final)

    except Exception as e:
        st.error(f"Hata: {e}")
