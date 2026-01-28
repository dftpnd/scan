#!/usr/bin/env python3
"""
Скрипт-«наблюдатель», который:
1. Периодически двигает мышь, имитируя активность пользователя.
2. Делает скриншот экрана каждые N секунд.

По аналогии со `scan_and_parse.py`, использует класс `MouseAutomation`.
"""

import sys
import time
import math
import os
import re
import json
import hashlib
from typing import Optional, Tuple, List, Set, Dict
from pathlib import Path

import requests
import pyautogui
import pytesseract
from automation import MouseAutomation


def _get_subscriber_chat_ids(token: str) -> Set[int]:
    """
    Получить множество chat_id всех пользователей/чатов,
    которые когда‑либо писали этому боту (через getUpdates).
    """
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"⚠️  Не удалось получить getUpdates из Telegram: {e}")
        return set()

    result = data.get("result", [])
    chat_ids: Set[int] = set()

    for update in result:
        msg = update.get("message") or update.get("edited_message") or update.get("channel_post")
        if not msg:
            continue
        chat = msg.get("chat") or {}
        chat_id = chat.get("id")
        if isinstance(chat_id, int):
            chat_ids.add(chat_id)

    return chat_ids


def _create_unique_id(time_str: str, amount: float) -> str:
    """
    Создать уникальный ID из времени и суммы.
    Используем только время и сумму, так как событие может распознаваться по-разному из-за ошибок OCR.
    """
    # Нормализуем время: если пустое, используем пустую строку
    time_normalized = time_str.strip() if time_str else ""
    combined = f"{time_normalized}|{amount:.2f}"
    return hashlib.md5(combined.encode("utf-8")).hexdigest()


def _extract_table_rows_from_image(image) -> List[Dict]:
    """
    Распознать текст на изображении и вытащить строки таблицы.
    Каждая строка содержит: событие, время, сумму.
    Возвращает список объектов с полями: event, time, amount, unique_id.
    """
    try:
        text = pytesseract.image_to_string(image)
    except Exception as e:
        print(f"⚠️  Ошибка OCR (pytesseract): {e}")
        return []

    # Выводим в консоль полный распознанный текст
    print("----- РАСПОЗНАННЫЙ ТЕКСТ СО СКРИНШОТА -----")
    print(text)
    print("----- КОНЕЦ РАСПОЗНАННОГО ТЕКСТА -----")

    lines = text.splitlines()
    amount_pattern = re.compile(r"\$[0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{2})")
    time_pattern = re.compile(r"\b\d{1,2}:\d{2}\s*(?:AM|PM)\b", re.IGNORECASE)

    rows: List[Dict] = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Ищем сумму и время в строке
        amounts_in_line = amount_pattern.findall(line)
        times_in_line = time_pattern.findall(line)

        if not amounts_in_line:
            continue

        time_str = times_in_line[0].strip() if times_in_line else ""

        # Извлекаем сумму
        for match in amounts_in_line:
            raw = match.replace("$", "").replace(",", "")
            try:
                amount = float(raw)
            except ValueError:
                continue

            # Событие - это всё, что осталось в строке после удаления суммы и времени
            event_line = line
            event_line = re.sub(amount_pattern, "", event_line)
            event_line = re.sub(time_pattern, "", event_line)
            event_line = re.sub(r"\s+", " ", event_line).strip()

            # Если событие пустое или содержит только спецсимволы, всё равно добавляем строку
            # (событие может быть плохо распознано OCR, но сумма и время важнее для уникальности)
            if not event_line or event_line.strip() in ["@", "#", "®", "©"]:
                # Если событие не распознано, используем пустую строку
                event_line = ""

            unique_id = _create_unique_id(time_str, amount)
            rows.append({
                "event": event_line,
                "time": time_str,
                "amount": amount,
                "unique_id": unique_id
            })

    if rows:
        print(f"Найдено строк таблицы на скриншоте: {len(rows)}")
    else:
        print("Строки таблицы на скриншоте не найдены.")

    return rows


# Файл для хранения массива всех уникальных строк таблицы,
# чтобы не дублировать сообщения даже после перезапуска скрипта.
TABLE_ROWS_FILE = Path(__file__).resolve().parent / "table_rows.json"


def _load_table_rows() -> List[Dict]:
    """
    Загрузить массив всех уникальных строк таблицы из файла.
    """
    if not TABLE_ROWS_FILE.exists():
        return []
    try:
        raw = TABLE_ROWS_FILE.read_text(encoding="utf-8")
        data = json.loads(raw)
        if isinstance(data, list):
            print(f"Загружено {len(data)} строк таблицы из файла.")
            return data
        return []
    except Exception as e:
        print(f"⚠️  Не удалось загрузить файл {TABLE_ROWS_FILE}: {e}")
        return []


