import streamlit as st
import pandas as pd
import os

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

# --- ÜST PANEL VE İSTATİSTİK ---
st.title("👓 Teknik Takip Sistemi")

if not df.empty:
    toplam_kisi = df["Optisyen Adı"].nunique()
    st.markdown(f"""
        <div style="background-color:#E8F0FE; padding:15px; border-radius:12px; border-left: 8px solid #1A73E8; margin-bottom: 20px;">
            <p style="margin:0; font-size:0.9rem; font-weight:bold; color:#5f6368;">İÇ ANADOLU</p>
            <h1 style="margin:0; color:#1A73E8; font-size:2.2rem;">Toplam Optisyen Sayısı: {toplam_kisi}</h1>
        </div>
    """, unsafe_allow_html=True)

    # --- BUTONLU MAĞAZA DAĞILIMI (YENİ) ---
    if st.button("🏬 Mağaza Bazlı Dağılımı Göster / Gizle"):
        st.subheader("📍 Mağaza Bazlı Personel Sayıları")
        dagilim = df.groupby("Mağaza")["Optisyen Adı"].nunique().reset_index()
        dagilim.columns = ["Mağaza Adı", "Optisyen Sayısı"]
        dagilim = dagilim.sort_values(by="Optisyen Sayısı", ascending=False)
        
        # Grafik ve Tablo Yan Yana
        col_graf, col_tablo = st.columns([2, 1])
        with col_graf:
            st.bar_chart(dagilim.set_index("Mağaza Adı"))
        with col_tablo:
            st.table(dagilim)
        st.divider()

# --- DİĞER BÖLÜMLER ---
st.sidebar.header("👤 Yeni Kayıt")
with st.sidebar.form("yeni_personel"):
    isim = st.text_input("Ad Soyad")
    magaza = st.selectbox("Mağaza", options=MAGAZA_LISTESI)
    tarih = st.date_input("Tarih")
    if st.form_submit_button("Kaydet"):
        if isim:
            yeni = {"Tarih": str(tarih), "Optisyen Adı": turkce_buyuk(isim), "Mağaza": magaza, "Toplam Puan": 0}
            for m in ANKET_MADDELERİ: yeni[m] = "YAPILMADI"
            df = pd.concat([df, pd.DataFrame([yeni])], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.rerun()

tab_liste, tab_yonetim = st.tabs(["📋 Kayıt Listesi", "⚙️ Kayıt Yönetimi"])

with tab_liste:
    st.dataframe(df[["Tarih", "Optisyen Adı", "Mağaza", "Toplam Puan"]], use_container_width=True)

with tab_yonetim:
    if "edit_idx" not in st.session_state: st.session_state.edit_idx = None
    if st.session_state.edit_idx is not None:
        idx = st.session_state.edit_idx
        row = df.iloc[idx]
        with st.form("edit_form"):
            cevaplar = {}
            c1, c2 = st.columns(2)
            for i, m in enumerate(ANKET_MADDELERİ):
                col = c1 if i < 13 else c2
                current = row[m] if m in row else "YAPILMADI"
                cevaplar[m] = col.radio(m, ["İYİ", "ORTA", "ÇOK İYİ", "YAPILMADI"], index=["İYİ", "ORTA", "ÇOK İYİ", "YAPILMADI"].index(current), horizontal=True)
            if st.form_submit_button("Güncelle"):
                df.at[idx, "Toplam Puan"] = sum([PUAN_SISTEMI[v] for v in cevaplar.values()])
                for k, v in cevaplar.items(): df.at[idx, k] = v
                df.to_csv(DB_FILE, index=False)
                st.session_state.edit_idx = None
                st.rerun()
        if st.button("İptal"): st.session_state.edit_idx = None; st.rerun()
    else:
        for i, r in df.iterrows():
            col_ad, col_ed, col_sl = st.columns([3, 1, 1])
            col_ad.write(f"**{r['Optisyen Adı']}** ({r['Mağaza']})")
            if col_ed.button("✏️ Düzenle", key=f"ed_{i}"):
                st.session_state.edit_idx = i
                st.rerun()
            if col_sl.button("🗑️ Sil", key=f"sl_{i}"):
                silme_onay_dialogu(i, r['Optisyen Adı'])
