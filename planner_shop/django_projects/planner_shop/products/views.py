import os
import json
import uuid
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from django.conf import settings
from .models import Product
from .forms import ProductForm, JSONImportForm

def home(request):
    return render(request, 'products/home.html')

def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            # Проверяем какой тип сохранения выбран
            if 'export_json' in request.POST:
                # Экспорт в JSON
                product_data = form.cleaned_data
                json_data = json.dumps(product_data, indent=4, ensure_ascii=False, default=str)
                response = HttpResponse(json_data, content_type='application/json')
                response['Content-Disposition'] = 'attachment; filename="product_export.json"'
                return response
            elif 'export_xml' in request.POST:
                # Экспорт в XML
                product_data = form.cleaned_data
                xml_data = '<?xml version="1.0" encoding="UTF-8"?>\n<product>\n'
                for key, value in product_data.items():
                    if value is not None:
                        xml_data += f'    <{key}>{value}</{key}>\n'
                xml_data += '</product>'
                response = HttpResponse(xml_data, content_type='application/xml')
                response['Content-Disposition'] = 'attachment; filename="product_export.xml"'
                return response
            else:
                # Сохранение в БД
                product = form.save()
                messages.success(request, f'Товар "{product.title}" успешно создан!')
                return redirect('home')
    else:
        form = ProductForm()
    
    return render(request, 'products/product_form.html', {'form': form})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})

def import_products(request):
    if request.method == 'POST':
        form = JSONImportForm(request.POST, request.FILES)
        if form.is_valid():
            json_file = request.FILES['json_file']
            
            # Санитизация имени файла
            safe_name = f"import_{uuid.uuid4().hex[:8]}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Сохраняем файл
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'temp_imports'))
            filename = fs.save(safe_name, json_file)
            file_path = fs.path(filename)
            
            try:
                # Проверка валидности JSON
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Проверяем - массив товаров или один товар
                if isinstance(data, list):
                    # Обрабатываем массив товаров
                    imported_count = 0
                    errors = []
                    
                    for index, product_data in enumerate(data):
                        try:
                            # Проверка структуры данных для каждого товара
                            required_fields = ['title', 'product_type', 'price', 'sku']
                            for field in required_fields:
                                if field not in product_data:
                                    raise ValueError(f"Товар #{index+1}: отсутствует поле '{field}'")
                            
                            # Проверка типа товара
                            valid_types = ['planner', 'sticker', 'kit', 'accessory']
                            if product_data.get('product_type') not in valid_types:
                                raise ValueError(f"Товар #{index+1}: недопустимый тип товара")
                            
                            # Получаем и преобразуем discount
                            discount_str = product_data.get('discount', '0')
                            try:
                                discount = float(discount_str)
                            except (ValueError, TypeError):
                                raise ValueError(f"Товар #{index+1}: неверный формат скидки '{discount_str}'")
                            
                            if discount < 0 or discount > 100:
                                raise ValueError(f"Товар #{index+1}: скидка должна быть от 0% до 100%")
                            
                            # Преобразуем price в число
                            price_str = product_data['price']
                            try:
                                price = float(price_str)
                            except (ValueError, TypeError):
                                raise ValueError(f"Товар #{index+1}: неверный формат цены '{price_str}'")
                            
                            # Преобразуем stock_quantity в число
                            stock_quantity_str = product_data.get('stock_quantity', '0')
                            try:
                                stock_quantity = int(stock_quantity_str)
                            except (ValueError, TypeError):
                                raise ValueError(f"Товар #{index+1}: неверный формат количества '{stock_quantity_str}'")
                            
                            # Проверяем уникальность SKU
                            if Product.objects.filter(sku=product_data['sku']).exists():
                                raise ValueError(f"Товар #{index+1}: SKU '{product_data['sku']}' уже существует")
                            
                            # Создание товара
                            product = Product.objects.create(
                                title=product_data['title'],
                                product_type=product_data['product_type'],
                                description=product_data.get('description', ''),
                                price=price,
                                discount=discount,
                                sku=product_data['sku'],
                                is_available=product_data.get('is_available', True),
                                stock_quantity=stock_quantity,
                            )
                            imported_count += 1
                            
                        except Exception as e:
                            errors.append(f"Товар #{index+1}: {str(e)}")
                    
                    # Формируем сообщение о результате
                    if imported_count > 0:
                        success_msg = f'Успешно импортировано {imported_count} товаров!'
                        if errors:
                            success_msg += f' Ошибки: {", ".join(errors)}'
                        messages.success(request, success_msg)
                    else:
                        messages.error(request, f'Не удалось импортировать ни одного товара. Ошибки: {", ".join(errors)}')
                       
                else:
                    # Обрабатываем один товар
                    required_fields = ['title', 'product_type', 'price', 'sku']
                    for field in required_fields:
                        if field not in data:
                            raise ValueError(f"Отсутствует обязательное поле: {field}")
                    
                    valid_types = ['planner', 'sticker', 'kit', 'accessory']
                    if data.get('product_type') not in valid_types:
                        raise ValueError(f"Недопустимый тип товара: {data.get('product_type')}")
                    
                    # Преобразуем discount в число
                    discount_str = data.get('discount', '0')
                    try:
                        discount = float(discount_str)
                    except (ValueError, TypeError):
                        raise ValueError(f"Неверный формат скидки '{discount_str}'")
                    
                    if discount < 0 or discount > 100:
                        raise ValueError("Скидка должна быть от 0% до 100%")
                    
                    # Преобразуем price в число
                    price_str = data['price']
                    try:
                        price = float(price_str)
                    except (ValueError, TypeError):
                        raise ValueError(f"Неверный формат цены '{price_str}'")
                    
                    # Преобразуем stock_quantity в число
                    stock_quantity_str = data.get('stock_quantity', '0')
                    try:
                        stock_quantity = int(stock_quantity_str)
                    except (ValueError, TypeError):
                        raise ValueError(f"Неверный формат количества '{stock_quantity_str}'")
                    
                    # Проверяем уникальность SKU
                    if Product.objects.filter(sku=data['sku']).exists():
                        raise ValueError(f"SKU '{data['sku']}' уже существует")
                    
                    product = Product.objects.create(
                        title=data['title'],
                        product_type=data['product_type'],
                        description=data.get('description', ''),
                        price=price,
                        discount=discount,
                        sku=data['sku'],
                        is_available=data.get('is_available', True),
                        stock_quantity=stock_quantity,
                    )
                    
                    messages.success(request, f'Товар "{product.title}" успешно импортирован!')
               
                # Удаляем временный файл после успешного импорта
                if os.path.exists(file_path):
                    os.remove(file_path)
               
            except Exception as e:
                # Удаляем невалидный файл
                if os.path.exists(file_path):
                    os.remove(file_path)
                messages.error(request, f'Ошибка: {str(e)}')
            
            return redirect('import_products')
   
    else:
        form = JSONImportForm()
   
    return render(request, 'products/import_products.html', {'form': form})

