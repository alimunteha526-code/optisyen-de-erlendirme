import streamlit as st
import pandas as pd
import os
from io import BytesIO

# --- AYARLAR VE VERİ TABANI ---
DB_FILE = "optisyen_veritabanı.csv"

def veriyi_yukle():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Tarih", "Optisyen Adı", "Mağaza", "Puan", "Değerlendirme Notu"])

st.set_page_config(page_title="Optisyen Yönetim Sistemi", layout="wide")

# Türkçe büyük harf fonksiyonu
def turkce_buyuk(metin):
    if not metin: return ""
    return metin.replace('i', 'İ').replace('ı', 'I').upper()

# Veriyi çek
df = veriyi_yukle()

# --- BAŞLIK ---
st.title("👓 Optisyen Değerlendirme ve İstatistik Paneli")

# --- 📊 İSTATİSTİK BÖLÜMÜ (YENİ) ---
if not df.empty:
    st.subheader("📊 Genel İstatistikler")
    col_toplam, col_magaza_sayisi, col_ortalama = st.columns(3)
    
    # Toplam Benzersiz Optisyen Sayısı
    toplam_optisyen = df["Optisyen Adı"].nunique()
    # Toplam Benzersiz Mağaza Sayısı
    toplam_magaza = df["Mağaza"].nunique()
    # Genel Puan Ortalaması
    genel_ort = df["Puan"].mean()

    col_toplam.metric("Toplam Optisyen Sayısı", f"{toplam_optisyen} Kişi")
    col_magaza_sayisi.metric("Toplam Mağaza Sayısı", f"{toplam_magaza}")
    col_ortalama.metric("Genel Puan Ortalaması", f"{genel_ort:.2f} / 10")

    # Mağaza Bazlı Dağılım Grafiği
    st.write("---")
    st.subheader("🏬 Mağaza Bazlı Optisyen Dağılımı")
    # Her mağazadaki BENZERSİZ optisyen sayısını hesapla
    magaza_dagilimi = df.groupby("Mağaza")["Optisyen Adı"].nunique()
    st.bar_chart(magaza_dagilimi)
    st.write("---")

# --- SOL PANEL: VERİ GİRİŞİ / DÜZENLEME ---
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

st.sidebar.header("📝 Veri İşlemleri")

default_name = ""
default_magaza = ""
default_puan = 7
default_not = ""

if st.session_state.edit_index is not None:
    row = df.iloc[st.session_state.edit_index]
    default_name = row["Optisyen Adı"]
    default_magaza = row["Mağaza"]
    default_puan = int(row["Puan"])
    default_not = row["Değerlendirme Notu"]

with st.sidebar.form("optisyen_form"):
    isim_input = st.text_input("Optisyen Adı Soyadı", value=default_name)
    magaza_input = st.text_input("Çalıştığı Mağaza", value=default_magaza)
    puan = st.slider("Performans Puanı", 1, 10, default_puan)
    notlar_input = st.text_area("Notlar", value=default_not)
    tarih = st.date_input("Tarih")
    
    submit_label = "Değişiklikleri Kaydet" if st.session_state.edit_index is not None else "Sisteme Kaydet"
    kaydet = st.form_submit_button(submit_label)

if kaydet:
    if isim_input and magaza_input:
        yeni_satir = {
            "Tarih": str(tarih),
            "Optisyen Adı": turkce_buyuk(isim_input),
            "Mağaza": turkce_buyuk(magaza_input),
            "Puan": puan,
            "Değerlendirme Notu": turkce_buyuk(notlar_input)
        }
        if st.session_state.edit_index is not None:
            df.iloc[st.session_state.edit_index] = yeni_satir
            st.session_state.edit_index = None
        else:
            df = pd.concat([df, pd.DataFrame([yeni_satir])], ignore_index=True)
        df.to_csv(DB_FILE, index=False)
        st.rerun()

# --- ANA SEKMELER ---
tab1, tab2, tab3 = st.tabs(["📋 Tüm Kayıtlar & Filtre", "⚙️ Kayıt Düzenle / Sil", "📥 Rapor Al"])

with tab1:
    if not df.empty:
        kayitli_isimler = sorted(df["Optisyen Adı"].unique())
        secilen_isimler = st.multiselect("Optisyen Seç", options=kayitli_isimler)
        filtrelenmis_df = df if not secilen_isimler else df[df["Optisyen Adı"].isin(secilen_isimler)]
        st.dataframe(filtrelenmis_df, use_container_width=True)
    else:
        st.info("Veri yok.")

with tab2:
    if not df.empty:
        for index, row in df.iterrows():
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(f"**{row['Optisyen Adı']}** ({row['Mağaza']})")
            if c2.button("✏️ Düzenle", key=f"e_{index}"):
                st.session_state.edit_index = index
                st.rerun()
            if c3.button("🗑️ Sil", key=f"d_{index}"):
                df = df.drop(index).to_csv(DB_FILE, index=False)
                st.rerun()

with tab3:
    if not df.empty:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Rapor')
        st.download_button("Excel İndir", output.getvalue(), "Optisyen_Raporu.xlsx")
