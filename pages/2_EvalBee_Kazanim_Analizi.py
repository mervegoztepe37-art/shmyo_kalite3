import io
import pandas as pd
import streamlit as st

st.set_page_config(page_title='SHMYO | EvalBee Kazanım Analizi', layout='wide')
st.title('SHMYO • EvalBee Kazanım Analizi')
st.caption('TLT203 Hematoloji | BŞEÜ EBS 2026–2027 | Pilot modül')
SOURCE='https://ebs.bilecik.edu.tr/Program/DersBilgileri?BolumNo=256&DersNo=11105&Yil=2026'
OUTCOMES={
'DÖÇ-1':'Hematolojinin temel kavramlarının, normal ve patolojik süreçlerini tanımlayabilir.',
'DÖÇ-2':'Kan hücrelerinin yapılarını ve fonksiyonlarını tanımlayabilir.',
'DÖÇ-3':'Kan hücrelerinin yapısal bozukluklarını ve hastalıklarını tanımlayabilir.',
'DÖÇ-4':'Hematoloji laboratuvar testlerini tanımlayabilir ve uygulayabilir.'}
PROGRAM={1:'Mesleki alan bilgisi ve becerileri',4:'Alanına ait temel bilgi ve becerileri kullanabilme',5:'Mesleki problemleri analitik ve eleştirel değerlendirme',11:'Tıbbi laboratuvar ortamını ve işleyişini bilme',12:'Numune kabulü, analiz, raporlama ve sonuç iletme'}
ALL_PCS=list(range(1,14))
st.info('Resmî DÖÇ–PÇ matrisi: dört DÖÇ de PÇ-1, 4, 5, 11, 12 ile 5/5 ilişkili. Bu nedenle bu dersin PÇ başarı yüzdeleri aynı olabilir; program geneli başarısı olarak yorumlanmamalıdır.')
with st.expander('Resmî ders öğrenme çıktıları ve ilişki matrisi'):
    st.dataframe(pd.DataFrame([{'Kod':k,'Çıktı':v,**{f'PÇ-{p}':5 if p in PROGRAM else None for p in ALL_PCS}} for k,v in OUTCOMES.items()]),hide_index=True,use_container_width=True)
    st.markdown(f'[BŞEÜ EBS kaynak sayfası]({SOURCE})')

st.subheader('1 • Soru eşleştirmeleri')
count=st.number_input('Soru sayısı',min_value=1,max_value=200,value=20)
base=pd.DataFrame({'Soru':[f'S{i}' for i in range(1,count+1)],'DÖÇ':[f'DÖÇ-{(i-1)%4+1}' for i in range(1,count+1)],'Puan':[1.0]*count,'Doğru cevap':['A']*count})
mapfile=st.file_uploader('İsteğe bağlı soru eşleştirme CSV/XLSX yükle',type=['csv','xlsx'],key='map')
def read_file(f):
    return pd.read_csv(f) if f.name.lower().endswith('.csv') else pd.read_excel(f)
if mapfile:
    try: base=read_file(mapfile)
    except Exception as e: st.error(f'Eşleştirme dosyası okunamadı: {e}');st.stop()
mapping=st.data_editor(base,hide_index=True,num_rows='dynamic',use_container_width=True)
st.caption('DÖÇ atamaları örnek olarak dağıtılmıştır; gerçek sınav için her sorunun eşleştirmesini ve doğru cevabını düzeltin. Çoklu DÖÇ eşleştirmesi bu pilotta desteklenmiyor.')

st.subheader('2 • EvalBee sonuçlarını yükle')
st.write('Öğrenci cevapları biçimi: `Ogrenci,S1,S2,...` (A/B/C/D/E). Alternatif: 1=doğru, 0=yanlış matrisi. EvalBee dışa aktarma sütunlarını gerekirse bu şablona uyarlayın.')
mode=st.radio('Dosya türü', ['Öğrenci cevapları (A-E)','Doğru/yanlış matrisi (1/0)'],horizontal=True)
file=st.file_uploader('CSV veya Excel sonuç dosyası',type=['csv','xlsx'],key='results')
if st.button('Örnek sonuç şablonunu indir'):
    pass
