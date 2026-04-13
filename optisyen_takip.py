import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Niğde Vardiya Paneli", layout="wide")

st.title("📅 Niğde Şubeleri Vardiya Paneli")
st.markdown("Tablo üzerinde istediğiniz değişikliği yapabilirsiniz. Her gün 1 kişi izinlidir.")

# --- AYARLAR ---
st.sidebar.header("🏢 Şube ve Personel")
s_isim = st.sidebar.text_input("Şube Adı:", "Niğde 1")
p_input = st.sidebar.text_area("Personel İsimleri (4 kişi):", "Ahmet, Ayşe, Mehmet, Fatma")

gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
mesai_saatleri = ["05:30 - 14:00", "07:30 - 16:00", "13:30 - 22:00", "14:30 - 23:00"]

personeller = [p.strip() for p in p_input.split(",") if p.strip()]

def vardiya_uret():
    if len(personeller) < 4:
        return None
    
    df = pd.DataFrame(index=personeller, columns=gunler)
    
    # Her gün için tam 1 kişi izinli atama algoritması
    for g_idx, gun in enumerate(gunler):
        izinli_idx = g_idx % len(personeller)
        izinli_p = personeller[izinli_idx]
        df.at[izinli_p, gun] = "İZİNLİ"
        
        aktifler = [p for p in personeller if p != izinli_p]
        random.shuffle(aktifler)
        for m_idx, p in enumerate(aktifler):
            df.at[p, gun] = f"{s_isim} ({mesai_saatleri[m_idx]})"
    return df

# --- ÇALIŞTIRMA ---
if st.sidebar.button("🔄 Yeni Taslak Oluştur"):
    st.session_state['v_tablosu'] = vardiya_uret()

if 'v_tablosu' in st.session_state:
    st.subheader("✍️ Vardiya Çizelgesi (Düzenlemek için hücreye tıklayın)")
    
    # STREAMLIT'IN KENDİ DÜZENLEYİCİSİ (Hata vermeyen yöntem)
    duzenlenmis_df = st.data_editor(st.session_state['v_tablosu'], use_container_width=True)
    
    st.divider()
    
    # PDF alternatifi olarak Excel ve Yazdırma görünümü
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 Excel Olarak İndir",
            data=duzenlenmis_df.to_csv().encode('utf-8-sig'),
            file_name=f"{s_isim}_vardiya.csv",
            mime="text/csv"
        )
    with col2:
        st.info("💡 PDF almak için: Tabloyu seçip kopyalayın ve Excel/Word'e yapıştırıp PDF kaydedin veya sayfayı yazdır (CTRL+P) diyerek PDF seçin.")

else:
    st.info("Lütfen yan menüden personelleri kontrol edip 'Yeni Taslak Oluştur' butonuna basın.")
