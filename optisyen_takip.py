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

# --- BAŞLIK ---
st.title("👓 Optisyen Değerlendirme Sistemi")

df = veriyi_yukle()

# --- SOL PANEL: VERİ GİRİŞİ ---
st.sidebar.header("📝 Yeni Veri Girişi")
with st.sidebar.form("optisyen_form"):
    # Girişleri alırken otomatik büyük harfe çevirme işlemi aşağıda yapılıyor
    isim_input = st.text_input("Optisyen Adı Soyadı")
    magaza_input = st.selectbox("Çalıştığı Mağaza", ["Merkez Şube", "Kuzey AVM", "Güney Çarşı", "Havalimanı"])
    puan = st.slider("Performans Puanı", 1, 10, 7)
    notlar_input = st.text_area("Yönetici Notu / Müşteri Yorumu")
    tarih = st.date_input("Değerlendirme Tarihi")
    
    kaydet = st.form_submit_button("Sisteme Kaydet")

if kaydet:
    if isim_input:
        # TÜRKÇE KARAKTER UYUMLU BÜYÜK HARFE ÇEVİRME
        # .upper() bazen 'i' harfini 'I' yapar, 'İ' yapması için küçük bir düzeltme ekledik.
        isim_buyuk = isim_input.replace('i', 'İ').replace('ı', 'I').upper()
        magaza_buyuk = magaza_input.replace('i', 'İ').replace('ı', 'I').upper()
        notlar_buyuk = notlar_input.replace('i', 'İ').replace('ı', 'I').upper() if notlar_input else ""

        yeni_veri = {
            "Tarih": str(tarih),
            "Optisyen Adı": isim_buyuk,
            "Mağaza": magaza_buyuk,
            "Puan": puan,
            "Değerlendirme Notu": notlar_buyuk
        }
        
        df = pd.concat([df, pd.DataFrame([yeni_veri])], ignore_index=True)
        df.to_csv(DB_FILE, index=False)
        st.sidebar.success(f"{isim_buyuk} kaydı başarıyla eklendi!")
        st.rerun()
    else:
        st.sidebar.error("Lütfen bir isim giriniz!")

# --- ANA PANEL: VERİ GÖRÜNTÜLEME VE ÇIKTI ---
tab1, tab2 = st.tabs(["📊 Veri Tablosu", "📑 Rapor Al (Excel)"])

with tab1:
    st.subheader("Kayıtlı Optisyen Listesi")
    if not df.empty:
        arama = st.text_input("🔍 İsim veya Mağaza ile Filtrele").upper() # Arama yaparken de büyük harfe çevirir
        filtrelenmis_df = df[df.apply(lambda row: arama in row.astype(str).values, axis=1)]
        st.dataframe(filtrelenmis_df, use_container_width=True)
    else:
        st.info("Henüz hiç kayıt yapılmamış.")

with tab2:
    st.subheader("Excel Raporu Oluştur")
    if not df.empty:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Performans_Raporu')
        
        excel_data = output.getvalue()
        st.download_button(
            label="💾 Excel Dosyasını Bilgisayara İndir",
            data=excel_data,
            file_name=f"Optisyen_Raporu.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Rapor oluşturmak için veri bulunamadı.")
