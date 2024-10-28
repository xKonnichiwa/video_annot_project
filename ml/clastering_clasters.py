# Импорт стандартных библиотек
import json  # Импорт модуля для работы с JSON (чтение и запись данных)
import re  # Импорт модуля для работы с регулярными выражениями (поиск и замена шаблонов в строках)

# Импорт классов и функций из библиотеки sklearn
from sklearn.feature_extraction.text import TfidfVectorizer  # Импорт класса для векторизации текста с помощью TF-IDF

# Импорт класса Counter из стандартного модуля collections для подсчета частоты элементов в коллекциях
from collections import Counter

# Импорт пользовательских функций и классов из модуля clastersTojson
from clastersTojson import (
    apply_agglomerative,  # Импорт функции для выполнения агломеративной кластеризации
    convert_to_serializable,  # Импорт функции для преобразования объектов в сериализуемый формат (например, для JSON)
    determine_optimal_clusters_silhouette,  # Импорт функции для определения оптимального количества кластеров
    merge_shot_data,  # Импорт функции для объединения данных аудио и видео по шотам
    print_metrics  # Импорт функции для вывода метрик качества кластеризации
)

def merge_cluster_data(cluster_shots, audio_shots, video_shots):
    """
    Объединяет и усредняет данные для всех шотов в кластере, создавая одно описание для каждого кластера.

    Аргументы:
    cluster_shots — список шотов, которые принадлежат текущему кластеру.
    audio_shots — словарь с данными аудио-шотов, структура: {'shot_id': данные аудио}.
    video_shots — словарь с данными видео-шотов, структура: {'shot_id': данные видео}.

    Возвращает:
    cluster_description — словарь, содержащий объединенные и усредненные метрики для всего кластера.
    Структура словаря:
    - 'transcription': Наиболее часто встречающаяся транскрипция в кластере.
    - 'sentiment': Наиболее часто встречающаяся тональность (sentiment) в кластере.
    - 'rms': Среднее значение RMS по всем шотам.
    - 'spectral_centroid': Среднее значение спектрального центра по всем шотам.
    - 'spectral_bandwidth': Средняя спектральная ширина по всем шотам.
    - 'clap_analysis': Наиболее часто встречающийся звуковой класс по данным CLAP.
    - 'labeled_transcriptions': Наиболее часто встречающаяся метка категории для сегментов текста.
    - 'avg_video_objects': Список уникальных объектов, найденных в видео.
    - 'avg_events': Список уникальных событий, обнаруженных в видео.
    - 'moving_objects': Описание всех движущихся объектов в текстовом формате.
    """

    # --- Инициализация списков для хранения данных по всем шотам ---
    
    all_transcriptions = []  # Список для хранения всех транскрипций
    all_sentiments = []  # Список для хранения всех меток тональности
    all_rms = []  # Список для хранения значений RMS
    all_spectral_centroids = []  # Список для хранения спектральных центров
    all_spectral_bandwidths = []  # Список для хранения спектральной ширины
    all_clap_analysis = []  # Список для хранения меток звуковых классов
    all_labeled_transcriptions = []  # Список для хранения категорий текста
    all_video_objects = []  # Список для хранения всех объектов, найденных в видео
    all_video_events = []  # Список для хранения всех событий, найденных в видео
    all_moving_objects = []  # Список для хранения описания всех движущихся объектов

    # --- Проход по каждому шоту в кластере ---
    
    for shot in cluster_shots:
        # Проверяем, присутствует ли шот и в аудио-, и в видео-данных
        if shot in audio_shots and shot in video_shots:
            
            # Объединяем данные аудио и видео для текущего шота
            description = merge_shot_data(audio_shots[shot], video_shots[shot])

            # --- Сбор данных для дальнейшего усреднения и анализа ---
            
            # Добавляем транскрипцию, тональность и звуковой анализ в соответствующие списки
            all_transcriptions.append(description['transcription'])
            all_sentiments.append(description['sentiment'])
            all_rms.append(description['rms'])
            all_spectral_centroids.append(description['spectral_centroid'])
            all_spectral_bandwidths.append(description['spectral_bandwidth'])
            all_clap_analysis.append(description['clap_analysis'])
            all_labeled_transcriptions.append(description['labeled_transcriptions'])

            # Расширяем список объектов и событий
            all_video_objects.extend(description['avg_video_objects'])
            all_video_events.extend(description['avg_events'])
            all_moving_objects.append(description['moving_objects'])

    # --- Анализ собранных данных: усреднение и выбор наиболее частых элементов ---
    
    # Для строковых данных (транскрипции, метки) определяем самый частый элемент
    most_common_transcription = Counter(all_transcriptions).most_common(1)[0][0]  # Самая частая транскрипция
    most_common_sentiment = Counter(all_sentiments).most_common(1)[0][0]  # Самая частая метка тональности
    most_common_clap_analysis = Counter(all_clap_analysis).most_common(1)[0][0]  # Самый частый звуковой класс
    most_common_labeled_transcription = Counter(all_labeled_transcriptions).most_common(1)[0][0]  # Самая частая категория текста

    # --- Усреднение числовых данных ---
    
    avg_rms = sum(all_rms) / len(all_rms) if all_rms else 0  # Среднее значение RMS
    avg_spectral_centroid = sum(all_spectral_centroids) / len(all_spectral_centroids) if all_spectral_centroids else 0  # Средний спектральный центр
    avg_spectral_bandwidth = sum(all_spectral_bandwidths) / len(all_spectral_bandwidths) if all_spectral_bandwidths else 0  # Средняя спектральная ширина

    # --- Определение уникальных объектов и событий ---
    
    avg_video_objects = list(set(all_video_objects))  # Уникальные объекты, найденные в видео
    avg_events = list(set(all_video_events))  # Уникальные события в видео
    
    # Преобразование списка движущихся объектов в строку
    all_moving_objects_str = ', '.join(all_moving_objects)

    # --- Формирование итогового описания для всего кластера ---
    
    cluster_description = {
        'transcription': most_common_transcription,  # Самая частая транскрипция
        'sentiment': most_common_sentiment,  # Самая частая метка тональности
        'rms': avg_rms,  # Среднее значение RMS
        'spectral_centroid': avg_spectral_centroid,  # Средний спектральный центр
        'spectral_bandwidth': avg_spectral_bandwidth,  # Средняя спектральная ширина
        'clap_analysis': most_common_clap_analysis,  # Самый частый звуковой класс
        'labeled_transcriptions': most_common_labeled_transcription,  # Самая частая категория текста
        'avg_video_objects': avg_video_objects,  # Уникальные объекты в видео
        'avg_events': avg_events,  # Уникальные события в видео
        'moving_objects': all_moving_objects_str  # Описание всех движущихся объектов
    }

    # --- Возвращение итогового описания кластера ---
    
    return cluster_description  # Возвращаем словарь с объединенными данными для кластера

