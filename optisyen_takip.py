import streamlit as st
import pandas as pd
import random
import io

st.set_page_config(page_title="Niğde Şubeleri Personel Yönetimi", layout="wide")

st.title("📅 Şube Bazlı Haftalık Vardiya Sistemi")

# --- YAN MENÜ (AYARLAR) ---
st.sidebar.header("🏢 Şube ve Personel Tanımlama")

# Şube 1 Ayarları
s1_isim = st.sidebar.text_input("1. Şube Adı:", "Niğde 1")
s1_personel = st.sidebar.text_area(f"{s1_isim} Personelleri (Virgülle ayırın):", "Ahmet, Ayşe, Mehmet, Fatma")

# Şube 2 Ayarları
s2_isim = st.sidebar.text_input("2. Şube Adı:", "Niğde 2")
s2_personel = st.sidebar.text_area(f"{s2_isim} Personelleri (Virgülle ayırın):", "Can, Ece, Ali, Zeynep")

# Şube 3 Ayarları
s3_isim = st.sidebar.text_input("3. Şube Adı:", "Niğde 3")
s3_personel = st.sidebar.text_area(f"{s3_isim} Personelleri (Virgülle ayırın):", "Burak, Deniz, Selin, Mert")

gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
mesai_saatleri = ["05:30 - 14:00", "07:30 - 16:00", "13:30 - 22:00", "14:30 - 23:00"]

def vardiya_hesapla(p_listesi, s_adi):
    # Temiz liste oluştur
    personeller = [p.strip() for p in p_listesi.split(",") if p.strip()]
    if len(personeller) == 0:
        return None
    
    matris = {p: {g: "" for g in gunler} for p in personeller}
    
    # Hafta içi izin atama (Herkes 1 gün izinli)
    is_gunleri = gunler[:5]
    for p in personeller:
        izin_gunu = random.choice(is_gunleri)
        matris[p][izin_gunu] = "İZİNLİ"
        
    # Vardiya saatlerini dağıt
    for g in gunler:
        aktifler = [p for p in personeller if matris[p][g] != "İZİNLİ"]
        random.shuffle(aktifler)
        for idx, p in enumerate(aktifler):
            # Saatleri döngüsel ata (05:30, 07:30 vb.)
            saat = mesai_saatleri[idx % len(mesai_saatleri)]
            matris[p][g] = f"{s_adi} ({saat})"
            
    return pd.DataFrame(matris).T

# --- ANA EKRAN ---
if st.sidebar.button("🚀 Tüm Şubelerin Vardiyasını Oluştur"):
    st.session_state['s1_df'] = vardiya_hesapla(s1_personel, s1_isim)
    st.session_state['s2_df'] = vardiya_hesapla(s2_personel, s2_isim)
    st.session_state['s3_df'] = vardiya_hesapla(s3_personel, s3_isim)
    st.success("Tüm şubeler için vardiyalar başarıyla oluşturuldu!")

# Tabloları Sekmelerde Göster
if 's1_df' in st.session_state:
    tabs = st.tabs([f"📍 {s1_isim}", f"📍 {s2_isim}", f"📍 {s3_isim}"])
    
    with tabs[0]:
        st.subheader(f"{s1_isim} Personel Bazlı Çizelge")
        st.table(st.session_state['s1_df'])
        
    with tabs[1]:
        st.subheader(f"{s2_isim} Personel Bazlı Çizelge")
        st.table(st.session_state['s2_df'])
        
    with tabs[2]:
        st.subheader(f"{s3_isim} Personel Bazlı Çizelge")
        st.table(st.session_state['s3_df'])

    # Excel İndirme
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        st.session_state['s1_df'].to_excel(writer, sheet_name=s1_isim[:30])
        st.session_state['s2_df'].to_excel(writer, sheet_name=s2_isim[:30])
        st.session_state['s3_df'].to_excel(writer, sheet_name=s3_isim[:30])
    
    st.sidebar.markdown("---")
    st.sidebar.download_button(
        label="📥 Tüm Şubeleri Excel İndir",
        data=buffer.getvalue(),
        file_name="sube_bazli_vardiya.xlsx",
        mime="application/vnd.ms-excel"
    )
else:
    st.info("Lütfen yan menüden şube isimlerini ve personellerini girip 'Vardiya Oluştur' butonuna basın.")
