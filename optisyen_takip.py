import streamlit as st
import pandas as pd
import random
import io

st.set_page_config(page_title="Niğde Şube Vardiya Sistemi", layout="wide")

st.title("📄 Niğde Şubeleri Haftalık Vardiya Planı")
st.markdown("4 Personel, 3 Şube. Herkes hafta içi 1 gün izinli ve günlük max 8.5 saat mesai.")

# Sabitler
sube_listesi = ["Niğde 1", "Niğde 2", "Niğde 3"]
gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
mesai_saatleri = ["05:30 - 14:00", "07:30 - 16:00", "13:30 - 22:00", "14:30 - 23:00"]

# Personel Girişi
st.sidebar.header("Personel Listesi")
personel_input = st.sidebar.text_area("4 Personel Yazın (Virgülle ayırın):", "Ahmet, Ayşe, Mehmet, Fatma")
personeller = [p.strip() for p in personel_input.split(",") if p.strip()][:4]

if len(personeller) < 4:
    st.error("Lütfen tam olarak 4 personel ismi giriniz.")
else:
    if st.button("🗓️ Yeni Haftalık Plan Oluştur"):
        # Haftalık ana veri yapısı
        # { 'Personel': { 'Pazartesi': 'Şube/Saat', ... } }
        haftalik_matris = {p: {g: "" for g in gunler} for p in personeller}
        
        # 1. İzin Atama (Hafta içi 5 gün, 4 personel için her güne bir izin veya boşluk)
        is_gunleri = gunler[:5] # Pzt - Cum
        random.shuffle(is_gunleri)
        for i, p in enumerate(personeller):
            haftalik_matris[p][is_gunleri[i]] = "İZİNLİ"

        # 2. Şube ve Mesai Atama
        for g in gunler:
            aktif_personeller = [p for p in personeller if haftalik_matris[p][g] != "İZİNLİ"]
            random.shuffle(aktif_personeller)
            
            # Eğer o gün herkes çalışıyorsa (Hafta sonu), 4. kişi yedek olur
            # Eğer 3 kişi çalışıyorsa (Hafta içi izin durumu), her biri bir şubeye gider
            for idx, p in enumerate(aktif_personeller):
                if idx < 3: # İlk 3 kişi şubelere
                    haftalik_matris[p][g] = f"{sube_listesi[idx]} ({mesai_saatleri[idx]})"
                else: # 4. kişi varsa (Hafta sonu) yedek/destek
                    haftalik_matris[p][g] = f"Destek/Yedek ({mesai_saatleri[3]})"

        # Görselleştirme: Şube Bazlı Sekmeler
        tabs = st.tabs([f"📍 {s}" for s in sube_listesi] + ["👤 Tüm Personel Özeti"])

        # Şube Sekmeleri
        for i, sube in enumerate(sube_listesi):
            with tabs[i]:
                st.subheader(f"{sube} Haftalık Çizelgesi")
                sube_data = []
                for g in gunler:
                    gorevli = "Atanmadı"
                    saat = ""
                    for p in personeller:
                        if sube in haftalik_matris[p][g]:
                            gorevli = p
                            saat = haftalik_matris[p][g].split("(")[1].replace(")", "")
                    sube_data.append({"Gün": g, "Görevli Personel": gorevli, "Mesai Saati": saat})
                st.table(pd.DataFrame(sube_data))

        # Genel Özet Sekmesi
        with tabs[3]:
            st.subheader("Tüm Personel Dağılımı")
            df_genel = pd.DataFrame(haftalik_matris).T
            st.dataframe(df_genel)

        # Excel Çıktısı Hazırlama
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_genel.to_excel(writer, sheet_name='Genel_Ozet')
            # Şube bazlı sayfalar ekle
            for sube in sube_listesi:
                temp_list = []
                for g in gunler:
                    for p in personeller:
                        if sube in haftalik_matris[p][g]:
                            temp_list.append([g, p, haftalik_matris[p][g]])
                pd.DataFrame(temp_list, columns=["Gün", "Personel", "Vardiya"]).to_excel(writer, sheet_name=sube, index=False)
        
        st.download_button(
            label="📥 Haftalık Planı Excel Olarak İndir",
            data=output.getvalue(),
            file_name="nigde_sube_haftalik_plan.xlsx",
            mime="application/vnd.ms-excel"
        )
