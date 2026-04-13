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
sabah_vardiyasi = "05:30 - 14:00"
kapanis_vardiyasi = "14:30 - 23:00"
ara_vardiyalar = ["07:30 - 16:00", "13:30 - 22:00"]
tum_saatler = [sabah_vardiyasi, kapanis_vardiyasi] + ara_vardiyalar

st.title("📅 Operasyonel Kurallı Vardiya Sistemi")
st.success("✅ Kural Uygulandı: İzin öncesi 05:30, İzin dönüşü 14:30 sabitlemesi aktif.")

# --- YAN MENÜ ---
st.sidebar.header("🏢 Şube ve Personel")
s1_isim = st.sidebar.text_input("1. Şube Adı:", "Niğde 1")
s1_p = st.sidebar.text_area(f"{s1_isim} Personelleri:", "Ahmet, Ayşe, Mehmet, Fatma")

s2_isim = st.sidebar.text_input("2. Şube Adı:", "Niğde 2")
s2_p = st.sidebar.text_area(f"{s2_isim} Personelleri:", "Can, Ece, Ali, Zeynep")

s3_isim = st.sidebar.text_input("3. Şube Adı:", "Niğde 3")
s3_p = st.sidebar.text_area(f"{s3_isim} Personelleri:", "Burak, Deniz, Selin, Mert")

# --- AKILLI VARDİYA MOTORU ---
def akilli_vardiya_olustur(p_listesi):
    personeller = [p.strip() for p in p_listesi.split(",") if p.strip()]
    if not personeller: return pd.DataFrame(columns=tarihli_gunler)
    
    matris = {p: {g: "" for g in tarihli_gunler} for p in personeller}
    sayac = {p: {v: 0 for v in tum_saatler} for p in personeller}

    # 1. İzinleri ve Özel Kuralları Belirle (Hafta içi izinler)
    for idx, p in enumerate(personeller):
        izin_index = idx % 5 # Pazartesi-Cuma arası her birine farklı gün
        matris[p][tarihli_gunler[izin_index]] = "İZİNLİ"
        
        # İzin öncesi kuralı (Pazar izinli değilse, izinden önceki gün sabah gel)
        if izin_index > 0:
            matris[p][tarihli_gunler[izin_index-1]] = sabah_vardiyasi
            sayac[p][sabah_vardiyasi] += 1
            
        # İzin dönüşü kuralı (İzinden sonraki gün kapanış gel)
        if izin_index < 6:
            matris[p][tarihli_gunler[izin_index+1]] = kapanis_vardiyasi
            sayac[p][kapanis_vardiyasi] += 1

    # 2. Kalan Boşlukları Eşit Dağıt
    for g in tarihli_gunler:
        aktifler = [p for p in personeller if matris[p][g] == ""]
        # O gün için zaten atanmış vardiyaları çıkar (Kuraldan gelenler)
        atanmislar = [matris[p][g] for p in personeller if matris[p][g] not in ["", "İZİNLİ"]]
        
        kalan_vardiyalar = tum_saatler.copy()
        for v in atanmislar:
            if v in kalan_vardiyalar: kalan_vardiyalar.remove(v)
            
        random.shuffle(aktifler)
        for p in aktifler:
            if not kalan_vardiyalar: break # Vardiya biterse (personel > vardiya durumu)
            
            # Personelin en az yaptığı vardiyayı seç
            kalan_vardiyalar.sort(key=lambda v: sayac[p][v])
            secilen = kalan_vardiyalar.pop(0)
            matris[p][g] = secilen
            sayac[p][secilen] += 1
                
    return pd.DataFrame(matris).T

# --- HESAPLA ---
st.sidebar.markdown("---")
if st.sidebar.button("🚀 Kurallara Göre Hesapla", use_container_width=True):
    st.session_state['s1'] = akilli_vardiya_olustur(s1_p)
    st.session_state['s2'] = akilli_vardiya_olustur(s2_p)
    st.session_state['s3'] = akilli_vardiya_olustur(s3_p)

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
        df1.to_excel(writer, sheet_name=s1_isim[:30]); df2.to_excel(writer, sheet_name=s2_isim[:30]); df3.to_excel(writer, sheet_name=s3_isim[:30])
    st.sidebar.download_button(label="📊 Excel Olarak İndir", data=buffer.getvalue(), file_name="kural_vardiya.xlsx", use_container_width=True)

    # PDF
    if st.sidebar.button("📄 PDF Olarak İndir / Yazdır", use_container_width=True):
        st.components.v1.html("<script>window.print();</script>", height=0)
else:
    st.info("Lütfen sol menüdeki butona basarak kurallı dağıtımı başlatın.")
