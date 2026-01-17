import streamlit as st
import openpyxl
import io

# Sayfa Ayarları
st.set_page_config(page_title="Zayi Raporu - Birebir Onarım", layout="wide")

st.title("📊 Cam Zayi Raporu - Birebir Görünüm")
st.info("💡 Bu mod, dikey yazıları, renkli grupları ve mağaza isimlerini orijinal dosyanızdaki gibi korur.")

# Filtrelenecek mağaza listesi
istenen_magazalar = [
    "M38003", "M51001", "M42004", "M51002", "M38001", "M38005", 
    "M68001", "M42006", "M42002", "M46001", "M38002", "M42001", 
    "M40001", "M42005", "M38004", "M70001", "M50001"
]

uploaded_file = st.file_uploader("Orijinal Excel dosyasını yükleyin", type=['xlsx'])

if uploaded_file is not None:
    try:
        # 1. Dosyayı TÜM biçim özellikleriyle yükle
        wb = openpyxl.load_workbook(uploaded_file, data_only=False)
        ws = wb.active

        # 2. SOLDAKİ GRUPLANDIRMALARI (+/-) KALDIR
        ws.sheet_format.outlineLevelRow = 0
        ws.sheet_format.outlineLevelCol = 0
        for r in range(1, ws.max_row + 1):
            ws.row_dimensions[r].outline_level = 0
            ws.row_dimensions[r].hidden = False

        # 3. BAŞLIK VE ÜST BİRİM TESPİTİ
        header_row = 1
        ub_col_idx = 1
        found = False
        for r in range(1, 30):
            for c in range(1, 15):
                cell_val = str(ws.cell(r, c).value).strip().upper()
                if "ÜST BIRIM" in cell_val:
                    header_row = r
                    ub_col_idx = c
                    found = True
                    break
            if found: break

        # 4. SOLDAKİ GEREKSİZ SÜTUNLARI SİL (Bölge/Müdür)
        if ub_col_idx > 1:
            ws.delete_cols(1, ub_col_idx - 1)
            ub_col_idx = 1 # Artık Üst Birim 1. sütun

        # 5. ÜSTTEKİ BOŞLUKLARI SİL
        if header_row > 1:
            ws.delete_rows(1, header_row - 1)
            header_row = 1

        # 6. MAĞAZALARI FİLTRELE (CERRAHİ TEMİZLİK)
        # Mağaza isimlerinin gitmemesi için sadece listede olmayan satırları siliyoruz
        max_row = ws.max_row
        # Sondan başa doğru silmek Excel hücre birleşmelerini daha az bozar
        for r in range(max_row, header_row, -1):
            cell_content = str(ws.cell(r, 1).value).strip()
            
            # Eğer hücre boş değilse ve bir mağaza kodu içeriyorsa
            if cell_content != "None" and len(cell_content) >= 5:
                # Bizim listemizde olmayan bir mağaza ise satırı komple sil
                if not any(magaza in cell_content for magaza in istenen_magazalar):
                    ws.delete_rows(r)
            elif cell_content == "None":
                # Eğer tamamen boş bir satırsa (başlık harici) temizle
                if r > header_row:
                    ws.delete_rows(r)

        # 7. GÖRSEL DÜZENLEME (Mavi Başlık Yüksekliği)
        # Orijinal dikey yazıların sığması için yüksekliği koru
        ws.row_dimensions[1].height = 70 
        ws.column_dimensions['A'].width = 20 # İsimlerin sığması için A sütununu genişlet

        # 8. ÇIKTI
        output = io.BytesIO()
        wb.save(output)
        
        st.success("✅ İşlem tamamlandı! Orijinal renkler ve mağaza isimleri korundu.")
        
        st.download_button(
            label="📥 Birebir Görünümlü Excel'i İndir",
            data=output.getvalue(),
            file_name="Zayi_Raporu_Birebir_Son.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Hata oluştu: {e}")
