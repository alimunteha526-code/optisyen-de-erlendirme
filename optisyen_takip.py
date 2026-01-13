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

st.set_page_config(page_title="Optisyen Değerlendirme Sistemi", layout="wide")

# Türkçe büyük harf fonksiyonu
def turkce_buyuk(metin):
    if not metin: return ""
    return metin.replace('i', 'İ').replace('ı', 'I').upper()

# Veriyi çek
df = veriyi_yukle()

# --- BAŞLIK ---
st.title("👓 Optisyen Değerlendirme ve Yönetim Paneli")

# --- SOL PANEL: VERİ GİRİŞİ / DÜZENLEME ---
st.sidebar.header("📝 Veri Giriş & Düzenleme")

# Düzenleme modunda mıyız kontrol et (Session State kullanımı)
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

# Form alanları için varsayılan değerleri belirle
default_name = ""
default_magaza = ""
default_puan = 7
default_not = ""

if st.session_state.edit_index is not None:
    st.sidebar.warning("Şu an bir kaydı DÜZENLİYORSUNUZ.")
    row = df.iloc[st.session_state.edit_index]
    default_name = row["Optisyen Adı"]
    default_magaza = row["Mağaza"]
    default_puan = int(row["Puan"])
    default_not = row["Değerlendirme Notu"]

with st.sidebar.form("optisyen_form"):
    isim_input = st.text_input("Optisyen Adı Soyadı", value=default_name)
    magaza_input = st.text_input("Çalıştığı Mağaza", value=default_magaza)
    puan = st.slider("Performans Puanı", 1, 10, default_puan)
    notlar_input = st.text_area("Yönetici Notu", value=default_not)
    tarih = st.date_input("Tarih")
    
    submit_label = "Değişiklikleri Kaydet" if st.session_state.edit_index is not None else "Sisteme Kaydet"
    kaydet = st.form_submit_button(submit_label)

if kaydet:
    if isim_input and magaza_input:
        isim_buyuk = turkce_buyuk(isim_input)
        magaza_buyuk = turkce_buyuk(magaza_input)
        notlar_buyuk = turkce_buyuk(notlar_input)

        yeni_satir = {
            "Tarih": str(tarih),
            "Optisyen Adı": isim_buyuk,
            "Mağaza": magaza_buyuk,
            "Puan": puan,
            "Değerlendirme Notu": notlar_buyuk
        }

        if st.session_state.edit_index is not None:
            # Düzenleme modundaysak mevcut satırı güncelle
            df.iloc[st.session_state.edit_index] = yeni_satir
            st.session_state.edit_index = None
            st.sidebar.success("Kayıt başarıyla güncellendi!")
        else:
            # Yeni kayıt ekle
            df = pd.concat([df, pd.DataFrame([yeni_satir])], ignore_index=True)
            st.sidebar.success("Yeni kayıt eklendi!")
        
        df.to_csv(DB_FILE, index=False)
        st.rerun()

# İptal butonu (Sadece düzenleme modundaysa görünür)
if st.session_state.edit_index is not None:
    if st.sidebar.button("Düzenlemeyi İptal Et"):
        st.session_state.edit_index = None
        st.rerun()

# --- ANA PANEL ---
tab1, tab2, tab3 = st.tabs(["📊 Veri Tablosu", "⚙️ Kayıtları Yönet (Sil/Değiştir)", "📑 Rapor Al"])

with tab1:
    if not df.empty:
        # Filtreleme bölümü
        col1, col2 = st.columns(2)
        with col1:
            secilen_isimler = st.multiselect("Optisyen Filtresi", options=sorted(df["Optisyen Adı"].unique()))
        with col2:
            secilen_magazalar = st.multiselect("Mağaza Filtresi", options=sorted(df["Mağaza"].unique()))

        filtrelenmis_df = df.copy()
        if secilen_isimler: filtrelenmis_df = filtrelenmis_df[filtrelenmis_df["Optisyen Adı"].isin(secilen_isimler)]
        if secilen_magazalar: filtrelenmis_df = filtrelenmis_df[filtrelenmis_df["Mağaza"].isin(secilen_magazalar)]

        st.dataframe(filtrelenmis_df, use_container_width=True)
    else:
        st.info("Henüz veri girilmemiş.")

with tab2:
    st.subheader("🗑️ Sil ve ✏️ Değiştir")
    if not df.empty:
        for index, row in df.iterrows():
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.write(f"**{row['Optisyen Adı']}** | {row['Mağaza']} | Puan: {row['Puan']}")
            
            # DEĞİŞTİR BUTONU
            if c2.button("✏️ DEĞİŞTİR", key=f"edit_{index}"):
                st.session_state.edit_index = index
                st.rerun()
            
            # SİL BUTONU
            if c3.button("🗑️ SİL", key=f"del_{index}"):
                df = df.drop(index)
                df.to_csv(DB_FILE, index=False)
                st.warning("Kayıt silindi.")
                st.rerun()
    else:
        st.info("İşlem yapılacak kayıt bulunamadı.")

with tab3:
    if not df.empty:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Rapor')
        st.download_button(label="💾 Excel Olarak İndir", data=output.getvalue(), file_name="Rapor.xlsx")
