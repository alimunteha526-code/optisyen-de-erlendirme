import streamlit as st
import pandas as pd
import random
import io

st.set_page_config(page_title="Niğde Şube Vardiya Paneli", layout="wide")

st.title("🏪 Niğde Şubeleri Haftalık Vardiya Sistemi")
st.markdown("4 Personel | 3 Şube | Hafta İçi 1 Gün İzin | Max 8.5 Saat Çalışma")

# Ayarlar
sube_listesi = ["Niğde 1", "Niğde 2", "Niğde 3"]
gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
mesai_saatleri = ["05:30 - 14:00", "07:30 - 16:00", "13:30 - 22:00", "14:30 - 23:00"]

# Personel Girişi
st.sidebar.header("Personel Yönetimi")
personel_input = st.sidebar.text_area("4 Personel İsmi (Virgülle ayırın):", "Ahmet, Ayşe, Mehmet, Fatma")
personeller = [p.strip() for p in personel_input.split(",") if p.strip()][:4]

if len(personeller) < 4:
    st.error("Lütfen tam olarak 4 personel ismi giriniz.")
else:
    if st.button("🗓️ Haftalık Planı Oluştur"):
        # Boş haftalık matris
        haftalik_matris = {p: {g: "" for g in gunler} for p in personeller}
        
        # 1. Hafta İçi İzin Atama (Pzt-Cum arası her personele 1 gün)
        is_gunleri = gunler[:5]
        random.shuffle(is_gunleri)
        for i, p in enumerate(personeller):
            haftalik_matris[p][is_gunleri[i]] = "İZİNLİ"

        # 2. Şubelere Dağıtım
        for g in gunler:
            aktif_personeller = [p for p in personeller if haftalik_matris[p][g] != "İZİNLİ"]
            random.shuffle(aktif_personeller)
            
            for idx, p in enumerate(aktif_personeller):
                # 4. kişi olduğunda (hafta sonu) o kişiyi Niğde 1'e veya seçili bir şubeye 2. kişi olarak atar
                s_index = idx if idx < 3 else 0 # 4. kişi varsa Niğde 1'e (indeks 0) destek gider
                saat = mesai_saatleri[idx]
                haftalik_matris[p][g] = f"{sube_listesi[s_index]} ({saat})"

        # Arayüz: Şube Bazlı Sekmeler
        tabs = st.tabs([f"📍 {s}" for s in sube_listesi] + ["📋 Genel Liste"])

        for i, sube in enumerate(sube_listesi):
            with tabs[i]:
                st.subheader(f"{sube} Şubesi Haftalık Tablosu")
                sube_verisi = []
                for g in gunler:
                    # Bu şubede o gün çalışanları bul (Birden fazla kişi olabilir)
                    calisanlar = []
                    saatler = []
                    for p in personeller:
                        if sube in haftalik_matris[p][g]:
                            calisanlar.append(p)
                            saatler.append(haftalik_matris[p][g].split("(")[1].replace(")", ""))
                    
                    sube_verisi.append({
                        "Gün": g,
                        "Personel": ", ".join(calisanlar) if calisanlar else "KAPALI/BOŞ",
                        "Mesai Saati": ", ".join(saatler) if saatler else "-"
                    })
                st.table(pd.DataFrame(sube_verisi))

        with tabs[3]:
            st.subheader("Tüm Personel Dağılım Özeti")
            st.dataframe(pd.DataFrame(haftalik_matris).T)

        # Excel Export
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            pd.DataFrame(haftalik_matris).T.to_excel(writer, sheet_name='Genel_Ozet')
            for sube in sube_listesi:
                temp_list = []
                for g in gunler:
                    for p in personeller:
                        if sube in haftalik_matris[p][g]:
                            temp_list.append([g, p, haftalik_matris[p][g].split("(")[1].replace(")", "")])
                pd.DataFrame(temp_list, columns=["Gün", "Personel", "Saat"]).to_excel(writer, sheet_name=sube, index=False)

        st.sidebar.success("✅ Plan hazırlandı.")
        st.sidebar.download_button(
            label="📥 Excel Olarak İndir",
            data=output.getvalue(),
            file_name="nigde_vardiya_listesi.xlsx",
            mime="application/vnd.ms-excel"
        )

st.info("Not: Hafta sonu 4 kişi de çalıştığı için bir şubede iki personel (farklı saatlerde) görünebilir.")
