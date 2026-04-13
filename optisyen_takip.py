import streamlit as st
import pandas as pd
import random
import io
import base64

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Niğde Şube Vardiya Paneli", layout="wide")

# --- YAZDIRMA (PDF) İÇİN ÖZEL CSS ---
# Bu kod, yazdır butonuna basıldığında menüleri gizler ve sadece tabloyu bırakır.
st.markdown("""
    <style>
    @media print {
        section[data-testid="stSidebar"], 
        .stButton, 
        header, 
        .stTabs [data-baseweb="tab-list"] {
            display: none !important;
        }
        .main .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.title("📅 Profesyonel Şube Vardiya Sistemi")
st.markdown("Tabloları düzenlemek için hücrelere çift tıklayın. Çıktı almak için sol menüyü kullanın.")

# --- YAN MENÜ AYARLARI ---
st.sidebar.header("🏢 Şube ve Personel Tanımlama")

s1_isim = st.sidebar.text_input("1. Şube Adı:", "Niğde 1")
s1_p = st.sidebar.text_area(f"{s1_isim} Personelleri:", "Ahmet, Ayşe, Mehmet, Fatma")

s2_isim = st.sidebar.text_input("2. Şube Adı:", "Niğde 2")
s2_p = st.sidebar.text_area(f"{s2_isim} Personelleri:", "Can, Ece, Ali, Zeynep")

s3_isim = st.sidebar.text_input("3. Şube Adı:", "Niğde 3")
s3_p = st.sidebar.text_area(f"{s3_isim} Personelleri:", "Burak, Deniz, Selin, Mert")

gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
mesai_saatleri = ["05:30 - 14:00", "07:30 - 16:00", "13:30 - 22:00", "14:30 - 23:00"]

# --- VARDİYA MOTORU ---
def vardiya_uret(p_listesi):
    personeller = [p.strip() for p in p_listesi.split(",") if p.strip()]
    if len(personeller) < 4:
        return pd.DataFrame(columns=gunler)
    
    matris = {p: {g: "" for g in gunler} for p in personeller}
    
    # 1. Hafta İçi İzin Atama (Pzt-Cum) - Herkes 1 gün izinli
    is_gunleri = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma"]
    random.shuffle(is_gunleri)
    
    for idx, p in enumerate(personeller):
        izin_gunu = is_gunleri[idx % 5]
        matris[p][izin_gunu] = "İZİNLİ"
        
    # 2. Mesai Saatlerini Dağıtma (Hafta sonu herkes çalışır)
    for g in gunler:
        aktifler = [p for p in personeller if matris[p][g] != "İZİNLİ"]
        random.shuffle(aktifler)
        for m_idx, p in enumerate(aktifler):
            # Şube adı olmadan sadece saat yazılır
            matris[p][g] = mesai_saatleri[m_idx % 4]
            
    return pd.DataFrame(matris).T

# --- HESAPLAMA TETİKLEYİCİ ---
if st.sidebar.button("🚀 Vardiyaları Oluştur", use_container_width=True):
    st.session_state['s1'] = vardiya_uret(s1_p)
    st.session_state['s2'] = vardiya_uret(s2_p)
    st.session_state['s3'] = vardiya_uret(s3_p)

# --- ANA EKRAN TABLOLAR ---
if 's1' in st.session_state:
    tabs = st.tabs([f"📍 {s1_isim}", f"📍 {s2_isim}", f"📍 {s3_isim}"])
    
    with tabs[0]:
        st.subheader(f"{s1_isim} Haftalık Çizelge")
        df1 = st.data_editor(st.session_state['s1'], key="edit_s1", use_container_width=True)
    with tabs[1]:
        st.subheader(f"{s2_isim} Haftalık Çizelge")
        df2 = st.data_editor(st.session_state['s2'], key="edit_s2", use_container_width=True)
    with tabs[2]:
        st.subheader(f"{s3_isim} Haftalık Çizelge")
        df3 = st.data_editor(st.session_state['s3'], key="edit_s3", use_container_width=True)

    # --- ÇIKTI YÖNETİMİ ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Çıktı Al")

    # 1. Excel İndir
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df1.to_excel(writer, sheet_name=s1_isim[:30])
        df2.to_excel(writer, sheet_name=s2_isim[:30])
        df3.to_excel(writer, sheet_name=s3_isim[:30])
    
    st.sidebar.download_button(
        label="📊 Excel Dosyasını İndir",
        data=buffer.getvalue(),
        file_name="sube_vardiya_listesi.xlsx",
        mime="application/vnd.ms-excel",
        use_container_width=True
    )

    # 2. PDF Yazdır (Otomatik Pencere Açar)
    if st.sidebar.button("📄 PDF Olarak İndir / Yazdır", use_container_width=True):
        # JavaScript ile yazdırma penceresini tetikler
        st.components.v1.html("<script>window.print();</script>", height=0)
    
    st.sidebar.caption("💡 PDF için açılan pencerede 'PDF Kaydet' seçeneğini kullanın.")

else:
    st.info("Lütfen personelleri girip 'Vardiyaları Oluştur' butonuna basın.")