sample=pd.DataFrame({'Ogrenci':['Örnek-1','Örnek-2'],**{f'S{i}':['A','B'] for i in range(1,count+1)}})
st.download_button('Boş formatı örnekleyen CSV indir',sample.to_csv(index=False).encode('utf-8-sig'),'evalbee_cevap_sablonu.csv','text/csv')
if file:
    try:
        df=read_file(file)
        if 'Ogrenci' not in df.columns: raise ValueError('Ogrenci sütunu bulunamadı')
        if df['Ogrenci'].isna().any() or df['Ogrenci'].duplicated().any(): raise ValueError('Öğrenci kimlikleri boş veya yineleniyor')
        if df.empty: raise ValueError('Öğrenci satırı bulunamadı')
        if not {'Soru','DÖÇ','Puan','Doğru cevap'}.issubset(mapping.columns): raise ValueError('Soru eşleştirme sütunları eksik')
        if mapping['Soru'].duplicated().any(): raise ValueError('Yinelenen soru kodu var')
        if not set(mapping['DÖÇ']).issubset(OUTCOMES): raise ValueError('Tanımsız DÖÇ var')
        if (pd.to_numeric(mapping['Puan'],errors='coerce')<=0).any() or pd.to_numeric(mapping['Puan'],errors='coerce').isna().any(): raise ValueError('Soru puanları pozitif sayılar olmalı')
        if not set(mapping['Soru']).issubset(df.columns): raise ValueError('Cevap dosyasında bazı soru sütunları eksik')
        result=[]
        for _,q in mapping.iterrows():
            s=q['Soru']; answers=df[s]
            if mode.startswith('Öğrenci'):
                correct=str(q['Doğru cevap']).strip().upper()
                if correct not in 'ABCDE' or len(correct)!=1: raise ValueError(f'{s} için doğru cevap A-E arasında olmalı')
                valid=answers.fillna('').astype(str).str.strip().str.upper()
                if not valid.isin(['','A','B','C','D','E']).all(): raise ValueError(f'{s} sütununda geçersiz seçenek')
                scores=(valid==correct).astype(float)
            else:
                valid=pd.to_numeric(answers,errors='coerce')
                if valid.isna().any() or not valid.isin([0,1]).all(): raise ValueError(f'{s} sütununda 0/1 dışı değer var')
                scores=valid.astype(float)
            result.append({'Soru':s,'DÖÇ':q['DÖÇ'],'Puan':float(q['Puan']),'Başarı %':round(100*scores.mean(),2)})
        questions=pd.DataFrame(result)
        doc=questions.groupby('DÖÇ').apply(lambda g: pd.Series({'Başarı %':round((g['Başarı %']*g['Puan']).sum()/g['Puan'].sum(),2),'Soru sayısı':len(g)}),include_groups=False).reset_index()
        pc=[]
        for p in ALL_PCS:
            linked=doc if p in PROGRAM else doc.iloc[:0]
            pc.append({'Program çıktısı':f'PÇ-{p}','Başarı %':round((linked['Başarı %']*linked['Soru sayısı']).sum()/linked['Soru sayısı'].sum(),2) if len(linked) else None,'Durum':'Bu sınavla ölçülmedi' if not len(linked) else 'Ders düzeyi gösterge'})
        pcs=pd.DataFrame(pc)
        st.subheader('3 • Analiz sonuçları')
        st.metric('Öğrenci sayısı',len(df))
        st.write('Soru bazlı başarı');st.dataframe(questions,hide_index=True,use_container_width=True)
        st.write('Ders öğrenme çıktısı başarısı');st.dataframe(doc,hide_index=True,use_container_width=True)
        st.bar_chart(doc.set_index('DÖÇ')['Başarı %'])
        st.write('Program çıktısına katkı göstergesi');st.dataframe(pcs,hide_index=True,use_container_width=True)
        st.caption('PÇ yüzdeleri, bu dersin sorularından türetilen dolaylı göstergedir; doğrudan tüm programın çıktı kazanımı değildir. Resmî ilişki katsayıları bu ders için 5/5 ve aynıdır.')
        output=io.BytesIO()
        with pd.ExcelWriter(output,engine='openpyxl') as writer:
            questions.to_excel(writer,sheet_name='Soru Analizi',index=False)
            doc.to_excel(writer,sheet_name='DÖÇ Analizi',index=False)
            pcs.to_excel(writer,sheet_name='PÇ Göstergesi',index=False)
            mapping.to_excel(writer,sheet_name='Eşleştirme',index=False)
        st.download_button('Analiz raporunu Excel indir',output.getvalue(),'hematoloji_kazanim_analizi.xlsx','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e: st.error(f'Veri doğrulama hatası: {e}')
