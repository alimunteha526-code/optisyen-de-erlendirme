import pandas as pd
import random

# 1. Veri Hazırlığı: Şubeler ve Çalışan Listesi
subeler = ["Kadıköy Şubesi", "Beşiktaş Şubesi", "Şişli Şubesi"]
calisanlar = [
    "Ahmet", "Ayşe", "Mehmet", "Fatma", "Can", 
    "Ece", "Ali", "Zeynep", "Burak", "Deniz", 
    "Selin", "Mert"
]

def vardiya_olustur(calisan_listesi, sube_listesi):
    # Listeyi karıştırarak her seferinde farklı sonuç alalım
    random.shuffle(calisan_listesi)
    
    plan = []
    index = 0
    
    # Her şubeye 4 kişi atayacak şekilde (2 Sabah, 2 Akşam) bir döngü
    for sube in sube_listesi:
        # Sabah Vardiyası (Örnek: 2 kişi)
        sabah = calisan_listesi[index:index+2]
        index += 2
        
        # Akşam Vardiyası (Örnek: 2 kişi)
        aksam = calisan_listesi[index:index+2]
        index += 2
        
        plan.append({
            "Şube": sube,
            "Sabah Vardiyası (08:00 - 16:00)": ", ".join(sabah),
            "Akşam Vardiyası (16:00 - 00:00)": ", ".join(aksam)
        })
    
    return pd.DataFrame(plan)

# Programı çalıştır ve sonucu göster
vardiya_tablosu = vardiya_olustur(calisanlar, subeler)

print("--- Haftalık Şube Vardiya Planı ---")
print(vardiya_tablosu.to_string(index=False))

# İstersen Excel'e de aktarabilirsin
# vardiya_tablosu.to_excel("vardiya_plani.xlsx", index=False)
