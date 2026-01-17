import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Zayi Raporu", layout="wide")
st.title("📊 Cam Zayi Raporu Görselleştirici")

uploaded_file = st.file_uploader("Excel dosyasını yükleyin", type=['xlsx'])

if uploaded_file is not None:
    try:
        # 1. Dosyayı ham (başlıksız) oku
        df_raw = pd.read_excel(uploaded_file, header=None)

        # 2. Gerçek başlık satırını bul (BÖLGE veya ÜST BIRIM kelimesini ara)
        target_row_index = None
        for i, row in df_raw.iterrows():
            # Satırdaki tüm hücreleri metne çevir ve büyük harf yapıp birleştir
            row_content = " ".join([str(val).upper() for val in row.values])
            if "BÖLGE" in row_content or "ÜST BIRIM" in row_content or "NET SATIŞ" in row_content:
                target_row_index = i
                break

        if target_row_index is None:
            st.error("Dosya içinde 'BÖLGE' veya 'ÜST BIRIM' sütunu bulunamadı. Lütfen doğru dosyayı yüklediğinizden emin olun.")
            st.write("Dosyanın ilk 5 satırı şöyle görünüyor:", df_raw.head(5))
        else:
            # 3. Tabloyu yeniden yapılandır
            df = df_raw.iloc[target_row_index:].copy()
            df.columns = df.iloc[0] # Bulduğumuz satırı başlık yap
            df = df[1:].reset_index(drop=True) # Başlık satırını veriden çıkar
            
            # Sütun isimlerini temizle
            df.columns = df.columns.astype(str).str.strip().str.upper()

            # 4. İstenen sütunları eşleştir
            hedef_sutunlar = [
                'BÖLGE', 'ÜST BIRIM', 'NET SATIŞ MIKTARI (CAM)', 
                'TOPLAM CAM ZAYI ADET', 'TOPLAM CAM ZAYI ORANI'
            ]
            
            mevcut_sutunlar = [col for col in hedef_sutunlar if col in df.columns]

            if not mevcut_sutunlar:
                st.warning("Aranan başlıklar bulunamadı. Bulunanlar: " + str(list(df.columns[:10])))
            else:
                # Veriyi temizle (Boş satırları at, ilk 20 veriyi al)
                df_final = df[mevcut_sutunlar].dropna(how='all').head(20)

                # 5. Görselleştirme
                fig, ax = plt.subplots(figsize=(14, len(df_final) * 0.7 + 2))
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

                # Başlıkları beyaz ve kalın yap
                for j in range(len(df_final.columns)):
                    tablo[0, j].get_text().set_color('white')
                    tablo[0, j].get_text().set_weight('bold')

                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=200, bbox_inches='tight')
                buf.seek(0)

                st.success("✅ Tablo başarıyla oluşturuldu!")
                st.image(buf)
                st.download_button("Raporu İndir", buf, "rapor.png", "image/png")

    except Exception as e:
        st.error(f"Bir hata oluştu: {e}")
