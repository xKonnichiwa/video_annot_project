import {Column, Entity, OneToMany,ManyToOne} from 'typeorm';
import {BaseModel} from "framework";
import {VideoSceneDetection} from "./video-scene-detection";
import {VideoSceneEvent} from "./video-scene-event";
import {VideoSceneFace} from "./video-scene-face";
import {Video} from "./video";


@Entity('video_scenes')
export class VideoScene extends BaseModel {
    @Column('int')
    video_id!: number;

    @Column('int')
    original_id!: number;

    @ManyToOne(() => Video, la => la.scenes)
    video!: Video;

    @OneToMany(() => VideoSceneDetection, la => la.scene)
    detections!: VideoSceneDetection[];

    @OneToMany(() => VideoSceneEvent, la => la.scene)
    events!: VideoSceneEvent[];

    @OneToMany(() => VideoSceneFace, la => la.scene)
    faces!: VideoSceneFace[];
}
