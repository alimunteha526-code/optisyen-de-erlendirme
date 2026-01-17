import streamlit as st
import openpyxl
from openpyxl.utils import get_column_letter
import io

# Sayfa Yapılandırması
st.set_page_config(page_title="Zayi Raporu - Birebir Biçim", layout="centered")

st.title("📊 Cam Zayi Raporu - Birebir Görünüm")
st.info("Bu sürüm; sütun genişliklerini, renkli grupları ve dikey yazıları orijinal dosyanızdan birebir kopyalar.")

# Görseldeki tam mağaza listesi
istenen_magazalar = [
    "M38003", "M51001", "M42004", "M51002", "M38001", "M38005", 
    "M68001", "M42006", "M42002", "M46001", "M38002", "M42001", 
    "M40001", "M42005", "M38004", "M70001", "M50001"
]

uploaded_file = st.file_uploader("Orijinal Excel dosyasını yükleyin", type=['xlsx'])

if uploaded_file is not None:
    try:
        # 1. Dosyayı tüm biçim özellikleriyle yükle (data_only=False biçimleri korur)
        wb = openpyxl.load_workbook(uploaded_file, data_only=False)
        ws = wb.active

        # 2. GRUPLANDIRMA BUTONLARINI (+/-) KALDIR
        # Sol taraftaki seviye çizgilerini ve butonları tamamen temizler
        ws.sheet_format.outlineLevelRow = 0
        ws.sheet_format.outlineLevelCol = 0
        for r in range(1, ws.max_row + 1):
            ws.row_dimensions[r].outline_level = 0
            ws.row_dimensions[r].hidden = False

        # 3. "Üst Birim" Başlığını ve Sütununu Tespit Et
        header_row = 1
        ub_col_idx = 1
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

        # 4. SOLDAKİ GEREKSİZ SÜTUNLARI SİL (Bölge/Müdür)
        # Rapor doğrudan Üst Birim ile başlasın
        if ub_col_idx > 1:
            ws.delete_cols(1, ub_col_idx - 1)
        
        # 5. ÜSTTEKİ BOŞ SATIRLARI SİL
        # Mavi başlığı sayfanın en üstüne taşır
        if header_row > 1:
            ws.delete_rows(1, header_row - 1)
            header_row = 1 

        # 6. MAĞAZALARI FİLTRELE (Listede olmayanları temizle)
        # Sondan başa silme işlemi tablo yapısını bozmaz
        max_row = ws.max_row
        for r in range(max_row, header_row, -1):
            m_kodu = str(ws.cell(r, 1).value).strip()
            
            # Eğer satır bir mağaza kodu içeriyorsa ve bizim listemizde yoksa sil
            if m_kodu not in istenen_magazalar and m_kodu != "None" and len(m_kodu) > 2:
                ws.delete_rows(r)

        # 7. MAVİ BAŞLIK YÜKSEKLİĞİNİ DÜZENLE
        # Görseldeki pürüzsüz görünüm için satır yüksekliğini sabitliyoruz
        ws.row_dimensions[1].height = 65 

        # 8. ÇIKTIYI HAZIRLA
        output = io.BytesIO()
        wb.save(output)
        
        st.success("✅ İşlem tamamlandı! Orijinal renkler ve sütun genişlikleri korundu.")
        
        st.download_button(
            label="📥 Birebir Görünümlü Excel'i İndir",
            data=output.getvalue(),
            file_name="Zayi_Raporu_Birebir_Final.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Bir hata oluştu: {e}")