def calculate_distance(shot1, shot2):
    """
    Функция для расчета расстояния между шотами по их порядковым номерам.
    
    Аргументы:
    shot1 — идентификатор первого шота в формате строки, например, 'shot_1'.
    shot2 — идентификатор второго шота в формате строки, например, 'shot_5'.

    Возвращает:
    Расстояние между шотами, рассчитанное на основе разницы их порядковых номеров.
    Например, если `shot1` = 'shot_1' и `shot2` = 'shot_5', функция вернет 4.
    """
    
    # --- Извлечение порядковых номеров из идентификаторов шотов ---
    
    # Используем метод `split` для разделения строк 'shot_1' и 'shot_2' по символу '_'.
    # Разделение строки 'shot_1' даст список ['shot', '1'], и второй элемент (индекс [1]) — это номер шота.
    # Преобразуем этот номер в целое число с помощью `int()`.
    shot1_number = int(shot1.split('_')[1])  # Извлечение номера первого шота
    shot2_number = int(shot2.split('_')[1])  # Извлечение номера второго шота

    # --- Расчет абсолютной разницы между порядковыми номерами ---
    
    # Возвращаем абсолютное значение разницы между номерами шотов.
    # Например, для номеров 1 и 5 разница будет abs(1 - 5) = 4.
    return abs(shot1_number - shot2_number)  # Возвращаем расстояние между шотами

