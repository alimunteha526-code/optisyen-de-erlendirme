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

# --- ÜST PANEL ---
st.title("👓 Optisyen Teknik Değerlendirme Sistemi")

if not df.empty:
    toplam_kisi = df["Optisyen Adı"].nunique()
    st.markdown(f"""
        <div style="background-color:#E8F0FE; padding:15px; border-radius:12px; border-left: 8px solid #1A73E8; margin-bottom: 20px;">
            <p style="margin:0; font-size:0.9rem; font-weight:bold; color:#5f6368;">İÇ ANADOLU</p>
            <h1 style="margin:0; color:#1A73E8; font-size:2.2rem;">Toplam Optisyen Sayısı: {toplam_kisi}</h1>
        </div>
    """, unsafe_allow_html=True)

# --- SOL PANEL: TOPLU VE TEKİL KAYIT ---
st.sidebar.header("👤 Personel İşlemleri")

with st.sidebar.expander("📥 Excel/CSV ile Toplu Yükle"):
    yuklenen_dosya = st.file_uploader("Dosya seçin (.xlsx veya .csv)", type=["xlsx", "csv"])
    if yuklenen_dosya:
        try:
            if yuklenen_dosya.name.endswith('.csv'):
                excel_df = pd.read_csv(yuklenen_dosya)
            else:
                excel_df = pd.read_excel(yuklenen_dosya)
            
            if "Optisyen Adı" in excel_df.columns and "Mağaza" in excel_df.columns:
                if st.button("Sisteme Aktar"):
                    # Eksik kolonları tamamla
                    excel_df = excel_df[["Optisyen Adı", "Mağaza"]]
                    excel_df["Tarih"] = pd.Timestamp.now().strftime("%Y-%m-%d")
                    excel_df["Toplam Puan"] = 0
                    for m in ANKET_MADDELERİ: excel_df[m] = "YAPILMADI"
                    
                    df = pd.concat([df, excel_df], ignore_index=True)
                    df.to_csv(DB_FILE, index=False)
                    st.success("Aktarım Tamamlandı!")
                    st.rerun()
            else:
                st.error("Sütun isimleri: 'Optisyen Adı' ve 'Mağaza' olmalı.")
        except Exception as e:
            st.error(f"Kütüphane Hatası: Lütfen 'pip install openpyxl' komutunu çalıştırın. Detay: {e}")

# --- ANA SEKMELER ---
tab_liste, tab_anket, tab_yonetim, tab_rapor = st.tabs(["📋 Liste", "✍️ Anket", "⚙️ Düzenle/Sil", "📥 Dışa Aktar"])

with tab_liste:
    st.dataframe(df[["Tarih", "Optisyen Adı", "Mağaza", "Toplam Puan"]], use_container_width=True)

with tab_anket:
    if not df.empty:
        secilen = st.selectbox("Personel Seçin:", df["Optisyen Adı"].tolist(), key="main_anket_sel")
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
            if st.form_submit_button("Kaydet"):
                puan = sum([PUAN_SISTEMI[v] for v in yeni_cevaplar.values()])
                df.at[idx, "Toplam Puan"] = puan
                for k, v in yeni_cevaplar.items(): df.at[idx, k] = v
                df.to_csv(DB_FILE, index=False)
                st.success("Anket Kaydedildi!")
                st.rerun()

with tab_yonetim:
    for i, r in df.iterrows():
        col_ad, col_sil = st.columns([4, 1])
        col_ad.write(f"**{r['Optisyen Adı']}** ({r['Mağaza']})")
        if col_sil.button("🗑️ Sil", key=f"del_btn_{i}"):
            silme_onay_dialogu(i, r['Optisyen Adı'])

with tab_rapor:
    st.subheader("📥 Verileri Yedekle / Raporla")
    csv_data = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="Tüm Verileri CSV Olarak İndir",
        data=csv_data,
        file_name='optisyen_teknik_rapor.csv',
        mime='text/csv',
    )
