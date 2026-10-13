import io
import re
import pandas as pd
import streamlit as st
from docx import Document

st.set_page_config(page_title='Word Toplu Soru Aktarımı', page_icon='📄', layout='wide')
st.title('📄 Word Belgesinden Toplu Soru Aktarımı')
st.warning('Pilot sürüm: Öğrenci adı, numarası veya başka kişisel veri içeren belgeleri yüklemeyin. Bu sayfa soruları kalıcı veritabanına kaydetmez.')
st.caption('Birden çok kitapçık içeren belgelerde her kitapçık ayrı değerlendirilir. Görsellerin bulunduğu sorular elle kontrol edilmelidir.')

QUESTION = re.compile(r'^\s*(\d{1,3})\s*[).]\s*(.+)$')
OPTION = re.compile(r'^\s*([A-E])\s*[).]\s*(.*)$', re.I)
HEAD = re.compile(r'HEMATOLOJİ DERSİ VİZE SINAVI|^SORULAR\s*$', re.I)

def parse_docx(blob):
    doc = Document(io.BytesIO(blob))
    books, current, item = [], [], None
    for p in doc.paragraphs:
        s = ' '.join(p.text.split())
        if not s:
            continue
        if HEAD.search(s):
            if current:
                books.append(current)
                current = []
                item = None
            continue
        q = QUESTION.match(s)
        opt = OPTION.match(s)
        if q:
            if item:
                current.append(item)
            number = int(q.group(1))
            if current and number == 1:
                books.append(current)
                current = []
            item = {'Soru No': number, 'Soru': q.group(2), **{c:'' for c in 'ABCDE'}, 'Doğru Cevap':'', 'DÖÇ':'', 'Bloom':'', 'Kontrol':'Bekliyor'}
        elif opt and item is not None:
            item[opt.group(1).upper()] = opt.group(2)
        elif item is not None:
            # Soru veya şık metni birden fazla paragrafta devam edebilir.
            filled = [c for c in 'ABCDE' if item[c]]
            if filled:
                item[filled[-1]] += ' ' + s
            else:
                item['Soru'] += ' ' + s
    if item:
        current.append(item)
    if current:
        books.append(current)
    return books, len(doc.part.rels)

uploaded = st.file_uploader('Word sınav belgesini seçin', type=['docx'])
if uploaded:
    try:
        books, _ = parse_docx(uploaded.getvalue())
    except Exception as e:
        st.error(f'Dosya okunamadı: {e}')
        st.stop()
    if not books:
        st.error('Soru algılanamadı. Soruların 1) veya 1. biçiminde numaralanmış olması gerekir.')
        st.stop()
    st.success(f'{len(books)} soru grubu/kitapçık adayı, toplam {sum(len(b) for b in books)} soru kaydı bulundu.')
    idx = st.selectbox('Kitapçık/grup seçin', range(len(books)), format_func=lambda x: f'Grup {x+1} ({len(books[x])} soru)')
    df = pd.DataFrame(books[idx])
    st.info('Aşağıdaki tabloyu kontrol edin. Görsel içeren sorularda görseller henüz aktarılmaz; cevap anahtarını ve DÖÇ eşleştirmesini elle girin. Aynı sorunun farklı kitapçıklardaki kopyaları otomatik birleştirilmez.')
    edited = st.data_editor(df, num_rows='dynamic', use_container_width=True, key=f'edit_{uploaded.name}_{idx}', column_config={'Doğru Cevap':st.column_config.SelectboxColumn('Doğru Cevap', options=['','A','B','C','D','E']), 'Bloom':st.column_config.SelectboxColumn('Bloom',options=['','Hatırlama','Anlama','Uygulama','Analiz','Değerlendirme','Yaratma']), 'Kontrol':st.column_config.SelectboxColumn('Kontrol',options=['Bekliyor','Onaylandı','Düzeltilecek'])})
    incomplete = edited[edited[['A','B','C','D','E']].apply(lambda r:any(not str(v).strip() for v in r),axis=1)]
    if len(incomplete):
        st.warning(f'{len(incomplete)} kayıtta eksik seçenek var. İndirmeden önce kontrol edin.')
    csv = edited.to_csv(index=False).encode('utf-8-sig')
    st.download_button('Düzenlenen soruları CSV indir',csv,file_name=f'hematoloji_kitapcik_{idx+1}.csv',mime='text/csv')
    out=io.BytesIO()
    with pd.ExcelWriter(out,engine='openpyxl') as writer:
        edited.to_excel(writer,index=False,sheet_name='Sorular')
    st.download_button('Düzenlenen soruları Excel indir',out.getvalue(),file_name=f'hematoloji_kitapcik_{idx+1}.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    st.caption('Bu sayfa mevcut soru bankasına otomatik kayıt yapmaz. Sonraki sürümde ortak veritabanı bağlantısı eklenecektir.')