def split_cluster(cluster_shots, threshold=10):
    """
    Функция для разделения шотов в кластере на подгруппы на основе расстояния между ними.

    Аргументы:
    cluster_shots — список идентификаторов шотов, например, ['shot_1', 'shot_2', 'shot_10'].
    threshold — пороговое значение расстояния между шотами, при превышении которого шоты будут
                разделены на разные подгруппы (по умолчанию: 10).

    Возвращает:
    sub_clusters — список подгрупп шотов, каждая подгруппа представлена как отдельный список.
    Например, если шоты имеют идентификаторы ['shot_1', 'shot_2', 'shot_15'], при `threshold=10` 
    функция вернет [['shot_1', 'shot_2'], ['shot_15']].
    """

    # --- Проверка на случай, если в кластере только один или ни одного шота ---
    
    if len(cluster_shots) <= 1:
        return [cluster_shots]  # Если список пуст или содержит только один шот, возвращаем его как единственную группу

    # --- Сортировка шотов по их порядковым номерам ---
    
    # Сортируем шоты на основе их порядковых номеров, извлекая их с помощью `shot.split('_')[1]`.
    # Например, если `cluster_shots` = ['shot_15', 'shot_2', 'shot_1'], после сортировки получится ['shot_1', 'shot_2', 'shot_15'].
    cluster_shots = sorted(cluster_shots, key=lambda shot: int(shot.split('_')[1]))

    # --- Инициализация первой подгруппы и списка подгрупп ---
    
    sub_clusters = []  # Пустой список для хранения подгрупп
    current_subcluster = [cluster_shots[0]]  # Инициализируем первую подгруппу первым шотом

    # --- Проход по шотам и разделение на подгруппы ---
    
    for i in range(1, len(cluster_shots)):
        # Вычисляем расстояние между текущим и предыдущим шотом
        distance = calculate_distance(cluster_shots[i - 1], cluster_shots[i])
        
        # --- Условие добавления шота в текущую подгруппу ---
        
        if distance <= threshold:
            # Если расстояние меньше или равно порогу `threshold`, добавляем шот в текущую подгруппу
            current_subcluster.append(cluster_shots[i])
        else:
            # Иначе заканчиваем текущую подгруппу и начинаем новую
            sub_clusters.append(current_subcluster)  # Сохраняем текущую подгруппу
            current_subcluster = [cluster_shots[i]]  # Создаем новую подгруппу, начиная с текущего шота

    # --- Добавление последней подгруппы ---
    
    sub_clusters.append(current_subcluster)  # Добавляем последнюю подгруппу в список подгрупп

    # --- Возвращение результата ---
    
    return sub_clusters  # Возвращаем список подгрупп

def remove_cluster(cluster_map, cluster_to_remove):
    """
    Удаляет заданный кластер и все связанные с ним группы из словаря кластеров.

    Аргументы:
    cluster_map — словарь, содержащий структуру кластеров, где:
        - Ключ: идентификатор кластера (например, 'cluster_1').
        - Значение: список связанных кластеров или элементов, относящихся к данному кластеру.
    Пример структуры: {'cluster_1': {'element_1', 'element_2'}, 'cluster_2': {'element_3', 'cluster_1'}}.

    cluster_to_remove — идентификатор кластера, который нужно удалить.

    Возвращает:
    Словарь с удаленными группами, где:
    - Ключ: удаленный кластер.
    - Значение: список групп (списков), которые были удалены.
    Если удаленных групп нет, возвращает пустой словарь.
    Пример возвращаемого значения: {'cluster_1': [['element_1', 'element_2', 'cluster_1']]}
    """

    # --- Инициализация переменных ---
    
    removed_groups = []  # Список для хранения удаленных групп

    # --- Проверка наличия кластера для удаления ---
    
    if cluster_to_remove in cluster_map:  # Если кластер, который нужно удалить, присутствует в cluster_map
        # Если у удаляемого кластера есть связанные элементы, добавляем их в список удаленных групп
        if cluster_map[cluster_to_remove]:
            removed_groups.append(list(cluster_map[cluster_to_remove]) + [cluster_to_remove])
        
        # Удаляем сам кластер из словаря
        del cluster_map[cluster_to_remove]

    # --- Поиск всех групп, которые содержат кластер для удаления ---
    
    to_remove = set()  # Множество для хранения идентификаторов групп, которые нужно удалить

    # Проходим по всем кластерам и их связанным элементам
    for key, value in cluster_map.items():
        if cluster_to_remove in value:  # Если кластер для удаления присутствует в значениях текущей группы
            to_remove.add(key)  # Добавляем ключ группы в список для удаления

    # --- Удаление групп, которые содержат удаляемый кластер ---
    
    for group in to_remove:
        # Если группа содержит связанные значения, добавляем их в список удаленных групп
        if cluster_map[group]:
            removed_groups.append(list(cluster_map[group]) + [group])
        
        # Удаляем группу из основного словаря
        del cluster_map[group]

    # --- Формирование результата ---
    
    # Если были удаленные группы, возвращаем словарь с удаленными элементами
    # Формат: {удаленный кластер: список удаленных групп}
    return {cluster_to_remove: removed_groups} if removed_groups else {}

