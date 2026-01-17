import streamlit as st
import openpyxl
import io

# Sayfa Yapılandırması
st.set_page_config(page_title="Zayi Raporu - Birleştirmesiz", layout="wide")

st.title("📊 Cam Zayi Raporu - Saf Veri Düzeni")
st.info("✅ 'Birleştir ve Ortala' özellikleri kaldırıldı. Her veri kendi hücresine ayrıldı.")

# Mağaza Kodları ve İsimleri
magaza_sozlugu = {
    "M38001": "KAYSERI PARK AVM", "M38002": "KAYSERI MEYSU OUTLET AVM",
    "M38003": "FORUM KAYSERI AVM", "M38004": "KAYSERI KUMSMALL AVM",
    "M38005": "KAYSERI TUNALIFE AVM", "M42001": "NOVADA KONYA OUTLET AVM",
    "M42002": "KONYA KENT PLAZA AVM", "M42004": "M1 KONYA AVM",
    "M42005": "KONYA KAZIMKARABEKIR CADDE", "M42006": "KONYA ENNTEPE AVM",
    "M51001": "NIGDE CADDE", "M51002": "NIGDE TEMA PARK AVM",
    "M68001": "AKSARAY NORA CITY AVM", "M40001": "KIRSEHIR CADDE",
    "M46001": "MARAS PIAZZA AVM", "M70001": "PARK KARAMAN AVM",
    "M50001": "NEVSEHIR NISSARA AVM"
}

uploaded_file = st.file_uploader("Orijinal Excel dosyasını yükleyin", type=['xlsx'])

if uploaded_file is not None:
    try:
        wb = openpyxl.load_workbook(uploaded_file, data_only=False)
        ws = wb.active

        # 1. TÜM BİRLEŞTİRİLMİŞ HÜCRELERİ ÇÖZ (Unmerge)
        # Bu işlem 'Birleştir ve Ortala' yapılmış tüm hücreleri bağımsız hale getirir.
        merged_cells_range = list(ws.merged_cells.ranges)
        for cell_group in merged_cells_range:
            ws.unmerge_cells(str(cell_group))

        # 2. Gruplandırma (+/-) Butonlarını Temizle
        ws.sheet_format.outlineLevelRow = 0
        for r in range(1, ws.max_row + 1):
            ws.row_dimensions[r].outline_level = 0

        # 3. Başlık ve Üst Birim Tespiti
        header_row, ub_col_idx = 1, 1
        found = False
        for r in range(1, 30):
            for c in range(1, 15):
                val = str(ws.cell(r, c).value).strip().upper()
                if "ÜST BIRIM" in val:
                    header_row, ub_col_idx, found = r, c, True
                    break
            if found: break

        # 4. Sol Sütunları ve Üst Boşlukları Sil
        if ub_col_idx > 1:
            ws.delete_cols(1, ub_col_idx - 1)
        if header_row > 1:
            ws.delete_rows(1, header_row - 1)
            header_row = 1

        # 5. Mağazaları Filtrele ve İsimleri Yaz
        max_row = ws.max_row
        for r in range(max_row, header_row, -1):
            m_kodu = str(ws.cell(r, 1).value).strip()
            
            if m_kodu in magaza_sozlugu:
                ws.cell(row=r, column=2).value = magaza_sozlugu[m_kodu]
            elif m_kodu != "None" and len(m_kodu) >= 5:
                ws.delete_rows(r)
            elif m_kodu == "None" or m_kodu == "":
                if r > header_row: ws.delete_rows(r)

        # 6. Görsel Düzenlemeler
        ws.row_dimensions[1].height = 60
        ws.column_dimensions['A'].width = 12
        ws.column_dimensions['B'].width = 30
        
        # Birleştirme kalktığı için başlıkları tekrar ortalayalım (Hücre bazında)
        for cell in ws[1]:
            cell.alignment = openpyxl.styles.Alignment(horizontal='center', vertical='center', wrapText=True)

        output = io.BytesIO()
        wb.save(output)
        
        st.success("✅ Tüm birleştirmeler kaldırıldı ve rapor hazırlandı.")
        st.download_button(
            label="📥 Birleştirmesiz Excel'i İndir",
            data=output.getvalue(),
            file_name="Zayi_Raporu_Unmerged.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Hata: {e}")
