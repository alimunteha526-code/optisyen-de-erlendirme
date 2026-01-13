import streamlit as st
import pandas as pd
import os
from io import BytesIO

# --- AYARLAR VE VERİ TABANI ---
DB_FILE = "optisyen_veritabani.csv"

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
default_name, default_magaza, default_puan, default_not = "", "", 7, ""
if st.session_state.edit_index is not None:
    row = df.iloc[st.session_state.edit_index]
    default_name, default_magaza, default_puan, default_not = row["Optisyen Adı"], row["Mağaza"], int(row["Puan"]), row["Değerlendirme Notu"]

with st.sidebar.form("optisyen_form"):
    isim_input = st.text_input("Optisyen Adı Soyadı", value=default_name)
    magaza_input = st.text_input("Çalıştığı Mağaza", value=default_magaza)
    puan = st.slider("Performans Puanı", 1, 10, default_puan)
    notlar_input = st.text_area("Notlar", value=default_not)
    tarih = st.date_input("Tarih")
    kaydet = st.form_submit_button("Sisteme Kaydet")

if kaydet and isim_input and magaza_input:
    yeni_satir = {"Tarih": str(tarih), "Optisyen Adı": turkce_buyuk(isim_input), "Mağaza": turkce_buyuk(magaza_input), "Puan": puan, "Değerlendirme Notu": turkce_buyuk(notlar_input)}
    if st.session_state.edit_index is not None:
        df.iloc[st.session_state.edit_index] = yeni_satir
        st.session_state.edit_index = None
    else:
        df = pd.concat([df, pd.DataFrame([yeni_satir])], ignore_index=True)
    df.to_csv(DB_FILE, index=False)
    st.rerun()

# --- ANA PANELLER (YENİ SEKME DÜZENİ) ---
tab_liste, tab_istatistik, tab_yonetim, tab_rapor = st.tabs([
    "📋 Kayıt Listesi", 
    "📊 Mağaza İstatistikleri", 
    "⚙️ Düzenle/Sil", 
    "📥 Rapor Al"
])

with tab_liste:
    if not df.empty:
        arama = st.text_input("🔍 Hızlı Ara (İsim veya Mağaza)").upper()
        filtrelenmis = df[df.apply(lambda r: arama in str(r.values).upper(), axis=1)]
        st.dataframe(filtrelenmis, use_container_width=True)
    else:
        st.info("Kayıt bulunamadı.")

with tab_istatistik:
    st.subheader("🏬 Mağaza Bazlı Dağılım ve Özet")
    if not df.empty:
        # Üst Metrikler
        c1, c2, c3 = st.columns(3)
        c1.metric("Toplam Optisyen", df["Optisyen Adı"].nunique())
        c2.metric("Toplam Mağaza", df["Mağaza"].nunique())
        c3.metric("Ortalama Puan", round(df["Puan"].mean(), 2))

        st.divider()

        # Mağaza Bazlı Tablo ve Grafik
        col_grafik, col_tablo = st.columns([2, 1])
        
        # Mağaza verilerini hazırla
        magaza_ozet = df.groupby("Mağaza").agg({
            "Optisyen Adı": "nunique",
            "Puan": "mean"
        }).rename(columns={"Optisyen Adı": "Optisyen Sayısı", "Puan": "Puan Ortalaması"})

        with col_grafik:
            st.write("**Mağaza Bazlı Çalışan Sayısı Grafiği**")
            st.bar_chart(magaza_ozet["Optisyen Sayısı"])

        with col_tablo:
            st.write("**Mağaza Detay Listesi**")
            st.table(magaza_ozet)
    else:
        st.warning("İstatistik oluşturmak için henüz yeterli veri yok.")

with tab_yonetim:
    if not df.empty:
        for idx, r in df.iterrows():
            col_metin, col_edit, col_del = st.columns([3, 1, 1])
            col_metin.write(f"**{r['Optisyen Adı']}** - {r['Mağaza']}")
            if col_edit.button("✏️ Düzenle", key=f"edit_{idx}"):
                st.session_state.edit_index = idx
                st.rerun()
            if col_del.button("🗑️ Sil", key=f"del_{idx}"):
                df.drop(idx).to_csv(DB_FILE, index=False)
                st.rerun()

with tab_rapor:
    if not df.empty:
        buf = BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        st.download_button("💾 Excel Dosyasını İndir", buf.getvalue(), "Optisyen_Raporu.xlsx")
