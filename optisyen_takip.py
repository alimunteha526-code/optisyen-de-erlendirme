import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Optisyen Zayi Raporu", layout="wide")

st.title("📊 Cam Zayi Raporu - Orijinal Biçim")

uploaded_file = st.file_uploader("Excel dosyasını yükleyin", type=['xlsx'])

if uploaded_file is not None:
    try:
        # 1. Excel'i ham haliyle oku
        df_raw = pd.read_excel(uploaded_file, header=None)
        
        # 2. Gerçek tablo başlangıcını bul (Bölge/Üst Birim araması)
        start_row = 0
        for i, row in df_raw.iterrows():
            line = " ".join(map(str, row.values)).upper()
            if "ÜST BIRIM" in line or "BÖLGE" in line:
                start_row = i
                break
        
        # Tabloyu yapılandır
        df = df_raw.iloc[start_row:].copy()
        df.columns = df.iloc[0] # Excel'deki orijinal başlıklar
        df = df[1:].reset_index(drop=True)
        
        # Gereksiz tamamen boş sütunları ve satırları temizle
        df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
        
        # 'M' ile başlayan mağaza kodlarını içeren satırları filtrele (Opsiyonel)
        # Eğer tüm satırları istiyorsan bu kısmı bırakabiliriz
        ub_col = df.columns[2] # Genelde 3. sütun Üst Birimdir
        df = df[df[ub_col].astype(str).str.contains('M', na=False)]

        if not df.empty:
            # 3. GÖRSELLEŞTİRME (Excel gibi geniş ve okunaklı)
            # Sütun sayısı çok fazla olduğu için genişliği artırıyoruz
            col_count = len(df.columns)
            row_count = len(df)
            
            fig, ax = plt.subplots(figsize=(col_count * 1.8, row_count * 0.6 + 2))
            ax.axis('off')

            # Tabloyu çiz
            tablo = ax.table(
                cellText=df.values,
                colLabels=df.columns,
                loc='center',
                cellLoc='left' # Excel gibi sola yaslı
            )

            # Stil Ayarları
            tablo.auto_set_font_size(False)
            tablo.set_fontsize(10)
            tablo.scale(1, 2.5) # Satırları genişlet

            # Başlık satırını boya (Excel stili)
            for j in range(col_count):
                tablo[0, j].get_text().set_weight('bold')
                tablo[0, j].set_facecolor('#D3D3D3') # Açık gri başlık

            # PNG olarak kaydet
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)

            st.success(f"✅ {row_count} Mağaza Excel formatında hazırlandı.")
            st.image(buf)
            st.download_button("Resmi Farklı Kaydet", buf, "zayi_raporu.png", "image/png")
        else:
            st.warning("Eşleşen mağaza verisi bulunamadı.")

    except Exception as e:
        st.error(f"Hata: {e}")
