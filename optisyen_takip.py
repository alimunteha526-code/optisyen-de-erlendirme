import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Özel Mağaza Raporu", layout="wide")
st.title("📊 Mağaza Koduna Göre Filtrelenmiş Rapor")

# --- BURAYI DÜZENLEYİN ---
# Sadece bu listedeki mağaza kodları (Üst Birim) görünecek
# Örnek: [101, 102, 205] gibi kodları buraya ekleyin
filtre_kodlar = [101, 102] 
# --------------------------

uploaded_file = st.file_uploader("Excel dosyasını yükleyin", type=['xlsx'])

if uploaded_file is not None:
    try:
        # 1. Dosyayı ham oku ve gerçek başlığı bul
        df_raw = pd.read_excel(uploaded_file, header=None)
        
        target_row_index = None
        for i, row in df_raw.iterrows():
            row_content = " ".join([str(val).upper() for val in row.values])
            if "ÜST BIRIM" in row_content or "BÖLGE" in row_content:
                target_row_index = i
                break

        if target_row_index is not None:
            # 2. Tabloyu yapılandır (Excel'deki orijinal sütun isimlerini koru)
            df = df_raw.iloc[target_row_index:].copy()
            df.columns = df.iloc[0] 
            df = df[1:].reset_index(drop=True)
            
            # 3. Filtreleme İşlemi
            # 'ÜST BIRIM' sütununu bul (Büyük/küçük harf duyarlılığını aşmak için)
            ub_col = next((c for c in df.columns if "ÜST BIRIM" in str(c).upper()), None)
            
            if ub_col:
                # Veriyi sayısal değere çevirip filtrele (Hata payını azaltmak için)
                df[ub_col] = pd.to_numeric(df[ub_col], errors='coerce')
                df = df[df[ub_col].isin(filtre_kodlar)]
            
            if df.empty:
                st.warning(f"Belirtilen {filtre_kodlar} kodlarına ait veri bulunamadı. Lütfen kodları kontrol edin.")
            else:
                # 4. Görselleştirme (Excel Biçimiyle Aynı)
                df_final = df.fillna("") # Boş hücreleri temiz göster

                # Satır sayısına göre dinamik yükseklik
                fig_height = max(4, len(df_final) * 0.8 + 2)
                fig, ax = plt.subplots(figsize=(20, fig_height))
                ax.axis('off')

                # Tablo oluşturma
                tablo = ax.table(
                    cellText=df_final.values, 
                    colLabels=df_final.columns, 
                    loc='center', 
                    cellLoc='center',
                    colColours=["#2c3e50"] * len(df_final.columns)
                )

                # Stil Ayarları
                tablo.auto_set_font_size(False)
                tablo.set_fontsize(9)
                tablo.scale(1, 3.5) # Satır yüksekliğini Excel'e benzer şekilde genişletir

                # Başlıkları Beyaz ve Kalın Yap
                for j in range(len(df_final.columns)):
                    tablo[0, j].get_text().set_color('white')
                    tablo[0, j].get_text().set_weight('bold')

                # Çıktı
                buf = io.BytesIO()
                plt.savefig(buf, format='png', dpi=200, bbox_inches='tight')
                buf.seek(0)

                st.success(f"✅ {len(df_final)} Mağaza için rapor hazırlandı.")
                st.image(buf)
                st.download_button("Görseli Kaydet (PNG)", buf, "ozel_mağaza_raporu.png", "image/png")
        else:
            st.error("Başlık satırı (ÜST BİRİM) bulunamadı.")

    except Exception as e:
        st.error(f"Bir hata oluştu: {e}")
