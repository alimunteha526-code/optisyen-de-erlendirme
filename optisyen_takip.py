import streamlit as st
import pandas as pd
import random
import io

# Sayfa Genişliği
st.set_page_config(page_title="Niğde Şube Vardiya Paneli", layout="wide")

st.title("📅 Haftalık Şube Vardiya Çizelgesi")

# --- YAN MENÜ (AYARLAR) ---
st.sidebar.header("⚙️ Ayarlar")

# Şube İsimlerini Düzenleme
s1_isim = st.sidebar.text_input("1. Şube İsmi:", "Niğde 1")
s2_isim = st.sidebar.text_input("2. Şube İsmi:", "Niğde 2")
s3_isim = st.sidebar.text_input("3. Şube İsmi:", "Niğde 3")
sube_listesi = [s1_isim, s2_isim, s3_isim]

# Personel İsimlerini Düzenleme
personel_input = st.sidebar.text_area("Personel İsimleri (4 kişi):", "Ahmet, Ayşe, Mehmet, Fatma")
personeller = [p.strip() for p in personel_input.split(",") if p.strip()][:4]

gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
mesai_saatleri = ["05:30 - 14:00", "07:30 - 16:00", "13:30 - 22:00", "14:30 - 23:00"]

if len(personeller) < 4:
    st.error("Lütfen tam olarak 4 personel giriniz.")
else:
    if st.sidebar.button("🔄 Yeni Vardiya Oluştur"):
        # Haftalık Veri Matrisi
        haftalik_matris = {p: {g: "" for g in gunler} for p in personeller}
        
        # 1. Hafta İçi İzin Atama (Pzt-Cum arası her personele 1 gün)
        is_gunleri = gunler[:5]
        random.shuffle(is_gunleri)
        for i, p in enumerate(personeller):
            haftalik_matris[p][is_gunleri[i]] = "İZİNLİ"

        # 2. Şubelere Dağıtım Mantığı (Görseldeki gibi)
        for g in gunler:
            aktif_personeller = [p for p in personeller if haftalik_matris[p][g] != "İZİNLİ"]
            random.shuffle(aktif_personeller)
            
            for idx, p in enumerate(aktif_personeller):
                # 4. kişi varsa 1. şubeye destek gider (veya döngüsel dağılır)
                s_idx = idx if idx < 3 else 0 
                haftalik_matris[p][g] = f"{sube_listesi[s_idx]} ({mesai_saatleri[idx]})"

        # Session State'e kaydet (Sayfa yenilendiğinde verinin kaybolmaması için)
        st.session_state['vardiya_verisi'] = haftalik_matris

    # Veri varsa göster
    if 'vardiya_verisi' in st.session_state:
        matris = st.session_state['vardiya_verisi']
        
        # Sekmeler
        sekme_isimleri = ["📊 Genel Tablo"] + [f"📍 {s}" for s in sube_listesi]
        tabs = st.tabs(sekme_isimleri)

        # TAB 1: GENEL TABLO (Görseldeki format)
        with tabs[0]:
            st.subheader("Tüm Personel Haftalık Dağılımı")
            df_genel = pd.DataFrame(matris).T
            st.table(df_genel)

        # ŞUBE ÖZEL SEKMELERİ
        for i, sube in enumerate(sube_listesi):
            with tabs[i+1]:
                st.subheader(f"{sube} Haftalık Listesi")
                sube_ozel_liste = []
                for g in gunler:
                    gorevli_bilgisi = []
                    for p in personeller:
                        if sube in matris[p][g]:
                            saat = matris[p][g].split("(")[1].replace(")", "")
                            gorevli_bilgisi.append(f"{p} ({saat})")
                    
                    sube_ozel_liste.append({
                        "Gün": g,
                        "Görevli": " / ".join(gorevli_bilgisi) if gorevli_bilgisi else "PERSONEL YOK"
                    })
                st.table(pd.DataFrame(sube_ozel_liste))

        # Excel İndirme
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            pd.DataFrame(matris).T.to_excel(writer, sheet_name='Genel_Liste')
        
        st.sidebar.download_button(
            label="📥 Excel Olarak İndir",
            data=buffer.getvalue(),
            file_name="sube_vardiya_listesi.xlsx",
            mime="application/vnd.ms-excel"
        )
