#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы управления мышью
"""

from automation import MouseAutomation
import time

def test_mouse():
    print("="*60)
    print("ТЕСТ УПРАВЛЕНИЯ МЫШЬЮ")
    print("="*60)
    
    # Пробуем сначала с pyautogui
    print("\n1. Тест с pyautogui (по умолчанию)")
    try:
        auto1 = MouseAutomation(use_applescript=False)
        print("✅ Инициализация успешна")
        
        # Получаем текущую позицию
        pos = auto1.get_cursor_position()
        print(f"Текущая позиция: {pos}")
        
        # Пробуем переместить
        print("\nПробую переместить курсор на 100, 100...")
        time.sleep(2)
        auto1.move_cursor(100, 100, duration=0.5)
        print("✅ Перемещение успешно!")
        
        time.sleep(1)
        
        # Пробуем клик
        print("\nПробую кликнуть на 200, 200...")
        time.sleep(1)
        auto1.click(200, 200)
        print("✅ Клик успешен!")
        
    except Exception as e:
        print(f"❌ Ошибка с pyautogui: {e}")
        print("\n" + "="*60)
        print("2. Пробую с AppleScript (для macOS)")
        print("="*60)
        
        try:
            auto2 = MouseAutomation(use_applescript=True)
            print("✅ Инициализация успешна")
            
            # Получаем текущую позицию
            pos = auto2.get_cursor_position()
            print(f"Текущая позиция: {pos}")
            
            # Пробуем переместить
            print("\nПробую переместить курсор на 100, 100...")
            time.sleep(2)
            auto2.move_cursor(100, 100)
            print("✅ Перемещение успешно!")
            
            time.sleep(1)
            
            # Пробуем клик
            print("\nПробую кликнуть на 200, 200...")
            time.sleep(1)
            auto2.click(200, 200)
            print("✅ Клик успешен!")
            
        except Exception as e2:
            print(f"❌ Ошибка с AppleScript: {e2}")
            print("\n" + "="*60)
            print("РЕКОМЕНДАЦИИ:")
            print("="*60)
            print("1. Проверьте разрешения в Системных настройках:")
            print("   Системные настройки → Конфиденциальность и безопасность")
            print("   - Управление компьютером: разрешено")
            print("   - Захват экрана: разрешено")
            print("\n2. Для Terminal/Python должно быть разрешено управление")
            print("\n3. Перезапустите терминал после изменения разрешений")
            return False
    
    print("\n" + "="*60)
    print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
    print("="*60)
    return True

if __name__ == "__main__":
    test_mouse()
