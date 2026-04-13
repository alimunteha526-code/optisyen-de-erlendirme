import streamlit as st
import pandas as pd
import random
import io

st.set_page_config(page_title="Niğde Şubeleri Vardiya Paneli", layout="wide")

st.title("📅 Şube Bazlı Haftalık Vardiya Sistemi")
st.markdown("Hücrelerde sadece mesai saatleri görünür. Düzenlemek için hücreye çift tıklayın.")

# --- YAN MENÜ (AYARLAR) ---
st.sidebar.header("🏢 Şube ve Personel Tanımlama")

# Şube Ayarları
s1_isim = st.sidebar.text_input("1. Şube Adı:", "Niğde 1")
s1_personel = st.sidebar.text_area(f"{s1_isim} Personelleri:", "Ahmet, Ayşe, Mehmet, Fatma")

s2_isim = st.sidebar.text_input("2. Şube Adı:", "Niğde 2")
s2_personel = st.sidebar.text_area(f"{s2_isim} Personelleri:", "Can, Ece, Ali, Zeynep")

s3_isim = st.sidebar.text_input("3. Şube Adı:", "Niğde 3")
s3_personel = st.sidebar.text_area(f"{s3_isim} Personelleri:", "Burak, Deniz, Selin, Mert")

gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
mesai_saatleri = ["05:30 - 14:00", "07:30 - 16:00", "13:30 - 22:00", "14:30 - 23:00"]

def vardiya_hesapla(p_listesi):
    personeller = [p.strip() for p in p_listesi.split(",") if p.strip()]
    if len(personeller) < 4:
        return pd.DataFrame(columns=gunler)
    
    matris = {p: {g: "" for g in gunler} for p in personeller}
    
    # Her gün için tam 1 kişi izinli atama
    for g_idx, gun in enumerate(gunler):
        izinli_idx = g_idx % len(personeller)
        izinli_p = personeller[izinli_idx]
        matris[izinli_p][gun] = "İZİNLİ"
        
        # Diğer çalışanlara SADECE mesai saatlerini ata (Şube adı silindi)
        aktifler = [p for p in personeller if p != izinli_p]
        random.shuffle(aktifler)
        for m_idx, p in enumerate(aktifler):
            # Sadece saati yazıyoruz
            matris[p][gun] = mesai_saatleri[m_idx % len(mesai_saatleri)]
            
    return pd.DataFrame(matris).T

# --- ANA EKRAN ---
if st.sidebar.button("🚀 Vardiyaları Oluştur"):
    st.session_state['s1_df'] = vardiya_hesapla(s1_personel)
    st.session_state['s2_df'] = vardiya_hesapla(s2_personel)
    st.session_state['s3_df'] = vardiya_hesapla(s3_personel)
    st.success("Taslaklar oluşturuldu!")

# Tabloları Sekmelerde Göster
if 's1_df' in st.session_state:
    tabs = st.tabs([f"📍 {s1_isim}", f"📍 {s2_isim}", f"📍 {s3_isim}"])
    
    with tabs[0]:
        st.subheader(f"{s1_isim} Çizelgesi")
        df1_final = st.data_editor(st.session_state['s1_df'], key="ed1", use_container_width=True)
        
    with tabs[1]:
        st.subheader(f"{s2_isim} Çizelgesi")
        df2_final = st.data_editor(st.session_state['s2_df'], key="ed2", use_container_width=True)
        
    with tabs[2]:
        st.subheader(f"{s3_isim} Çizelgesi")
        df3_final = st.data_editor(st.session_state['s3_df'], key="ed3", use_container_width=True)

    # Excel İndirme
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df1_final.to_excel(writer, sheet_name=s1_isim[:31])
        df2_final.to_excel(writer, sheet_name=s2_isim[:31])
        df3_final.to_excel(writer, sheet_name=s3_isim[:31])
    
    st.sidebar.markdown("---")
    st.sidebar.download_button(
        label="📥 Güncel Listeyi Excel İndir",
        data=buffer.getvalue(),
        file_name="nigde_vardiya_temiz_liste.xlsx",
        mime="application/vnd.ms-excel"
    )
else:
    st.info("Lütfen 'Vardiyaları Oluştur' butonuna basın.")
