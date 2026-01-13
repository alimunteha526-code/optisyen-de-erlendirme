import streamlit as st
import pandas as pd
import os
from io import BytesIO

# --- AYARLAR VE VERİ TABANI ---
DB_FILE = "optisyen_teknik_veritabani.csv"

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
    "Kanalı öne arkaya alma, polisaj, nilör derinlik ayarlama",
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

st.set_page_config(page_title="Optisyen Teknik Yönetim", layout="wide")

def turkce_buyuk(metin):
    return metin.replace('i', 'İ').replace('ı', 'I').upper() if metin else ""

df = veriyi_yukle()

# Session State Yönetimi
if "active_edit_index" not in st.session_state:
    st.session_state.active_edit_index = None

# --- BAŞLIK ---
st.title("👓 Optisyen Teknik Takip Sistemi")

# --- TOPLAM OPTİSYEN SAYISI (İSTEDİĞİNİZ YENİ BÖLÜM) ---
if not df.empty:
    toplam_kisi = df["Optisyen Adı"].nunique()
    st.markdown(f"""
        <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; border-left: 5px solid #ff4b4b; margin-bottom: 20px;">
            <h2 style="margin:0; color:#31333F;">👥 Toplam Optisyen Sayısı: {toplam_kisi}</h2>
        </div>
    """, unsafe_allow_html=True)
else:
    st.info("Sistemde henüz kayıtlı optisyen bulunmuyor.")

# --- SOL PANEL: HIZLI PERSONEL EKLEME ---
st.sidebar.header("👤 Personel Kaydı")
with st.sidebar.form("hizli_kayit"):
    isim_input = st.text_input("Optisyen Adı Soyadı")
    magaza_input = st.selectbox("Mağaza", options=MAGAZA_LISTESI)
    tarih_input = st.date_input("Kayıt Tarihi")
    kaydet_btn = st.form_submit_button("Personeli Listeye Ekle")

if kaydet_btn and isim_input:
    yeni_personel = {
        "Tarih": str(tarih_input),
        "Optisyen Adı": turkce_buyuk(isim_input),
        "Mağaza": magaza_input,
        "Toplam Puan": 0
    }
    for madde in ANKET_MADDELERİ:
        yeni_personel[madde] = "YAPILMADI"
        
    df = pd.concat([df, pd.DataFrame([yeni_personel])], ignore_index=True)
    df.to_csv(DB_FILE, index=False)
    st.rerun()

# --- ANA PANELLER ---
tab_liste, tab_istatistik, tab_yonetim = st.tabs(["📋 Personel Listesi", "📊 Performans Analizi", "⚙️ Kayıt Düzenle / Teknik Anket"])

with tab_liste:
    st.subheader("📋 Genel Liste")
    display_df = df[["Tarih", "Optisyen Adı", "Mağaza", "Toplam Puan"]].copy()
    st.dataframe(display_df, use_container_width=True)

with tab_istatistik:
    if not df.empty and df["Toplam Puan"].sum() > 0:
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Mağaza Bazlı Ortalama Teknik Puan**")
            st.bar_chart(df.groupby("Mağaza")["Toplam Puan"].mean())
        with c2:
            st.write("**Mağaza Bazlı Personel Sayısı**")
            magaza_sayilari = df.groupby("Mağaza")["Optisyen Adı"].nunique()
            st.table(magaza_sayilari)
    else:
        st.info("İstatistik oluşması için teknik anketlerin doldurulması gerekir.")

with tab_yonetim:
    if st.session_state.active_edit_index is not None:
        idx = st.session_state.active_edit_index
        row = df.iloc[idx]
        st.warning(f"📝 {row['Optisyen Adı']} için Teknik Anketi Dolduruyorsunuz")
        
        with st.form("teknik_anket_formu"):
            yeni_cevaplar = {}
            col_a, col_b = st.columns(2)
            for i, madde in enumerate(ANKET_MADDELERİ):
                current_val = row[madde] if row[madde] in PUAN_SISTEMI else "YAPILMADI"
                target_col = col_a if i < 13 else col_b
                yeni_cevaplar[madde] = target_col.radio(f"{i+1}. {madde}", 
                                                       options=["İYİ", "ORTA", "ÇOK İYİ", "YAPILMADI"], 
                                                       index=["İYİ", "ORTA", "ÇOK İYİ", "YAPILMADI"].index(current_val),
                                                       horizontal=True)
            
            if st.form_submit_button("Anketi Kaydet ve Hesapla"):
                t_puan = sum([PUAN_SISTEMI[val] for val in yeni_cevaplar.values()])
                for m, v in yeni_cevaplar.items():
                    df.at[idx, m] = v
                df.at[idx, "Toplam Puan"] = t_puan
                df.to_csv(DB_FILE, index=False)
                st.session_state.active_edit_index = None
                st.rerun()
        
        if st.button("Düzenlemeyi İptal Et"):
            st.session_state.active_edit_index = None
            st.rerun()
    else:
        for index, row in df.iterrows():
            c1, c2, c3 = st.columns([3, 2, 1])
            durum = "✅ Tamamlandı" if row["Toplam Puan"] > 0 else "⏳ Bekliyor"
            c1.write(f"**{row['Optisyen Adı']}** ({row['Mağaza']})")
            c2.write(f"Durum: {durum} | Puan: {row['Toplam Puan']}")
            col_btn1, col_btn2 = c3.columns(2)
            if col_btn1.button("✏️", key=f"edit_btn_{index}"):
                st.session_state.active_edit_index = index
                st.rerun()
            if col_btn2.button("🗑️", key=f"del_btn_{index}"):
                df = df.drop(index)
                df.to_csv(DB_FILE, index=False)
                st.rerun()
