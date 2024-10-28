from openai import OpenAI
import json

# Функция для отправки данных на анализ к модели
def send_request_to_mistral(transcriptions_text, clap_analysis, detections, events):
    # Формируем данные для отправки
    audio_data = f"Транскрипция: {transcriptions_text}. Анализ хлопков: {', '.join(clap_analysis)}."
    
    # Фильтруем detections и events по уверенности
    filtered_detections = [det for det in detections if det['confidence'] > 0.7]
    filtered_events = [event for event in events if event['probability'] > 0.7]
    
    video_data = (
        f"Объекты обнаружения: {', '.join([det['class'] for det in filtered_detections])}. "
        f"Объекты событий: {', '.join([event['name'] for event in filtered_events])}."
    )
    
    # Объединяем данные аудио и видео
    combined_data = f"{audio_data} {video_data}"
    
    # Подготавливаем сообщение для модели
    messages = [
        { "role": "system", "content": "Extract the key content of the scene based on audio and video data. The answer should consist of one sentence that conveys only the essence of the scene without unnecessary details, avoiding introductory phrases or additional recommendations. The answer must be in Russian." },
        { "role": "user", "content": combined_data }
    ]
    
    client = OpenAI(base_url='http://localhost:11434/v1/', api_key='ollama')

    # Запрос к модели
    response = client.chat.completions.create(
        model="mistral",
        messages=messages,
        temperature=0.35,
        max_tokens=300,
    )
    
    # Возвращаем ответ
    return response.choices[0].message.content

def analyze_json_scenes(audio_json_path, video_json_path, result_name):
    # Путь к файлу с анализом сцен
    output_json_path = "data/scene_analysis_results_"+result_name+".json"

    # Загружаем JSON с видеоданными
    with open(video_json_path, 'r', encoding='utf-8') as f:
        video_scenes = json.load(f)

    # Загружаем JSON с аудиоданными
    with open(audio_json_path, 'r', encoding='utf-8') as f:
        audio_scenes = json.load(f)

    analysis_results = {}

    # Проходим по каждой сцене из видеоданных
    for scene_name, video_data in video_scenes.items():
        if not video_data:
            continue
        
        # Получаем detections и события
        detections = video_data[0]['detections']
        events = video_data[0]['events']

        # Проверяем наличие аудиоданных для данной сцены
        if scene_name in audio_scenes:
            audio_data = audio_scenes[scene_name]
            print(scene_name)
            print(": ")
            print(audio_data)
            print("\n")
            if not audio_data:
                continue
            
            # Получаем аудиоданные
            transcriptions_text = audio_data['transcriptions'][0]['text']
            clap_analysis = audio_data['clap_analysis']
            
            # Получаем краткое описание сцены
            result = send_request_to_mistral(transcriptions_text, clap_analysis, detections, events)
            
            # Добавляем результат в словарь в формате "scene_n": *result_n*
            analysis_results[scene_name] = result

    # Записываем результаты в файл JSON
    with open(output_json_path, 'w', encoding='utf-8') as outfile:
        json.dump(analysis_results, outfile, ensure_ascii=False, indent=4)

    print(f"Results saved to {output_json_path}")