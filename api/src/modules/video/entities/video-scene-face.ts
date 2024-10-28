import {Column, Entity, ManyToOne} from 'typeorm';
import {BaseModel} from "framework";
import {VideoScene} from "./video-scene";


@Entity('video_scenes_faces')
export class VideoSceneFace extends BaseModel {
    @Column('int')
    scene_id!: number;

    @Column('varchar')
    emotion_label!: string;

    @Column('float')
    emotion_probability!: number;

    @ManyToOne(() => VideoScene, la => la.faces)
    scene!: VideoScene;
}
