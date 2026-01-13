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

st.set_page_config(page_title="İç Anadolu Optisyen Yönetimi", layout="wide")
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
st.title("👓 Optisyen Teknik Takip & Kayıt Sistemi")

if not df.empty:
    toplam_kisi = df["Optisyen Adı"].nunique()
    st.info(f"📍 Bölge Genelinde Toplam Optisyen Sayısı: {toplam_kisi}")

# --- YAN PANEL: VERİ GİRİŞİ ---
st.sidebar.header("📥 Veri İşlemleri")

# 1. ÖZELLİK: TEK TEK KAYIT ETME
with st.sidebar.expander("➕ Tekil Personel Ekle"):
    with st.form("tekil_kayit_form"):
        yeni_isim = st.text_input("Ad Soyad").upper().strip()
        yeni_magaza = st.selectbox("Mağaza", options=MAGAZA_LISTESI)
        submit_tekil = st.form_submit_button("Sisteme Kaydet")
        
        if submit_tekil:
            if yeni_isim:
                yeni_satir = {
                    "Tarih": pd.Timestamp.now().strftime("%Y-%m-%d"),
                    "Optisyen Adı": yeni_isim,
                    "Mağaza": yeni_magaza,
                    "Toplam Puan": 0
                }
                # Anket maddelerini boş (YAPILMADI) olarak ekle
                for m in ANKET_MADDELERİ: yeni_satir[m] = "YAPILMADI"
                
                df = pd.concat([df, pd.DataFrame([yeni_satir])], ignore_index=True)
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success(f"✅ {yeni_isim} başarıyla kaydedildi!")
                st.rerun()
            else:
                st.error("Lütfen bir isim giriniz!")

# 2. ÖZELLİK: TOPLU YÜKLEME
with st.sidebar.expander("📂 Toplu Excel/CSV Yükle"):
    dosya = st.file_uploader("Dosya Seç", type=["xlsx", "csv"])
    if dosya:
        try:
            if dosya.name.endswith('.csv'):
                try: ex_df = pd.read_csv(dosya, encoding='utf-8')
                except: 
                    dosya.seek(0)
                    ex_df = pd.read_csv(dosya, encoding='cp1254')
            else:
                ex_df = pd.read_excel(dosya, engine='openpyxl')
            
            ex_df.columns = [str(c).strip() for c in ex_df.columns]
            temp_cols = {c: str(c).upper() for c in ex_df.columns}
            
            ad_col = next((o for o, c in temp_cols.items() if c in ["OPTİSYEN ADI", "AD SOYAD", "PERSONEL"]), None)
            mgz_col = next((o for o, c in temp_cols.items() if c in ["MAĞAZA", "ŞUBE", "YER"]), None)

            if ad_col and mgz_col:
                ex_df = ex_df.rename(columns={ad_col: "Optisyen Adı", mgz_col: "Mağaza"})
                if st.button("Listeyi İçeri Aktar"):
                    yeni_liste = ex_df[["Optisyen Adı", "Mağaza"]].copy()
                    yeni_liste["Optisyen Adı"] = yeni_liste["Optisyen Adı"].astype(str).str.upper()
                    yeni_liste["Tarih"] = pd.Timestamp.now().strftime("%Y-%m-%d")
                    yeni_liste["Toplam Puan"] = 0
                    for m in ANKET_MADDELERİ: yeni_liste[m] = "YAPILMADI"
                    df = pd.concat([df, yeni_liste], ignore_index=True)
                    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                    st.success("Toplu aktarım başarılı!")
                    st.rerun()
            else:
                st.error("Sütunlar bulunamadı! (Optisyen Adı ve Mağaza olmalı)")
        except Exception as e:
            st.error(f"Hata: {e}")

# --- ANA SEKMELER ---
tab1, tab2, tab3, tab4 = st.tabs(["📋 Liste", "✍️ Anket", "⚙️ Düzenle/Sil", "📊 Analiz"])

with tab1:
    if not df.empty:
        st.dataframe(df[["Tarih", "Optisyen Adı", "Mağaza", "Toplam Puan"]], use_container_width=True)
    else:
        st.info("Henüz kayıtlı personel yok.")

with tab2:
    if not df.empty:
        secilen_opt = st.selectbox("Personel Seç:", options=sorted(df["Optisyen Adı"].unique()))
        idx = df[df["Optisyen Adı"] == secilen_opt].index[0]
        row = df.iloc[idx]
        with st.form("anket_form"):
            st.markdown(f"### {secilen_opt} Değerlendirmesi")
            cevaplar = {}
            c1, c2 = st.columns(2)
            for i, m in enumerate(ANKET_MADDELERİ):
                col = c1 if i < 13 else c2
                cur = row[m] if m in row else "YAPILMADI"
                cevaplar[m] = col.radio(f"**{m}**", ["İYİ", "ORTA", "ÇOK İYİ", "YAPILMADI"], 
                                        index=["İYİ", "ORTA", "ÇOK İYİ", "YAPILMADI"].index(cur), horizontal=True)
            if st.form_submit_button("Anketi Kaydet"):
                puan = sum([PUAN_SISTEMI[v] for v in cevaplar.values()])
                df.at[idx, "Toplam Puan"] = puan
                for k, v in cevaplar.items(): df.at[idx, k] = v
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success(f"Kaydedildi! Puan: {puan}")
                st.rerun()

with tab3:
    for i, r in df.iterrows():
        ca, cb, cc = st.columns([3, 2, 1])
        ca.write(f"**{r['Optisyen Adı']}**")
        cb.write(f"🏢 {r['Mağaza']}")
        if cc.button("🗑️ Sil", key=f"del_{i}"):
            silme_onay_dialogu(i, r['Optisyen Adı'])

with tab4:
    if not df.empty:
        ozet = df.groupby("Mağaza").agg({"Optisyen Adı": "count", "Toplam Puan": "mean"}).reset_index()
        ozet.columns = ["Mağaza", "Personel Sayısı", "Teknik Ort."]
        st.bar_chart(ozet.set_index("Mağaza")["Teknik Ort."])
        st.table(ozet)
