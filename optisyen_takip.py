import streamlit as st
import pandas as pd
import os
from io import BytesIO

# --- AYARLAR VE VERİ TABANI ---
DB_FILE = "optisyen_veritabani.csv"

# Görselden alınan sabit mağaza listesi
MAGAZA_LISTESI = [
    "KAYSERİ PARK AVM",
    "KAYSERİ MEYSU OUTLET AVM",
    "NOVADA KONYA OUTLET AVM",
    "FORUM KAYSERİ AVM",
    "NEVŞEHİR NİSSARA AVM",
    "MARAŞ PİAZZA AVM",
    "KONYA KENT PLAZA AVM",
    "M1 KONYA AVM",
    "KAYSERİ KUMSMALL AVM",
    "PARK KARAMAN AVM",
    "NİĞDE CADDE",
    "AKSARAY NORA CITY AVM",
    "KIRŞEHİR CADDE",
    "KAYSERİ TUNALIFE AVM",
    "KONYA KAZIMKARABEKİR CADDE",
    "KONYA ENNTEPE AVM"
]

def veriyi_yukle():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Tarih", "Optisyen Adı", "Mağaza", "Puan", "Değerlendirme Notu"])

st.set_page_config(page_title="Optisyen Yönetim Sistemi", layout="wide")

def turkce_buyuk(metin):
    if not metin: return ""
    return metin.replace('i', 'İ').replace('ı', 'I').upper()

df = veriyi_yukle()

# --- BAŞLIK ---
st.title("👓 Optisyen Değerlendirme ve Yönetim Paneli")

# --- SOL PANEL: VERİ GİRİŞİ / DÜZENLEME ---
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

st.sidebar.header("📝 Veri İşlemleri")

# Form değerleri hazırlığı
default_name, default_magaza, default_puan, default_not = "", MAGAZA_LISTESI[0], 7, ""
if st.session_state.edit_index is not None:
    row = df.iloc[st.session_state.edit_index]
    default_name = row["Optisyen Adı"]
    default_magaza = row["Mağaza"]
    default_puan = int(row["Puan"])
    default_not = row["Değerlendirme Notu"]

with st.sidebar.form("optisyen_form"):
    isim_input = st.text_input("Optisyen Adı Soyadı", value=default_name)
    
    # SADECE BELİRTİLEN MAĞAZALARIN OLDUĞU SEÇİM KUTUSU
    magaza_input = st.selectbox("Çalıştığı Mağaza", options=MAGAZA_LISTESI, index=MAGAZA_LISTESI.index(default_magaza) if default_magaza in MAGAZA_LISTESI else 0)
    
    puan = st.slider("Performans Puanı", 1, 10, default_puan)
    notlar_input = st.text_area("Notlar", value=default_not)
    tarih = st.date_input("Tarih")
    
    submit_label = "Değişiklikleri Kaydet" if st.session_state.edit_index is not None else "Sisteme Kaydet"
    kaydet = st.form_submit_button(submit_label)

if kaydet and isim_input:
    yeni_satir = {
        "Tarih": str(tarih), 
        "Optisyen Adı": turkce_buyuk(isim_input), 
        "Mağaza": magaza_input, # Zaten listeden seçildiği için direkt alıyoruz
        "Puan": puan, 
        "Değerlendirme Notu": turkce_buyuk(notlar_input)
    }
    
    if st.session_state.edit_index is not None:
        df.iloc[st.session_state.edit_index] = yeni_satir
        st.session_state.edit_index = None
    else:
        df = pd.concat([df, pd.DataFrame([yeni_satir])], ignore_index=True)
        
    df.to_csv(DB_FILE, index=False)
    st.sidebar.success("İşlem başarıyla tamamlandı!")
    st.rerun()

# --- ANA PANELLER ---
tab_liste, tab_istatistik, tab_yonetim, tab_rapor = st.tabs([
    "📋 Kayıt Listesi", 
    "📊 Mağaza İstatistikleri", 
    "⚙️ Düzenle/Sil", 
    "📥 Rapor Al"
])

# (Diğer sekmelerin kodları öncekiyle aynı şekilde çalışmaya devam eder)
with tab_liste:
    if not df.empty:
        arama = st.text_input("🔍 Hızlı Ara (İsim)").upper()
        filtrelenmis = df[df["Optisyen Adı"].str.contains(arama)]
        st.dataframe(filtrelenmis, use_container_width=True)
    else:
        st.info("Kayıt bulunamadı.")

with tab_istatistik:
    st.subheader("🏬 Mağaza Bazlı Dağılım")
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric("Toplam Optisyen", df["Optisyen Adı"].nunique())
        c2.metric("Aktif Mağaza Sayısı", df["Mağaza"].nunique())
        c3.metric("Genel Puan Ort.", round(df["Puan"].mean(), 2))
        
        magaza_ozet = df.groupby("Mağaza").agg({"Optisyen Adı": "nunique", "Puan": "mean"}).rename(columns={"Optisyen Adı": "Çalışan Sayısı", "Puan": "Ort. Puan"})
        st.bar_chart(magaza_ozet["Çalışan Sayısı"])
        st.table(magaza_ozet)

with tab_yonetim:
    for idx, r in df.iterrows():
        c_m, c_e, c_d = st.columns([3, 1, 1])
        c_m.write(f"**{r['Optisyen Adı']}** - {r['Mağaza']}")
        if c_e.button("✏️ Düzenle", key=f"e_{idx}"):
            st.session_state.edit_index = idx
            st.rerun()
        if c_d.button("🗑️ Sil", key=f"d_{idx}"):
            df.drop(idx).to_csv(DB_FILE, index=False)
            st.rerun()

with tab_rapor:
    if not df.empty:
        buf = BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        st.download_button("💾 Excel İndir", buf.getvalue(), "Optisyen_Raporu.xlsx")
