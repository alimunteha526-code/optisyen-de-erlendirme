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

# --- MODAL: SİLME ONAYI (EKRANIN ORTASINDA) ---
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

# --- ÜST PANEL ---
st.title("👓 Optisyen Teknik Takip Sistemi")
if not df.empty:
    toplam_kisi = df["Optisyen Adı"].nunique()
    st.markdown(f"""
        <div style="background-color:#F0F2F6; padding:20px; border-radius:10px; border-left: 5px solid #FF4B4B; margin-bottom:20px;">
            <h3 style="margin:0; color:#31333F;">Toplam Kayıtlı Optisyen Sayısı: {toplam_kisi}</h3>
        </div>
    """, unsafe_allow_html=True)

# --- SOL PANEL ---
st.sidebar.header("📥 Veri Yükleme")

with st.sidebar.expander("➕ Yeni Personel Ekle"):
    with st.form("tekil_form"):
        ad = st.text_input("Ad Soyad").upper()
        mgz = st.selectbox("Mağaza", options=MAGAZA_LISTESI)
        if st.form_submit_button("Sisteme Kaydet"):
            if ad:
                yeni = {"Tarih": pd.Timestamp.now().strftime("%Y-%m-%d"), "Optisyen Adı": ad, "Mağaza": mgz, "Toplam Puan": 0}
                for m in ANKET_MADDELERİ: yeni[m] = "YAPILMADI"
                df = pd.concat([df, pd.DataFrame([yeni])], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.rerun()

with st.sidebar.expander("📂 Excel/CSV Toplu Yükle"):
    dosya = st.file_uploader("Dosya Seç", type=["xlsx", "csv"])
    if dosya:
        try:
            if dosya.name.endswith('.csv'):
                ex_df = pd.read_csv(dosya)
            else:
                # openpyxl motorunu zorla
                ex_df = pd.read_excel(dosya, engine='openpyxl')
            
            if "Optisyen Adı" in ex_df.columns and "Mağaza" in ex_df.columns:
                if st.button("Listeyi İçeri Aktar"):
                    ex_df = ex_df[["Optisyen Adı", "Mağaza"]]
                    ex_df["Tarih"] = pd.Timestamp.now().strftime("%Y-%m-%d")
                    ex_df["Toplam Puan"] = 0
                    for m in ANKET_MADDELERİ: ex_df[m] = "YAPILMADI"
                    df = pd.concat([df, ex_df], ignore_index=True)
                    df.to_csv(DB_FILE, index=False)
                    st.success("Aktarım başarılı!")
                    st.rerun()
            else:
                st.error("Hata: Sütun başlıkları tam olarak 'Optisyen Adı' ve 'Mağaza' olmalı.")
        except ImportError:
            st.error("❌ 'openpyxl' kütüphanesi eksik. Terminale 'pip install openpyxl' yazın.")
        except Exception as e:
            st.error(f"Dosya okunamadı: {e}")

# --- ANA SEKMELER ---
tab1, tab2, tab3, tab4 = st.tabs(["📋 Liste", "✍️ Anket Yap", "⚙️ Yönetim", "📊 Mağaza Analizi"])

with tab1:
    st.dataframe(df[["Tarih", "Optisyen Adı", "Mağaza", "Toplam Puan"]], use_container_width=True)

with tab2:
    if not df.empty:
        secilen_opt = st.selectbox("Anket yapılacak kişiyi seçin:", df["Optisyen Adı"].tolist())
        idx = df[df["Optisyen Adı"] == secilen_opt].index[0]
        row = df.iloc[idx]
        with st.form("anket_form"):
            cevaplar = {}
            c1, c2 = st.columns(2)
            for i, m in enumerate(ANKET_MADDELERİ):
                col = c1 if i < 13 else c2
                cur = row[m] if m in row else "YAPILMADI"
                cevaplar[m] = col.radio(f"**{m}**", ["İYİ", "ORTA", "ÇOK İYİ", "YAPILMADI"], 
                                        index=["İYİ", "ORTA", "ÇOK İYİ", "YAPILMADI"].index(cur), horizontal=True)
            if st.form_submit_button("Anketi Sonuçlandır"):
                puan = sum([PUAN_SISTEMI[v] for v in cevaplar.values()])
                df.at[idx, "Toplam Puan"] = puan
                for k, v in cevaplar.items(): df.at[idx, k] = v
                df.to_csv(DB_FILE, index=False)
                st.success(f"Kaydedildi. Yeni Puan: {puan}")
                st.rerun()

with tab3:
    for i, r in df.iterrows():
        col_a, col_b = st.columns([4, 1])
        col_a.write(f"**{r['Optisyen Adı']}** — {r['Mağaza']}")
        if col_b.button("🗑️ Sil", key=f"del_{i}"):
            silme_onay_dialogu(i, r['Optisyen Adı'])

with tab4:
    if not df.empty:
        st.subheader("📍 Mağaza Bazlı Teknik Seviye")
        analiz = df.groupby("Mağaza").agg({"Optisyen Adı": "nunique", "Toplam Puan": "mean"}).reset_index()
        analiz.columns = ["Mağaza", "Personel Sayısı", "Teknik Puan Ort."]
        st.bar_chart(analiz.set_index("Mağaza")["Teknik Puan Ort."])
        st.table(analiz.style.format({"Teknik Puan Ort.": "{:.2f}"}))
