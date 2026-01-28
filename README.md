# Автоматизация мыши и скриншотов

Проект для автоматизации работы с мышью и создания скриншотов на macOS.

## Возможности

- ✅ Перемещение курсора мыши
- ✅ Клики по заданным координатам (левый, правый, двойной клик)
- ✅ Создание скриншотов (весь экран или область)
- ✅ Распознавание текста с помощью OCR (бесплатные API)
- ✅ Перетаскивание мыши

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

**Важно для macOS:** При первом запуске macOS может запросить разрешения на доступ к:
- Управление компьютером (для управления мышью)
- Захват экрана (для скриншотов)

Разрешите доступ в настройках: **Системные настройки → Конфиденциальность и безопасность**

### Решение проблем с зависанием мыши на macOS

Если курсор не двигается или зависает, попробуйте:

1. **Использовать AppleScript (рекомендуется для macOS):**
```python
auto = MouseAutomation(use_applescript=True)
```

2. **Проверить разрешения:**
   - Системные настройки → Конфиденциальность и безопасность
   - Убедитесь, что Terminal/Python имеет разрешение на "Управление компьютером"
   - Перезапустите терминал после изменения разрешений

3. **Запустить тест:**
```bash
python test_mouse.py
```

Этот скрипт автоматически проверит оба метода и покажет, какой работает.

## Использование

### Базовое использование

```python
from automation import MouseAutomation

# Создаем экземпляр
# Для macOS рекомендуется использовать AppleScript:
auto = MouseAutomation(use_applescript=True)  # или False для pyautogui

# Переместить курсор
auto.move_cursor(500, 300, duration=0.5)

# Кликнуть по координатам
auto.click(500, 300)

# Сделать скриншот
auto.screenshot("my_screenshot.png")
```

### Примеры

#### 1. Перемещение курсора
```python
auto = MouseAutomation()
auto.move_cursor(100, 100, duration=1.0)  # Плавное перемещение за 1 секунду
```

#### 2. Клики
```python
# Обычный клик
auto.click(200, 200)

# Двойной клик
auto.double_click(200, 200)

# Правый клик
auto.right_click(200, 200)
```

#### 3. Скриншоты
```python
# Скриншот всего экрана (автоматическое имя файла)
auto.screenshot()

# Скриншот с указанным именем
auto.screenshot("my_screenshot.png")

# Скриншот области (x, y, width, height)
auto.screenshot("region.png", region=(0, 0, 400, 300))
```

#### 4. Получить текущую позицию курсора
```python
x, y = auto.get_cursor_position()
print(f"Курсор находится в ({x}, {y})")
```

#### 5. Перетаскивание
```python
auto.drag(100, 100, 500, 500, duration=1.0)
```

#### 6. Распознавание текста (OCR)
```python
# Скриншот с автоматическим распознаванием текста (OCR.space API - бесплатный)
result = auto.screenshot_and_ocr("screenshot.png", ocr_method='ocrspace')
if result['success']:
    print(result['text'])

# Или использовать Tesseract (локальный, требует установки)
result = auto.screenshot_and_ocr("screenshot.png", ocr_method='tesseract')

# Распознать текст из существующего файла
text = auto.ocr_from_file("existing_image.png", ocr_method='ocrspace')
```

**Методы OCR:**
- **`ocrspace`** (по умолчанию) - бесплатный API, 25,000 запросов/день, не требует установки
- **`tesseract`** - локальный OCR, полностью бесплатный, требует установки Tesseract

## Быстрый старт (единый скрипт)

**Рекомендуется:** Используйте `scan_and_parse.py` для полного цикла автоматизации:

```bash
# Интерактивный режим
python scan_and_parse.py

# Или с параметрами из командной строки
python scan_and_parse.py 500 300 true
```

Этот скрипт выполняет последовательно:
1. ✅ Перемещает курсор в указанные координаты
2. ✅ Делает клик
3. ✅ Делает скриншот
4. ✅ Распознает текст из скриншота

### Использование как модуль

```python
from scan_and_parse import scan_and_parse

# Простой вызов
result = scan_and_parse(500, 300)

# С настройками
result = scan_and_parse(
    x=500,
    y=300,
    click=True,
    screenshot_region=(0, 0, 800, 600),  # Область скриншота
    ocr_method='ocrspace',
    wait_before_click=0.5,
    wait_after_click=1.0
)

if result['success']:
    print(f"Текст: {result['text']}")
    print(f"Скриншот: {result['screenshot_path']}")
```

## Другие примеры

```bash
# Основной пример
python automation.py

# Тест работы мыши
python test_mouse.py

# Пример OCR
python example_ocr.py
```

Скриншоты сохраняются в папку `screen-scan` на рабочем столе (`~/Desktop/screen-scan/`).

## API

### MouseAutomation

#### `move_cursor(x, y, duration=0.5)`
Перемещает курсор в указанные координаты.

#### `click(x=None, y=None, button='left', clicks=1, interval=0.1)`
Выполняет клик. Если координаты не указаны, кликает по текущей позиции.

#### `double_click(x=None, y=None)`
Двойной клик.

#### `right_click(x=None, y=None)`
Правый клик.

#### `screenshot(filename=None, region=None)`
Создает скриншот. Возвращает путь к файлу.

#### `get_cursor_position()`
Возвращает текущую позицию курсора (x, y).

#### `drag(start_x, start_y, end_x, end_y, duration=1.0)`
Перетаскивает мышь от одной точки к другой.

#### `screenshot_and_ocr(filename=None, region=None, ocr_method='ocrspace', ocr_api_key=None)`
Делает скриншот и распознает текст. Возвращает словарь с результатами:
- `screenshot_path` - путь к сохраненному скриншоту
- `text` - распознанный текст
- `success` - успешность операции
- `error` - сообщение об ошибке (если есть)

#### `ocr_from_file(image_path, ocr_method='ocrspace', ocr_api_key=None)`
Распознает текст из существующего файла изображения.

## Установка OCR

### OCR.space (рекомендуется, по умолчанию)
Не требует дополнительной установки. Работает сразу после установки зависимостей.

Для увеличения лимитов можно получить бесплатный API ключ на [ocr.space](https://ocr.space/ocrapi/freekey).

### Tesseract OCR (локальный)
Если хотите использовать локальный Tesseract:

1. Установите Tesseract:
```bash
brew install tesseract
```

2. Установите языковые пакеты (опционально):
```bash
brew install tesseract-lang
```

3. Используйте в коде:
```python
result = auto.screenshot_and_ocr("screenshot.png", ocr_method='tesseract')
```

## Безопасность

По умолчанию включена защита FAILSAFE: если переместить мышь в верхний левый угол экрана, выполнение прервется. Это можно отключить при инициализации:

```python
auto = MouseAutomation(fail_safe=False)
```