def view_files(request):
    """Просмотр всех импортированных файлов"""
    import_dir = os.path.join(settings.MEDIA_ROOT, 'temp_imports')
    
    # Создаем директорию если её нет
    os.makedirs(import_dir, exist_ok=True)
    
    files_data = []
    json_files = [f for f in os.listdir(import_dir) if f.endswith('.json')]
    
    if not json_files:
        messages.info(request, "Нет загруженных файлов для отображения.")
    else:
        for filename in json_files:
            file_path = os.path.join(import_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                files_data.append({
                    'filename': filename,
                    'content': content,
                    'size': os.path.getsize(file_path)
                })
            except Exception as e:
                files_data.append({
                    'filename': filename,
                    'error': f'Ошибка чтения: {str(e)}'
                })
    
    return render(request, 'products/view_files.html', {'files_data': files_data})

def delete_product(request, product_id):
    """Удаление товара"""
    try:
        product = Product.objects.get(id=product_id)
        product_title = product.title
        product.delete()
        messages.success(request, f'Товар "{product_title}" успешно удален!')
    except Product.DoesNotExist:
        messages.error(request, 'Товар не найден!')
    
    return redirect('product_list')

def delete_file(request, filename):
    """Удаление файла"""
    try:
        file_path = os.path.join(settings.MEDIA_ROOT, 'temp_imports', filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            messages.success(request, f'Файл "{filename}" успешно удален!')
        else:
            messages.error(request, 'Файл не найден!')
    except Exception as e:
        messages.error(request, f'Ошибка при удалении файла: {str(e)}')
    
    return redirect('view_files')

def delete_all_files(request):
    """Удаление всех файлов"""
    try:
        import_dir = os.path.join(settings.MEDIA_ROOT, 'temp_imports')
        if os.path.exists(import_dir):
            for filename in os.listdir(import_dir):
                file_path = os.path.join(import_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            messages.success(request, 'Все файлы успешно удалены!')
        else:
            messages.info(request, 'Нет файлов для удаления.')
    except Exception as e:
        messages.error(request, f'Ошибка при удалении файлов: {str(e)}')
    
    return redirect('view_files')

