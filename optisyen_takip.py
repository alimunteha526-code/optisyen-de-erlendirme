import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# Sayfa yapılandırması
st.set_page_config(page_title="Cam Zayi Raporu", layout="wide")
st.title("📊 Cam Zayi Raporu - Görselleştirici")

uploaded_file = st.file_uploader("Excel veya CSV dosyasını seçin", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        # 1. Veriyi Oku
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # 2. Sütun İsimlerini Temizle (Büyük/Küçük harf ve boşluk hatasını önler)
        df.columns = df.columns.str.strip().str.upper()

        # 3. İstenen Sütunları Belirle
        hedef_sutunlar = ['STOK ADI', 'EN', 'BOY', 'ADET', 'TOPLAM M2', 'FİRE NEDENİ']
        mevcut_sutunlar = [col for col in hedef_sutunlar if col in df.columns]

        if len(df) == 0:
            st.error("Dosya içeriği boş görünüyor!")
        elif not mevcut_sutunlar:
            st.error(f"Dosyada uygun sütun bulunamadı. Mevcut sütunlar: {', '.join(df.columns)}")
        else:
            # Sadece mevcut olanları al ve boşları doldur
            df_display = df[mevcut_sutunlar].fillna('-').head(30)

            # 4. Görselleştirme (Division by zero hatasını önlemek için boyut kontrolü)
            row_count = len(df_display)
            fig_height = max(2, row_count * 0.5 + 1) # En az 2 birim yükseklik
            
            fig, ax = plt.subplots(figsize=(12, fig_height))
            ax.axis('off')
            
            tablo = ax.table(
                cellText=df_display.values, 
                colLabels=df_display.columns, 
                loc='center', 
                cellLoc='center',
                colColours=["#4c5c96"] * len(df_display.columns)
            )
            
            tablo.auto_set_font_size(False)
            tablo.set_fontsize(9)
            tablo.scale(1, 2)

            # Başlık stilini ayarla
            for j in range(len(df_display.columns)):
                tablo[0, j].get_text().set_color('white')
                tablo[0, j].get_text().set_weight('bold')

            # 5. Çıktıyı hazırla
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=200, bbox_inches='tight')
            buf.seek(0)

            st.subheader("✅ Rapor Hazır")
            st.image(buf)
            
            st.download_button(
                label="Resmi İndir (PNG)",
                data=buf,
                file_name="zayi_raporu.png",
                mime="image/png"
            )

    except Exception as e:
        st.error(f"Beklenmedik bir hata oluştu: {e}")
else:
    st.info("Lütfen bir Excel veya CSV dosyası yükleyerek başlayın.")
