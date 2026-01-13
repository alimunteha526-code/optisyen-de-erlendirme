import streamlit as st
import pandas as pd
import os
from io import BytesIO

# --- AYARLAR VE VERİ TABANI ---
DB_FILE = "optisyen_teknik_veritabanı.csv"

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

PUAN_SISTEMI = {"İYİ": 1, "ORTA": 2, "ÇOK İYİ": 4, "YAPILMADI": 0}

def veriyi_yukle():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    cols = ["Tarih", "Optisyen Adı", "Mağaza", "Toplam Puan"] + ANKET_MADDELERİ
    return pd.DataFrame(columns=cols)

st.set_page_config(page_title="İç Anadolu Optisyen Yönetimi", layout="wide")

def turkce_buyuk(metin):
    return metin.replace('i', 'İ').replace('ı', 'I').upper() if metin else ""

df = veriyi_yukle()

# --- SİLME ONAY DİALOGU (ORTADA ÇIKAN PENCERE) ---
@st.dialog("Kayıt Silme Onayı")
def silme_onay_kutusu(index, isim):
    st.write(f"⚠️ **{isim}** isimli optisyenin tüm verileri kalıcı olarak silinecektir.")
    st.write("Bu işlemi onaylıyor musunuz?")
    col1, col2 = st.columns(2)
    if col1.button("✅ Evet, Sil", use_container_width=True):
        global df
        df = df.drop(index)
        df.to_csv(DB_FILE, index=False)
        st.success("Kayıt silindi!")
        st.rerun()
    if col2.button("❌ Vazgeç", use_container_width=True):
        st.rerun()

# --- DÜZENLEME MODU KONTROLÜ ---
if "active_edit_index" not in st.session_state:
    st.session_state.active_edit_index = None

# --- BAŞLIK VE İSTATİSTİK ---
st.title("👓 Teknik Takip Sistemi")
if not df.empty:
    toplam_kisi = df["Optisyen Adı"].nunique()
    st.markdown(f"""
        <div style="background-color:#E8F0FE; padding:20px; border-radius:15px; border-left: 10px solid #1A73E8; margin-bottom: 25px;">
            <span style="color:#5f6368; font-size:1rem; font-weight:bold;">İÇ ANADOLU</span>
            <h1 style="margin:0; color:#1A73E8; font-size:2.8rem;">Toplam Optisyen Sayısı: {toplam_kisi}</h1>
        </div>
    """, unsafe_allow_html=True)

# --- SOL PANEL: KAYIT ---
st.sidebar.header("👤 Personel Kaydı")
with st.sidebar.form("kayit_formu"):
    isim = st.text_input("Ad Soyad")
    magaza = st.selectbox("Mağaza", options=MAGAZA_LISTESI)
    tarih = st.date_input("Tarih")
    if st.form_submit_button("Sisteme Ekle"):
        if isim:
            yeni = {"Tarih": str(tarih), "Optisyen Adı": turkce_buyuk(isim), "Mağaza": magaza, "Toplam Puan": 0}
            for m in ANKET_MADDELERİ: yeni[m] = "YAPILMADI"
            df = pd.concat([df, pd.DataFrame([yeni])], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.rerun()

# --- ANA SEKMELER ---
tab_liste, tab_yonetim = st.tabs(["📋 Kayıt Listesi", "⚙️ Kayıt Yönetimi"])

with tab_liste:
    st.dataframe(df[["Tarih", "Optisyen Adı", "Mağaza", "Toplam Puan"]], use_container_width=True)

with tab_yonetim:
    if st.session_state.active_edit_index is not None:
        idx = st.session_state.active_edit_index
        row = df.iloc[idx]
        st.info(f"📝 {row['Optisyen Adı']} Anket Düzenleme")
        with st.form("duzenle_form"):
            cevaplar = {}
            c1, c2 = st.columns(2)
            for i, m in enumerate(ANKET_MADDELERİ):
                col = c1 if i < 13 else c2
                cevaplar[m] = col.radio(f"{m}", options=["İYİ", "ORTA", "ÇOK İYİ", "YAPILMADI"], 
                                        index=["İYİ", "ORTA", "ÇOK İYİ", "YAPILMADI"].index(row[m]), horizontal=True)
            if st.form_submit_button("Kaydet"):
                df.at[idx, "Toplam Puan"] = sum([PUAN_SISTEMI[v] for v in cevaplar.values()])
                for k, v in cevaplar.items(): df.at[idx, k] = v
                df.to_csv(DB_FILE, index=False)
                st.session_state.active_edit_index = None
                st.rerun()
        if st.button("İptal"):
            st.session_state.active_edit_index = None
            st.rerun()
    else:
        for i, r in df.iterrows():
            col_b, col_e, col_d = st.columns([3, 1, 1])
            col_b.write(f"**{r['Optisyen Adı']}** — {r['Mağaza']}")
            if col_e.button("✏️ Düzenle", key=f"e_{i}"):
                st.session_state.active_edit_index = i
                st.rerun()
            if col_d.button("🗑️ Sil", key=f"d_{i}"):
                silme_onay_kutusu(i, r['Optisyen Adı']) # ORTADA ÇIKAN UYARIYI ÇAĞIRIR
