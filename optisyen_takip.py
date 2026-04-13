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

# --- TARİH HESAPLAMA ---
def haftalik_tarihleri_getir():
    bugun = datetime.now()
    pazartesi = bugun - timedelta(days=bugun.weekday())
    gun_isimleri = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
    return [f"{gun_isimleri[i]} ({(pazartesi + timedelta(days=i)).strftime('%d.%m.%Y')})" for i in range(7)]

tarihli_gunler = haftalik_tarihleri_getir()
kapanis_saati = "14:30 - 23:00"
diger_saatler = ["05:30 - 14:00", "07:30 - 16:00", "13:30 - 22:00"]
tum_vardiyalar = [kapanis_saati] + diger_saatler

st.title("📅 Adil Vardiya Dağıtım Sistemi")
st.info("Sistem, her personelin tüm vardiya saatlerinden (sabah, ara, akşam) hafta boyunca eşit sayıda almasını sağlar.")

# --- YAN MENÜ ---
st.sidebar.header("🏢 Şube ve Personel")
s1_isim = st.sidebar.text_input("1. Şube Adı:", "Niğde 1")
s1_p = st.sidebar.text_area(f"{s1_isim} Personelleri:", "Ahmet, Ayşe, Mehmet, Fatma")

s2_isim = st.sidebar.text_input("2. Şube Adı:", "Niğde 2")
s2_p = st.sidebar.text_area(f"{s2_isim} Personelleri:", "Can, Ece, Ali, Zeynep")

s3_isim = st.sidebar.text_input("3. Şube Adı:", "Niğde 3")
s3_p = st.sidebar.text_area(f"{s3_isim} Personelleri:", "Burak, Deniz, Selin, Mert")

# --- ADİL VARDİYA MOTORU ---
def adil_vardiya_olustur(p_listesi):
    personeller = [p.strip() for p in p_listesi.split(",") if p.strip()]
    if not personeller: return pd.DataFrame(columns=tarihli_gunler)
    
    matris = {p: {g: "" for g in tarihli_gunler} for p in personeller}
    
    # Hafta içi izin ataması
    is_gunleri = tarihli_gunler[:5]
    for idx, p in enumerate(personeller):
        matris[p][is_gunleri[idx % 5]] = "İZİNLİ"

    # Her personel için vardiya kullanım sayacı
    # Örnek: {'Ahmet': {'14:30 - 23:00': 0, ...}}
    sayac = {p: {v: 0 for v in tum_vardiyalar} for p in personeller}

    for g in tarihli_gunler:
        aktifler = [p for p in personeller if matris[p][g] != "İZİNLİ"]
        gunluk_vardiyalar = tum_vardiyalar.copy()
        
        # O gün çalışacak her personel için en az kullanılan vardiyayı seçmeye çalış
        random.shuffle(aktifler) 
        for p in aktifler:
            # Mevcut vardiyaları, personelin daha önce kaç kez yaptığına göre sırala
            gunluk_vardiyalar.sort(key=lambda v: sayac[p][v])
            secilen_vardiya = gunluk_vardiyalar.pop(0)
            matris[p][g] = secilen_vardiya
            sayac[p][secilen_vardiya] += 1
                
    return pd.DataFrame(matris).T

# --- HESAPLA ---
st.sidebar.markdown("---")
if st.sidebar.button("🚀 Eşit Dağılımlı Hesapla", use_container_width=True):
    st.session_state['s1'] = adil_vardiya_olustur(s1_p)
    st.session_state['s2'] = adil_vardiya_olustur(s2_p)
    st.session_state['s3'] = adil_vardiya_olustur(s3_p)

# --- GÖSTERİM VE ÇIKTI ---
if 's1' in st.session_state:
    tabs = st.tabs([f"📍 {s1_isim}", f"📍 {s2_isim}", f"📍 {s3_isim}"])
    with tabs[0]: df1 = st.data_editor(st.session_state['s1'], key="d1", use_container_width=True)
    with tabs[1]: df2 = st.data_editor(st.session_state['s2'], key="d2", use_container_width=True)
    with tabs[2]: df3 = st.data_editor(st.session_state['s3'], key="d3", use_container_width=True)

    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Çıktı Al")

    # Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df1.to_excel(writer, sheet_name=s1_isim[:30])
        df2.to_excel(writer, sheet_name=s2_isim[:30])
        df3.to_excel(writer, sheet_name=s3_isim[:30])
    
    st.sidebar.download_button(label="📊 Excel Olarak İndir", data=buffer.getvalue(), 
                               file_name="esit_vardiya_listesi.xlsx", mime="application/vnd.ms-excel", use_container_width=True)

    # PDF
    if st.sidebar.button("📄 PDF Olarak İndir / Yazdır", use_container_width=True):
        st.components.v1.html("<script>window.print();</script>", height=0)
else:
    st.info("Lütfen sol menüdeki butona basarak adil dağıtımı başlatın.")
