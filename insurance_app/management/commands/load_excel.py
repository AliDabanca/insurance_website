# insurance_app/management/commands/load_excel.py

import os
import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from insurance_app.models import Customer, Policy # Customer ve Policy modellerini import et
from django.db import transaction # Atomik işlemler için
import numpy as np # NaT kontrolü için

class Command(BaseCommand):
    help = 'Excel dosyasındaki müşteri ve poliçe verilerini veritabanına aktarır veya günceller.'

    def add_arguments(self, parser):
        # Excel dosyasının yolunu argüman olarak alıyoruz
        parser.add_argument('excel_file', type=str, help='Verilerin alınacağı Excel dosyasının yolu')

    def handle(self, *args, **options):
        excel_path = options['excel_file']

        # Excel dosyasının varlığını kontrol et
        if not os.path.exists(excel_path):
            raise CommandError(f"HATA: Excel dosyası bulunamadı: {excel_path}")

        try:
            # Excel dosyasını oku
            df = pd.read_excel(excel_path)
        except Exception as e:
            raise CommandError(f"HATA: Excel dosyasını okurken bir sorun oluştu: {e}")

        # Sütun adlarını Django model alan adlarına uygun hale getir
        # Excel başlıklarını dikkatlice kontrol et ve eşleştir!
        df.rename(columns={
            'MÜŞTERİ': 'name',
            'PLAKA': 'plate',
            'TC': 'tc_id',
            'RUHSAT': 'license',
            'DOĞUM TARİHİ': 'birth_date',
            'ŞEHİR': 'city',
            'TELEFON': 'phone',
            'MESLEK': 'job',
            'POLİÇE': 'policy_type',
            'SİGORTA SİRKETİ': 'insurance_company', # Excel'deki 'SİRKETİ' ile eşleşti
            'TARİH': 'due_date',
            'REFERANS': 'referans' # Excel'deki 'REFERANS' ile eşleşti
        }, inplace=True)

        # Modelinizdeki tüm beklenen alanları kontrol edin ve Excel'de olmayanlar için None atayın
        # Bu, get() yerine doğrudan df[col] kullanırken KeyError almayı engeller
        expected_columns = [
            'name', 'tc_id', 'birth_date', 'city', 'phone', 'job', 'referans', # Customer modeline ait alanlar
            'plate', 'license', 'policy_type', 'insurance_company', 'due_date' # Policy modeline ait alanlar
        ]
        for col in expected_columns:
            if col not in df.columns:
                df[col] = None

        # Tarih formatını düzelt
        date_columns = ['birth_date', 'due_date']
        for col in date_columns:
            if col in df.columns and df[col].dtype != '<M8[ns]': # Zaten tarih ise tekrar çevirme
                df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True) # Hatalı tarihleri NaT (Not a Time) yapar

        # Eksik string ve sayısal değerleri doldur
        # TC_ID ve Telefon gibi unique veya sayısal olması beklenen alanlara dikkat et.
        # Modelde default olarak '-' verdiğin için burada da '-' ile doldurabiliriz.
        customer_str_fields = ['name', 'tc_id', 'city', 'phone', 'job', 'referans']
        policy_str_fields = ['plate', 'license', 'policy_type', 'insurance_company']

        for col in customer_str_fields:
            if col in df.columns:
                df[col] = df[col].fillna('-').astype(str)
        for col in policy_str_fields:
            if col in df.columns:
                df[col] = df[col].fillna('-').astype(str)

        # TC_ID'nin benzersizliğini ve formatını garanti altına al
        if 'tc_id' in df.columns:
            df['tc_id'] = df['tc_id'].apply(lambda x: str(x).strip().replace('.0', '') if pd.notna(x) else '-')

        self.stdout.write(self.style.SUCCESS("Veritabanına aktarım işlemi başlıyor..."))

        # Toplu işlem (transaction) kullanarak performansı artır ve hatalarda geri almayı sağla
        with transaction.atomic():
            for index, row in df.iterrows():
                try:
                    tc_id_value = row['tc_id']
                    if not tc_id_value or tc_id_value == '-':
                        self.stdout.write(self.style.WARNING(f"⚠️ Satır {index + 1}: TC kimlik numarası boş veya '-' olduğu için atlanıyor. Veri: {row.to_dict()}"))
                        continue

                    # Tarih değerlerini None'a çevir eğer NaT ise (Django'nun DateField'ı için)
                    birth_date_val = row.get('birth_date', None)
                    if pd.isna(birth_date_val): # Pandas NaT veya np.nan kontrolü için
                        birth_date_val = None

                    due_date_val = row.get('due_date', None)
                    if pd.isna(due_date_val): # Pandas NaT veya np.nan kontrolü için
                        due_date_val = None

                    # 1. Müşteriyi Oluştur veya Güncelle
                    # customer.objects.update_or_create sadece Customer modelinde bulunan alanları kabul etmeli
                    customer, created_customer = Customer.objects.update_or_create(
                        tc_id=tc_id_value,
                        defaults={
                            'name': row.get('name', 'Bilinmiyor'),
                            'birth_date': birth_date_val,
                            'city': row.get('city', '-'),
                            'phone': row.get('phone', '-'),
                            'job': row.get('job', '-'),
                            'referans': row.get('referans', '-'),
                        }
                    )
                    if created_customer:
                        self.stdout.write(self.style.SUCCESS(f"✅ Satır {index + 1}: Yeni müşteri oluşturuldu: {customer.name} (TC: {customer.tc_id})"))
                    # else: # Müşteri zaten var mesajını çok fazla basmaması için kapatılabilir
                    #    self.stdout.write(self.style.MIGRATE_HEADING(f"🔄 Satır {index + 1}: Mevcut müşteri güncellendi: {customer.name} (TC: {customer.tc_id})"))

                    # 2. Poliçeyi Oluştur
                    # Her Excel satırı için bir poliçe oluşturuyoruz, aynı TC'ye sahip olsa bile
                    Policy.objects.create(
                        customer=customer, # Yukarıda oluşturulan/bulunan Customer nesnesi ile ilişkilendir
                        plate=row.get('plate', '-'),
                        license=row.get('license', '-'),
                        policy_type=row.get('policy_type', '-'),
                        insurance_company=row.get('insurance_company', '-'),
                        due_date=due_date_val
                    )
                    self.stdout.write(self.style.SUCCESS(f"✅ Satır {index + 1}: Poliçe oluşturuldu: {customer.name} - {row.get('policy_type', '-')}"))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Satır {index + 1} kaydedilemedi: {e} - Veri: {row.to_dict()}"))

        self.stdout.write(self.style.SUCCESS("✅ Excel verileri aktarma işlemi tamamlandı."))