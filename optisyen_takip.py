import streamlit as st
import pandas as pd
import os
from io import BytesIO

# --- AYARLAR VE VERİ TABANI ---
DB_FILE = "optisyen_teknik_veritabani.csv"

MAGAZA_LISTESI = [
    "KAYSERİ PARK AVM", "KAYSERİ MEYSU OUTLET AVM", "NOVADA KONYA OUTLET AVM",
    "FORUM KAYSERİ AVM", "NEVŞEHİR NİSSARA AVM", "MARAŞ PİAZZA AVM",
    "KONYA KENT PLAZA AVM", "M1 KONYA AVM", "KAYSERİ KUMSMALL AVM",
    "PARK KARAMAN AVM", "NİĞDE CADDE", "AKSARAY NORA CITY AVM",
    "KIRŞEHİR CADDE", "KAYSERİ TUNALIFE AVM", "KONYA KAZIMKARABEKİR CADDE",
    "KONYA ENNTEPE AVM"
]

ANKET_MADDELERİ = [
    "Tek odaklı montaj bilgisi.", "Çok odaklı montaj bilgisi.", "Stellests montaj bilgisi",
    "Faset montaj bilgisi.", "Kapalı çerçeve Nilör montaj bilgisi.",
    "Kanalı öne arkaya alma, polisaj, nilör derinlik ayarlama",
    "Metal çerçeve ayar bakım Kemik çerçeve ayar bakım",
    "Isıtıcı kullanımı, asetat ve enjeksiyon ayırımı", "Nilör çerçeve ayar bakım",
    "Üst ve alt kanal misina takma", "Gövde eğikliği tespit etme", "Faset çerçeve ayar bakım",
    "Pandoskopik, Retroskopik açı verme", "Rayban mineral cam çıkartma",
    "Destek ekranı kullanma bilgisi", "Zayi kodları bilgisi", "Eltaşı cam küçültme bilgisi",
    "Nilör makinası kullanım bilgisi", "El matkabı kullanım bilgisi",
    "Makina arızaları izlenecek adım bilgisi", "Makina ve atölye temizliği",
    "Makina kalibrasyon bilgisi ve tolerans tablosu", "Atölye malzemeleri kullanım alanları",
    "Uygun vida kullanımı", "Plaket takma geçmeli, vidalı"
]

PUAN_SISTEMI = {"İYİ": 1, "ORTA": 2, "ÇOK İYİ": 4}

def veriyi_yukle():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Tarih", "Optisyen Adı", "Mağaza", "Toplam Puan"])

st.set_page_config(page_title="Optisyen Teknik Değerlendirme", layout="wide")

def turkce_buyuk(metin):
    return metin.replace('i', 'İ').replace('ı', 'I').upper() if metin else ""

df = veriyi_yukle()

# --- ANA BAŞLIK ---
st.title("👓 Optisyen Teknik Değerlendirme Paneli")

# --- SOL PANEL: ANKET DOLDURMA ---
st.sidebar.header("📝 Yeni Teknik Anket")
with st.sidebar.form("anket_formu"):
    isim_input = st.text_input("Optisyen Adı Soyadı")
    magaza_input = st.selectbox("Mağaza", options=MAGAZA_LISTESI)
    tarih = st.date_input("Değerlendirme Tarihi")
    
    st.write("---")
    st.write("**Teknik Değerlendirme Maddeleri**")
    
    cevaplar = {}
    for madde in ANKET_MADDELERİ:
        cevaplar[madde] = st.radio(madde, options=["İYİ", "ORTA", "ÇOK İYİ"], horizontal=True)
    
    kaydet = st.form_submit_button("Anketi Tamamla ve Puanla")

if kaydet and isim_input:
    # Toplam Puan Hesaplama (1, 2, 4 üzerinden)
    toplam_puan = sum([PUAN_SISTEMI[c] for c in cevaplar.values()])
    
    yeni_kayit = {
        "Tarih": str(tarih),
        "Optisyen Adı": turkce_buyuk(isim_input),
        "Mağaza": magaza_input,
        "Toplam Puan": toplam_puan
    }
    
    df = pd.concat([df, pd.DataFrame([yeni_kayit])], ignore_index=True)
    df.to_csv(DB_FILE, index=False)
    st.sidebar.success(f"Anket Kaydedildi! Toplam Puan: {toplam_puan}")
    st.rerun()

# --- ANA SEKMELER ---
tab_liste, tab_istatistik, tab_yonetim = st.tabs(["📋 Kayıtlar", "📊 Mağaza Analizi", "⚙️ Düzenle/Sil"])

with tab_liste:
    st.subheader("📋 Teknik Değerlendirme Sonuçları")
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Henüz anket doldurulmadı.")

with tab_istatistik:
    if not df.empty:
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Mağaza Bazlı Ortalama Teknik Puan**")
            magaza_puan = df.groupby("Mağaza")["Toplam Puan"].mean()
            st.bar_chart(magaza_puan)
        with c2:
            st.write("**Personel Sayıları**")
            st.table(df.groupby("Mağaza")["Optisyen Adı"].nunique())
    else:
        st.warning("Veri bekleniyor...")

with tab_yonetim:
    for idx, r in df.iterrows():
        col_m, col_d = st.columns([4, 1])
        col_m.write(f"**{r['Optisyen Adı']}** | {r['Mağaza']} | Puan: {r['Toplam Puan']}")
        if col_d.button("🗑️ Sil", key=f"del_{idx}"):
            df.drop(idx).to_csv(DB_FILE, index=False)
            st.rerun()
