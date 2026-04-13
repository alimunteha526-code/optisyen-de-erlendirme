import streamlit as st
import pandas as pd
import random
from st_aggrid import AgGrid, GridOptionsBuilder # pip install st-aggrid
from weasyprint import HTML # PDF için
import base64

st.set_page_config(page_title="Niğde Şube Vardiya Paneli", layout="wide")

st.title("📅 Gelişmiş Şube Vardiya Paneli")
st.markdown("Her gün 1 kişi izinli olacak şekilde ayarlanmıştır. Tablo üzerinde değişiklik yapabilirsiniz.")

# --- YAN MENÜ ---
st.sidebar.header("🏢 Şube Ayarları")
s1_isim = st.sidebar.text_input("1. Şube Adı:", "Niğde 1")
s1_personel = st.sidebar.text_area(f"{s1_isim} Personelleri (4 kişi önerilir):", "Ahmet, Ayşe, Mehmet, Fatma")

gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
mesai_saatleri = ["05:30 - 14:00", "07:30 - 16:00", "13:30 - 22:00", "14:30 - 23:00"]

def vardiya_olustur(p_listesi, s_adi):
    personeller = [p.strip() for p in p_listesi.split(",") if p.strip()]
    if len(personeller) < 4: return None
    
    # Boş tablo
    df = pd.DataFrame(index=personeller, columns=gunler)
    
    # Her gün için tam 1 kişi izinli atama
    izin_sirasi = list(range(len(personeller)))
    random.shuffle(izin_sirasi)
    
    for g_idx, gun in enumerate(gunler):
        # Her gün için sırayla birine izin ver (7 gün olduğu için döngüsel)
        izinli_kisi_idx = g_idx % len(personeller)
        izinli_personel = personeller[izinli_kisi_idx]
        
        df.at[izinli_personel, gun] = "İZİNLİ"
        
        # Diğerlerine mesai ata
        aktifler = [p for p in personeller if p != izinli_personel]
        random.shuffle(aktifler)
        for m_idx, p in enumerate(aktifler):
            saat = mesai_saatleri[m_idx % len(mesai_saatleri)]
            df.at[p, gun] = f"{s_adi} ({saat})"
    return df

# --- PDF OLUŞTURMA FONKSİYONU ---
def create_pdf(df, title):
    html_content = f"""
    <html>
    <head>
        <style>
            table {{ width: 100%; border-collapse: collapse; font-family: Arial; font-size: 10px; }}
            th, td {{ border: 1px solid black; padding: 8px; text-align: center; }}
            th {{ background-color: #f2f2f2; }}
            .header {{ text-align: center; font-size: 18px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="header">{title} Haftalık Vardiya Çizelgesi</div>
        {df.to_html()}
    </body>
    </html>
    """
    return html_content

# --- ÇALIŞTIR ---
if st.sidebar.button("🚀 Vardiyayı Taslak Olarak Oluştur"):
    st.session_state['data_df'] = vardiya_olustur(s1_personel, s1_isim)

if 'data_df' in st.session_state:
    st.subheader("✍️ Tabloyu Düzenle (Hücreye çift tıklayarak değiştirebilirsiniz)")
    
    # Düzenlenebilir Tablo Ayarları
    gb = GridOptionsBuilder.from_dataframe(st.session_state['data_df'].reset_index())
    gb.configure_default_column(editable=True, sortable=True)
    grid_options = gb.build()
    
    response = AgGrid(
        st.session_state['data_df'].reset_index(),
        gridOptions=grid_options,
        update_mode='MODEL_CHANGED',
        data_return_mode='AS_INPUT',
        theme='alpine',
    )
    
    updated_df = response['data']
    
    # PDF İndirme Butonu
    if st.button("📄 PDF Olarak İndir"):
        html_string = create_pdf(updated_df, s1_isim)
        # Not: PDF üretimi için lokalde weasyprint kurulu olmalıdır. 
        # Alternatif olarak HTML indirme sunulabilir:
        st.download_button(
            label="HTML/PDF Taslağını İndir",
            data=html_string,
            file_name="vardiya.html",
            mime="text/html"
        )
        st.success("PDF taslağı hazır! (Not: PDF'e dönüştürmek için bu dosyayı tarayıcıda açıp Yazdır -> PDF diyebilirsiniz)")
