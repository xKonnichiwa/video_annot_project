# --- Стандартные библиотеки Python ---
import json  # Библиотека для работы с JSON файлами (чтение, запись, парсинг)
import os  # Библиотека для работы с файловой системой (например, проверка существования файлов, создание директорий)
import numpy as np  # Библиотека для работы с массивами и математическими операциями (например, для обработки данных)

# --- Библиотеки для обработки видео ---
from moviepy.editor import VideoFileClip, concatenate_videoclips  # Импорт класса VideoFileClip для работы с видео (извлечение, резка), Дополнительно импортируем concatenate_videoclips для объединения видеоклипов
from scenedetect import VideoManager, SceneManager  # Импорт классов VideoManager и SceneManager для детектирования сцен в видео
from scenedetect.detectors import ContentDetector  # Детектор ContentDetector для анализа содержимого видео и выявления сцен

# --- Модули для обработки аудио и кластеризации (импорт собственных модулей) ---
from audio import process_video_to_audio_analysis  # Импорт функции для обработки аудио и анализа звука в видео
from clastering_clasters import process_clusters  # Импорт функции для обработки кластеров (например, шотов)
from video import process_video  # Импорт функции для обработки видео (например, детектирование объектов, сегментация)
from clastersTojson import process_and_analyze  # Импорт функции для анализа и объединения данных аудио и видео в JSON формат
import shutil


