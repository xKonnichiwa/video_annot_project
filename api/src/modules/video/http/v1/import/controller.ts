import {Body, EntityNotFoundException, getRepository, JsonController, Post} from "framework";
import * as fs from 'fs';
import {ImportVideoDto} from "./requests/import";
import {VideoScene} from "../../../entities/video-scene";
import {Video} from "../../../entities/video";
import {VideoSceneDetection} from "../../../entities/video-scene-detection";
import {VideoSceneEvent} from "../../../entities/video-scene-event";
import {VideoSceneFace} from "../../../entities/video-scene-face";
import {VideoSceneAudio} from "../../../entities/video-scene-audio";
import {VideoSceneCoords} from "../../../entities/video-scene-coords";

type VideoSceneFrameJson = {
    detections: Array<{ class: string, confidence: number }>
    events: Array<{ class_id: string, name: string, probability: number }>
    poi: Record<'faces', Array<{ emotion: { label: string, probability: number } }>>
}
type VideoSceneJson = Record<string, Array<VideoSceneFrameJson>>;


type AudioSceneFrameJson = {
    transcriptions: Array<{ text: string }>
    summary: Array<{ summary: string }>
    sentiment_analysis: Array<{ sentiment: string, confidence: number }>
    clap_analysis: string[],
    labeled_transcriptions: string[],

}
type AudioSceneJson = Record<string, AudioSceneFrameJson>;


type ShotsBySceneJson = Record<string, string[]>;


type ShotsJson = Record<string, { start_time: string, end_time: string, }>;

@JsonController("/api/v1/import")
export class ImportVideoController {
    constructor() {
    }

    @Post("/")
    public async index(@Body dto: ImportVideoDto) {
        // post-validation
        if (dto.name.match(/[^\w-_]+/gi)) {
            throw new EntityNotFoundException('folder', dto.name);
        }

        const videoId = await this.importVideo(dto.name);
        await this.importAudio(dto.name, videoId);
        await this.importShots(dto.name, videoId);


        return {success: true};
    }

    private async loadFile<T>(folder: string, name: string): Promise<T> {
        // I/O operations
        const path = `./shared/${folder}/${name}`
        const exists = fs.existsSync(path);

        if (!exists) {
            throw new EntityNotFoundException('file', path);
        }

        const file = fs.readFileSync(path);
        return JSON.parse(file.toString()) as T;
    }

    private async importVideo(filename: string): Promise<number> {
        const json = await this.loadFile<VideoSceneJson>(filename, 'video_scenes.json')

        // save DB

        const video = await getRepository(Video).save({
            name: filename,
        })

        for (const key in json) {
            const id = parseInt(key.substring(6));
            if (isNaN(id)) {
                throw new Error(key + ' is not `scene_$ID`')
            }

            const scene = await getRepository(VideoScene).save({
                video_id: video.id,
                original_id: id,
            })

            // video detections
            const detections: Array<Partial<VideoSceneDetection>> = [];
            const events: Array<Partial<VideoSceneEvent>> = [];
            const faces: Array<Partial<VideoSceneFace>> = [];

            for (const frame of json[key]) {
                for (const detect of frame.detections) {
                    detections.push({
                        class: detect.class,
                        confidence: detect.confidence,
                        scene_id: scene.id
                    })
                }

                for (const event of frame.events) {
                    events.push({
                        class_id: event.class_id,
                        name: event.name,
                        probability: event.probability,
                        scene_id: scene.id
                    })
                }

                for (const face of frame.poi.faces) {
                    faces.push({
                        emotion_label: face.emotion.label,
                        emotion_probability: face.emotion.probability,
                        scene_id: scene.id
                    })
                }
            }

            await getRepository(VideoSceneDetection).save(detections);
            await getRepository(VideoSceneEvent).save(events);
            await getRepository(VideoSceneFace).save(faces);
        }

        return video.id;
    }

    private async importAudio(filename: string, videoId: number): Promise<void> {
        const json = await this.loadFile<AudioSceneJson>(filename, 'audio_scenes.json')

        // save DB

        for (const key in json) {
            const id = parseInt(key.substring(6));
            if (isNaN(id)) {
                throw new Error('audio:' + key + ' is not `scene_$ID`')
            }
            const frame = json[key];

            const scene = await getRepository(VideoScene).findOneOrFail({
                where: {
                    video_id: videoId,
                    original_id: id,
                }
            })

            // video detections
            const audios: Array<Partial<VideoSceneAudio>> = [];

            audios.push({
                scene_id: scene.id,
                transcription: frame.transcriptions[0]?.text,
                summary: frame.summary[0]?.summary,
                sentiment_label: frame.sentiment_analysis[0]?.sentiment,
                sentiment_confidence: frame.sentiment_analysis[0]?.confidence,
                clap_labels: frame.clap_analysis.join(',').toLowerCase(),
                labeled_transcriptions: frame.labeled_transcriptions.join(',').toLowerCase(),
            })

            await getRepository(VideoSceneAudio).save(audios);
        }
    }

    private async importShots(filename: string, videoId: number): Promise<void> {
        const shotsByScene = await this.loadFile<ShotsBySceneJson>(filename, 'shots_by_scene.json');
        const shots = await this.loadFile<ShotsJson>(filename, 'shots.json');


        // save DB

        for (const key in shotsByScene) {
            const id = parseInt(key);
            if (isNaN(id)) {
                throw new Error('shots:' + key + ' is not `scene_$ID`')
            }


            const scene = await getRepository(VideoScene).findOneOrFail({
                where: {
                    video_id: videoId,
                    original_id: id,
                }
            })

            const first = shotsByScene[key][0];
            const firstShot = shots[first];
            if (firstShot === undefined) {
                throw new EntityNotFoundException(`first shot ${first}`, first)
            }

            const last = shotsByScene[key][shotsByScene[key].length - 1];
            const lastShot = shots[last];
            if (lastShot === undefined) {
                throw new EntityNotFoundException(`last shot ${last}`, last)
            }


            await getRepository(VideoSceneCoords).save({
                scene_id: scene.id,
                from: shots[first].start_time,
                to: shots[last].end_time,
            });
        }
    }
}
