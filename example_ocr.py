#!/usr/bin/env python3
"""
Пример использования OCR для распознавания текста на скриншотах
"""

from automation import MouseAutomation
import time

def main():
    auto = MouseAutomation()
    
    print("=== Пример использования OCR ===\n")
    
    # Даем время подготовиться
    print("Подготовка... 3 секунды")
    time.sleep(3)
    
    # Пример 1: Скриншот всего экрана с распознаванием текста
    print("\n1. Делаю скриншот всего экрана и распознаю текст...")
    result = auto.screenshot_and_ocr(
        filename="full_screen_ocr.png",
        ocr_method='ocrspace'  # Используем бесплатный OCR.space API
    )
    
    if result['success']:
        print(f"\n✅ Успешно распознано!")
        print(f"Скриншот: {result['screenshot_path']}")
        print(f"\nРаспознанный текст:\n{'-' * 50}")
        print(result['text'])
        print('-' * 50)
    else:
        print(f"\n❌ Ошибка: {result['error']}")
    
    # Пример 2: Скриншот области с OCR
    print("\n\n2. Делаю скриншот области (верхний левый угол) и распознаю текст...")
    result = auto.screenshot_and_ocr(
        filename="region_ocr.png",
        region=(0, 0, 800, 600),  # Область 800x600 пикселей
        ocr_method='ocrspace'
    )
    
    if result['success']:
        print(f"\n✅ Успешно распознано!")
        print(f"Распознанный текст:\n{result['text']}")
    
    # Пример 3: Распознавание текста из существующего файла
    print("\n\n3. Распознаю текст из ранее созданного скриншота...")
    try:
        # Используем первый созданный скриншот
        text = auto.ocr_from_file(
            result['screenshot_path'],
            ocr_method='ocrspace'
        )
        print(f"Распознанный текст:\n{text}")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    print("\n✅ Готово!")

if __name__ == "__main__":
    main()
