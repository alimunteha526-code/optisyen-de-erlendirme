import streamlit as st
import openpyxl
import io

st.set_page_config(page_title="Zayi Raporu - Biçim Koruyucu", layout="centered")

st.title("📊 Cam Zayi Raporu - Tam Biçim Korumalı")
st.info("Bu yöntemle Excel'deki tüm orijinal renkler, çizgiler ve fontlar birebir korunur.")

# Mağaza Listesi
istenen_magazalar = [
    "M38003", "M51001", "M42004", "M51002", "M38001", "M38005", 
    "M68001", "M42006", "M42002", "M46001", "M38002", "M42001", 
    "M40001", "M42005", "M38004", "M70001", "M50001"
]

uploaded_file = st.file_uploader("Orijinal Excel dosyasını yükleyin", type=['xlsx'])

if uploaded_file is not None:
    try:
        # 1. Dosyayı openpyxl ile aç (Biçimleri korumak için en iyi yol)
        wb = openpyxl.load_workbook(uploaded_file, data_only=False) # Formülleri değil biçimi koru
        ws = wb.active

        # 2. ÜST BİRİM sütununu ve Başlık satırını bul
        start_row = 1
        ub_col_idx = 3 # Varsayılan olarak 3. sütun (C)
        
        found = False
        for row in range(1, 20):
            for col in range(1, 10):
                val = str(ws.cell(row, col).value).upper()
                if "ÜST BIRIM" in val:
                    start_row = row
                    ub_col_idx = col
                    found = True
                    break
            if found: break

        # 3. İLK İKİ SÜTUNU SİL (A ve B sütunlarını siler)
        # Not: İlk sütunu sildiğimizde diğeri 1. sütun olur, bu yüzden iki kez 1 siliyoruz.
        ws.delete_cols(1, 2)
        ub_col_idx -= 2 # Sütunlar kaydığı için indeksi güncelliyoruz

        # 4. İSTENMEYEN SATIRLARI SİL
        # Sondan başa doğru silmek Excel yapısını bozmaz
        max_row = ws.max_row
        for r in range(max_row, start_row, -1):
            cell_val = str(ws.cell(r, ub_col_idx).value).strip()
            if cell_val not in istenen_magazalar:
                ws.delete_rows(r)

        # 5. BAŞLIK ÜSTÜNDEKİ BOŞLUKLARI SİL (Opsiyonel)
        if start_row > 1:
            ws.delete_rows(1, start_row - 1)

        # 6. KAYDETME (Belleğe yazma)
        output = io.BytesIO()
        wb.save(output)
        
        st.success("✅ Orijinal biçimler korundu, gereksiz satır ve sütunlar temizlendi.")
        
        st.download_button(
            label="📥 Orijinal Biçimli Excel'i İndir",
            data=output.getvalue(),
            file_name="zayi_raporu_orijinal_stil.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Sistem Hatası: {e}")
