import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# Sayfa yapılandırması
st.set_page_config(page_title="Cam Zayi Raporu", layout="wide")
st.title("📊 Cam Zayi Raporu - Görselleştirici")

# Dosya yükleme alanı
uploaded_file = st.file_uploader("Düzenlenmiş Excel veya CSV dosyasını seçin", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        # Veriyi oku
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Sütunları temizle ve filtrele
        secilecek_sutunlar = ['STOK ADI', 'EN', 'BOY', 'ADET', 'TOPLAM m2', 'FİRE NEDENİ']
        mevcut_sutunlar = [col for col in secilecek_sutunlar if col in df.columns]
        df_display = df[mevcut_sutunlar].fillna('-') # Boş hücreleri doldur

        # Tabloyu oluştur
        fig, ax = plt.subplots(figsize=(15, len(df_display) * 0.6 + 2))
        ax.axis('off')
        
        tablo = ax.table(
            cellText=df_display.values, 
            colLabels=df_display.columns, 
            loc='center', 
            cellLoc='center',
            colColours=["#4c5c96"] * len(df_display.columns) # Başlık rengi
        )
        
        tablo.auto_set_font_size(False)
        tablo.set_fontsize(10)
        tablo.scale(1.2, 2.5)

        # Başlık hücrelerini beyaz yap
        for j in range(len(df_display.columns)):
            tablo[0, j].get_text().set_color('white')
            tablo[0, j].get_text().set_weight('bold')

        # Görseli belleğe kaydet
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)

        # EKRANA BASMA (Boş ekranı önleyen kısım)
        st.subheader("Oluşturulan Tablo Önizlemesi")
        st.image(buf, use_container_width=True)

        # İNDİRME BUTONU
        st.download_button(
            label="Tabloyu JPG/PNG Olarak İndir",
            data=buf,
            file_name="cam_zayi_raporu.png",
            mime="image/png"
        )

    except Exception as e:
        st.error(f"Hata oluştu: {e}")
else:
    st.info("Lütfen bir dosya yükleyin. Ekran şu an bu yüzden boş görünüyor.")
