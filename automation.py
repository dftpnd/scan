#!/usr/bin/env python3
"""
Автоматизация мыши и скриншотов
Функции для движения курсора, кликов и создания скриншотов
"""

import pyautogui
import time
import requests
import base64
import subprocess
import platform
import sys
from typing import Tuple, Optional, Dict, Any
from pathlib import Path
from PIL import Image


class MouseAutomation:
    """Класс для автоматизации работы с мышью и скриншотами"""
    
    def __init__(self, fail_safe: bool = True, pause: float = 0.1, use_applescript: bool = None):
        """
        Инициализация автоматизации
        
        Args:
            fail_safe: Если True, перемещение мыши в угол экрана прервет выполнение
            pause: Пауза между действиями (в секундах)
            use_applescript: Использовать AppleScript для macOS (True/False/None=автоопределение)
        """
        pyautogui.FAILSAFE = fail_safe
        pyautogui.PAUSE = pause
        self.screen_size = pyautogui.size()
        self.is_macos = platform.system() == 'Darwin'
        
        # Для macOS по умолчанию используем pyautogui, но с fallback на cliclick
        # use_applescript теперь означает "использовать cliclick если pyautogui не работает"
        if use_applescript is None:
            self.use_applescript = False  # По умолчанию пробуем pyautogui
        else:
            self.use_applescript = use_applescript and self.is_macos
        
        print(f"Размер экрана: {self.screen_size}")
        if self.is_macos:
            print(f"Система: macOS")
            print(f"Метод управления мышью: {'cliclick (fallback)' if self.use_applescript else 'pyautogui (с fallback на cliclick)'}")
        
        # Проверяем разрешения
        self._check_permissions()
    
    def _check_permissions(self) -> None:
        """Проверка разрешений для macOS"""
        if self.is_macos:
            print("\n⚠️  Проверка разрешений macOS...")
            print("Убедитесь, что в Системных настройках → Конфиденциальность и безопасность:")
            print("  - Управление компьютером: разрешено для Terminal/Python")
            print("  - Захват экрана: разрешено для Terminal/Python")
    
    def _move_cursor_applescript(self, x: int, y: int) -> None:
        """Перемещение курсора через AppleScript (для macOS)"""
        # Сначала пробуем pyautogui (может работать если есть разрешения)
        try:
            pyautogui.moveTo(x, y, duration=0)
            return
        except Exception:
            pass
        
        # Если pyautogui не работает, пробуем cliclick (если установлен)
        try:
            subprocess.run(['cliclick', f'm:{x},{y}'], 
                         check=True, capture_output=True, timeout=5)
            return
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Если cliclick не установлен, предлагаем установить
            raise Exception(
                "Не удалось переместить курсор через pyautogui.\n"
                "Установите cliclick для более надежной работы:\n"
                "  brew install cliclick\n\n"
                "Или проверьте разрешения:\n"
                "  Системные настройки → Конфиденциальность и безопасность → Управление компьютером"
            )
    
    def move_cursor(self, x: int, y: int, duration: float = 0.5) -> None:
        """
        Переместить курсор мыши в указанные координаты
        
        Args:
            x: Координата X
            y: Координата Y
            duration: Время перемещения в секундах (0 = мгновенно)
        """
        print(f"Перемещаю курсор в ({x}, {y})")
        
        # Сначала пробуем pyautogui
        try:
            pyautogui.moveTo(x, y, duration=duration)
            return
        except Exception as e1:
            # Если pyautogui не работает, пробуем cliclick (для macOS)
            if self.is_macos:
                try:
                    self._move_cursor_applescript(x, y)
                    return
                except Exception as e2:
                    error_msg = f"❌ Ошибка при перемещении курсора:\n"
                    error_msg += f"  pyautogui: {e1}\n"
                    error_msg += f"  cliclick: {e2}"
                    print(error_msg)
                    print("\n💡 Решение:")
                    print("  1. Установите cliclick: brew install cliclick")
                    print("  2. Или проверьте разрешения:")
                    print("     Системные настройки → Конфиденциальность и безопасность → Управление компьютером")
                    raise Exception(error_msg)
            else:
                raise e1
    
    def _click_applescript(self, x: int, y: int, button: str = 'left', clicks: int = 1) -> None:
        """Клик через AppleScript (для macOS)"""
        # Сначала перемещаем курсор
        self._move_cursor_applescript(x, y)
        time.sleep(0.1)  # Небольшая задержка для перемещения
        
        # Сначала пробуем pyautogui
        try:
            pyautogui.click(x, y, button=button, clicks=clicks)
            return
        except Exception:
            pass
        
        # Если pyautogui не работает, пробуем cliclick (если установлен)
        try:
            button_map = {
                'left': 'c',      # click
                'right': 'rc',     # right click
                'middle': 'mc'     # middle click
            }
            click_type = button_map.get(button, 'c')
            
            for i in range(clicks):
                subprocess.run(['cliclick', f'{click_type}:{x},{y}'], 
                             check=True, capture_output=True, timeout=5)
                if i < clicks - 1:
                    time.sleep(0.1)  # Небольшая задержка между кликами
            return
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise Exception(
                f"Не удалось выполнить клик через pyautogui.\n"
                f"Установите cliclick для более надежной работы:\n"
                f"  brew install cliclick\n\n"
                f"Или проверьте разрешения:\n"
                f"  Системные настройки → Конфиденциальность и безопасность → Управление компьютером"
            )
    
    def click(self, x: Optional[int] = None, y: Optional[int] = None, 
              button: str = 'left', clicks: int = 1, interval: float = 0.1) -> None:
        """
        Выполнить клик по указанным координатам
        
        Args:
            x: Координата X (если None, клик по текущей позиции)
            y: Координата Y (если None, клик по текущей позиции)
            button: Кнопка мыши ('left', 'right', 'middle')
            clicks: Количество кликов
            interval: Интервал между кликами (в секундах)
        """
        try:
            if x is not None and y is not None:
                print(f"Кликаю по координатам ({x}, {y}) кнопкой {button}")
                # Сначала пробуем pyautogui
                try:
                    pyautogui.click(x, y, button=button, clicks=clicks, interval=interval)
                    return
                except Exception as e1:
                    # Если pyautogui не работает, пробуем cliclick (для macOS)
                    if self.is_macos:
                        try:
                            self._click_applescript(x, y, button, clicks)
                            if clicks > 1 and interval > 0:
                                time.sleep(interval * (clicks - 1))
                            return
                        except Exception as e2:
                            error_msg = f"❌ Ошибка при клике:\n"
                            error_msg += f"  pyautogui: {e1}\n"
                            error_msg += f"  cliclick: {e2}"
                            print(error_msg)
                            print("\n💡 Решение:")
                            print("  1. Установите cliclick: brew install cliclick")
                            print("  2. Или проверьте разрешения:")
                            print("     Системные настройки → Конфиденциальность и безопасность → Управление компьютером")
                            raise Exception(error_msg)
                    else:
                        raise e1
            else:
                print(f"Кликаю по текущей позиции кнопкой {button}")
                # Получаем текущую позицию
                pos = pyautogui.position()
                try:
                    pyautogui.click(button=button, clicks=clicks, interval=interval)
                    return
                except Exception as e1:
                    # Если pyautogui не работает, пробуем cliclick (для macOS)
                    if self.is_macos:
                        try:
                            self._click_applescript(pos.x, pos.y, button, clicks)
                            if clicks > 1 and interval > 0:
                                time.sleep(interval * (clicks - 1))
                            return
                        except Exception as e2:
                            raise Exception(f"Ошибка при клике: pyautogui={e1}, cliclick={e2}")
                    else:
                        raise e1
        except Exception as e:
            error_msg = f"❌ Ошибка при клике: {e}"
            print(error_msg)
            raise
    
    def double_click(self, x: Optional[int] = None, y: Optional[int] = None) -> None:
        """
        Двойной клик по координатам
        
        Args:
            x: Координата X
            y: Координата Y
        """
        self.click(x, y, clicks=2)
    
    def right_click(self, x: Optional[int] = None, y: Optional[int] = None) -> None:
        """
        Правый клик по координатам
        
        Args:
            x: Координата X
            y: Координата Y
        """
        self.click(x, y, button='right')
    
    def screenshot(self, filename: Optional[str] = None, 
                   region: Optional[Tuple[int, int, int, int]] = None) -> str:
        """
        Сделать скриншот экрана
        
        Args:
            filename: Имя файла для сохранения (если None, генерируется автоматически)
            region: Область для скриншота (x, y, width, height) или None для всего экрана
        
        Returns:
            Путь к сохраненному файлу
        """
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        # Создаем директорию screen-scan на рабочем столе если её нет
        desktop_path = Path.home() / "Desktop"
        screenshots_dir = desktop_path / "screen-scan"
        screenshots_dir.mkdir(exist_ok=True)
        filepath = screenshots_dir / filename
        
        print(f"Делаю скриншот: {filepath}")
        
        if region:
            screenshot = pyautogui.screenshot(region=region)
        else:
            screenshot = pyautogui.screenshot()
        
        screenshot.save(str(filepath))
        print(f"Скриншот сохранен: {filepath}")
        return str(filepath)
    
    def get_cursor_position(self) -> Tuple[int, int]:
        """
        Получить текущую позицию курсора
        
        Returns:
            Кортеж (x, y) с координатами курсора
        """
        try:
            pos = pyautogui.position()
            print(f"Текущая позиция курсора: {pos}")
            return pos
        except Exception as e:
            print(f"❌ Ошибка при получении позиции курсора: {e}")
            raise
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, 
             duration: float = 1.0) -> None:
        """
        Перетащить мышь от одной точки к другой
        
        Args:
            start_x: Начальная координата X
            start_y: Начальная координата Y
            end_x: Конечная координата X
            end_y: Конечная координата Y
            duration: Время перетаскивания в секундах
        """
        print(f"Перетаскиваю от ({start_x}, {start_y}) к ({end_x}, {end_y})")
        pyautogui.drag(start_x, start_y, end_x, end_y, duration=duration, button='left')
    
    def screenshot_and_ocr(self, filename: Optional[str] = None,
                           region: Optional[Tuple[int, int, int, int]] = None,
                           ocr_method: str = 'ocrspace',
                           ocr_api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Сделать скриншот и распознать текст с помощью OCR
        
        Args:
            filename: Имя файла для сохранения (если None, генерируется автоматически)
            region: Область для скриншота (x, y, width, height) или None для всего экрана
            ocr_method: Метод OCR ('ocrspace' или 'tesseract')
            ocr_api_key: API ключ для OCR.space (опционально, можно использовать бесплатный)
        
        Returns:
            Словарь с результатами: {'screenshot_path': str, 'text': str, 'success': bool, 'error': str}
        """
        # Сначала делаем скриншот
        screenshot_path = self.screenshot(filename, region)
        
        # Распознаем текст
        result = {
            'screenshot_path': screenshot_path,
            'text': '',
            'success': False,
            'error': None
        }
        
        try:
            print(f"\n{'='*60}")
            print("🔍 Начинаю распознавание текста (русский язык)...")
            print(f"{'='*60}")
            
            if ocr_method == 'ocrspace':
                text = self._ocr_ocrspace(screenshot_path, ocr_api_key)
            elif ocr_method == 'tesseract':
                text = self._ocr_tesseract(screenshot_path)
            else:
                raise ValueError(f"Неизвестный метод OCR: {ocr_method}")
            
            result['text'] = text
            result['success'] = True
            
            # Выводим распознанные данные в консоль
            print(f"\n✅ Текст успешно распознан!")
            print(f"📁 Файл: {screenshot_path}")
            print(f"📝 Метод: {ocr_method}")
            print(f"\n{'─'*60}")
            print("РАСПОЗНАННЫЙ ТЕКСТ:")
            print(f"{'─'*60}")
            if text.strip():
                print(text)
            else:
                print("(Текст не обнаружен на изображении)")
            print(f"{'─'*60}")
            print(f"Длина текста: {len(text)} символов")
            print(f"{'='*60}\n")
            
        except Exception as e:
            result['error'] = str(e)
            print(f"\n❌ Ошибка при распознавании текста: {e}")
            print(f"{'='*60}\n")
        
        return result
    
    def _ocr_ocrspace(self, image_path: str, api_key: Optional[str] = None, max_retries: int = 3) -> str:
        """
        Распознавание текста через OCR.space API (бесплатный)
        
        Args:
            image_path: Путь к изображению
            api_key: API ключ (опционально, можно использовать без ключа с лимитами)
            max_retries: Максимальное количество попыток при ошибке
        
        Returns:
            Распознанный текст
        """
        # OCR.space бесплатный API endpoint
        url = "https://api.ocr.space/parse/image"
        
        # Проверяем размер файла (OCR.space имеет лимит ~1MB для бесплатного API)
        file_size = Path(image_path).stat().st_size
        if file_size > 1024 * 1024:  # Больше 1MB
            print(f"⚠️  Внимание: размер файла {file_size / 1024 / 1024:.2f}MB, может быть слишком большим")
        
        for attempt in range(max_retries):
            try:
                with open(image_path, 'rb') as image_file:
                    files = {'file': image_file}
                    data = {
                        'apikey': api_key or 'helloworld',  # Бесплатный ключ по умолчанию
                        'language': 'rus',  # Русский язык
                        'isOverlayRequired': False,
                        'detectOrientation': True,
                        'OCREngine': 2,  # Используем более точный движок для русского
                    }
                    
                    # Увеличиваем таймаут до 60 секунд и добавляем retry
                    timeout = 60
                    if attempt > 0:
                        print(f"🔄 Попытка {attempt + 1}/{max_retries}...")
                        time.sleep(2 * attempt)  # Экспоненциальная задержка
                    
                    response = requests.post(url, files=files, data=data, timeout=timeout)
                    response.raise_for_status()
                    
                    result = response.json()
                    
                    if result.get('OCRExitCode') == 1:
                        # Успешно распознано
                        parsed_results = result.get('ParsedResults', [])
                        if parsed_results:
                            text = parsed_results[0].get('ParsedText', '')
                            return text.strip()
                        else:
                            return ''
                    else:
                        error_message = result.get('ErrorMessage', 'Неизвестная ошибка OCR')
                        if attempt < max_retries - 1:
                            print(f"⚠️  OCR ошибка: {error_message}, повторяю попытку...")
                            continue
                        raise Exception(f"OCR.space ошибка: {error_message}")
                        
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"⏱️  Таймаут соединения, повторяю попытку {attempt + 1}/{max_retries}...")
                    continue
                raise Exception("Таймаут соединения с OCR.space API. Попробуйте позже или используйте Tesseract (локальный OCR)")
            except requests.exceptions.ConnectionError as e:
                if attempt < max_retries - 1:
                    print(f"🔌 Ошибка соединения, повторяю попытку {attempt + 1}/{max_retries}...")
                    continue
                raise Exception(f"Ошибка соединения с OCR.space API: {e}. Проверьте интернет-соединение")
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️  Ошибка: {e}, повторяю попытку {attempt + 1}/{max_retries}...")
                    time.sleep(2 * attempt)
                    continue
                raise
    
    def _ocr_tesseract(self, image_path: str) -> str:
        """
        Распознавание текста через Tesseract OCR (локальный, требует установки)
        
        Args:
            image_path: Путь к изображению
        
        Returns:
            Распознанный текст
        """
        try:
            import pytesseract
        except ImportError:
            raise ImportError(
                "pytesseract не установлен. Установите: pip install pytesseract\n"
                "Также установите Tesseract OCR: brew install tesseract (macOS)"
            )
        
        try:
            image = Image.open(image_path)
            # Пробуем сначала русский язык
            try:
                text = pytesseract.image_to_string(image, lang='rus')
                return text.strip()
            except Exception as rus_error:
                # Если русский язык не установлен, пробуем английский
                print("⚠️  Русский языковой пакет не найден, использую английский")
                print("💡 Для установки русского языка: brew install tesseract-lang")
                try:
                    text = pytesseract.image_to_string(image, lang='eng')
                    return text.strip()
                except Exception as eng_error:
                    # Если и английский не работает, пробуем без указания языка
                    print("⚠️  Пробую без указания языка...")
                    text = pytesseract.image_to_string(image)
                    return text.strip()
        except Exception as e:
            error_msg = str(e)
            if 'rus.traineddata' in error_msg or 'Failed loading language' in error_msg:
                raise Exception(
                    f"Русский языковой пакет не установлен.\n"
                    f"Установите: brew install tesseract-lang\n"
                    f"Или используйте OCR.space (он поддерживает русский без установки): ocr_method='ocrspace'\n"
                    f"Ошибка: {e}"
                )
            raise Exception(f"Ошибка Tesseract OCR: {e}")
    
    def ocr_from_file(self, image_path: str, 
                      ocr_method: str = 'ocrspace',
                      ocr_api_key: Optional[str] = None) -> str:
        """
        Распознать текст из существующего файла изображения
        
        Args:
            image_path: Путь к файлу изображения
            ocr_method: Метод OCR ('ocrspace' или 'tesseract')
            ocr_api_key: API ключ для OCR.space (опционально)
        
        Returns:
            Распознанный текст
        """
        print(f"\n{'='*60}")
        print("🔍 Начинаю распознавание текста из файла (русский язык)...")
        print(f"📁 Файл: {image_path}")
        print(f"{'='*60}")
        
        try:
            if ocr_method == 'ocrspace':
                text = self._ocr_ocrspace(image_path, ocr_api_key)
            elif ocr_method == 'tesseract':
                text = self._ocr_tesseract(image_path)
            else:
                raise ValueError(f"Неизвестный метод OCR: {ocr_method}")
            
            # Выводим распознанные данные в консоль
            print(f"\n✅ Текст успешно распознан!")
            print(f"📝 Метод: {ocr_method}")
            print(f"\n{'─'*60}")
            print("РАСПОЗНАННЫЙ ТЕКСТ:")
            print(f"{'─'*60}")
            if text.strip():
                print(text)
            else:
                print("(Текст не обнаружен на изображении)")
            print(f"{'─'*60}")
            print(f"Длина текста: {len(text)} символов")
            print(f"{'='*60}\n")
            
            return text
            
        except Exception as e:
            print(f"\n❌ Ошибка при распознавании текста: {e}")
            print(f"{'='*60}\n")
            raise


def main():
    """Пример использования"""
    auto = MouseAutomation()
    
    # Получаем размер экрана
    screen_width, screen_height = auto.screen_size
    print(f"\nРазмер экрана: {screen_width}x{screen_height}")
    
    # Получаем текущую позицию курсора
    current_pos = auto.get_cursor_position()
    print(f"Текущая позиция: {current_pos}\n")
    
    # Пример 1: Переместить курсор
    print("=== Пример 1: Перемещение курсора ===")
    auto.move_cursor(100, 100, duration=0.5)
    time.sleep(1)
    
    # Пример 2: Клик по координатам
    print("\n=== Пример 2: Клик по координатам ===")
    auto.click(200, 200)
    time.sleep(1)
    
    # Пример 3: Скриншот
    print("\n=== Пример 3: Скриншот всего экрана ===")
    auto.screenshot()
    time.sleep(1)
    
    # Пример 4: Скриншот области
    print("\n=== Пример 4: Скриншот области ===")
    auto.screenshot("region_screenshot.png", region=(0, 0, 400, 300))
    
    # Пример 5: Скриншот с распознаванием текста
    print("\n=== Пример 5: Скриншот с OCR ===")
    result = auto.screenshot_and_ocr("ocr_screenshot.png", ocr_method='ocrspace')
    if result['success']:
        print(f"Распознанный текст: {result['text'][:100]}...")  # Первые 100 символов
    
    print("\n=== Готово! ===")


if __name__ == "__main__":
    main()
