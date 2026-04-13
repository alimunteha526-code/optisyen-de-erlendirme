import streamlit as st
import pandas as pd
import random
import io
from datetime import datetime, timedelta

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Niğde Şube Vardiya Paneli", layout="wide")

# --- YAZDIRMA (PDF) ÖZEL CSS ---
st.markdown("""
    <style>
    @media print {
        section[data-testid="stSidebar"], .stButton, header, .stTabs [data-baseweb="tab-list"], footer {
            display: none !important;
        }
        .main .block-container { padding: 0 !important; margin: 0 !important; }
    }
    </style>
""", unsafe_allow_html=True)

# --- TARİH HESAPLAMA FONKSİYONU ---
def haftalik_tarihleri_getir():
    bugun = datetime.now()
    pazartesi = bugun - timedelta(days=bugun.weekday())
    
    gun_isimleri = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
    tarihli_basliklar = []
    
    for i in range(7):
        gun_tarihi = pazartesi + timedelta(days=i)
        formatli_tarih = gun_tarihi.strftime('%d.%m.%Y')
        tarihli_basliklar.append(f"{gun_isimleri[i]} ({formatli_tarih})")
    
    return tarihli_basliklar

tarihli_gunler = haftalik_tarihleri_getir()
kapanis_saati = "14:30 - 23:00"
diger_saatler = ["05:30 - 14:00", "07:30 - 16:00", "13:30 - 22:00"]

st.title("📅 Tarihli Şube Vardiya Sistemi")
st.info(f"Bu çizelge **{tarihli_gunler[0]}** ile **{tarihli_gunler[-1]}** arasını kapsamaktadır.")

# --- YAN MENÜ ---
st.sidebar.header("🏢 Şube ve Personel")
s1_isim = st.sidebar.text_input("1. Şube Adı:", "Niğde 1")
s1_p = st.sidebar.text_area(f"{s1_isim} Personelleri:", "Ahmet, Ayşe, Mehmet, Fatma")

s2_isim = st.sidebar.text_input("2. Şube Adı:", "Niğde 2")
s2_p = st.sidebar.text_area(f"{s2_isim} Personelleri:", "Can, Ece, Ali, Zeynep")

s3_isim = st.sidebar.text_input("3. Şube Adı:", "Niğde 3")
s3_p = st.sidebar.text_area(f"{s3_isim} Personelleri:", "Burak, Deniz, Selin, Mert")

def vardiya_olustur(p_listesi):
    personeller = [p.strip() for p in p_listesi.split(",") if p.strip()]
    if not personeller: return pd.DataFrame(columns=tarihli_gunler)
    
    matris = {p: {g: "" for g in tarihli_gunler} for p in personeller}
    # İzinler sadece hafta içi (ilk 5 gün)
    is_gunleri_tarihli = tarihli_gunler[:5]
    
    for idx, p in enumerate(personeller):
        matris[p][is_gunleri_tarihli[idx % 5]] = "İZİNLİ"
    
    for g in tarihli_gunler:
        aktifler = [p for p in personeller if matris[p][g] != "İZİNLİ"]
        random.shuffle(aktifler)
        if len(aktifler) > 0:
            matris[aktifler[0]][g] = kapanis_saati
            for m_idx, p in enumerate(aktifler[1:]):
                matris[p][g] = diger_saatler[m_idx % len(diger_saatler)]
                
    return pd.DataFrame(matris).T

# --- HESAPLA ---
st.sidebar.markdown("---")
if st.sidebar.button("🚀 Vardiyaları Hesapla", use_container_width=True):
    st.session_state['s1'] = vardiya_olustur(s1_p)
    st.session_state['s2'] = vardiya_olustur(s2_p)
    st.session_state['s3'] = vardiya_olustur(s3_p)

# --- TABLOLAR VE BUTONLAR ---
if 's1' in st.session_state:
    tabs = st.tabs([f"📍 {s1_isim}", f"📍 {s2_isim}", f"📍 {s3_isim}"])
    
    with tabs[0]:
        df1 = st.data_editor(st.session_state['s1'], key="d1", use_container_width=True)
    with tabs[1]:
        df2 = st.data_editor(st.session_state['s2'], key="d2", use_container_width=True)
    with tabs[2]:
        df3 = st.data_editor(st.session_state['s3'], key="d3", use_container_width=True)

    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Çıktı Al")

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

    if st.sidebar.button("📄 PDF Olarak İndir / Yazdır", use_container_width=True):
        st.components.v1.html("<script>window.print();</script>", height=0)
else:
    st.info("Lütfen sol menüdeki 'Vardiyaları Hesapla' butonuna basın.")
