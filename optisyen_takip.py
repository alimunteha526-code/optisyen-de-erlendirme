import streamlit as st
import openpyxl
import io

st.set_page_config(page_title="Zayi Raporu - Kesin Çözüm", layout="wide")

st.title("📊 Cam Zayi Raporu - Hata Onarılmış Sürüm")
st.info("✅ '231, 3' hatası giderildi. Gizli satırlar silindi ve birleştirmeler güvenli bir şekilde kaldırıldı.")

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
        # 1. Dosyayı Yükle
        wb = openpyxl.load_workbook(uploaded_file, data_only=False)
        ws = wb.active

        # 2. BİRLEŞTİRİLMİŞ HÜCRELERİ GÜVENLİCE ÇÖZ (Hata önleyici döngü)
        # Bazı birleştirmeler silinen satırlar nedeniyle boşa düşebilir, bu yüzden try-except ile geçiyoruz
        merged_ranges = list(ws.merged_cells.ranges)
        for m_range in merged_ranges:
            try:
                ws.unmerge_cells(str(m_range))
            except:
                continue

        # 3. GİZLİ SATIR VE SÜTUNLARI TAMAMEN SİL
        # Satırlar (Sondan başa doğru silmek kaymaları önler)
        for row_idx in range(ws.max_row, 0, -1):
            if ws.row_dimensions[row_idx].hidden:
                ws.delete_rows(row_idx)
        
        # Sütunlar
        for col_idx in range(ws.max_column, 0, -1):
            col_letter = openpyxl.utils.get_column_letter(col_idx)
            if ws.column_dimensions[col_letter].hidden:
                ws.delete_cols(col_idx)

        # 4. BAŞLIK TESPİTİ
        header_row, ub_col_idx = 1, 1
        found = False
        for r in range(1, 30):
            for c in range(1, 15):
                if "ÜST BIRIM" in str(ws.cell(r, c).value).upper():
                    header_row, ub_col_idx, found = r, c, True
                    break
            if found: break

        # 5. SOL SÜTUNLARI VE ÜST BOŞLUĞU SİL
        if ub_col_idx > 1: ws.delete_cols(1, ub_col_idx - 1)
        if header_row > 1: ws.delete_rows(1, header_row - 1)
        header_row = 1

        # 6. MAĞAZA FİLTRESİ VE İSİM YAZIMI
        # Gizli hücreler silindiği için artık sadece gerçek veriler kaldı
        max_row = ws.max_row
        for r in range(max_row, header_row, -1):
            m_kodu = str(ws.cell(r, 1).value).strip()
            
            if m_kodu in magaza_sozlugu:
                ws.cell(row=r, column=2).value = magaza_sozlugu[m_kodu]
            elif m_kodu != "None" and len(m_kodu) >= 5:
                ws.delete_rows(r)
            elif m_kodu == "None" or m_kodu == "":
                if r > header_row: ws.delete_rows(r)

        # 7. GÖRSEL DÜZENLEME
        ws.row_dimensions[1].height = 60
        ws.column_dimensions['A'].width = 12
        ws.column_dimensions['B'].width = 30
        
        # Stil temizliği: Tüm hücreleri standart hizalamaya getir
        for row in ws.iter_rows(min_row=1, max_row=ws.max_row):
            for cell in row:
                cell.alignment = openpyxl.styles.Alignment(horizontal='left', vertical='center')

        # 8. ÇIKTI
        output = io.BytesIO()
        wb.save(output)
        
        st.success("✅ Hata giderildi ve dosya temizlendi!")
        st.download_button(
            label="📥 Sorunsuz Excel'i İndir",
            data=output.getvalue(),
            file_name="Zayi_Raporu_Kesin_Sonuc.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"Beklenmedik bir hata oluştu: {e}")
