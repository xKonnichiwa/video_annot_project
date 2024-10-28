import {Column, Entity, ManyToOne} from 'typeorm';
import {BaseModel} from "framework";
import {VideoScene} from "./video-scene";


@Entity('video_scenes_events')
export class VideoSceneEvent extends BaseModel {
    @Column('int')
    scene_id!: number;

    @Column('varchar')
    class_id!: string;

    @Column('varchar')
    name!: string;

    @Column('float')
    probability!: number;

    @ManyToOne(() => VideoScene, la => la.events)
    scene!: VideoScene;
}
