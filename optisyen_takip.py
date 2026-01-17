import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# Sayfa ayarlarını en başta yapıyoruz
st.set_page_config(page_title="Zayi Raporu", layout="wide")

st.title("📊 Mağaza Zayi Raporu Oluşturucu")

uploaded_file = st.file_uploader("Excel dosyasını yükleyin", type=['xlsx'])

if uploaded_file is not None:
    # Hata oluşmasını engellemek için bir konteyner oluşturuyoruz
    container = st.container()
    
    try:
        # 1. Excel'i oku
        df_raw = pd.read_excel(uploaded_file, header=None)
        
        # Başlık satırını bul
        start_row = 0
        for i, row in df_raw.iterrows():
            row_str = " ".join(map(str, row.values)).upper()
            if "ÜST BIRIM" in row_str or "BÖLGE" in row_str:
                start_row = i
                break
        
        # Veriyi yapılandır
        df = df_raw.iloc[start_row:].copy()
        df.columns = df.iloc[0]
        df = df[1:].reset_index(drop=True)
        
        # Tamamen boş satır/sütun temizliği
        df = df.dropna(how='all', axis=1).dropna(how='all', axis=0)
        df_final = df.fillna("-")

        with container:
            st.success("✅ Veri başarıyla işlendi.")
            
            # Seçenek Butonları
            col1, col2 = st.columns(2)
            
            # --- EXCEL ÇIKTISI ---
            with col1:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_final.to_excel(writer, index=False)
                st.download_button(
                    label="📥 Excel Olarak İndir",
                    data=output.getvalue(),
                    file_name="zayi_raporu.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            # --- FOTOĞRAF ÇIKTISI ---
            with col2:
                # Görsel oluşturma
                fig_width = max(16, len(df_final.columns) * 1.2)
                fig_height = max(4, len(df_final) * 0.5 + 2)
                
                # Bellek dostu çizim
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
                tablo.scale(1, 2.5)
                
                # Başlık renklendirme
                for (row, col), cell in tablo.get_celld().items():
                    if row == 0:
                        cell.set_facecolor('#4e73df')
                        cell.get_text().set_color('white')
                        cell.get_text().set_weight('bold')

                img_buf = io.BytesIO()
                plt.savefig(img_buf, format='png', dpi=120, bbox_inches='tight')
                plt.close(fig) # Hafızayı temizle
                
                st.download_button(
                    label="🖼️ Fotoğraf (PNG) Olarak İndir",
                    data=img_buf.getvalue(),
                    file_name="zayi_raporu.png",
                    mime="image/png"
                )

            # Önizleme (Tarayıcıyı yormamak için sadece ilk 15 satırı gösteriyoruz)
            st.subheader("Tablo Önizlemesi (İlk 15 Satır)")
            st.dataframe(df_final.head(15), use_container_width=True)

    except Exception as e:
        st.error(f"Bir hata oluştu: {str(e)}")

else:
    st.info("Lütfen bir dosya yükleyin.")
