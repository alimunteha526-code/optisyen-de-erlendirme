import streamlit as st
import pandas as pd
import random
import io

st.set_page_config(page_title="Niğde Şubeleri Personel Yönetimi", layout="wide")

st.title("📅 Şube Bazlı Haftalık Vardiya Sistemi")
st.markdown("Hücrelere çift tıklayarak **manuel değişiklik** yapabilirsiniz. Her gün tam 1 kişi izinli olacak şekilde ayarlanmıştır.")

# --- YAN MENÜ (AYARLAR) ---
st.sidebar.header("🏢 Şube ve Personel Tanımlama")

# Şube Ayarları
s1_isim = st.sidebar.text_input("1. Şube Adı:", "Niğde 1")
s1_personel = st.sidebar.text_area(f"{s1_isim} Personelleri:", "Ahmet, Ayşe, Mehmet, Fatma")

s2_isim = st.sidebar.text_input("2. Şube Adı:", "Niğde 2")
s2_personel = st.sidebar.text_area(f"{s2_isim} Personelleri:", "Can, Ece, Ali, Zeynep")

s3_isim = st.sidebar.text_input("3. Şube Adı:", "Niğde 3")
s3_personel = st.sidebar.text_area(f"{s3_isim} Personelleri:", "Burak, Deniz, Selin, Mert")

gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
# 8.5 saat sınırına uygun mesai saatleri
mesai_saatleri = ["05:30 - 14:00", "07:30 - 16:00", "13:30 - 22:00", "14:30 - 23:00"]

def vardiya_hesapla(p_listesi, s_adi):
    # Temiz liste oluştur
    personeller = [p.strip() for p in p_listesi.split(",") if p.strip()]
    if len(personeller) < 4:
        st.warning(f"{s_adi} için en az 4 personel girilmelidir.")
        return pd.DataFrame(columns=gunler)
    
    matris = {p: {g: "" for g in gunler} for p in personeller}
    
    # Her gün için TAM 1 KİŞİ İZİNLİ atama (Döngüsel ve adil)
    for g_idx, gun in enumerate(gunler):
        # 7 gün boyunca her gün bir sonraki kişi izinli olur
        izinli_idx = g_idx % len(personeller)
        izinli_p = personeller[izinli_idx]
        
        matris[izinli_p][gun] = "İZİNLİ"
        
        # Diğer çalışanlara mesai saatlerini ata
        aktifler = [p for p in personeller if p != izinli_p]
        random.shuffle(aktifler)
        for m_idx, p in enumerate(aktifler):
            saat = mesai_saatleri[m_idx % len(mesai_saatleri)]
            matris[p][gun] = f"{s_adi} ({saat})"
            
    return pd.DataFrame(matris).T

# --- ANA EKRAN ---
if st.sidebar.button("🚀 Tüm Şubelerin Vardiyasını Oluştur"):
    st.session_state['s1_df'] = vardiya_hesapla(s1_personel, s1_isim)
    st.session_state['s2_df'] = vardiya_hesapla(s2_personel, s2_isim)
    st.session_state['s3_df'] = vardiya_hesapla(s3_personel, s3_isim)
    st.success("Vardiya taslakları oluşturuldu! Tablolara tıklayarak düzenleyebilirsiniz.")

# Tabloları Sekmelerde ve Düzenlenebilir Formda Göster
if 's1_df' in st.session_state:
    tabs = st.tabs([f"📍 {s1_isim}", f"📍 {s2_isim}", f"📍 {s3_isim}"])
    
    # Düzenlenen verileri saklamak için değişkenler
    with tabs[0]:
        st.subheader(f"{s1_isim} - Haftalık Çizelge")
        df1_edit = st.data_editor(st.session_state['s1_df'], key="editor1", use_container_width=True)
        
    with tabs[1]:
        st.subheader(f"{s2_isim} - Haftalık Çizelge")
        df2_edit = st.data_editor(st.session_state['s2_df'], key="editor2", use_container_width=True)
        
    with tabs[2]:
        st.subheader(f"{s3_isim} - Haftalık Çizelge")
        df3_edit = st.data_editor(st.session_state['s3_df'], key="editor3", use_container_width=True)

    # Excel İndirme İşlemi (Düzenlenmiş halleriyle)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df1_edit.to_excel(writer, sheet_name=s1_isim[:31])
        df2_edit.to_excel(writer, sheet_name=s2_isim[:31])
        df3_edit.to_excel(writer, sheet_name=s3_isim[:31])
    
    st.sidebar.markdown("---")
    st.sidebar.download_button(
        label="📥 Güncel Listeyi Excel İndir",
        data=buffer.getvalue(),
        file_name="nigde_sube_vardiya_listesi.xlsx",
        mime="application/vnd.ms-excel"
    )
    
    st.info("💡 **PDF Almak İçin:** Tabloyu düzenledikten sonra klavyeden **CTRL + P** tuşlarına basarak 'PDF Olarak Kaydet' seçeneğini kullanabilirsiniz.")
else:
    st.info("Lütfen yan menüden personel isimlerini kontrol edip 'Vardiyayı Oluştur' butonuna basın.")
