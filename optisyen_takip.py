import streamlit as st
import pandas as pd
import random
from io import BytesIO

# Sayfa Ayarları
st.set_page_config(page_title="Vardiya Takip Paneli", layout="wide")

st.title("🗓️ Şube Vardiya Planlama Paneli")
st.markdown("---")

# Yan Menü: Ayarlar
st.sidebar.header("⚙️ Yapılandırma")

# Şube İsimleri
sube_1 = st.sidebar.text_input("1. Şube Adı", "Merkez Şube")
sube_2 = st.sidebar.text_input("2. Şube Adı", "Çarşı Şube")
sube_3 = st.sidebar.text_input("3. Şube Adı", "AVM Şubesi")
subeler = [sube_1, sube_2, sube_3]

# Çalışan Listesi
varsayilan_calisanlar = "Ahmet, Ayşe, Mehmet, Fatma, Can, Ece, Ali, Zeynep, Burak, Deniz, Selin, Mert"
calisan_input = st.sidebar.text_area("Çalışan Listesi (Virgülle ayırın)", varsayilan_calisanlar)
calisanlar = [name.strip() for name in calisan_input.split(",") if name.strip()]

# Vardiya Oluşturma Fonksiyonu
def plan_olustur():
    if len(calisanlar) < 12:
        st.error(f"⚠️ Yetersiz personel! 3 şube için en az 12 kişi lazım. Şu an: {len(calisanlar)}")
        return None
    
    secilenler = random.sample(calisanlar, 12)
    random.shuffle(secilenler)
    
    veriler = []
    for i, sube in enumerate(subeler):
        sabah = secilenler[i*4 : i*4+2]
        aksam = secilenler[i*4+2 : i*4+4]
        veriler.append({
            "Şube": sube,
            "Sabah (09:00 - 17:00)": ", ".join(sabah),
            "Akşam (13:00 - 21:00)": ", ".join(aksam)
        })
    return pd.DataFrame(veriler)

# Ana Ekran
col1, col2 = st.columns([1, 1])

if st.button("🚀 Yeni Vardiya Planı Oluştur"):
    df = plan_olustur()
    
    if df is not None:
        st.subheader("📊 Haftalık Dağılım")
        # Tabloyu göster
        st.table(df)
        
        # Excel İndirme Hazırlığı
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Vardiya')
        
        st.download_button(
            label="📥 Planı Excel Olarak İndir",
            data=output.getvalue(),
            file_name="vardiya_plani.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

st.sidebar.markdown("---")
st.sidebar.info("İpucu: Personel sayısını artırarak rotasyonu daha adil hale getirebilirsiniz.")
