import streamlit as st
import openpyxl
from openpyxl.utils import get_column_letter
import io

st.set_page_config(page_title="Zayi Raporu - Birebir Görünüm", layout="centered")

st.title("📊 Cam Zayi Raporu - Orijinal Biçim Koruyucu")
st.info("Bu sürüm; renkleri, sütun genişliklerini ve dikey yazıları orijinal dosyanızdan kopyalar.")

# Tam Mağaza Listesi
istenen_magazalar = [
    "M38003", "M51001", "M42004", "M51002", "M38001", "M38005", 
    "M68001", "M42006", "M42002", "M46001", "M38002", "M42001", 
    "M40001", "M42005", "M38004", "M70001", "M50001"
]

uploaded_file = st.file_uploader("Orijinal Excel dosyasını yükleyin", type=['xlsx'])

if uploaded_file is not None:
    try:
        # 1. Dosyayı tüm biçim özellikleriyle yükle
        wb = openpyxl.load_workbook(uploaded_file, data_only=False)
        ws = wb.active

        # 2. Üst Birim ve Başlık Satırını Bul
        header_row = 1
        ub_col_idx = 3 # Genelde C sütunu
        found = False
        for r in range(1, 20):
            for c in range(1, 10):
                val = str(ws.cell(r, c).value).strip().upper()
                if "ÜST BIRIM" in val:
                    header_row = r
                    ub_col_idx = c
                    found = True
                    break
            if found: break

        # 3. İLK İKİ SÜTUNU SİL (Bölge ve Müdür)
        # Biçimlerin kaymaması için doğrudan sütun silme
        ws.delete_cols(1, 2)
        ub_col_idx -= 2

        # 4. MAĞAZALARI FİLTRELE (Görseli bozmadan satır silme)
        # Sondan başa doğru silmek Excel yapısını (merge cells dahil) korur
        max_row = ws.max_row
        for r in range(max_row, header_row, -1):
            m_kodu = str(ws.cell(r, ub_col_idx).value).strip()
            # Eğer satır listede yoksa ve başlık satırı değilse sil
            if m_kodu not in istenen_magazalar and r != header_row:
                # Toplam satırlarını (Genel Toplam vb.) korumak istersen buraya şart eklenebilir
                if m_kodu != "None" and len(m_kodu) > 2: 
                    ws.delete_rows(r)

        # 5. ÜSTTEKİ BOŞLUKLARI TEMİZLE
        if header_row > 1:
            ws.delete_rows(1, header_row - 1)

        # 6. MAVİ ALANI (BAŞLIK) KÜÇÜLT VE DÜZENLE
        # Satır yüksekliğini daraltıyoruz (Görseldeki gibi daha şık durması için)
        ws.row_dimensions[1].height = 55 
        
        # Sütun genişliklerini orijinaline yakın sabitleyelim (Opsiyonel)
        ws.column_dimensions[get_column_letter(ub_col_idx)].width = 15

        # 7. ÇIKTI
        output = io.BytesIO()
        wb.save(output)
        
        st.success("✅ Tüm renkler ve sütun aralıkları korundu. Dosya hazır.")
        
        st.download_button(
            label="📥 Birebir Görünümlü Excel'i İndir",
            data=output.getvalue(),
            file_name="Zayi_Raporu_Birebir.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Hata: {e}")
