import streamlit as st
import pandas as pd
import random
import io

st.set_page_config(page_title="Niğde Vardiya Paneli", layout="wide")

st.title("📄 Niğde Şubeleri Haftalık Tek Liste")
st.markdown("4 Personel için 8.5 saat sınırına uygun haftalık plan.")

# Ayarlar
subeler = ["Niğde 1", "Niğde 2", "Niğde 3"]
gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
saatler = ["05:30", "07:30", "13:30", "14:30"]

# Personel Listesi (4 Kişi)
st.sidebar.header("Personel Yönetimi")
personel_input = st.sidebar.text_area("Personel İsimleri (4 kişi):", "Ahmet, Ayşe, Mehmet, Fatma")
personeller = [p.strip() for p in personel_input.split(",") if p.strip()][:4]

if len(personeller) < 4:
    st.error("Lütfen en az 4 personel ismi giriniz.")
else:
    if st.button("🗓️ Haftalık Tabloyu Oluştur"):
        data = []
        
        for gun in gunler:
            # Her gün için personelleri karıştır
            gunluk_personel = personeller.copy()
            random.shuffle(gunluk_personel)
            
            # 4 personel olduğu için dağılım mantığı:
            # P1 -> Niğde 1 (Sabah), P2 -> Niğde 2 (Sabah), P3 -> Niğde 3 (Öğle), P4 -> Gezici/Yedek
            plan = {
                "Gün": gun,
                "Niğde 1 (05:30 - 14:00)": gunluk_personel[0],
                "Niğde 2 (07:30 - 16:00)": gunluk_personel[1],
                "Niğde 3 (13:30 - 22:00)": gunluk_personel[2],
                "Yedek/İzinli (14:30 - 23:00)": gunluk_personel[3]
            }
            data.append(plan)
        
        df = pd.DataFrame(data)
        
        # Tek bir büyük tablo olarak göster
        st.subheader("📋 Haftalık Çalışma Çizelgesi")
        st.table(df)
        
        st.info("💡 Not: Mesai süreleri günlük 8.5 saati geçmeyecek şekilde (yarım saat mola dahil) ayarlanmıştır.")

        # Excel Çıktısı
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Haftalik_Plan')
            
        st.download_button(
            label="📥 Listeyi Excel (Yazdırılabilir) Olarak İndir",
            data=buffer.getvalue(),
            file_name="nigde_haftalik_vardiya.xlsx",
            mime="application/vnd.ms-excel"
        )

st.markdown("""
---
**Vardiya Saatleri ve Kurallar:**
* **05:30 Giriş:** 14:00 Çıkış (8.5 Saat)
* **07:30 Giriş:** 16:00 Çıkış (8.5 Saat)
* **13:30 Giriş:** 22:00 Çıkış (8.5 Saat)
* **14:30 Giriş:** 23:00 Çıkış (8.5 Saat)
* *Her personel günde sadece bir şubede görev alır.*
""")
