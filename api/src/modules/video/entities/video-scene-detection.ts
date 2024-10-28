import {Column, Entity, ManyToOne} from 'typeorm';
import {BaseModel} from "framework";
import {Video} from "./video";
import {VideoScene} from "./video-scene";


@Entity('video_scenes_detections')
export class VideoSceneDetection extends BaseModel {
    @Column('int')
    scene_id!: number;

    @Column('varchar')
    class!: string;

    @Column('float')
    confidence!: number;

    @ManyToOne(() => VideoScene, la => la.detections)
    scene!: VideoScene;
}
