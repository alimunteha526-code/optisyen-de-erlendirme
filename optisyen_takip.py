import streamlit as st
import openpyxl
from openpyxl.utils import get_column_letter
import io

st.set_page_config(page_title="Zayi Raporu - Stil Koruyucu", layout="centered")

st.title("📊 Cam Zayi Raporu - Biçim Onarıcı")
st.markdown("---")
st.info("Bu mod, Excel'deki dikey yazıları ve özel renkleri (kırmızı/yeşil) olduğu gibi korur.")

# Görseldeki mağaza kodları
istenen_magazalar = [
    "M38003", "M51001", "M42004", "M51002", "M38001", "M38005", 
    "M68001", "M42006", "M42002", "M46001", "M38002", "M42001", 
    "M40001", "M42005", "M38004", "M70001", "M50001"
]

uploaded_file = st.file_uploader("Bozuk çıkan orijinal Excel'i yükleyin", type=['xlsx'])

if uploaded_file is not None:
    try:
        # 1. Dosyayı openpyxl ile (biçimleri koruyarak) yükle
        wb = openpyxl.load_workbook(uploaded_file, data_only=False)
        ws = wb.active

        # 2. Başlık ve "Üst Birim" sütununu bul
        # Görsellerde Üst Birim genellikle C sütununda (3. sütun)
        target_col_idx = 3 
        header_row = 1
        
        found = False
        for r in range(1, 15):
            for c in range(1, 10):
                if "ÜST BIRIM" in str(ws.cell(r, c).value).upper():
                    header_row = r
                    target_col_idx = c
                    found = True
                    break
            if found: break

        # 3. İLK İKİ SÜTUNU SİL (A ve B sütunlarını siler)
        # Stil bozulmaması için doğrudan sütun silme komutu kullanılır
        ws.delete_cols(1, 2)
        target_col_idx -= 2 # Sütunlar kaydığı için takip indeksini güncelle

        # 4. MAĞAZALARI FİLTRELE (İstenmeyen satırları sil)
        # Excel'de satır silerken sondan başa gitmek kaymaları önler
        max_row = ws.max_row
        for row_num in range(max_row, header_row, -1):
            cell_value = str(ws.cell(row_num, target_col_idx).value).strip()
            
            # Eğer hücre boşsa veya listede yoksa satırı sil
            if cell_value not in istenen_magazalar:
                ws.delete_rows(row_num)

        # 5. DOSYAYI HAZIRLA
        output = io.BytesIO()
        wb.save(output)
        processed_data = output.getvalue()

        st.success("✅ Dosya başarıyla onarıldı! Renkler ve biçimler korundu.")
        
        st.download_button(
            label="📥 Onarılmış Excel'i İndir",
            data=processed_data,
            file_name="Onarilmis_Zayi_Raporu.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"İşlem sırasında bir hata oluştu: {e}")
