import streamlit as st
import pandas as pd
import random
import io

st.set_page_config(page_title="Niğde Şubeleri Personel Yönetimi", layout="wide")

st.title("📅 Hafta Sonu İzin Olmayan Vardiya Sistemi")
st.markdown("Hafta sonu herkes çalışır, personeller hafta içi (Pzt-Cum) birer gün izin kullanır.")

# --- YAN MENÜ (AYARLAR) ---
st.sidebar.header("🏢 Şube ve Personel Tanımlama")

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
    
    # 1. HAFTA İÇİ İZİN ATAMA (Pzt-Cum)
    # Her personeli hafta içi rastgele farklı bir güne izinli atayalım
    is_gunleri = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
    random.shuffle(is_gunleri)
    
    for idx, p in enumerate(personeller):
        # Eğer personel sayısı 4 ise, hafta içi 5 günden 4'ü izinle dolar. 
        # Herkesin 1 gün izinli olmasını garanti eder.
        izin_gunu = is_gunleri[idx % len(is_gunleri)]
        matris[p][izin_gunu] = "İZİNLİ"
        
    # 2. MESAİ SAATLERİNİ DAĞITMA
    for g in gunler:
        aktifler = [p for p in personeller if matris[p][g] != "İZİNLİ"]
        random.shuffle(aktifler)
        
        for m_idx, p in enumerate(aktifler):
            # Hafta sonu herkes aktif olduğu için mesai saatleri döngüsel atanır
            matris[p][g] = mesai_saatleri[m_idx % len(mesai_saatleri)]
            
    return pd.DataFrame(matris).T

# --- ANA EKRAN ---
if st.sidebar.button("🚀 Hafta Sonu Çalışmalı Vardiya Oluştur"):
    st.session_state['s1_df'] = vardiya_hesapla(s1_personel)
    st.session_state['s2_df'] = vardiya_hesapla(s2_personel)
    st.session_state['s3_df'] = vardiya_hesapla(s3_personel)
    st.success("Vardiyalar hafta sonu tam kadro olacak şekilde oluşturuldu!")

# Sekmelerde Düzenlenebilir Tablolar
if 's1_df' in st.session_state:
    tabs = st.tabs([f"📍 {s1_isim}", f"📍 {s2_isim}", f"📍 {s3_isim}"])
    
    with tabs[0]:
        st.subheader(f"{s1_isim} Haftalık Çizelge")
        df1_final = st.data_editor(st.session_state['s1_df'], key="ed1_hs", use_container_width=True)
        
    with tabs[1]:
        st.subheader(f"{s2_isim} Haftalık Çizelge")
        df2_final = st.data_editor(st.session_state['s2_df'], key="ed2_hs", use_container_width=True)
        
    with tabs[2]:
        st.subheader(f"{s3_isim} Haftalık Çizelge")
        df3_final = st.data_editor(st.session_state['s3_df'], key="ed3_hs", use_container_width=True)

    # Excel Çıktısı
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df1_final.to_excel(writer, sheet_name=s1_isim[:31])
        df2_final.to_excel(writer, sheet_name=s2_isim[:31])
        df3_final.to_excel(writer, sheet_name=s3_isim[:31])
    
    st.sidebar.markdown("---")
    st.sidebar.download_button(
        label="📥 Güncel Listeyi Excel İndir",
        data=buffer.getvalue(),
        file_name="nigde_haftasonu_mesai_listesi.xlsx",
        mime="application/vnd.ms-excel"
    )
else:
    st.info("Lütfen yan menüden 'Vardiya Oluştur' butonuna basın.")
