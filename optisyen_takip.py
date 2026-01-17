import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Operasyon Zayi Raporu", layout="wide")
st.title("📊 Cam Zayi Operasyon Raporu")

uploaded_file = st.file_uploader("Excel dosyasını seçin", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        # 1. Dosyayı oku
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        
        # Sütunları temizle
        df.columns = df.columns.astype(str).str.strip().str.upper()

        # 2. Sizin paylaştığınız yeni sütun yapısına göre eşleştirme
        # Kod artık hem eski teknik detayları hem de yeni operasyonel başlıkları arar
        esleme_haritasi = {
            'BÖLGE': 'BÖLGE',
            'ÜST BIRIM': 'ÜST BIRIM',
            'NET SATIŞ MIKTARI (CAM)': 'SATIŞ MİKTARI',
            'TOPLAM CAM ZAYI ADET': 'ZAYİ ADET',
            'TOPLAM CAM ZAYI ORANI': 'ZAYİ ORANI',
            'TOPLAM CAM ZAYI HEDEF': 'HEDEF',
            'MAGAZANIN ETKISINDE OLAN CAM ZAYILER': 'MAĞAZA ETKİSİ'
        }

        # Mevcut olanları seç
        mevcut_sutunlar = [col for col in esleme_haritasi.keys() if col in df.columns]

        if not mevcut_sutunlar:
            st.error(f"Dosyada raporlanabilir sütun bulunamadı. Mevcut sütunlar: {list(df.columns[:5])}...")
        else:
            # Veriyi hazırla (Görselde çok sütun olmaması için en kritikleri alalım)
            df_final = df[mevcut_sutunlar].head(20)
            
            # Sütun isimlerini daha kısa hale getirelim (Görsel sığsın diye)
            df_final.columns = [esleme_haritasi[c] for c in df_final.columns]

            # 3. Görselleştirme
            row_count = len(df_final)
            fig_height = max(4, row_count * 0.7 + 2)
            fig, ax = plt.subplots(figsize=(16, fig_height))
            ax.axis('off')

            tablo = ax.table(
                cellText=df_final.values, 
                colLabels=df_final.columns, 
                loc='center', 
                cellLoc='center',
                colColours=["#2c3e50"] * len(df_final.columns)
            )

            tablo.auto_set_font_size(False)
            tablo.set_fontsize(9)
            tablo.scale(1, 3) # Satır yüksekliği

            # Başlık stilini düzenle
            for j in range(len(df_final.columns)):
                tablo[0, j].get_text().set_color('white')
                tablo[0, j].get_text().set_weight('bold')

            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=200, bbox_inches='tight')
            buf.seek(0)

            st.success("✅ Operasyonel veriler başarıyla tabloya dönüştürüldü!")
            st.image(buf)
            st.download_button("Raporu Görsel Olarak İndir", buf, "operasyon_raporu.png", "image/png")

    except Exception as e:
        st.error(f"İşlem sırasında hata: {e}")
