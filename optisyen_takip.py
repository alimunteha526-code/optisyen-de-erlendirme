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

# --- ÜST PANEL ---
st.title("👓 Teknik Takip Sistemi")

if not df.empty:
    toplam_kisi = df["Optisyen Adı"].nunique()
    st.markdown(f"""
        <div style="background-color:#E8F0FE; padding:15px; border-radius:12px; border-left: 8px solid #1A73E8; margin-bottom: 20px;">
            <p style="margin:0; font-size:0.9rem; font-weight:bold; color:#5f6368;">İÇ ANADOLU</p>
            <h1 style="margin:0; color:#1A73E8; font-size:2.2rem;">Toplam Optisyen Sayısı: {toplam_kisi}</h1>
        </div>
    """, unsafe_allow_html=True)

# --- SOL PANEL: HIZLI KAYIT ---
st.sidebar.header("👤 Yeni Personel")
with st.sidebar.form("yeni_personel"):
    isim = st.text_input("Ad Soyad")
    magaza = st.selectbox("Mağaza", options=MAGAZA_LISTESI)
    if st.form_submit_button("Hızlı Kayıt Oluştur"):
        if isim:
            yeni = {"Tarih": pd.Timestamp.now().strftime("%Y-%m-%d"), "Optisyen Adı": turkce_buyuk(isim), "Mağaza": magaza, "Toplam Puan": 0}
            for m in ANKET_MADDELERİ: yeni[m] = "YAPILMADI"
            df = pd.concat([df, pd.DataFrame([yeni])], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.rerun()

# --- ANA SEKMELER (GÜNCELLENDİ) ---
tab_liste, tab_anket, tab_yonetim, tab_analiz = st.tabs([
    "📋 Kayıt Listesi", 
    ✍️ Teknik Anket Yap", 
    "⚙️ Personel Düzenle/Sil", 
    "📊 Analiz"
])

with tab_liste:
    st.subheader("📋 Mevcut Personel Listesi")
    st.dataframe(df[["Tarih", "Optisyen Adı", "Mağaza", "Toplam Puan"]], use_container_width=True)

with tab_anket:
    st.subheader("✍️ Optisyen Teknik Değerlendirme Formu")
    if not df.empty:
        secilen_optisyen = st.selectbox("Anketini doldurmak/güncellemek istediğiniz optisyeni seçin:", 
                                        options=df["Optisyen Adı"].tolist(),
                                        key="anket_select")
        
        idx = df[df["Optisyen Adı"] == secilen_optisyen].index[0]
        row = df.iloc[idx]
        
        with st.form("yeni_anket_formu"):
            st.info(f"📍 Mağaza: {row['Mağaza']} | Mevcut Puan: {row['Toplam Puan']}")
            yeni_cevaplar = {}
            col1, col2 = st.columns(2)
            for i, m in enumerate(ANKET_MADDELERİ):
                col = col1 if i < 13 else col2
                current_val = row[m] if m in row else "YAPILMADI"
                yeni_cevaplar[m] = col.radio(f"**{i+1}.** {m}", 
                                             ["İYİ", "ORTA", "ÇOK İYİ", "YAPILMADI"], 
                                             index=["İYİ", "ORTA", "ÇOK İYİ", "YAPILMADI"].index(current_val),
                                             horizontal=True)
            
            if st.form_submit_button("Anketi Kaydet / Güncelle"):
                t_puan = sum([PUAN_SISTEMI[v] for v in yeni_cevaplar.values()])
                for k, v in yeni_cevaplar.items(): df.at[idx, k] = v
                df.at[idx, "Toplam Puan"] = t_puan
                df.to_csv(DB_FILE, index=False)
                st.success(f"✅ {secilen_optisyen} için anket başarıyla kaydedildi! Yeni Puan: {t_puan}")
                st.rerun()
    else:
        st.info("Önce sol panelden personel kaydı oluşturmalısınız.")

with tab_yonetim:
    st.subheader("⚙️ Personel Bilgilerini Güncelle veya Sil")
    for i, r in df.iterrows():
        c_ad, c_mag, c_sil = st.columns([3, 2, 1])
        c_ad.write(f"**{r['Optisyen Adı']}**")
        c_mag.write(f"🏢 {r['Mağaza']}")
        if c_sil.button("🗑️ Sil", key=f"del_p_{i}"):
            silme_onay_dialogu(i, r['Optisyen Adı'])

with tab_analiz:
    st.subheader("📊 Mağaza Teknik Analizi")
    if not df.empty:
        analiz_df = df.groupby("Mağaza").agg({"Optisyen Adı": "nunique", "Toplam Puan": "mean"}).reset_index()
        analiz_df.columns = ["Mağaza", "Kişi Sayısı", "Puan Ortalaması"]
        st.table(analiz_df.style.format({"Puan Ortalaması": "{:.2f}"}))
        st.bar_chart(analiz_df.set_index("Mağaza")["Puan Ortalaması"])
