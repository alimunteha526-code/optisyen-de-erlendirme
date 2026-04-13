import streamlit as st
import pandas as pd
import random
import io
import json
from datetime import datetime, timedelta

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Furkan Baysak Shift Paneli", layout="wide")

# --- YAZDIRMA (PDF) ÖZEL CSS ---
st.markdown("""
    <style>
    @media print {
        section[data-testid="stSidebar"], .stButton, header, .stTabs [data-baseweb="tab-list"], footer {
            display: none !important;
        }
        .main .block-container { padding: 0 !important; margin: 0 !important; }
        h1 { text-align: center; color: black !important; }
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

st.title("🎂 Niğde Furkan Baysak Pastaneleri Shift Programı")

# --- YAN MENÜ ---
st.sidebar.header("🏢 Şube ve Personel Yönetimi")
s1_isim = st.sidebar.text_input("1. Şube Adı:", "Furkan Baysak Şube 1")
s1_p = st.sidebar.text_area(f"{s1_isim} Ekibi:", "Ahmet, Ayşe, Mehmet, Fatma")

s2_isim = st.sidebar.text_input("2. Şube Adı:", "Furkan Baysak Şube 2")
s2_p = st.sidebar.text_area(f"{s2_isim} Ekibi:", "Can, Ece, Ali, Zeynep")

s3_isim = st.sidebar.text_input("3. Şube Adı:", "Furkan Baysak Şube 3")
s3_p = st.sidebar.text_area(f"{s3_isim} Ekibi:", "Burak, Deniz, Selin, Mert")

# --- SHIFT MOTORU ---
def shift_olustur(p_listesi):
    personeller = [p.strip() for p in p_listesi.split(",") if p.strip()]
    if not personeller: return pd.DataFrame(columns=tarihli_gunler)
    
    matris = {p: {g: "" for g in tarihli_gunler} for p in personeller}
    sayac = {p: {v: 0 for v in tum_saatler} for p in personeller}

    for idx, p in enumerate(personeller):
        izin_gun_idx = idx % 5 
        matris[p][tarihli_gunler[izin_gun_idx]] = "İZİNLİ"
        
        onceki_gun_idx = (izin_gun_idx - 1) % 7
        if matris[p][tarihli_gunler[onceki_gun_idx]] == "":
            matris[p][tarihli_gunler[onceki_gun_idx]] = sabah_vardiyasi
            sayac[p][sabah_vardiyasi] += 1
            
        sonraki_gun_idx = (izin_gun_idx + 1) % 7
        if matris[p][tarihli_gunler[sonraki_gun_idx]] == "":
            matris[p][tarihli_gunler[sonraki_gun_idx]] = kapanis_vardiyasi
            sayac[p][kapanis_vardiyasi] += 1

    for g in tarihli_gunler:
        aktifler = [p for p in personeller if matris[p][g] == ""]
        random.shuffle(aktifler)
        atanmis_vardiyalar = [matris[p][g] for p in personeller if matris[p][g] not in ["", "İZİNLİ"]]
        kalan_vardiyalar = [v for v in tum_saatler if v not in atanmis_vardiyalar] or tum_saatler.copy()

        for p in aktifler:
            if not kalan_vardiyalar: break
            kalan_vardiyalar.sort(key=lambda v: sayac[p][v])
            secilen = kalan_vardiyalar.pop(0)
            matris[p][g] = secilen
            sayac[p][secilen] += 1
    return pd.DataFrame(matris).T

# --- KAYIT VE YÜKLEME BUTONLARI ---
st.sidebar.markdown("---")
if st.sidebar.button("🚀 Yeni Shift Hazırla", use_container_width=True):
    st.session_state['s1'] = shift_olustur(s1_p)
    st.session_state['s2'] = shift_olustur(s2_p)
    st.session_state['s3'] = shift_olustur(s3_p)
    st.toast("Yeni shift oluşturuldu!")

if st.sidebar.button("🗑️ Verileri Sıfırla", use_container_width=True):
    for key in ['s1', 's2', 's3']:
        if key in st.session_state: del st.session_state[key]
    st.rerun()

# --- GÖSTERİM ---
if 's1' in st.session_state:
    tabs = st.tabs([f"📍 {s1_isim}", f"📍 {s2_isim}", f"📍 {s3_isim}"])
    with tabs[0]: df1 = st.data_editor(st.session_state['s1'], key="f1", use_container_width=True)
    with tabs[1]: df2 = st.data_editor(st.session_state['s2'], key="f2", use_container_width=True)
    with tabs[2]: df3 = st.data_editor(st.session_state['s3'], key="f3", use_container_width=True)

    # Değişiklikleri Kaydet
    st.session_state['s1'] = df1
    st.session_state['s2'] = df2
    st.session_state['s3'] = df3

    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Çıktı Seçenekleri")
    
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df1.to_excel(writer, sheet_name=s1_isim[:30]); df2.to_excel(writer, sheet_name=s2_isim[:30]); df3.to_excel(writer, sheet_name=s3_isim[:30])
    st.sidebar.download_button(label="📊 Excel Dosyası Al", data=buffer.getvalue(), file_name="Furkan_Baysak_Shift.xlsx", use_container_width=True)

    if st.sidebar.button("📄 PDF / Yazdır", use_container_width=True):
        st.components.v1.html("<script>window.print();</script>", height=0)
else:
    st.info("Kayıtlı shift bulunamadı. Sol menüden 'Yeni Shift Hazırla' butonuna basın.")
