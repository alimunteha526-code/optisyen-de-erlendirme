import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Tüm Mağazalar Zayi Raporu", layout="wide")
st.title("📊 Tüm Mağazalar Cam Zayi Raporu")

uploaded_file = st.file_uploader("Excel dosyasını yükleyin", type=['xlsx'])

if uploaded_file is not None:
    try:
        # 1. Dosyayı oku
        df_raw = pd.read_excel(uploaded_file, header=None)
        
        # 2. Gerçek başlık satırını bul (ÜST BIRIM kelimesini içeren satır)
        target_idx = None
        for i, row in df_raw.iterrows():
            if "ÜST BIRIM" in " ".join(map(str, row.values)).upper():
                target_idx = i
                break
        
        if target_idx is not None:
            # Tabloyu yapılandır
            df = df_raw.iloc[target_idx:].copy()
            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)
            
            # Sütunları temizle (İsimsiz kolonları ve noktaları kaldır)
            df = df.loc[:, df.columns.notna()]
            df = df.loc[:, ~df.columns.astype(str).str.contains('^Unnamed|^\\.')]

            # Boş satırları temizle (Mağaza kodu boş olanları at)
            ub_col = next((c for c in df.columns if "ÜST BIRIM" in str(c).upper()), df.columns[0])
            df = df.dropna(subset=[ub_col])

            # 3. Görselleştirme Ayarları
            df_final = df.fillna(0) # Sayısal boşluklara 0 yaz
            
            # Dinamik Boyutlandırma: Mağaza sayısı arttıkça tablo uzasın
            fig_height = max(6, len(df_final) * 0.5 + 2)
            fig_width = max(15, len(df_final.columns) * 1.5)
            
            fig, ax = plt.subplots(figsize=(fig_width, fig_height))
            ax.axis('off')

            # Tabloyu oluştur
            tablo = ax.table(
                cellText=df_final.values, 
                colLabels=df_final.columns, 
                loc='center', 
                cellLoc='center',
                colColours=["#2c3e50"] * len(df_final.columns)
            )

            # Stil: Yazı tipi ve hücre yüksekliği
            tablo.auto_set_font_size(False)
            tablo.set_fontsize(8)
            tablo.scale(1, 3) # Satırları Excel gibi ferahlatır

            # Başlıkları Beyaz Yap
            for j in range(len(df_final.columns)):
                tablo[0, j].get_text().set_color('white')
                tablo[0, j].get_text().set_weight('bold')

            # Resmi Belleğe Kaydet
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            buf.seek(0)

            st.success(f"✅ Toplam {len(df_final)} mağaza başarıyla listelendi.")
            st.image(buf)
            st.download_button("Tüm Listeyi Görsel Olarak İndir", buf, "tam_mağaza_listesi.png", "image/png")
        
        else:
            st.error("Başlık satırı bulunamadı. Lütfen dosyada 'ÜST BİRİM' sütunu olduğundan emin olun.")

    except Exception as e:
        st.error(f"İşlem sırasında bir hata oluştu: {e}")