def evaluate_clusters(agglomerative_clusters, merged_data):
    """
    Оценивает метрики для каждого кластера, основываясь на данных объектов и событий.

    Аргументы:
    agglomerative_clusters — список меток кластеров, присвоенных каждой записи (шоту) в данных.
                             Структура: [0, 1, 0, 2, ...], где каждая цифра указывает на номер кластера.
    merged_data — словарь, содержащий объединенные данные по каждому шоту, структура:
                  {'shot_1': данные шота, 'shot_2': данные шота, ...}.
                  Данные шота должны включать следующие ключи:
                  - 'avg_video_objects': Список уникальных объектов в видео.
                  - 'avg_events': Список уникальных событий в видео.
                  - 'sentiment': Тональность текущего шота (например, 'positive', 'neutral', 'negative').
                  - 'sound_type': Тип звукового сопровождения (например, 'Music', 'Speech').

    Возвращает:
    cluster_metrics — словарь, где:
                      Ключ: идентификатор кластера (например, 0, 1, 2).
                      Значение: общая метрика качества кластера, рассчитанная на основе различных параметров.
    Пример возвращаемого значения: {0: 1.25, 1: 0.8, 2: 1.5}.
    """

    cluster_metrics = {}  # Словарь для хранения метрик для каждого кластера

    # --- Преобразование ключей данных в список для удобства доступа ---
    
    keys_list = list(merged_data.keys())  # Преобразуем ключи merged_data в список для последовательного доступа

    # --- Проход по каждому уникальному кластеру в списке меток ---
    
    for cluster_id in set(agglomerative_clusters):
        # Создаем список данных для текущего кластера
        # Используем enumerate для доступа к индексам и меткам кластеров
        cluster_data = [merged_data[keys_list[idx]] for idx, label in enumerate(agglomerative_clusters) if label == cluster_id]
        
        # --- Метрика 1: Среднее количество уникальных объектов в каждом шоте кластера ---
        
        avg_objects_count = sum(len(data['avg_video_objects']) for data in cluster_data) / len(cluster_data)
        
        # --- Метрика 2: Среднее количество уникальных событий ---
        
        avg_events_count = sum(len(data['avg_events']) for data in cluster_data) / len(cluster_data)

        # --- Метрика 3: Разнообразие настроений в кластере ---
        
        unique_sentiments = len(set(data['sentiment'] for data in cluster_data))  # Количество уникальных меток настроений

        # --- Метрика 4: Количество уникальных типов звуков ---
        
        unique_sound_types = len(set(data['sound_type'] for data in cluster_data))  # Количество уникальных типов звуков

        # --- Объединение метрик в общий показатель ---
        
        # Суммарная метрика кластера:
        # Чем больше среднее количество объектов и событий, тем выше качество кластера,
        # но разнообразие настроений и звуковых типов должно быть минимальным.
        # Чтобы уменьшить влияние большого числа уникальных элементов, добавляем 1 (чтобы избежать деления на 0).
        total_metric = (avg_objects_count + avg_events_count) / (unique_sentiments + unique_sound_types + 1)

        # --- Сохранение метрики для текущего кластера ---
        
        cluster_metrics[cluster_id] = total_metric  # Сохраняем метрику для текущего кластера
    
    # --- Возвращение словаря с метриками ---
    
    return cluster_metrics  # Возвращаем словарь с метриками для каждого кластера



