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
    "KONYA ENNTEPE AVM", "SİVAS CADDE", "PRIME MALL"
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
df = veriyi_yukle()

# --- MODAL: SİLME ONAYI ---
@st.dialog("Kayıt Silinsin mi?")
def silme_onay_dialogu(index, isim):
    st.warning(f"⚠️ **{isim}** isimli optisyenin tüm verileri kalıcı olarak silinecektir.")
    c1, c2 = st.columns(2)
    if c1.button("✅ Evet, Sil", use_container_width=True):
        global df
        df = df.drop(index).reset_index(drop=True)
        df.to_csv(DB_FILE, index=False)
        st.success("Kayıt silindi!")
        st.rerun()
    if c2.button("❌ Vazgeç", use_container_width=True):
        st.rerun()

# --- ÜST BİLGİ PANELİ ---
st.title("👓 Optisyen Teknik Takip & Değerlendirme")
if not df.empty:
    toplam_kisi = df["Optisyen Adı"].nunique()
    st.markdown(f"""
        <div style="background-color:#E8F0FE; padding:15px; border-radius:12px; border-left: 8px solid #1A73E8; margin-bottom: 20px;">
            <p style="margin:0; font-size:0.9rem; font-weight:bold; color:#5f6368;">BÖLGE ÖZETİ</p>
            <h1 style="margin:0; color:#1A73E8; font-size:2.2rem;">Toplam Optisyen Sayısı: {toplam_kisi}</h1>
        </div>
    """, unsafe_allow_html=True)

# --- SOL PANEL: KAYIT İŞLEMLERİ ---
st.sidebar.header("👤 Personel Yönetimi")

with st.sidebar.expander("➕ Tekil Kayıt Ekle"):
    with st.form("tekil_form"):
        y_isim = st.text_input("Ad Soyad").upper()
        y_magaza = st.selectbox("Mağaza", options=MAGAZA_LISTESI)
        if st.form_submit_button("Sisteme Ekle"):
            if y_isim:
                yeni_row = {"Tarih": pd.Timestamp.now().strftime("%Y-%m-%d"), "Optisyen Adı": y_isim, "Mağaza": y_magaza, "Toplam Puan": 0}
                for m in ANKET_MADDELERİ: yeni_row[m] = "YAPILMADI"
                df = pd.concat([df, pd.DataFrame([yeni_row])], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.rerun()

with st.sidebar.expander("📥 Excel/CSV Toplu Yükle"):
    yuklenen_dosya = st.file_uploader("Dosya seçin", type=["xlsx", "csv"])
    if yuklenen_dosya:
        try:
            if yuklenen_dosya.name.endswith('.csv'):
                excel_df = pd.read_csv(yuklenen_dosya)
            else:
                excel_df = pd.read_excel(yuklenen_dosya, engine='openpyxl')
            
            if "Optisyen Adı" in excel_df.columns and "Mağaza" in excel_df.columns:
                if st.button("Verileri Aktar"):
                    excel_df = excel_df[["Optisyen Adı", "Mağaza"]]
                    excel_df["Tarih"] = pd.Timestamp.now().strftime("%Y-%m-%d")
                    excel_df["Toplam Puan"] = 0
                    for m in ANKET_MADDELERİ: excel_df[m] = "YAPILMADI"
                    df = pd.concat([df, excel_df], ignore_index=True)
                    df.to_csv(DB_FILE, index=False)
                    st.success("Başarıyla aktarıldı!")
                    st.rerun()
            else:
                st.error("Excel'de 'Optisyen Adı' ve 'Mağaza' sütunları olmalı!")
        except Exception as e:
            st.error(f"Hata: Lütfen 'pip install openpyxl' yazın veya CSV yükleyin. Detay: {e}")

# --- ANA SEKMELER ---
tab_liste, tab_anket, tab_yonetim, tab_analiz = st.tabs([
    "📋 Kayıt Listesi", 
    "✍️ Teknik Anket Yap", 
    "⚙️ Personel Düzenle/Sil", 
    "📊 Mağaza Analizi"
])

with tab_liste:
    st.subheader("📋 Mevcut Personel Durumu")
    st.dataframe(df[["Tarih", "Optisyen Adı", "Mağaza", "Toplam Puan"]], use_container_width=True)

with tab_anket:
    st.subheader("✍️ Teknik Değerlendirme Formu")
    if not df.empty:
        secilen = st.selectbox("Anket yapılacak personeli seçin:", df["Optisyen Adı"].tolist())
        idx = df[df["Optisyen Adı"] == secilen].index[0]
        row = df.iloc[idx]
        
        with st.form("anket_formu"):
            yeni_cevaplar = {}
            c1, c2 = st.columns(2)
            for i, m in enumerate(ANKET_MADDELERİ):
                col = c1 if i < 13 else c2
                current = row[m] if m in row else "YAPILMADI"
                yeni_cevaplar[m] = col.radio(f"{m}", ["İYİ", "ORTA", "ÇOK İYİ", "YAPILMADI"], 
                                             index=["İYİ", "ORTA", "ÇOK İYİ", "YAPILMADI"].index(current), horizontal=True)
            
            if st.form_submit_button("Anketi Kaydet ve Puanla"):
                toplam = sum([PUAN_SISTEMI[v] for v in yeni_cevaplar.values()])
                df.at[idx, "Toplam Puan"] = toplam
                for k, v in yeni_cevaplar.items(): df.at[idx, k] = v
                df.to_csv(DB_FILE, index=False)
                st.success(f"Kaydedildi! Yeni Puan: {toplam}")
                st.rerun()
    else:
        st.info("Henüz kayıtlı personel yok.")

with tab_yonetim:
    st.subheader("⚙️ Personel Bilgi Yönetimi")
    for i, r in df.iterrows():
        col_ad, col_btn = st.columns([4, 1])
        col_ad.write(f"**{r['Optisyen Adı']}** — {r['Mağaza']}")
        if col_btn.button("🗑️ Sil", key=f"del_sys_{i}"):
            silme_onay_dialogu(i, r['Optisyen Adı'])

with tab_analiz:
    st.subheader("📊 Mağaza Bazlı Performans")
    if not df.empty:
        analiz = df.groupby("Mağaza").agg({"Optisyen Adı": "nunique", "Toplam Puan": "mean"}).reset_index()
        analiz.columns = ["Mağaza", "Personel Sayısı", "Ort. Puan"]
        
        st.bar_chart(analiz.set_index("Mağaza")["Ort. Puan"])
        st.table(analiz.style.format({"Ort. Puan": "{:.2f}"}))
    else:
        st.info("Analiz için veri bulunmuyor.")
