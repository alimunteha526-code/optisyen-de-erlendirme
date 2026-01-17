import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Cam Zayi Raporu", layout="wide")
st.title("📊 Cam Zayi Raporu - Görselleştirici")

uploaded_file = st.file_uploader("Excel veya CSV dosyasını seçin", type=['xlsx', 'csv'])

if uploaded_file is not None:
    try:
        # 1. Dosyayı ham olarak oku
        if uploaded_file.name.endswith('.csv'):
            df_raw = pd.read_csv(uploaded_file)
        else:
            df_raw = pd.read_excel(uploaded_file, header=None) # Önce başlık olmadan oku

        # 2. Gerçek başlık satırını bulma (Header bulma mantığı)
        # 'STOK ADI' veya 'EN' kelimesinin geçtiği ilk satırı başlık yapalım
        header_row = 0
        for i, row in df_raw.iterrows():
            row_str = " ".join(map(str, row.values)).upper()
            if 'STOK ADI' in row_str or 'EN' in row_str or 'FİRE' in row_str:
                header_row = i
                break
        
        # Dosyayı bulduğumuz satırdan itibaren tekrar yapılandır
        df = df_raw.iloc[header_row:].copy()
        df.columns = df.iloc[0] # İlk satırı başlık yap
        df = df[1:] # Veriyi bir alt satırdan başlat
        
        # Sütun isimlerini temizle
        df.columns = df.columns.astype(str).str.strip().str.upper()

        # 3. İstenen Sütunları Seç
        hedef_sutunlar = ['STOK ADI', 'EN', 'BOY', 'ADET', 'TOPLAM M2', 'FİRE NEDENİ']
        # Eğer TOPLAM M2 bulamazsa sadece M2'yi de arasın
        if 'TOPLAM M2' not in df.columns and 'M2' in df.columns:
             df.rename(columns={'M2': 'TOPLAM M2'}, inplace=True)
        
        mevcut_sutunlar = [col for col in hedef_sutunlar if col in df.columns]

        if not mevcut_sutunlar:
            st.error(f"Sütunlar yine bulunamadı. Lütfen kontrol et: {list(df.columns[:10])}")
        else:
            # Temiz veri seti (ilk 25 satır)
            df_display = df[mevcut_sutunlar].dropna(subset=[mevcut_sutunlar[0]]).head(25)
            
            # 4. Görselleştirme
            row_count = len(df_display)
            fig_height = max(3, row_count * 0.6 + 1.5)
            
            fig, ax = plt.subplots(figsize=(14, fig_height))
            ax.axis('off')
            
            tablo = ax.table(
                cellText=df_display.values, 
                colLabels=df_display.columns, 
                loc='center', 
                cellLoc='center',
                colColours=["#2c3e50"] * len(df_display.columns)
            )
            
            tablo.auto_set_font_size(False)
            tablo.set_fontsize(10)
            tablo.scale(1, 2.8)

            for j in range(len(df_display.columns)):
                tablo[0, j].get_text().set_color('white')
                tablo[0, j].get_text().set_weight('bold')

            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=200, bbox_inches='tight')
            buf.seek(0)

            st.success("✅ Başlıklar başarıyla hizalandı ve tablo oluşturuldu!")
            st.image(buf)
            st.download_button("Görseli İndir", buf, "rapor.png", "image/png")

    except Exception as e:
        st.error(f"Bir hata oluştu: {e}")
