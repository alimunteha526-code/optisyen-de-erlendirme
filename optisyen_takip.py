import streamlit as st
import pandas as pd
import random
import io

# Sayfa Ayarları
st.set_page_config(page_title="Niğde Şubeleri Vardiya Paneli", layout="wide")

st.title("🏪 Niğde Şubeleri Haftalık Vardiya Planlayıcı")
st.markdown("Personel listesini güncelleyip 'Vardiya Oluştur' butonuna basınız.")

# Yan Menü (Ayarlar)
st.sidebar.header("⚙️ Planlama Ayarları")

# Şube isimleri sabitlendi
sube_isimleri = ["Niğde 1", "Niğde 2", "Niğde 3"]
gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

# Personel giriş alanı
varsayilan_personel = "Ahmet, Ayşe, Mehmet, Fatma, Can, Ece, Ali, Zeynep, Burak, Deniz, Selin, Mert, Kerem, Aslı, Murat"
personel_input = st.sidebar.text_area("Personel Listesi (Virgülle ayırarak yazın):", varsayilan_personel, height=200)

personel_listesi = [p.strip() for p in personel_input.split(",") if p.strip()]

if st.sidebar.button("🗓️ Haftalık Vardiyayı Oluştur"):
    if len(personel_listesi) < 6:
        st.error("⚠️ Hata: 3 şube için en az 6 personel girilmelidir.")
    else:
        haftalik_kayitlar = []
        
        # Günlere göre sekmeler oluştur
        tabs = st.tabs(gunler)
        
        for gun_index, gun in enumerate(gunler):
            with tabs[gun_index]:
                st.subheader(f"📅 {gun} Günü Planı")
                
                # Her gün için listeyi karıştır (Adil dağılım)
                gunluk_liste = personel_listesi.copy()
                random.shuffle(gunluk_liste)
                
                # Personeli 3 şubeye paylaştır
                pay = len(gunluk_liste) // 3
                
                gunluk_ozet = []
                
                for i in range(3):
                    bas = i * pay
                    son = (i + 1) * pay if i < 2 else len(gunluk_liste)
                    sube_personeli = gunluk_liste[bas:son]
                    
                    # Şube personelini Sabah/Akşam olarak böl
                    orta = len(sube_personeli) // 2
                    sabah = sube_personeli[:orta]
                    aksam = sube_personeli[orta:]
                    
                    sabah_str = ", ".join(sabah) if sabah else "Boş"
                    aksam_str = ", ".join(aksam) if aksam else "Boş"
                    
                    gunluk_ozet.append({
                        "Şube Adı": sube_isimleri[i],
                        "Sabah (09:00 - 17:00)": sabah_str,
                        "Akşam (14:00 - 22:00)": aksam_str
                    })
                    
                    # Excel için veriyi sakla
                    haftalik_kayitlar.append([gun, sube_isimleri[i], "Sabah", sabah_str])
                    haftalik_kayitlar.append([gun, sube_isimleri[i], "Akşam", aksam_str])
                
                # Tabloyu ekranda göster
                st.table(pd.DataFrame(gunluk_ozet))

        # Excel İndirme İşlemi
        df_export = pd.DataFrame(haftalik_kayitlar, columns=["Gün", "Şube", "Vardiya", "Personel"])
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_export.to_excel(writer, index=False, sheet_name='Nigde_Vardiya_Plani')
        
        st.sidebar.markdown("---")
        st.sidebar.download_button(
            label="📥 Haftalık Planı Excel Olarak İndir",
            data=buffer.getvalue(),
            file_name="nigde_subeleri_vardiya.xlsx",
            mime="application/vnd.ms-excel"
        )
        st.sidebar.success("✅ Plan başarıyla hazırlandı.")

else:
    st.info("Sol taraftaki ayarları kontrol edip butona basarak haftalık planı oluşturabilirsiniz.")

# Alt Bilgi
st.markdown("---")
st.caption("Not: Sistem her gün için personelleri rastgele dağıtır. Eğer özel bir gün için değişim yapmak isterseniz butona tekrar basarak listeyi yeniden karıştırabilirsiniz.")