def _save_table_rows(rows: List[Dict]) -> None:
    """
    Сохранить массив всех уникальных строк таблицы в файл.
    """
    try:
        TABLE_ROWS_FILE.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Сохранено {len(rows)} строк таблицы в {TABLE_ROWS_FILE}.")
    except Exception as e:
        print(f"⚠️  Не удалось сохранить файл {TABLE_ROWS_FILE}: {e}")


# Глобальное состояние: массив всех уникальных строк таблицы (загружаем из файла)
TABLE_ROWS: List[Dict] = _load_table_rows()


def run_mouse_watchdog(
    interval_seconds: float = 10.0,
    move_radius: int = 50,
    center: Optional[Tuple[int, int]] = None,
) -> None:
    """
    Бесконечный цикл:
    - слегка двигает мышь по кругу вокруг центра
    - делает скриншот всего экрана
    - ждет `interval_seconds`

    Args:
        interval_seconds: интервал между скриншотами (и движениями мыши), в секундах
        move_radius: радиус движения мыши вокруг центра, в пикселях
        center: центр окружности (x, y). Если None — берется центр экрана.
    """
    auto = MouseAutomation()

    screen_w, screen_h = auto.screen_size

    # По умолчанию водим мышь в верхнем левом углу,
    # чтобы небольшая окружность не выходила за границы экрана.
    if center is None:
        cx, cy = move_radius + 10, move_radius + 10
    else:
        cx, cy = center

    print("=" * 60)
    print("🖱️  MOUSE WATCHDOG ЗАПУЩЕН")
    print(f"Интервал: {interval_seconds} c, радиус движения: {move_radius}px")
    print(f"Центр движения: ({cx}, {cy})")
    print("Нажмите Ctrl+C, чтобы остановить.")
    print("=" * 60)

    angle = 0.0

    try:
        while True:
            # Вычисляем новую точку по окружности
            x = int(cx + move_radius * math.cos(angle))
            y = int(cy + move_radius * math.sin(angle))

            # Ограничиваем координаты границами экрана
            x = max(0, min(screen_w - 1, x))
            y = max(0, min(screen_h - 1, y))

            print("\n" + "-" * 60)
            print(f"Перемещаю мышь в ({x}, {y}) и делаю скриншот...")

            auto.move_cursor(x, y, duration=0.3)
            # Делаем скриншот только в памяти (на диск сохраним позже, если сумма > 3000
            # и появилась новая уникальная строка)
            screenshot = pyautogui.screenshot()

            # --- OCR: распознаём строки таблицы на скриншоте ---
            parsed_rows = _extract_table_rows_from_image(screenshot)
            if not parsed_rows:
                print("Нет распознанных строк таблицы — не отправляю скриншот в Telegram.")
                angle += math.pi / 6  # шаг по кругу (30 градусов)
                print(f"Ожидаю {interval_seconds} секунд...")
                time.sleep(interval_seconds)
                continue

            # Находим новые уникальные строки, которых ещё не было
            global TABLE_ROWS
            existing_ids = {row["unique_id"] for row in TABLE_ROWS}
            new_rows = [row for row in parsed_rows if row["unique_id"] not in existing_ids]

            if not new_rows:
                print("Новых уникальных строк нет — не отправляю скриншот.")
                # Выводим весь массив в консоль
                print("\n" + "=" * 60)
                print("ТЕКУЩИЙ МАССИВ СТРОК ТАБЛИЦЫ:")
                print("=" * 60)
                for i, row in enumerate(TABLE_ROWS, 1):
                    print(f"{i}. [{row['unique_id'][:8]}...] Событие: {row['event'][:50]}, "
                          f"Время: {row['time']}, Сумма: ${row['amount']:,.2f}")
                print("=" * 60 + "\n")
                angle += math.pi / 6  # шаг по кругу (30 градусов)
                print(f"Ожидаю {interval_seconds} секунд...")
                time.sleep(interval_seconds)
                continue

            # Добавляем новые строки в массив
            TABLE_ROWS.extend(new_rows)
            _save_table_rows(TABLE_ROWS)

            print(f"Добавлено {len(new_rows)} новых уникальных строк.")

            # Выводим весь массив в консоль
            print("\n" + "=" * 60)
            print("ТЕКУЩИЙ МАССИВ СТРОК ТАБЛИЦЫ:")
            print("=" * 60)
            for i, row in enumerate(TABLE_ROWS, 1):
                print(f"{i}. [{row['unique_id'][:8]}...] Событие: {row['event'][:50]}, "
                      f"Время: {row['time']}, Сумма: ${row['amount']:,.2f}")
            print("=" * 60 + "\n")

            # Проверяем, есть ли среди новых строк сумма > 15000
            new_rows_with_high_amount = [row for row in new_rows if row["amount"] > 15000]

            if not new_rows_with_high_amount:
                print("Среди новых строк нет суммы > 15000 — не делаю и не отправляю скриншот.")
                angle += math.pi / 6  # шаг по кругу (30 градусов)
                print(f"Ожидаю {interval_seconds} секунд...")
                time.sleep(interval_seconds)
                continue

            # Фильтруем строки, у которых есть и событие, и время
            valid_rows = [
                row for row in new_rows_with_high_amount
                if row["event"].strip() and row["time"].strip()
            ]

            if not valid_rows:
                print("Среди новых строк с суммой > 15000 нет строк с событием и временем — не отправляю скриншот в Telegram.")
                angle += math.pi / 6  # шаг по кругу (30 градусов)
                print(f"Ожидаю {interval_seconds} секунд...")
                time.sleep(interval_seconds)
                continue

            max_amount_new = max(row["amount"] for row in valid_rows)
            print(f"Есть новая строка с суммой > 15000 (максимум: ${max_amount_new:,.2f}) — сохраняю и отправляю скриншот в Telegram.")

            # Готовим данные для сохранения и отправки
            file_timestamp = time.strftime("%Y%m%d_%H%M%S")
            timestamp = time.strftime("%d/%m/%y %H:%M")  # для человека, "DD/MM/YY HH:MM"
            project_dir = Path(__file__).resolve().parent
            screens_dir = project_dir / "screens"
            screens_dir.mkdir(exist_ok=True)
            screenshot_path = screens_dir / f"{file_timestamp}.png"
            print(f"Сохраняю скриншот на диск: {screenshot_path}")
            screenshot.save(str(screenshot_path))

            # Отправка скриншота в Telegram всем подписавшимся (написавшим боту)
            token = os.getenv("TELEGRAM_BOT_TOKEN")
            if not token:
                print("⚠️  TELEGRAM_BOT_TOKEN не задан, пропускаю отправку в Telegram.")
            else:
                chat_ids = _get_subscriber_chat_ids(token)
                if not chat_ids:
                    print("⚠️  Нет подписчиков (никто еще не написал боту), некого оповещать.")
                else:
                    base_url = f"https://api.telegram.org/bot{token}"
                    photo_url = f"{base_url}/sendPhoto"

                    # Формируем текст для подписи к картинке
                    last_row = valid_rows[-1]
                    caption = f"Скриншот сделан в момент: {timestamp}\n\n"
                    caption += f"Событие: {last_row['event']}\n"
                    caption += f"Время: {last_row['time']}\n"
                    caption += f"Сумма: ${last_row['amount']:,.2f}"

                    for chat_id in chat_ids:
                        # Отправляем скриншот с текстом как подписью (caption)
                        try:
                            with open(screenshot_path, "rb") as f:
                                files = {"photo": f}
                                data = {"chat_id": chat_id, "caption": caption}
                                resp = requests.post(photo_url, data=data, files=files, timeout=15)
                            if resp.ok:
                                print(f"✅ Скриншот с описанием отправлен в Telegram (chat_id={chat_id}).")
                            else:
                                print(f"⚠️  Ошибка отправки скриншота в Telegram для chat_id={chat_id}: {resp.status_code} {resp.text}")
                        except Exception as e:
                            print(f"⚠️  Исключение при отправке скриншота в Telegram для chat_id={chat_id}: {e}")

            angle += math.pi / 6  # шаг по кругу (30 градусов)

            print(f"Ожидаю {interval_seconds} секунд...")
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("\n🛑 Остановлено пользователем (Ctrl+C).")
        print("Выход.")


def main():
    """
    Запуск из командной строки.

    Примеры:
        python mouse_watchdog.py
        python mouse_watchdog.py 10       # интервал 10 c
        python mouse_watchdog.py 5 80     # интервал 5 c, радиус 80 px
    """
    interval = 10.0
    radius = 50

    try:
        if len(sys.argv) >= 2:
            interval = float(sys.argv[1])
        if len(sys.argv) >= 3:
            radius = int(sys.argv[2])
    except ValueError:
        print("Использование: python mouse_watchdog.py [interval_seconds] [move_radius]")
        print("Пример:       python mouse_watchdog.py 10 50")
        sys.exit(1)

    run_mouse_watchdog(interval_seconds=interval, move_radius=radius)


if __name__ == "__main__":
    main()

