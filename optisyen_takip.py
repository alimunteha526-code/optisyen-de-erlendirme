import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Zayi Raporu Merkezi", layout="wide")
st.title("📊 Cam Zayi Raporu - İndirme Merkezi")

uploaded_file = st.file_uploader("Excel dosyasını yükleyin", type=['xlsx'])

if uploaded_file is not None:
    try:
        # 1. Dosyayı ham oku ve gerçek başlıkları bul
        df_raw = pd.read_excel(uploaded_file, header=None)
        
        start_row = 0
        for i, row in df_raw.iterrows():
            row_str = " ".join(map(str, row.values)).upper()
            if "ÜST BIRIM" in row_str or "BÖLGE" in row_str:
                start_row = i
                break
        
        # Tabloyu yapılandır
        df = df_raw.iloc[start_row:].copy()
        df.columns = df.iloc[0] 
        df = df[1:].reset_index(drop=True)
        
        # Boş sütunları ve satırları temizle
        df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
        
        # --- TÜM MAĞAZALARI VE SÜTUNLARI TUT ---
        df_final = df.fillna("-")

        # --- ARAYÜZ SEÇENEKLERİ ---
        col1, col2 = st.columns(2)
        
        with col1:
            # EXCEL OLARAK İNDİRME
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_final.to_excel(writer, index=False, sheet_name='Düzenlenmiş Rapor')
            excel_data = output.getvalue()
            st.download_button(
                label="📥 Düzenlenmiş Excel'i İndir",
                data=excel_data,
                file_name="cam_zayi_raporu_duzenli.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        with col2:
            # FOTOĞRAF OLUŞTURMA
            fig_width = max(18, len(df_final.columns) * 1.5)
            fig_height = max(6, len(df_final) * 0.6 + 2)
            fig, ax = plt.subplots(figsize=(fig_width, fig_height))
            ax.axis('off')

            tablo = ax.table(
                cellText=df_final.values, 
                colLabels=df_final.columns, 
                loc='center', 
                cellLoc='center'
            )
            tablo.auto_set_font_size(False)
            tablo.set_fontsize(9)
            tablo.scale(1, 2.8)

            for j in range(len(df_final.columns)):
                tablo[0, j].set_facecolor('#4e73df')
                tablo[0, j].get_text().set_color('white')
                tablo[0, j].get_text().set_weight('bold')

            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)
            
            st.download_button(
                label="🖼️ Raporu Fotoğraf (PNG) Olarak İndir",
                data=buf,
                file_name="zayi_raporu_gorsel.png",
                mime="image/png"
            )

        st.subheader("Tablo Önizlemesi")
        st.dataframe(df_final) # Ekranda tabloyu göster

    except Exception as e:
        st.error(f"Hata oluştu: {e}")
