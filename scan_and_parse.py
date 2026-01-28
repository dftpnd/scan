#!/usr/bin/env python3
"""
Единый скрипт для автоматизации:
1. Двигает курсор
2. Делает клик
3. Делает скриншот
4. Парсит текст из скриншота
"""

from automation import MouseAutomation
import time
import sys


def scan_and_parse(x: int, y: int, 
                   click: bool = True,
                   screenshot_region: tuple = None,
                   ocr_method: str = 'ocrspace',
                   wait_before_click: float = 0.5,
                   wait_after_click: float = 0.5,
                   move_duration: float = 0.5):
    """
    Полный цикл: перемещение → клик → скриншот → OCR
    
    Args:
        x: Координата X для курсора и клика
        y: Координата Y для курсора и клика
        click: Делать ли клик (по умолчанию True)
        screenshot_region: Область для скриншота (x, y, width, height) или None для всего экрана
        ocr_method: Метод OCR ('ocrspace' или 'tesseract')
        wait_before_click: Пауза перед кликом (в секундах)
        wait_after_click: Пауза после клика перед скриншотом (в секундах)
        move_duration: Длительность перемещения курсора (в секундах)
    
    Returns:
        Словарь с результатами: {'screenshot_path': str, 'text': str, 'success': bool}
    """
    
    print("="*60)
    print("🚀 ЗАПУСК АВТОМАТИЗАЦИИ")
    print("="*60)
    
    # Инициализация (пробуем pyautogui, при ошибке используем cliclick)
    auto = MouseAutomation(use_applescript=False)
    
    try:
        # Шаг 1: Перемещение курсора
        print(f"\n📍 ШАГ 1: Перемещаю курсор в ({x}, {y})")
        print("-" * 60)
        auto.move_cursor(x, y, duration=move_duration)
        print("✅ Курсор перемещен")
        time.sleep(wait_before_click)
        
        # Шаг 2: Клик
        if click:
            print(f"\n🖱️  ШАГ 2: Делаю клик по ({x}, {y})")
            print("-" * 60)
            auto.click(x, y)
            print("✅ Клик выполнен")
            time.sleep(wait_after_click)
        else:
            print(f"\n⏭️  ШАГ 2: Клик пропущен")
        
        # Шаг 3 и 4: Скриншот и распознавание текста (OCR) в одном действии
        print(f"\n📸 ШАГ 3: Делаю скриншот")
        print("-" * 60)
        if screenshot_region:
            print(f"Область: {screenshot_region}")
        else:
            print("Весь экран")
        
        print(f"\n🔍 ШАГ 4: Распознаю текст из скриншота")
        print("-" * 60)
        
        # Делаем скриншот и сразу распознаем текст
        result = auto.screenshot_and_ocr(
            filename=None,  # Автоматическое имя файла
            region=screenshot_region,
            ocr_method=ocr_method
        )
        
        screenshot_path = result['screenshot_path']
        text = result['text']
        success = result['success']
        error = result.get('error')
        
        if success:
            print("\n" + "="*60)
            print("✅ АВТОМАТИЗАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("⚠️  АВТОМАТИЗАЦИЯ ЗАВЕРШЕНА С ОШИБКОЙ OCR")
            print("="*60)
            print(f"Скриншот сохранен: {screenshot_path}")
            if error:
                print(f"Ошибка OCR: {error}")
        
        return {
            'screenshot_path': screenshot_path,
            'text': text,
            'success': success,
            'error': error
        }
        
    except Exception as e:
        error_msg = f"❌ Ошибка при выполнении автоматизации: {e}"
        print(f"\n{error_msg}")
        print("="*60)
        return {
            'screenshot_path': None,
            'text': '',
            'success': False,
            'error': str(e)
        }


def main():
    """Главная функция с примерами использования"""
    
    # Инициализируем переменные по умолчанию
    screenshot_region = None
    ocr_method = 'ocrspace'
    
    if len(sys.argv) >= 3:
        # Использование из командной строки
        try:
            x = int(sys.argv[1])
            y = int(sys.argv[2])
            click = sys.argv[3].lower() == 'true' if len(sys.argv) > 3 else True
            if len(sys.argv) > 4:
                ocr_method = sys.argv[4].lower()
                if ocr_method not in ['ocrspace', 'tesseract']:
                    print("⚠️  Неизвестный метод OCR, использую ocrspace")
                    ocr_method = 'ocrspace'
        except (ValueError, IndexError):
            print("Использование: python scan_and_parse.py <x> <y> [click=true/false] [ocr_method=ocrspace/tesseract]")
            print("Пример: python scan_and_parse.py 500 300 true ocrspace")
            sys.exit(1)
    else:
        # Интерактивный режим
        print("\n" + "="*60)
        print("📋 ИНТЕРАКТИВНЫЙ РЕЖИМ")
        print("="*60)
        
        try:
            x = int(input("\nВведите координату X: "))
            y = int(input("Введите координату Y: "))
            click_input = input("Делать клик? (y/n, по умолчанию y): ").strip().lower()
            click = click_input != 'n'
            
            region_input = input("Скриншот области? (y/n, по умолчанию n - весь экран): ").strip().lower()
            if region_input == 'y':
                try:
                    rx = int(input("  X области: "))
                    ry = int(input("  Y области: "))
                    rw = int(input("  Ширина: "))
                    rh = int(input("  Высота: "))
                    screenshot_region = (rx, ry, rw, rh)
                except ValueError:
                    print("⚠️  Неверный формат, использую весь экран")
                    screenshot_region = None
            
            ocr_input = input("Метод OCR (ocrspace/tesseract, по умолчанию ocrspace): ").strip().lower()
            ocr_method = ocr_input if ocr_input in ['ocrspace', 'tesseract'] else 'ocrspace'
        except (ValueError, KeyboardInterrupt):
            print("\n❌ Отменено пользователем")
            sys.exit(1)
    
    # Выполняем автоматизацию
    result = scan_and_parse(
        x=x,
        y=y,
        click=click,
        screenshot_region=screenshot_region,
        ocr_method=ocr_method
    )
    
    # Выводим итоговый результат
    print("\n" + "="*60)
    print("📊 ИТОГОВЫЙ РЕЗУЛЬТАТ")
    print("="*60)
    
    if result['screenshot_path']:
        print(f"📁 Скриншот: {result['screenshot_path']}")
    
    if result['success']:
        print(f"📝 Распознанный текст ({len(result['text'])} символов):")
        print("-" * 60)
        if result['text'].strip():
            print(result['text'])
        else:
            print("(Текст не обнаружен на изображении)")
    else:
        print("❌ OCR не удался")
        if result.get('error'):
            print(f"Ошибка: {result['error']}")
        print("\n💡 Решения:")
        if 'tesseract' in result.get('error', '').lower() or 'rus.traineddata' in result.get('error', ''):
            print("  Для Tesseract с русским языком:")
            print("    1. Установите русский языковой пакет:")
            print("       brew install tesseract-lang")
            print("    2. Или используйте OCR.space (поддерживает русский без установки):")
            print("       python scan_and_parse.py 500 300 true ocrspace")
        else:
            print("  1. Проверить интернет-соединение (для OCR.space)")
            print("  2. Использовать Tesseract (локальный OCR):")
            print("     brew install tesseract tesseract-lang")
            print("     python scan_and_parse.py 500 300 true tesseract")
    
    print("="*60)


if __name__ == "__main__":
    main()