def reindex_clusters(clusters, threshold=10):
    """
    Функция для переиндексации кластеров после их разделения на более мелкие подгруппы.
    
    Аргументы:
    clusters — словарь, содержащий исходные кластеры и их элементы (шоты), структура:
               {'0': ['shot_1', 'shot_2'], '1': ['shot_10', 'shot_15']}.
    threshold — пороговое значение для разделения шотов на подгруппы (по умолчанию: 10).
                Используется функцией `split_cluster` для определения, когда шоты должны быть разделены.

    Возвращает:
    new_clusters — словарь, содержащий переиндексированные кластеры и их подгруппы.
                   Ключи: новые индексы кластеров (строковые значения).
                   Значения: списки шотов, входящих в каждый новый кластер.
    Пример возвращаемого значения:
    {'2': ['shot_1', 'shot_2'], '3': ['shot_10'], '4': ['shot_15']}
    """

    # --- Инициализация нового словаря для хранения переиндексированных кластеров ---
    
    new_clusters = {}  # Пустой словарь для хранения новых кластеров после переиндексации

    # --- Находим максимальный индекс среди существующих кластеров ---
    
    # `map(int, clusters.keys())` — преобразуем ключи (строковые значения) в целые числа.
    # `max(...)` — находим максимальный числовой индекс среди существующих ключей.
    max_index = max(map(int, clusters.keys()))  # Например, если ключи '0', '1', '2', результатом будет 2

    # --- Проход по каждому кластеру и его элементам ---
    
    for cluster_idx, shots in clusters.items():
        # Сортируем шоты внутри текущего кластера и разделяем их на подгруппы на основе порогового значения `threshold`
        sub_clusters = split_cluster(sorted(shots), threshold)  # Например, [['shot_1', 'shot_2'], ['shot_10']]
        
        # --- Присваиваем новые индексы каждой подгруппе ---
        
        for sub_cluster in sub_clusters:
            new_index = max_index + 1  # Присваиваем новый индекс для каждой подгруппы
            new_clusters[str(new_index)] = sub_cluster  # Добавляем подгруппу в новый словарь с новым индексом
            max_index += 1  # Увеличиваем максимальный индекс на единицу для следующей подгруппы

    # --- Возвращаем новый словарь с переиндексированными кластерами ---
    
    return new_clusters  # Например: {'2': ['shot_1', 'shot_2'], '3': ['shot_10']}


def merge_clusters_if_needed(clusters):
    """
    Функция для объединения мелких кластеров (если их длина меньше заданного порога) с соседними кластерами.
    
    Аргументы:
    clusters — список кластеров, где каждый кластер представлен списком шотов.
               Например: [['shot_1', 'shot_2'], ['shot_10'], ['shot_15', 'shot_16']].

    Возвращает:
    clusters — список объединенных кластеров, если выполнение объединения было необходимо.
               Например: [['shot_1', 'shot_2', 'shot_10'], ['shot_15', 'shot_16']].
    """

    changed = True  # Флаг для отслеживания изменений (проверяет, были ли объединения в текущем цикле)

    # --- Основной цикл для объединения мелких кластеров ---
    
    while changed:  # Повторяем, пока есть изменения
        changed = False  # Сбрасываем флаг перед началом нового цикла
        new_clusters = []  # Список для хранения новых объединенных кластеров
        skip_next = False  # Флаг для пропуска следующего кластера, если он уже объединен

        # --- Проход по всем кластерам, кроме последнего ---
        
        for i in range(len(clusters) - 1):
            # Если флаг `skip_next` установлен, пропускаем текущий элемент, так как он уже был объединен
            if skip_next:
                skip_next = False
                continue

            # Текущий и следующий кластеры
            current_cluster = clusters[i]
            next_cluster = clusters[i + 1]

            # --- Проверка на возможность объединения ---
            
            # Объединяем, если оба кластера имеют меньше 4 элементов
            if len(current_cluster) < 4 and len(next_cluster) < 4:
                # Объединение текущего и следующего кластеров
                merged_cluster = current_cluster + next_cluster  # Конкатенация списков шотов
                new_clusters.append(merged_cluster)  # Добавляем объединенный кластер в новый список
                skip_next = True  # Устанавливаем флаг, чтобы пропустить следующий элемент
                changed = True  # Устанавливаем флаг изменений, так как было произведено объединение
            else:
                # Если объединение не требуется, добавляем текущий кластер как есть
                new_clusters.append(current_cluster)

        # --- Добавление последнего кластера, если он не был объединен ---
        
        # Если последний элемент не был объединен с предыдущим, добавляем его в новый список
        if not skip_next and len(clusters) > 0:
            new_clusters.append(clusters[-1])

        # Обновляем список кластеров после текущего цикла
        clusters = new_clusters  # Обновляем исходный список для следующей итерации цикла

    # --- Возвращение итогового списка кластеров ---
    
    return clusters  # Возвращаем новый список объединенных кластеров

