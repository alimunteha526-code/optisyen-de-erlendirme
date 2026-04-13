import streamlit as st
import pandas as pd
import random
import io
import base64

st.set_page_config(page_title="Niğde Şube Vardiya Paneli", layout="wide")

# --- CSS: Yazdırma Esnasında Menüleri Gizle ---
st.markdown("""
    <style>
    @media print {
        .stSidebar, .stButton, header, .stTabs [data-baseweb="tab-list"] {
            display: none !important;
        }
        .main .block-container {
            padding: 0 !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.title("📅 Profesyonel Şube Vardiya Sistemi")

# --- YAN MENÜ ---
st.sidebar.header("🏢 Şube ve Personel")
s1_isim = st.sidebar.text_input("1. Şube Adı:", "Niğde 1")
s1_p = st.sidebar.text_area(f"{s1_isim} Personelleri:", "Ahmet, Ayşe, Mehmet, Fatma")

s2_isim = st.sidebar.text_input("2. Şube Adı:", "Niğde 2")
s2_p = st.sidebar.text_area(f"{s2_isim} Personelleri:", "Can, Ece, Ali, Zeynep")

s3_isim = st.sidebar.text_input("3. Şube Adı:", "Niğde 3")
s3_p = st.sidebar.text_area(f"{s3_isim} Personelleri:", "Burak, Deniz, Selin, Mert")

gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
mesai_saatleri = ["05:30 - 14:00", "07:30 - 16:00", "13:30 - 22:00", "14:30 - 23:00"]

def vardiya_uret(p_listesi):
    personeller = [p.strip() for p in p_listesi.split(",") if p.strip()]
    if len(personeller) < 4: return pd.DataFrame(columns=gunler)
    
    matris = {p: {g: "" for g in gunler} for p in personeller}
    is_gunleri = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
    random.shuffle(is_gunleri)
    
    for idx, p in enumerate(personeller):
        matris[p][is_gunleri[idx % 5]] = "İZİNLİ"
        
    for g in gunler:
        aktifler = [p for p in personeller if matris[p][g] != "İZİNLİ"]
        random.shuffle(aktifler)
        for m_idx, p in enumerate(aktifler):
            matris[p][g] = mesai_saatleri[m_idx % 4]
    return pd.DataFrame(matris).T

if st.sidebar.button("🚀 Vardiyaları Oluştur", use_container_width=True):
    st.session_state['s1'] = vardiya_uret(s1_p)
    st.session_state['s2'] = vardiya_uret(s2_p)
    st.session_state['s3'] = vardiya_uret(s3_p)

if 's1' in st.session_state:
    tabs = st.tabs([f"📍 {s1_isim}", f"📍 {s2_isim}", f"📍 {s3_isim}"])
    
    with tabs[0]:
        df1 = st.data_editor(st.session_state['s1'], key="e1", use_container_width=True)
    with tabs[1]:
        df2 = st.data_editor(st.session_state['s2'], key="e2", use_container_width=True)
    with tabs[2]:
        df3 = st.data_editor(st.session_state['s3'], key="e3", use_container_width=True)

    # --- İNDİRME BÖLÜMÜ ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Çıktı Yönetimi")

    # 1. EXCEL İNDİR
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        for name, df in [(s1_isim, df1), (s2_isim, df2), (s3_isim, df3)]:
            df.to_excel(writer, sheet_name=name[:30])
    
    st.sidebar.download_button(
        label="📊 Excel Dosyasını İndir",
        data=buffer.getvalue(),
        file_name="vardiya_listesi.xlsx",
        mime="application/vnd.ms-excel",
        use_container_width=True
    )

    # 2. PDF YAZDIR BUTONU (Tek Tıkla Yazdırma Ekranını Açar)
    if st.sidebar.button("🖨️ PDF / Yazdır (Tek Tık)", use_container_width=True):
        st.markdown("<script>window.print();</script>", unsafe_allow_html=True)
    
    st.sidebar.caption("💡 Butona bastığınızda yazdırma ekranı otomatik açılacaktır.")

else:
    st.info("Lütfen personelleri girip 'Vardiyaları Oluştur' butonuna basın.")
