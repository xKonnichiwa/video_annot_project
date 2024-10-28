import {Column, Entity, ManyToOne} from 'typeorm';
import {BaseModel} from "framework";
import {Video} from "./video";
import {VideoScene} from "./video-scene";


@Entity('video_scenes_audios')
export class VideoSceneAudio extends BaseModel {
    @Column('int')
    scene_id!: number;

    @Column('varchar')
    transcription!: string;

    @Column('varchar')
    summary!: string;

    @Column('varchar')
    sentiment_label!: string;

    @Column('float')
    sentiment_confidence!: number;

    @Column('varchar')
    clap_labels!: string;

    @Column('varchar')
    labeled_transcriptions!: string;

    @ManyToOne(() => VideoScene, la => la.detections)
    scene!: VideoScene;
}
