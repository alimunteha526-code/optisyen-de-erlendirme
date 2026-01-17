import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Mağaza Raporu", layout="wide")

# --- MAĞAZA KODLARINI BURAYA YAZIN ---
# Örnek: ["M38002", "M06030"] gibi tırnak içinde ve tam yazın
filtre_kodlar = ["M38002", "M06030", "M42001"] 
# ------------------------------------

st.title("📊 Özel Mağaza Zayi Raporu")

uploaded_file = st.file_uploader("Excel dosyasını yükleyin", type=['xlsx'])

if uploaded_file is not None:
    try:
        # 1. Ham veriyi oku
        df_raw = pd.read_excel(uploaded_file, header=None)
        
        # 2. Başlık satırını dinamik olarak bul
        header_row_idx = None
        for i, row in df_raw.iterrows():
            row_str = " ".join(map(str, row.values)).upper()
            if "ÜST BIRIM" in row_str or "BÖLGE" in row_str:
                header_row_idx = i
                break
        
        if header_row_idx is not None:
            # Tabloyu oluştur (Orijinal haliyle)
            df = df_raw.iloc[header_row_idx:].copy()
            df.columns = df.iloc[0] # Orijinal başlıklar
            df = df[1:].reset_index(drop=True)
            
            # 3. Akıllı Filtreleme
            # 'ÜST BIRIM' sütununu bul
            ub_col = next((c for c in df.columns if "ÜST BIRIM" in str(c).upper()), None)
            
            if ub_col:
                # Veriyi temizle ve filtrele (Büyük harf ve boşluk duyarlılığını kaldırır)
                df[ub_col] = df[ub_col].astype(str).str.strip()
                df_filtered = df[df[ub_col].isin(filtre_kodlar)]
                
                if df_filtered.empty:
                    st.warning(f"Kodlar bulunamadı. Dosyadaki bazı örnek kodlar: {df[ub_col].head(3).tolist()}")
                else:
                    # 4. Görselleştirme (Dosyadaki biçimin aynısı)
                    df_final = df_filtered.fillna("-")
                    
                    # Sayfa genişliğine göre tablo boyutunu ayarla
                    fig, ax = plt.subplots(figsize=(24, len(df_final) * 0.8 + 2))
                    ax.axis('off')

                    tablo = ax.table(
                        cellText=df_final.values, 
                        colLabels=df_final.columns, 
                        loc='center', 
                        cellLoc='center',
                        colColours=["#f2f2f2"] * len(df_final.columns) # Hafif gri başlıklar
                    )

                    tablo.auto_set_font_size(False)
                    tablo.set_fontsize(8)
                    tablo.scale(1, 4) # Excel'deki gibi geniş satırlar

                    # Başlıkları koyu yap
                    for j in range(len(df_final.columns)):
                        tablo[0, j].get_text().set_weight('bold')

                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
                    buf.seek(0)

                    st.success(f"Filtrelendi: {len(df_final)} satır listeleniyor.")
                    st.image(buf)
                    st.download_button("Görseli JPG/PNG Olarak İndir", buf, "rapor.png", "image/png")
            else:
                st.error("Sütunlar arasında 'Üst Birim' bulunamadı.")
        else:
            st.error("Başlık satırı bulunamadı. Lütfen Excel sayfasını kontrol edin.")

    except Exception as e:
        st.error(f"Hata: {e}")
