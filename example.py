#!/usr/bin/env python3
"""
Простой пример использования автоматизации
"""

from automation import MouseAutomation
import time

def main():
    # Создаем экземпляр автоматизации
    auto = MouseAutomation()
    
    print("Начинаю автоматизацию...")
    print("(Для остановки переместите мышь в верхний левый угол экрана)\n")
    
    # Даем время подготовиться
    print("Подготовка... 3 секунды")
    time.sleep(3)
    
    # 1. Перемещаем курсор
    print("\n1. Перемещаю курсор в центр экрана")
    screen_width, screen_height = auto.screen_size
    center_x = screen_width // 2
    center_y = screen_height // 2
    auto.move_cursor(center_x, center_y, duration=1.0)
    time.sleep(1)
    
    # 2. Делаем клик
    print("\n2. Делаю клик")
    auto.click(center_x, center_y)
    time.sleep(1)
    
    # 3. Делаем скриншот
    print("\n3. Делаю скриншот")
    screenshot_path = auto.screenshot("example_screenshot.png")
    print(f"Скриншот сохранен: {screenshot_path}")
    
    # 4. Перемещаемся и делаем еще один скриншот
    print("\n4. Перемещаюсь и делаю еще один скриншот")
    auto.move_cursor(100, 100, duration=0.5)
    time.sleep(0.5)
    auto.screenshot("example_screenshot_2.png")
    
    # 5. Делаем скриншот с распознаванием текста
    print("\n5. Делаю скриншот с распознаванием текста (OCR)")
    result = auto.screenshot_and_ocr("example_ocr.png", ocr_method='ocrspace')
    if result['success']:
        print(f"\n✅ Текст распознан успешно!")
        print(f"Распознанный текст:\n{result['text']}")
    else:
        print(f"\n❌ Ошибка распознавания: {result['error']}")
    
    print("\n✅ Автоматизация завершена!")

if __name__ == "__main__":
    main()
