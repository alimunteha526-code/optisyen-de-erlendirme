import streamlit as st
import pandas as pd
import os

# --- AYARLAR VE VERİ TABANI ---
DB_FILE = "optisyen_teknik_veritabanı.csv"

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
st.title("👓 İç Anadolu Optisyen Teknik Takip Sistemi")

if not df.empty:
    toplam_kisi = df["Optisyen Adı"].nunique()
    st.info(f"📍 Sistemde Kayıtlı Toplam Optisyen: {toplam_kisi}")

# --- YAN PANEL: AKILLI DOSYA YÜKLEME ---
st.sidebar.header("📥 Veri Yükleme")

with st.sidebar.expander("📂 Excel veya CSV Yükle"):
    dosya = st.file_uploader("Dosyayı seçin", type=["xlsx", "csv"])
    if dosya:
        try:
            # Dosya Okuma ve Karakter Kodlaması Çözümü
            if dosya.name.endswith('.csv'):
                try:
                    ex_df = pd.read_csv(dosya, encoding='utf-8')
                except UnicodeDecodeError:
                    dosya.seek(0)
                    ex_df = pd.read_csv(dosya, encoding='cp1254')
            else:
                ex_df = pd.read_excel(dosya, engine='openpyxl')
            
            # Sütun İsimlerini Temizleme (Boşlukları sil, büyük harfe çevir)
            ex_df.columns = [str(c).strip() for c in ex_df.columns]
            temp_cols = {c: str(c).upper() for c in ex_df.columns}
            
            # Akıllı Eşleştirme (Alternatif başlıkları kontrol et)
            ad_col = next((o for o, c in temp_cols.items() if c in ["OPTİSYEN ADI", "OPTISYEN ADI", "AD SOYAD", "PERSONEL"]), None)
            mgz_col = next((o for o, c in temp_cols.items() if c in ["MAĞAZA", "MAGAZA", "ŞUBE", "SUBE", "YER"]), None)

            if ad_col and mgz_col:
                ex_df = ex_df.rename(columns={ad_col: "Optisyen Adı", mgz_col: "Mağaza"})
                
                if st.button("Verileri Sisteme Aktar"):
                    yeni_liste = ex_df[["Optisyen Adı", "Mağaza"]].copy()
                    yeni_liste["Optisyen Adı"] = yeni_liste["Optisyen Adı"].astype(str).str.upper()
                    yeni_liste["Tarih"] = pd.Timestamp.now().strftime("%Y-%m-%d")
                    yeni_liste["Toplam Puan"] = 0
                    for m in ANKET_MADDELERİ: yeni_liste[m] = "YAPILMADI"
                    
                    df = pd.concat([df, yeni_liste], ignore_index=True)
                    df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                    st.success(f"✅ {len(yeni_liste)} yeni personel başarıyla eklendi!")
                    st.rerun()
            else:
                st.error("❌ Sütun başlıkları anlaşılamadı!")
                st.info(f"Dosyanızdaki başlıklar: {list(ex_df.columns)}")
                st.warning("Lütfen sütunları 'Optisyen Adı' ve 'Mağaza' olarak adlandırın.")
        except Exception as e:
            st.error(f"⚠️ Dosya hatası: {e}")

# --- ANA SEKMELER ---
tab_liste, tab_anket, tab_yonetim, tab_analiz = st.tabs([
    "📋 Kayıt Listesi", 
    "✍️ Teknik Anket Yap", 
    "⚙️ Personel Yönetimi", 
    "📊 Mağaza Analizi"
])

with tab_liste:
    st.subheader("📋 Güncel Personel ve Puan Durumu")
    if not df.empty:
        st.dataframe(df[["Tarih", "Optisyen Adı", "Mağaza", "Toplam Puan"]], use_container_width=True)
    else:
        st.info("Sistemde henüz kayıtlı personel yok.")

with tab_anket:
    st.subheader("✍️ Teknik Değerlendirme Formu")
    if not df.empty:
        # Alfabetik sıralı liste
        liste_sirali = sorted(df["Optisyen Adı"].unique())
        secilen_opt = st.selectbox("Anket yapılacak personeli seçin:", options=liste_sirali)
        
        idx = df[df["Optisyen Adı"] == secilen_opt].index[0]
        row = df.iloc[idx]
        
        with st.form("anket_formu_detay"):
            st.markdown(f"**Mağaza:** {row['Mağaza']} | **Mevcut Puan:** {row['Toplam Puan']}")
            st.divider()
            
            yeni_cevaplar = {}
            col1, col2 = st.columns(2)
            
            for i, madde in enumerate(ANKET_MADDELERİ):
                hedef_col = col1 if i < 13 else col2
                mevcut_v = row[madde] if madde in row else "YAPILMADI"
                yeni_cevaplar[madde] = hedef_col.radio(
                    f"**{i+1}.** {madde}", 
                    ["İYİ", "ORTA", "ÇOK İYİ", "YAPILMADI"], 
                    index=["İYİ", "ORTA", "ÇOK İYİ", "YAPILMADI"].index(mevcut_v),
                    horizontal=True,
                    key=f"q_{idx}_{i}"
                )
            
            if st.form_submit_button("Anketi Kaydet ve Puanı Hesapla"):
                hesaplanan_puan = sum([PUAN_SISTEMI[v] for v in yeni_cevaplar.values()])
                df.at[idx, "Toplam Puan"] = hesaplanan_puan
                for k, v in yeni_cevaplar.items(): df.at[idx, k] = v
                
                df.to_csv(DB_FILE, index=False, encoding='utf-8-sig')
                st.success(f"✅ Kaydedildi! {secilen_opt} Teknik Puanı: {hesaplanan_puan}")
                st.rerun()
    else:
        st.warning("Anket yapabilmek için önce personel yüklemelisiniz.")

with tab_yonetim:
    st.subheader("⚙️ Personel Listesini Düzenle")
    if not df.empty:
        for i, r in df.iterrows():
            c1, c2, c3 = st.columns([3, 2, 1])
            c1.write(f"**{r['Optisyen Adı']}**")
            c2.write(f"🏢 {r['Mağaza']}")
            if c3.button("🗑️ Sil", key=f"del_btn_yonetim_{i}"):
                silme_onay_dialogu(i, r['Optisyen Adı'])
    else:
        st.info("Düzenlenecek kayıt yok.")

with tab_analiz:
    st.subheader("📊 Mağaza Teknik Performans Analizi")
    if not df.empty:
        ozet = df.groupby("Mağaza").agg({
            "Optisyen Adı": "count",
            "Toplam Puan": "mean"
        }).reset_index()
        ozet.columns = ["Mağaza", "Optisyen Sayısı", "Ortalama Teknik Puan"]
        
        st.bar_chart(ozet.set_index("Mağaza")["Ortalama Teknik Puan"])
        st.table(ozet.style.format({"Ortalama Teknik Puan": "{:.2f}"}))
    else:
        st.info("Analiz için veri yetersiz.")