def format_time(seconds):
    """
    Форматирует время, заданное в секундах, в строку формата 'HH:MM:SS'.

    Аргументы:
    seconds — время в секундах (может быть целым или вещественным числом).

    Возвращает:
    Строку в формате 'HH:MM:SS', где:
    - HH — часы (дополненные до 2 знаков).
    - MM — минуты (дополненные до 2 знаков).
    - SS — секунды (дополненные до 2 знаков).

    Пример:
    format_time(3661) -> '01:01:01'
    """
    
    # --- Шаг 1: Расчет часов ---
    
    hours = int(seconds // 3600)  # Часы вычисляются как целое число от деления на 3600 (количество секунд в часе)

    # --- Шаг 2: Расчет минут ---
    
    # Для вычисления минут:
    # Берем остаток от деления на 3600 (секунды, оставшиеся после выделения часов),
    # и делим его на 60, чтобы получить количество минут.
    minutes = int((seconds % 3600) // 60)

    # --- Шаг 3: Расчет секунд ---
    
    # Остаток от деления на 60 дает количество секунд.
    seconds = int(seconds % 60)

    # --- Шаг 4: Форматирование времени ---
    
    # Формируем строку формата 'HH:MM:SS' с дополнением нулями до 2 знаков
    return f"{hours:02}:{minutes:02}:{seconds:02}"


# Загрузка видео и настройка SceneManager
video_path = "10-22.mp4"  # Путь к видеофайлу
output_dir = "shots"  # Папка для сохранения шотов

# Проверяем и создаем папку для сохранения шотов, если она не существует
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Настройка менеджера видео и сцены
video_manager = VideoManager([video_path])
scene_manager = SceneManager()
scene_manager.add_detector(ContentDetector(threshold=30.0))  # Устанавливаем порог для разбиения на шоты

# Начинаем разбиение видео на шоты
video_manager.start()
scene_manager.detect_scenes(frame_source=video_manager)
scenes = scene_manager.get_scene_list()  # Получаем список шотов (сцен)
video_manager.release()

# Загружаем видео с помощью MoviePy
video_clip = VideoFileClip(video_path)
json_output_video_path = 'video_results_new_russia_V1.json'
json_output_audio_path = 'audio_results_new_russia_V1.json'
json_output_clasters_analiz_path = 'clasters_merged_russia_V1.json'

shot_timings = {}

for i, scene in enumerate(scenes):
    start_time = scene[0].get_seconds()  # Начало шота в секундах
    end_time = scene[1].get_seconds()  # Конец шота в секундах
    print(f"Shot {i+1}: Start - {format_time(start_time)}, End - {format_time(end_time)}")
    # Добавляем тайминги в словарь с ключом shot_{i+1}
    shot_timings[f"shot_{i + 1}"] = {
        "start_time": format_time(start_time),
        "end_time": format_time(end_time)
    }
    # Извлекаем подфрагмент (шот) из видео
    subclip = video_clip.subclip(start_time, end_time)

    # Сохраняем шот в виде отдельного видеофайла
    shot_output_path = os.path.join(output_dir, f"shot_{i+1}.mp4")
    subclip.write_videofile(shot_output_path, codec="libx264")
    # Пример использования
    video_path = f"shots/shot_{i+1}.mp4"

    process_video_to_audio_analysis(video_path,json_output_audio_path)
    process_video(video_path, json_output_video_path)  # Пропускать 10 кадров

    print(f"Shot {i+1} saved as {shot_output_path}")

# Проходим по каждому шоту и сохраняем его как отдельный файл


timings_output_path = os.path.join("shot_timings_russia_V1.json")
with open(timings_output_path, 'w', encoding='utf-8') as f:
    json.dump(shot_timings, f, ensure_ascii=False, indent=4)
    

process_and_analyze(json_output_audio_path,json_output_video_path, json_output_clasters_analiz_path)
process_clusters("clasters_merged_russia_V1.json", json_output_audio_path, json_output_video_path, "final_test_russia_V1.json")
print("All shots have been extracted and saved.")



def create_scenes_from_shots(shots_folder, final_json_file, scenes_folder):
    """
    Объединяет шоты (отрезки видео) в сцены на основе данных кластеризации и сохраняет каждую сцену как отдельный видеоклип.

    Аргументы:
    shots_folder — путь к папке, содержащей отдельные видеошоты в формате .mp4.
                   Пример: 'shots/'.
    final_json_file — путь к JSON файлу, содержащему информацию о кластеризации шотов (какие шоты входят в какую сцену).
                      Пример: 'final_test.json'.
    scenes_folder — путь к папке, в которую будут сохраняться созданные сцены.
                    Пример: 'scenes/'.

    Описание:
    - Считывает данные кластеризации из JSON файла.
    - Для каждого кластера (сцены) находит соответствующие видеошоты.
    - Объединяет шоты в единый видеоклип и сохраняет его в указанной папке `scenes_folder`.
    """

    # --- Шаг 1: Очистка выходной папки перед созданием сцен ---
    
    if os.path.exists(scenes_folder):
        # Удаляем все файлы и подкаталоги в папке `scenes_folder`
        shutil.rmtree(scenes_folder)

    # Создаем пустую папку для сохранения сцен
    os.makedirs(scenes_folder)

    # --- Шаг 2: Чтение данных кластеризации из JSON файла ---
    
    with open(final_json_file, 'r', encoding='utf-8') as f:
        cluster_data = json.load(f)

    # --- Шаг 3: Проход по каждому кластеру (сцене) ---
    
    for cluster_id, shots in cluster_data.items():
        clips = []

        # --- Шаг 4: Проход по каждому шоту в кластере ---
        
        for shot in shots:
            shot_file = os.path.join(shots_folder, f"{shot}.mp4")

            if os.path.exists(shot_file):
                clip = VideoFileClip(shot_file)
                
                # Добавляем только непустые клипы
                if clip.duration > 0:
                    clips.append(clip)
                else:
                    print(f"Пропуск пустого шота: {shot_file}")
            else:
                print(f"Файл {shot_file} не найден.")

        # --- Шаг 5: Объединение шотов и создание финального видеоклипа ---
        
        if clips:
            try:
                # Используем метод "compose", чтобы выровнять размеры клипов
                final_clip = concatenate_videoclips(clips, method="compose")

                # Сохранение объединенного клипа как новой сцены
                output_file = os.path.join(scenes_folder, f"scene_{cluster_id}.mp4")
                final_clip.write_videofile(output_file, codec='libx264')

                # Закрываем клипы, чтобы освободить ресурсы
                for clip in clips:
                    clip.close()
                final_clip.close()
            except Exception as e:
                print(f"Ошибка при объединении или сохранении сцены {cluster_id}: {e}")

# Пример вызова функции
shots_folder = "shots"  # Папка с шотами
final_json_file = "final_test_russia_V1.json"  # Файл с описанием кластеров
scenes_folder = "scenes"  # Папка для сохранения сцен

# Очистка и создание новых сцен
create_scenes_from_shots(shots_folder, final_json_file, scenes_folder)

def analyze_existing_scenes(scenes_folder):
    """
    Выполняет анализ аудио и видео для всех видеоклипов в папке сцен.
    
    Аргументы:
    scenes_folder — путь к папке, содержащей видеофайлы сцен (например, 'scenes/').
    
    Описание:
    - Проходит по всем .mp4 файлам в указанной папке.
    - Для каждого видеофайла выполняется анализ аудио и видео с помощью функции `process_video_to_audio_analysis`.
    - Анализируется только каждый 100-й кадр для ускорения обработки.
    """
    
    # --- Шаг 1: Проход по всем файлам в папке сцен ---
    
    # Перебираем все файлы в папке `scenes_folder`
    for scene_file in os.listdir(scenes_folder):
        # Проверяем, является ли текущий файл видеофайлом с расширением .mp4
        if scene_file.endswith(".mp4"):
            # --- Шаг 2: Формируем полный путь к видеофайлу ---
            
            # Путь к текущему видеофайлу сцены
            video_path = os.path.join(scenes_folder, scene_file)
            
            # --- Шаг 3: Определение путей для сохранения результатов анализа ---
            
            # Путь для сохранения результатов анализа аудио
            json_output_audio_path_scenes = 'json_audio_scenes_russia_V1.json'
            # Путь для сохранения результатов анализа видео
            json_output_video_path_scenes = 'json_video_scenes_russia_V1.json'

            # --- Шаг 4: Выполнение анализа аудио и видео ---
            
            # Анализ аудиодорожки и сохранение результатов в json_output_audio_path_scenes
            process_video_to_audio_analysis(video_path, json_output_audio_path_scenes)
            
            # Анализ видеодорожки, обрабатываем каждый 100-й кадр
            process_video(video_path, json_output_video_path_scenes, process_every_100_frames=True)


# Пример вызова функции
scenes_folder = "scenes"  # Папка с уже созданными сценами

analyze_existing_scenes(scenes_folder)

json_output_video_path_full = 'json_video_full_russia_V1.json'

process_video(video_path,json_output_video_path_full, process_every_100_frames = True)