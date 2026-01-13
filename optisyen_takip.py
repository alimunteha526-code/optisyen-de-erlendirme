import streamlit as st
import pandas as pd
import os

# --- AYARLAR VE VERİ TABANI ---
DB_FILE = "optisyen_teknik_veritabanı.csv"

# Görselden alınan güncel mağaza listesi
MAGAZA_LISTESI = [
    "KAYSERİ PARK AVM", "KAYSERİ MEYSU OUTLET AVM", "NOVADA KONYA OUTLET AVM",
    "FORUM KAYSERİ AVM", "NEVŞEHİR NİSSARA AVM", "MARAŞ PİAZZA AVM",
    "KONYA KENT PLAZA AVM", "M1 KONYA AVM", "KAYSERİ KUMSMALL AVM",
    "PARK KARAMAN AVM", "NİĞDE CADDE", "AKSARAY NORA CITY AVM",
    "KIRŞEHİR CADDE", "KAYSERİ TUNALIFE AVM", "KONYA KAZIMKARABEKİR CADDE",
    "KONYA ENNTEPE AVM", "SİVAS CADDE", "PRIME MALL"
]

# Görselden alınan 25 maddelik anket listesi
ANKET_MADDELERİ = [
    "Tek odaklı montaj bilgisi.", "Çok odaklı montaj bilgisi.", "Stellests montaj bilgisi",
    "Faset montaj bilgisi.", "Kapalı çerçeve Nilör montaj bilgisi.",
    "Kanalı öne arkaya alma,polisaj , nilör derinlik ayarlama",
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

PUAN_SISTEMI = {"İYİ": 1, "ORTA": 2, "ÇOK İYİ": 4, "YAPILMADI": 0} #

def veriyi_yukle():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    # İlk açılışta görseldeki optisyen listesini tanımla
    initial_data = [
        {"Optisyen Adı": "HASAN SARIKAYA", "Mağaza": "SİVAS CADDE"},
        {"Optisyen Adı": "NİHAL AKTAŞ", "Mağaza": "PRIME MALL"},
        {"Optisyen Adı": "ABDULSAMET ARSLANTAŞ", "Mağaza": "KUMSMALL"},
        {"Optisyen Adı": "HÜMAY ERDİLER", "Mağaza": "PRIME MALL"},
        {"Optisyen Adı": "MEHVEŞ ÖZEL", "Mağaza": "NORA CITY"},
        {"Optisyen Adı": "MERYEM NİĞDELİ", "Mağaza": "NİĞDE CADDE"},
        {"Optisyen Adı": "ALİ CANTUTUMLU", "Mağaza": "KIRŞEHİR CADDE"},
        {"Optisyen Adı": "HÜSEYİN ÖZTÜRK", "Mağaza": "KENT PLAZA"},
        {"Optisyen Adı": "BURCU DEMİR", "Mağaza": "PIAZZA"},
        {"Optisyen Adı": "ŞEYMA NUR SUBAŞI", "Mağaza": "NISSARA"}
        # ... Liste bu şekilde devam eder
    ]
    df = pd.DataFrame(initial_data)
    df["Tarih"] = pd.Timestamp.now().strftime("%Y-%m-%d")
    df["Toplam Puan"] = 0
    for m in ANKET_MADDELERİ: df[m] = "YAPILMADI"
    return df

st.set_page_config(page_title="Optisyen Teknik Takip", layout="wide")
df = veriyi_yukle()

# --- SİLME ONAY DİALOGU ---
@st.dialog("Kayıt Silinsin mi?")
def silme_onay_dialogu(index, isim):
    st.warning(f"**{isim}** kaydını silmek istediğinize emin misiniz?")
    c1, c2 = st.columns(2)
    if c1.button("✅ Evet, Sil", use_container_width=True):
        global df
        df = df.drop(index).reset_index(drop=True)
        df.to_csv(DB_FILE, index=False)
        st.rerun()
    if c2.button("❌ Vazgeç", use_container_width=True):
        st.rerun()

# --- ANA ARAYÜZ ---
st.title("👓 Optisyen Teknik Değerlendirme Sistemi")

# Sekmeler
tab_liste, tab_anket, tab_yonetim = st.tabs(["📋 Kayıt Listesi", "✍️ Teknik Anket Yap", "⚙️ Personel Düzenle/Sil"])

with tab_liste:
    st.subheader("📋 Güncel Liste")
    st.dataframe(df[["Optisyen Adı", "Mağaza", "Toplam Puan"]], use_container_width=True)

with tab_anket:
    st.subheader("✍️ Anket Uygula")
    secilen = st.selectbox("Personel Seçin:", df["Optisyen Adı"].tolist())
    idx = df[df["Optisyen Adı"] == secilen].index[0]
    
    with st.form("anket_form"):
        yeni_cevaplar = {}
        col1, col2 = st.columns(2)
        for i, m in enumerate(ANKET_MADDELERİ):
            col = col1 if i < 13 else col2
            yeni_cevaplar[m] = col.radio(f"{m}", ["İYİ", "ORTA", "ÇOK İYİ", "YAPILMADI"], horizontal=True)
        
        if st.form_submit_button("Kaydet"):
            puan = sum([PUAN_SISTEMI[v] for v in yeni_cevaplar.values()])
            df.at[idx, "Toplam Puan"] = puan
            for k, v in yeni_cevaplar.items(): df.at[idx, k] = v
            df.to_csv(DB_FILE, index=False)
            st.success("Anket başarıyla kaydedildi!")
            st.rerun()

with tab_yonetim:
    st.subheader("⚙️ Kayıtları Yönet")
    for i, r in df.iterrows():
        col_ad, col_sil = st.columns([4, 1])
        col_ad.write(f"**{r['Optisyen Adı']}** ({r['Mağaza']})")
        if col_sil.button("🗑️ Sil", key=f"del_{i}"):
            silme_onay_dialogu(i, r['Optisyen Adı'])