def merge_small_clusters(clusters):
    """
    Объединяет кластеры, в которых менее двух элементов, с предыдущим или следующим кластером.
    
    Описание:
    - Если кластер является первым в списке, он объединяется с последующим.
    - Если кластер не первый, он объединяется с предыдущим.
    - Пустые кластеры остаются на месте и пропускаются.
    - После каждого объединения функция начинает проход заново, чтобы учесть изменения структуры кластеров.
    
    Аргументы:
    clusters — список списков, где каждый список представляет собой кластер (например, [['shot_1'], ['shot_2', 'shot_3']]).

    Возвращает:
    clusters — измененный список кластеров, где все мелкие кластеры объединены.
    Пустые кластеры остаются на своих местах, чтобы сохранить структуру индексов.
    Пример возвращаемого значения: [['shot_1', 'shot_2', 'shot_3'], []]
    """
    
    i = 0  # Индекс для итерации по списку кластеров

    # --- Основной цикл для прохода по каждому кластеру ---
    
    while i < len(clusters):
        # --- Пропуск пустых кластеров ---
        
        if len(clusters[i]) == 0:  # Если текущий кластер пустой, пропускаем его
            i += 1
            continue

        # --- Проверка на маленькие кластеры ---
        
        # Если текущий кластер имеет меньше двух элементов
        if len(clusters[i]) < 2:
            # --- Объединение с соседними кластерами ---
            
            if i == 0:
                # Если это первый кластер в списке, объединяем его со следующим
                clusters[i] = clusters[i] + clusters[i + 1]  # Объединяем текущий и следующий кластеры
                clusters[i + 1] = []  # Очищаем следующий кластер после объединения
            else:
                # Если это не первый кластер, объединяем его с предыдущим
                clusters[i - 1] = clusters[i - 1] + clusters[i]  # Объединяем текущий и предыдущий кластеры
                clusters[i] = []  # Очищаем текущий кластер после объединения

            # --- Сброс индекса и начало прохода заново ---
            
            # Сбрасываем индекс `i`, чтобы начать проверку списка кластеров заново
            # Это необходимо, чтобы учесть изменения после объединения
            i = 0
        else:
            # Если текущий кластер имеет два или более элемента, просто переходим к следующему
            i += 1

    # --- Возвращение измененного списка кластеров ---
    
    return clusters  # Возвращаем список кластеров, где мелкие кластеры объединены

def remove_empty_and_reindex(clusters):
    """
    Функция для удаления пустых кластеров и переиндексации оставшихся кластеров.

    Аргументы:
    clusters — словарь, содержащий кластеры и их элементы (шоты).
               Ключи — индексы кластеров, значения — списки шотов.
               Пример: {0: ['shot_1', 'shot_2'], 1: [], 2: ['shot_3']}.

    Возвращает:
    reindexed_clusters — новый словарь, содержащий только непустые кластеры с переиндексированными ключами.
                         Переиндексация начинается с 1.
                         Пример возвращаемого значения: {1: ['shot_1', 'shot_2'], 2: ['shot_3']}.
    """

    # --- Удаление пустых кластеров ---
    
    # С помощью генератора словарей создаем новый словарь `non_empty_clusters`, содержащий только те кластеры, которые не пустые.
    # Условие `if v` проверяет, что значение (список шотов) не является пустым (например, `[]`).
    non_empty_clusters = {k: v for k, v in clusters.items() if v}  # Например, {0: ['shot_1'], 2: ['shot_3']} если кластер 1 пуст

    # --- Реиндексация кластеров ---
    
    # `enumerate(non_empty_clusters.items(), start=1)`:
    # - `enumerate` создает итератор, возвращающий пары (новый индекс, (старый индекс, шоты)).
    # - Параметр `start=1` указывает на начало новой нумерации с 1.
    # - В каждой итерации `new_index` — новый индекс кластера, `old_index` — старый индекс, `shots` — список шотов.
    reindexed_clusters = {new_index: shots for new_index, (old_index, shots) in enumerate(non_empty_clusters.items(), start=1)}
    
    # --- Возвращение нового словаря с реиндексированными кластерами ---
    
    return reindexed_clusters



