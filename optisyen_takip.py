import streamlit as st
import pandas as pd
import os
from io import BytesIO

# --- AYARLAR VE VERİ TABANI ---
DB_FILE = "optisyen_veritabani.csv"

def veriyi_yukle():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Tarih", "Optisyen Adı", "Mağaza", "Puan", "Değerlendirme Notu"])

st.set_page_config(page_title="Optisyen Değerlendirme", layout="wide")

# Veriyi çek
df = veriyi_yukle()

# Türkçe büyük harf fonksiyonu
def turkce_buyuk(metin):
    if not metin: return ""
    return metin.replace('i', 'İ').replace('ı', 'I').upper()

# --- BAŞLIK ---
st.title("👓 Optisyen Değerlendirme Sistemi")

# --- SOL PANEL: VERİ GİRİŞİ ---
st.sidebar.header("📝 Yeni Veri Girişi")
with st.sidebar.form("optisyen_form"):
    isim_input = st.text_input("Optisyen Adı Soyadı")
    magaza_input = st.text_input("Çalıştığı Mağaza")
    puan = st.slider("Performans Puanı", 1, 10, 7)
    notlar_input = st.text_area("Yönetici Notu / Müşteri Yorumu")
    tarih = st.date_input("Değerlendirme Tarihi")
    
    kaydet = st.form_submit_button("Sisteme Kaydet")

if kaydet:
    if isim_input and magaza_input:
        isim_buyuk = turkce_buyuk(isim_input)
        magaza_buyuk = turkce_buyuk(magaza_input)
        notlar_buyuk = turkce_buyuk(notlar_input)

        yeni_veri = {
            "Tarih": str(tarih),
            "Optisyen Adı": isim_buyuk,
            "Mağaza": magaza_buyuk,
            "Puan": puan,
            "Değerlendirme Notu": notlar_buyuk
        }
        
        df = pd.concat([df, pd.DataFrame([yeni_veri])], ignore_index=True)
        df.to_csv(DB_FILE, index=False)
        st.sidebar.success(f"{isim_buyuk} başarıyla eklendi!")
        st.rerun()
    else:
        st.sidebar.error("Lütfen isim ve mağaza bölümlerini doldurunuz!")

# --- ANA PANEL: VERİ GÖRÜNTÜLEME VE AKILLI FİLTRELEME ---
tab1, tab2 = st.tabs(["📊 Veri Tablosu ve Filtreler", "📑 Rapor Al (Excel)"])

with tab1:
    st.subheader("🔍 Akıllı Filtreleme")
    
    if not df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Kayıtlı isimlerden benzersiz bir liste oluşturup filtreye koyuyoruz
            kayitli_isimler = sorted(df["Optisyen Adı"].unique())
            secilen_isimler = st.multiselect("Optisyen İsmine Göre Filtrele", options=kayitli_isimler)
            
        with col2:
            # Kayıtlı mağazalardan benzersiz bir liste oluşturup filtreye koyuyoruz
            kayitli_magazalar = sorted(df["Mağaza"].unique())
            secilen_magazalar = st.multiselect("Mağazaya Göre Filtrele", options=kayitli_magazalar)

        # Filtreleme Mantığı
        filtrelenmis_df = df.copy()
        if secilen_isimler:
            filtrelenmis_df = filtrelenmis_df[filtrelenmis_df["Optisyen Adı"].isin(secilen_isimler)]
        if secilen_magazalar:
            filtrelenmis_df = filtrelenmis_df[filtrelenmis_df["Mağaza"].isin(secilen_magazalar)]

        st.divider()
        st.subheader("📋 Sonuçlar")
        st.dataframe(filtrelenmis_df, use_container_width=True)
        
        # Seçili verilere göre hızlı özet
        if not filtrelenmis_df.empty:
            st.info(f"Şu an {len(filtrelenmis_df)} kayıt listeleniyor. Ortalama Puan: {filtrelenmis_df['Puan'].mean():.2f}")
    else:
        st.info("Henüz hiç kayıt yapılmamış. Sol taraftan ilk verinizi ekleyebilirsiniz.")

with tab2:
    st.subheader("Excel Raporu Oluştur")
    # Filtrelenmiş veriyi veya tümünü indir
    rapor_verisi = filtrelenmis_df if not df.empty else df
    
    if not rapor_verisi.empty:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            rapor_verisi.to_excel(writer, index=False, sheet_name='Performans_Raporu')
        
        excel_data = output.getvalue()
        st.download_button(
            label="💾 Filtrelenmiş Listeyi Excel Olarak İndir",
            data=excel_data,
            file_name="Optisyen_Raporu.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("İndirilecek veri bulunamadı.")
