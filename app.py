import streamlit as st
st.set_page_config(page_title='SHMYO | Ölçme ve Değerlendirme', page_icon='🎓',layout='wide')
st.title('🎓 SHMYO Ölçme, Değerlendirme ve Kazanım Analizi')
st.write('Sınav yönetimi ile EvalBee sonuçlarını ders ve program çıktılarıyla eşleştirme modülleri tek web arayüzünde.')
st.warning('Bu sürüm pilot prototiptir. Gerçek öğrenci kimlikleri veya kişisel verileri yüklemeyin. Kullanıcı yetkilendirme ve kurumsal güvenlik henüz eklenmedi.')
a,b=st.columns(2)
with a:
 st.subheader('📚 Sınav yönetimi')
 st.write('Program, ders, öğrenme çıktısı, soru bankası, sınav ve temel madde analizi.')
 if st.button('Sınav yönetimini aç',use_container_width=True): st.switch_page('pages/1_Sinav_Yonetimi.py')
with b:
 st.subheader('📊 EvalBee kazanım analizi')
 st.write('Soru–DÖÇ–PÇ eşleştirmesi, öğrenci cevapları, başarı oranları ve Excel raporları.')
 if st.button('EvalBee modülünü aç',use_container_width=True): st.switch_page('pages/2_EvalBee_Kazanim_Analizi.py')
st.info('Modüller aynı site altında çalışır ancak veri akışı henüz tam bütünleşik değildir. EvalBee aktarımı standart CSV/XLSX şablonuyla yapılır.')