def process_clusters(input_file, json_output_audio_path, json_output_video_path, output_file):
    """
    Основная функция для обработки кластеров на основе данных аудио и видео.

    Аргументы:
    input_file — Путь к исходному файлу JSON с объединенными данными шотов и кластеров.
    json_output_audio_path — Путь к файлу с данными аудио-анализов.
    json_output_video_path — Путь к файлу с данными видео-анализов.
    output_file — Путь для сохранения финального JSON с обновленными кластерами.

    Этапы:
    1. Чтение исходных данных.
    2. Реиндексация кластеров.
    3. Обновление данных кластеров с использованием данных аудио и видео.
    4. Генерация описаний и векторизация.
    5. Оптимизация количества кластеров и их объединение.
    6. Сохранение обновленных кластеров.

    Возвращает:
    Ничего не возвращает, но сохраняет результат в `output_file`.
    """

    # --- Шаг 1: Чтение данных из файлов JSON ---

    # Чтение аудио-данных из файла
    with open(json_output_audio_path, 'r', encoding='utf-8') as f:
        audio_data = json.load(f)

    # Чтение видео-данных из файла
    with open(json_output_video_path, 'r', encoding='utf-8') as f:
        video_data = json.load(f)

    # Чтение исходных объединенных данных из файла
    with open(input_file, 'r', encoding='utf-8') as f:
        initial_merged_data = json.load(f)

    # --- Шаг 2: Реиндексация кластеров ---

    # Реиндексация кластеров, чтобы они начинались с 1 и шли последовательно
    reindexed_clusters = reindex_clusters(initial_merged_data)

    # --- Шаг 3: Обновление данных кластеров с использованием аудио и видео ---

    updated_merged_data = {}  # Словарь для хранения обновленных данных кластеров

    # Проходим по каждому кластеру и обновляем его данные, используя аудио- и видео-данные
    for cluster_id in reindexed_clusters:
        updated_merged_data[cluster_id] = merge_cluster_data(reindexed_clusters[cluster_id], audio_data, video_data)

    # --- Шаг 4: Генерация описаний кластеров для дальнейшей кластеризации ---

    # Генерируем текстовые описания для каждого кластера
    cluster_descriptions = [
        (
            f"Transcription: {shot['transcription']}, "
            f"Sentiment: {shot['sentiment']}, "
            f"Clap Analysis: {shot['clap_analysis']}, "
            f"Average Video Objects: {shot['avg_video_objects']}, "
            f"Average Video Events: {shot['avg_events']}, "
        )
        for shot in updated_merged_data.values()
    ]

    # Векторизация текстовых описаний с помощью TF-IDF
    vectorizer = TfidfVectorizer()
    description_matrix = vectorizer.fit_transform(cluster_descriptions)

    # --- Шаг 5: Определение оптимального количества кластеров ---

    num_descriptions = len(cluster_descriptions)  # Количество описаний (кластеров)
    # Определение оптимального количества кластеров с помощью силуэтного коэффициента
    optimal_cluster_count = determine_optimal_clusters_silhouette(description_matrix, num_descriptions)

    # --- Проверка на случай, если не удалось определить оптимальное количество кластеров ---
    
    if optimal_cluster_count is None or optimal_cluster_count < 1:
        optimal_cluster_count = 1  # Устанавливаем минимум 1 кластер

    # --- Шаг 6: Применение агломеративной кластеризации ---

    # Применение агломеративной кластеризации к матрице текстовых описаний
    agglomerative_labels = apply_agglomerative(description_matrix, optimal_cluster_count)

    shot_clusters_dict = {}  # Словарь для хранения распределения шотов по кластерам

    # --- Распределение шотов по кластерам ---

    for shot_key, description in updated_merged_data.items():
        # Получаем номер кластера для текущего шота
        cluster_id = int(agglomerative_labels[list(updated_merged_data.keys()).index(shot_key)])

        # Если кластера еще нет в словаре, создаем пустой список
        if cluster_id not in shot_clusters_dict:
            shot_clusters_dict[cluster_id] = []

        # Добавляем текущий шот в соответствующий кластер
        shot_clusters_dict[cluster_id].append(shot_key)

    # --- Шаг 7: Преобразование данных для сохранения ---

    # Преобразуем данные кластеров в сериализуемый формат
    serializable_clusters = convert_to_serializable(shot_clusters_dict)

    # --- Шаг 8: Объединение данных для финального вывода ---

    final_merged_data = {}  # Словарь для финальных данных

    # Проходим по каждому кластеру и его подкластеру
    for cluster_id, subclusters in serializable_clusters.items():
        all_shots = []  # Список для хранения всех шотов в текущем кластере

        # Добавляем шоты из подкластеров в текущий кластер
        for subcluster_id in subclusters:
            if subcluster_id in reindexed_clusters:
                all_shots.extend(reindexed_clusters[subcluster_id])

        # Сохраняем все шоты в текущий кластер
        final_merged_data[cluster_id] = all_shots

    # --- Шаг 9: Реиндексация финальных данных ---

    # Переиндексация финального словаря кластеров
    reindexed_clusters = reindex_clusters(final_merged_data)

    # После переиндексации финальные данные можно сохранить или использовать для дальнейшего анализа

    # Функция для извлечения чисел из названия шота
    def extract_number(shot_name):
        """
        Извлекает первое число из строки названия шота и возвращает его в виде целого числа.
        
        Аргументы:
        shot_name — строка, представляющая собой название шота (например, 'shot_10' или 'scene_15_shot_3').
        
        Возвращает:
        Целое число — первое найденное число в строке.
        Если число не найдено, возвращает `float('inf')` (бесконечность).
        Это позволяет использовать функцию в сортировках, где шоты без номеров перемещаются в конец списка.
        
        Пример:
        - Для 'shot_10' функция вернет 10.
        - Для 'scene_15_shot_3' функция вернет 15 (первое число в строке).
        - Для строки без числа (например, 'no_number_shot') функция вернет `float('inf')`.
        """
        
        # --- Поиск первого числа в названии шота ---
        
        # `re.search(r'\d+', shot_name)`:
        # - Ищет первое вхождение числового значения в строке.
        # - `\d+` — регулярное выражение для поиска последовательности одной или более цифр.
        # - `r''` — указывает на использование необработанных строк (raw string).
        # Если найдено соответствие, возвращается объект `Match`, иначе `None`.
        match = re.search(r'\d+', shot_name)  # Ищем первое число в названии шота
        # --- Возврат найденного числа или бесконечности ---
    
        # Если число найдено (`match` не равен None), преобразуем его в целое число с помощью `int(match.group())`.
        # Если соответствие не найдено, возвращаем `float('inf')`, что означает "бесконечность".
        return int(match.group()) if match else float('inf')  # Если нет числа, возвращаем бесконечность

    # Сортируем по первому элементу шотов, извлекая номер
    sorted_cluster_items = sorted(reindexed_clusters.items(), key=lambda item: extract_number(item[1][0]))

    # Сортируем шоты внутри каждого кластера
    for key in reindexed_clusters.keys():
        reindexed_clusters[key].sort(key=extract_number)

    # Реиндексируем с 1
    final_reindexed_clusters = {i: value for i, (key, value) in enumerate(sorted_cluster_items)}

    # Объединяем кластеры, если нужно
    merged_clusters = merge_clusters_if_needed(final_reindexed_clusters)

    # Повторная реиндексация после объединения кластеров
    final_reindexed = {i: value for i, value in enumerate(merged_clusters)}

    final_result = merge_small_clusters(final_reindexed)

    cleaned_clusters = remove_empty_and_reindex(final_result)

    # Сохранение результатов в JSON файл
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_clusters, f, ensure_ascii=False, indent=4)
    

