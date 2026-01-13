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

if "active_edit_index" not in st.session_state:
    st.session_state.active_edit_index = None

# --- BAŞLIK ---
st.title("👓 Teknik Takip Sistemi")

# --- İSTATİSTİK PANELİ ---
if not df.empty:
    toplam_kisi = df["Optisyen Adı"].nunique()
    st.markdown(f"""
        <div style="background-color:#E8F0FE; padding:20px; border-radius:15px; border-left: 10px solid #1A73E8; margin-bottom: 25px;">
            <span style="color:#5f6368; font-size:1rem; font-weight:bold;">İÇ ANADOLU</span>
            <h1 style="margin:0; color:#1A73E8; font-size:2.8rem;">Toplam Optisyen Sayısı: {toplam_kisi}</h1>
        </div>
    """, unsafe_allow_html=True)

# --- SOL PANEL: HIZLI KAYIT ---
st.sidebar.header("👤 Yeni Personel Ekle")
with st.sidebar.form("bolge_kayit"):
    isim = st.text_input("Optisyen Adı Soyadı")
    magaza = st.selectbox("Mağaza Seçiniz", options=MAGAZA_LISTESI)
    tarih = st.date_input("Kayıt Tarihi")
    if st.form_submit_button("Sisteme Dahil Et"):
        if isim:
            yeni = {"Tarih": str(tarih), "Optisyen Adı": turkce_buyuk(isim), "Mağaza": magaza, "Toplam Puan": 0}
            for m in ANKET_MADDELERİ: yeni[m] = "YAPILMADI"
            df = pd.concat([df, pd.DataFrame([yeni])], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.rerun()

# --- ANA SEKMELER ---
tab_liste, tab_istatistik, tab_yonetim = st.tabs(["📋 Kayıtlı Optisyenler", "📊 Mağaza Analizleri", "⚙️ Düzenle / Sil / Anket"])

with tab_liste:
    st.subheader("📋 Güncel Liste")
    if not df.empty:
        st.dataframe(df[["Tarih", "Optisyen Adı", "Mağaza", "Toplam Puan"]], use_container_width=True)
    else:
        st.info("Henüz kayıt bulunmuyor.")

with tab_istatistik:
    if not df.empty:
        st.subheader("📊 Mağaza Dağılımı")
        magaza_dagilimi = df.groupby("Mağaza")["Optisyen Adı"].nunique()
        st.bar_chart(magaza_dagilimi)

with tab_yonetim:
    st.subheader("⚙️ Kayıt Yönetimi")
    
    # DÜZENLEME (ANKET) MODU
    if st.session_state.active_edit_index is not None:
        idx = st.session_state.active_edit_index
        row = df.iloc[idx]
        st.info(f"📝 **{row['Optisyen Adı']}** için teknik anketi dolduruyorsunuz.")
        
        with st.form("anket_duzenle"):
            yeni_cevaplar = {}
            c1, c2 = st.columns(2)
            for i, madde in enumerate(ANKET_MADDELERİ):
                current_val = row[madde] if madde in row and row[madde] in PUAN_SISTEMI else "YAPILMADI"
                col = c1 if i < 13 else c2
                yeni_cevaplar[madde] = col.radio(f"{i+1}. {madde}", 
                                                 options=["İYİ", "ORTA", "ÇOK İYİ", "YAPILMADI"], 
                                                 index=["İYİ", "ORTA", "ÇOK İYİ", "YAPILMADI"].index(current_val),
                                                 horizontal=True)
            
            if st.form_submit_button("Değişiklikleri Kaydet"):
                t_puan = sum([PUAN_SISTEMI[v] for v in yeni_cevaplar.values()])
                for m, v in yeni_cevaplar.items():
                    df.at[idx, m] = v
                df.at[idx, "Toplam Puan"] = t_puan
                df.to_csv(DB_FILE, index=False)
                st.session_state.active_edit_index = None
                st.success("Kayıt güncellendi!")
                st.rerun()
        
        if st.button("Düzenlemeyi İptal Et"):
            st.session_state.active_edit_index = None
            st.rerun()
            
    # LİSTE MODU (SİL VE DÜZENLE BUTONLARI)
    else:
        if not df.empty:
            for i, r in df.iterrows():
                col_metin, col_anket, col_sil = st.columns([3, 1, 1])
                col_metin.write(f"**{r['Optisyen Adı']}** — {r['Mağaza']} (Puan: {r['Toplam Puan']})")
                
                # Düzenle/Anket Butonu
                if col_anket.button("✏️ Düzenle", key=f"edit_{i}"):
                    st.session_state.active_edit_index = i
                    st.rerun()
                
                # Sil Butonu
                if col_sil.button("🗑️ Sil", key=f"del_{i}"):
                    df = df.drop(i)
                    df.to_csv(DB_FILE, index=False)
                    st.warning(f"{r['Optisyen Adı']} kaydı silindi.")
                    st.rerun()
        else:
            st.info("İşlem yapılacak kayıt bulunamadı.")
