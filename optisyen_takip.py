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
        return pd.read_csv(DB_FILE, encoding='utf-8-sig')
    cols = ["Tarih", "Optisyen Adı", "Mağaza", "Toplam Puan"] + ANKET_MADDELERİ
    return pd.DataFrame(columns=cols)

st.set_page_config(page_title="Optisyen Teknik Yönetim", layout="wide")
df = veriyi_yukle()

# --- SİLME ONAY DİALOGU ---
@st.dialog("Kayıt Silinsin mi?")
def silme_onay_dialogu(index, isim):
    st.warning(f"⚠️ **{isim}** kaydını silmek üzeresiniz. Bu işlem geri alınamaz!")
    c1, c2 = st.columns(2)
    if c1.button("✅ Evet, Sil", use_container_width=True):
        global df
        df = df.drop(index).reset_index(drop=True)
        df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
        st.success("Kayıt silindi.")
        st.rerun()
    if c2.button("❌ Vazgeç", use_container_width=True):
        st.rerun()

# --- ÜST PANEL ---
st.title("👓 İç Anadolu Optisyen Teknik Takip")

if not df.empty:
    toplam_kisi = df["Optisyen Adı"].nunique()
    st.info(f"📍 Toplam Kayıtlı Optisyen: {toplam_kisi}")

# --- YAN PANEL: VERİ YÜKLEME ---
st.sidebar.header("📥 Veri İşlemleri")

with st.sidebar.expander("📂 Excel/CSV Dosyası Yükle"):
    dosya = st.file_uploader("Dosya Seç", type=["xlsx", "csv"])
    if dosya:
        try:
            if dosya.name.endswith('.csv'):
                try:
                    # Önce standart utf-8 dene
                    ex_df = pd.read_csv(dosya, encoding='utf-8')
                except UnicodeDecodeError:
                    # Hata verirse Türkçe karakterli Excel CSV formatını (cp1254) dene
                    dosya.seek(0)
                    ex_df = pd.read_csv(dosya, encoding='cp1254')
            else:
                # Excel okuma (openpyxl gerektirir)
                ex_df = pd.read_excel(dosya, engine='openpyxl')
            
            # Sütun isimlerindeki boşlukları temizle
            ex_df.columns = [str(c).strip() for c in ex_df.columns]
            
            if "Optisyen Adı" in ex_df.columns and "Mağaza" in ex_df.columns:
                if st.button("Listeyi Sisteme Aktar"):
                    yeni_veriler = ex_df[["Optisyen Adı", "Mağaza"]].copy()
                    yeni_veriler["Optisyen Adı"] = yeni_veriler["Optisyen Adı"].str.upper()
                    yeni_veriler["Tarih"] = pd.Timestamp.now().strftime("%Y-%m-%d")
                    yeni_veriler["Toplam Puan"] = 0
                    for m in ANKET_MADDELERİ: yeni_veriler[m] = "YAPILMADI"
                    
                    df = pd.concat([df, yeni_veriler], ignore_index=True)
                    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                    st.success(f"✅ {len(yeni_veriler)} kayıt başarıyla eklendi!")
                    st.rerun()
            else:
                st.error("Hata: Dosyada 'Optisyen Adı' ve 'Mağaza' sütunları bulunamadı.")
        except Exception as e:
            st.error(f"⚠️ Dosya okunurken bir hata oluştu: {e}")

# --- ANA SEKMELER ---
tab1, tab2, tab3, tab4 = st.tabs(["📋 Kayıt Listesi", "✍️ Teknik Anket", "⚙️ Yönetim", "📊 Analiz"])

with tab1:
    st.subheader("📋 Güncel Personel Listesi")
    if not df.empty:
        st.dataframe(df[["Tarih", "Optisyen Adı", "Mağaza", "Toplam Puan"]], use_container_width=True)
    else:
        st.info("Sistemde henüz kayıt bulunmuyor.")

with tab2:
    st.subheader("✍️ Optisyen Değerlendirme Formu")
    if not df.empty:
        secilen_opt = st.selectbox("Değerlendirilecek Optisyen:", options=df["Optisyen Adı"].tolist())
        idx = df[df["Optisyen Adı"] == secilen_opt].index[0]
        row = df.iloc[idx]
        
        with st.form("anket_formu"):
            st.write(f"🏢 **Mağaza:** {row['Mağaza']}")
            cevaplar = {}
            col1, col2 = st.columns(2)
            
            for i, madde in enumerate(ANKET_MADDELERİ):
                secili_col = col1 if i < 13 else col2
                mevcut_deger = row[madde] if madde in row else "YAPILMADI"
                cevaplar[madde] = secili_col.radio(
                    f"**{i+1}.** {madde}", 
                    ["İYİ", "ORTA", "ÇOK İYİ", "YAPILMADI"], 
                    index=["İYİ", "ORTA", "ÇOK İYİ", "YAPILMADI"].index(mevcut_deger),
                    horizontal=True,
                    key=f"radio_{idx}_{i}"
                )
            
            if st.form_submit_button("Anketi Kaydet / Güncelle"):
                puan = sum([PUAN_SISTEMI[v] for v in cevaplar.values()])
                df.at[idx, "Toplam Puan"] = puan
                for k, v in cevaplar.items(): df.at[idx, k] = v
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success(f"✅ {secilen_opt} için teknik puan güncellendi: {puan}")
                st.rerun()
    else:
        st.info("Önce personel eklemelisiniz.")

with tab3:
    st.subheader("⚙️ Personel Bilgilerini Düzenle")
    if not df.empty:
        for i, r in df.iterrows():
            c_ad, c_mgz, c_btn = st.columns([3, 2, 1])
            c_ad.write(f"**{r['Optisyen Adı']}**")
            c_mgz.write(f"🏢 {r['Mağaza']}")
            if c_btn.button("🗑️ Sil", key=f"del_btn_{i}"):
                silme_onay_dialogu(i, r['Optisyen Adı'])
    else:
        st.info("Düzenlenecek kayıt bulunamadı.")

with tab4:
    st.subheader("📊 Mağaza Bazlı İstatistikler")
    if not df.empty:
        # Analiz verisi hazırlama
        analiz_df = df.groupby("Mağaza").agg({
            "Optisyen Adı": "count",
            "Toplam Puan": "mean"
        }).reset_index()
        analiz_df.columns = ["Mağaza", "Optisyen Sayısı", "Teknik Puan Ortalaması"]
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.write("**Mağaza Teknik Seviyeleri (Ortalama)**")
            st.bar_chart(analiz_df.set_index("Mağaza")["Teknik Puan Ortalaması"])
        with col_g2:
            st.write("**Mağaza Personel Dağılımı**")
            st.bar_chart(analiz_df.set_index("Mağaza")["Optisyen Sayısı"])
            
        st.write("**Detaylı Mağaza Tablosu**")
        st.table(analiz_df.style.format({"Teknik Puan Ortalaması": "{:.2f}"}))
    else:
        st.info("Analiz yapılacak veri bulunmuyor.")
