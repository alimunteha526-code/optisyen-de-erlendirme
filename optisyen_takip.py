import streamlit as st
import pandas as pd
import os
from io import BytesIO

# Veri dosyası ayarı
DB_FILE = "optisyen_verileri.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Optisyen Adı", "Mağaza", "Değerlendirme Puanı", "Yorum"])

df = load_data()

st.title("👓 Optisyen Değerlendirme Çıktı Paneli")

# --- VERİ GİRİŞ ALANI (Öncekiyle aynı) ---
with st.expander("➕ Yeni Değerlendirme Ekle"):
    with st.form("yeni_kayit"):
        isim = st.text_input("Optisyen Adı")
        magaza = st.selectbox("Mağaza", ["Merkez", "Şube A", "Şube B"])
        puan = st.slider("Puan", 1, 10, 8)
        notlar = st.text_area("Yorumlar")
        kaydet = st.form_submit_button("Sisteme İşle")
        
        if kaydet and isim:
            yeni_satir = pd.DataFrame([[isim, magaza, puan, notlar]], columns=df.columns)
            df = pd.concat([df, yeni_satir], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.success("Kaydedildi!")

# --- ÇIKTI ALMA VE RAPORLAMA BÖLÜMÜ ---
st.subheader("📋 Mevcut Değerlendirmeler")
st.dataframe(df)

if not df.empty:
    # Excel Dosyasına Dönüştürme İşlemi
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Değerlendirme_Raporu')
        writer.close()
    
    processed_data = output.getvalue()

    # İndirme Butonu
    st.download_button(
        label="📥 Raporu Excel Olarak İndir",
        data=processed_data,
        file_name="optisyen_degerlendirme_raporu.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("Çıktı almak için henüz veri girişi yapılmadı.")