# insurance_app/management/commands/load_excel.py

import os
import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from insurance_app.models import Customer, Policy
from django.db import transaction
import numpy as np
import unicodedata

class Command(BaseCommand):
    help = 'Excel dosyasındaki müşteri ve poliçe verilerini veritabanına aktarır veya günceller.'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Verilerin alınacağı Excel dosyasının yolu')

    def handle(self, *args, **options):
        excel_path = options['excel_file']

        if not os.path.exists(excel_path):
            raise CommandError(f"HATA: Excel dosyası bulunamadı: {excel_path}")

        try:
            df = pd.read_excel(excel_path)
            self.stdout.write(self.style.SUCCESS(f'Excel dosyası başarıyla yüklendi: {excel_path}'))
        except Exception as e:
            raise CommandError(f"HATA: Excel dosyasını okurken bir sorun oluştu: {e}")

        original_columns = df.columns
        new_columns = []
        for col in original_columns:
            normalized_col = col.strip().lower()
            normalized_col = unicodedata.normalize('NFKD', normalized_col).encode('ascii', 'ignore').decode('utf-8')
            normalized_col = normalized_col.replace(' ', '_').replace('.', '').replace('/', '').replace('\\', '').replace('i̇', 'i')
            new_columns.append(normalized_col)
        df.columns = new_columns
        
        self.stdout.write(self.style.NOTICE(f'Normalleştirilmiş Sütun İsimleri: {df.columns.tolist()}'))

        with transaction.atomic():
            for index, row in df.iterrows():
                excel_row_num = index + 2 

                try:
                    customer_name_candidates = ['musteri', 'musteri_adi', 'ad_soyad', 'name']
                    customer_name = None
                    for candidate in customer_name_candidates:
                        if candidate in row and pd.notna(row[candidate]):
                            customer_name = str(row[candidate]).strip()
                            break
                    
                    if not customer_name:
                        self.stderr.write(self.style.WARNING(f'Satır {excel_row_num}: Müşteri adı boş veya bulunamadı. Müşteri atlanıyor. Satır Verisi: {row.to_dict()}'))
                        continue

                    customer_name = unicodedata.normalize('NFKD', customer_name).encode('ascii', 'ignore').decode('utf-8').upper()

                    tc_id_candidates = ['tc', 'tc_kimlik_no', 'tckimlik', 'tc_id']
                    tc_id = None
                    for candidate in tc_id_candidates:
                        if candidate in row and pd.notna(row[candidate]):
                            tc_id = str(int(row[candidate])).strip()
                            break
                    
                    if not tc_id:
                        self.stderr.write(self.style.WARNING(f'Satır {excel_row_num}: TC Kimlik No boş veya bulunamadı. Müşteri atlanıyor. Satır Verisi: {row.to_dict()}'))
                        continue

                    phone_candidates = ['telefon', 'tel', 'phone']
                    phone = None
                    for candidate in phone_candidates:
                        if candidate in row and pd.notna(row[candidate]):
                            phone = str(int(row[candidate])).strip()
                            break
                    if phone is None:
                        phone = None

                    customer_data = {
                        'name': customer_name,
                        'tc_id': tc_id,
                        'phone': phone,
                        'job': row.get('meslek', None) if pd.notna(row.get('meslek')) else None,
                        'birth_date': pd.to_datetime(row.get('dogum_tarihi'), errors='coerce').date() if pd.notna(row.get('dogum_tarihi')) else None,
                        'city': row.get('sehir', None) if pd.notna(row.get('sehir')) else None,
                    }

                    for key, value in customer_data.items():
                        if pd.isna(value) or value == '':
                            customer_data[key] = None
                        if isinstance(value, str):
                            customer_data[key] = value.strip()


                    customer, created = Customer.objects.update_or_create(
                        tc_id=customer_data['tc_id'],
                        defaults={k: v for k, v in customer_data.items() if k != 'tc_id'}
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Müşteri oluşturuldu: {customer.name}'))
                    
                    policy_type_candidates = ['poliçe', 'police_turu', 'policy_type', 'police']
                    policy_type = None
                    for candidate in policy_type_candidates:
                        if candidate in row and pd.notna(row[candidate]):
                            policy_type = str(row[candidate]).strip()
                            break
                    
                    if pd.isna(policy_type) or not policy_type:
                        self.stdout.write(self.style.WARNING(f'Satır {excel_row_num}: Poliçe türü boş veya bulunamadı. Poliçe oluşturulmadı. Satır Verisi: {row.to_dict()}'))
                        continue

                    insurance_company_candidates = ['sigorta_şirketi', 'sigorta_sirketi', 'insurance_company']
                    insurance_company = None
                    for candidate in insurance_company_candidates:
                        if candidate in row and pd.notna(row[candidate]):
                            insurance_company = str(row[candidate]).strip()
                            break
                    if pd.isna(insurance_company):
                        insurance_company = None
                    
                    plate = str(row.get('plaka', '')).strip() if pd.notna(row.get('plaka')) else None
                    license_val = str(row.get('ruhsat', '')).strip() if pd.notna(row.get('ruhsat')) else None
                    due_date = pd.to_datetime(row.get('tarih'), errors='coerce').date() if pd.notna(row.get('tarih')) else None

                    # Her zaman yeni bir Policy nesnesi oluştur (update_or_create yerine)
                    # Çünkü bir müşteri için aynı poliçe türünden birden fazla poliçe olabilir
                    Policy.objects.create(
                        customer=customer,
                        policy_type=policy_type,
                        insurance_company=insurance_company,
                        plate=plate,
                        license=license_val,
                        due_date=due_date
                    )
                    self.stdout.write(self.style.SUCCESS(f'Poliçe oluşturuldu: {policy_type} for {customer.name}'))

                except KeyError as ke:
                    self.stderr.write(self.style.ERROR(f'Satır {excel_row_num}: Excel dosyasında eksik veya yanlış adlandırılmış sütun: {ke}. Lütfen sütun adlarını kontrol edin.'))
                    self.stderr.write(self.style.ERROR(f'Sorunlu satır verileri (ham): {row.to_dict()}'))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f'Satır {excel_row_num} işlenirken beklenmeyen hata oluştu: {e}'))
                    self.stderr.write(self.style.ERROR(f'Sorunlu satır verileri (ham): {row.to_dict()}'))

        self.stdout.write(self.style.SUCCESS('Veri yükleme tamamlandı!'))