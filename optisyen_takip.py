import streamlit as st
import pandas as pd
import random
import io
import base64

st.set_page_config(page_title="Niğde Şube Vardiya Paneli", layout="wide")

st.title("📅 Profesyonel Şube Vardiya Yönetimi")
st.markdown("""
**Kullanım Klavuzu:**
1. Yan menüden personel isimlerini virgülle ayırarak girin.
2. 'Vardiyaları Oluştur' butonuna basın.
3. Tablo üzerinde istediğiniz değişikliği **çift tıklayarak** yapın.
4. Çıktı almak için **Excel** veya **PDF (Yazdır)** butonlarını kullanın.
""")

# --- AYARLAR ---
st.sidebar.header("🏢 Şube ve Personel")
s1_isim = st.sidebar.text_input("1. Şube Adı:", "Niğde 1")
s1_personel = st.sidebar.text_area(f"{s1_isim} Personelleri (4 kişi):", "Ahmet, Ayşe, Mehmet, Fatma")

s2_isim = st.sidebar.text_input("2. Şube Adı:", "Niğde 2")
s2_personel = st.sidebar.text_area(f"{s2_isim} Personelleri:", "Can, Ece, Ali, Zeynep")

s3_isim = st.sidebar.text_input("3. Şube Adı:", "Niğde 3")
s3_personel = st.sidebar.text_area(f"{s3_isim} Personelleri:", "Burak, Deniz, Selin, Mert")

gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
mesai_saatleri = ["05:30 - 14:00", "07:30 - 16:00", "13:30 - 22:00", "14:30 - 23:00"]

def vardiya_uret(p_listesi):
    personeller = [p.strip() for p in p_listesi.split(",") if p.strip()]
    if len(personeller) < 4: return pd.DataFrame(columns=gunler)
    
    matris = {p: {g: "" for g in gunler} for p in personeller}
    is_gunleri = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
    random.shuffle(is_gunleri)
    
    # Hafta içi 1 kişi izinli (Döngüsel)
    for idx, p in enumerate(personeller):
        matris[p][is_gunleri[idx % 5]] = "İZİNLİ"
        
    for g in gunler:
        aktifler = [p for p in personeller if matris[p][g] != "İZİNLİ"]
        random.shuffle(aktifler)
        for m_idx, p in enumerate(aktifler):
            matris[p][g] = mesai_saatleri[m_idx % 4]
    return pd.DataFrame(matris).T

# --- ÇALIŞTIRMA ---
if st.sidebar.button("🚀 Vardiyaları Oluştur"):
    st.session_state['s1'] = vardiya_uret(s1_personel)
    st.session_state['s2'] = vardiya_uret(s2_personel)
    st.session_state['s3'] = vardiya_uret(s3_personel)

if 's1' in st.session_state:
    tabs = st.tabs([f"📍 {s1_isim}", f"📍 {s2_isim}", f"📍 {s3_isim}"])
    
    with tabs[0]:
        df1 = st.data_editor(st.session_state['s1'], key="edit_s1", use_container_width=True)
    with tabs[1]:
        df2 = st.data_editor(st.session_state['s2'], key="edit_s2", use_container_width=True)
    with tabs[2]:
        df3 = st.data_editor(st.session_state['s3'], key="edit_s3", use_container_width=True)

    # --- PDF (Yazdır) Butonu ---
    # Tarayıcıyı tetikleyerek doğrudan PDF yazdırma penceresini açar
    st.sidebar.markdown("---")
    if st.sidebar.button("📄 Sayfayı PDF Olarak Yazdır"):
        st.markdown('<script>window.print();</script>', unsafe_allow_html=True)
        st.sidebar.info("Açılan pencerede 'PDF Olarak Kaydet' seçeneğini seçin.")

    # --- EXCEL İNDİRME ---
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df1.to_excel(writer, sheet_name=s1_isim[:30])
        df2.to_excel(writer, sheet_name=s2_isim[:30])
        df3.to_excel(writer, sheet_name=s3_isim[:30])
    
    st.sidebar.download_button(
        label="📥 Tüm Şubeleri Excel İndir",
        data=buffer.getvalue(),
        file_name="sube_vardiya_listesi.xlsx",
        mime="application/vnd.ms-excel"
    )

else:
    st.info("Lütfen personelleri girip 'Vardiyaları Oluştur' butonuna basın.")
