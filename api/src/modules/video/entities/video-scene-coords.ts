import {Column, Entity, ManyToOne} from 'typeorm';
import {BaseModel} from "framework";
import {Video} from "./video";
import {VideoScene} from "./video-scene";


@Entity('video_scenes_coords')
export class VideoSceneCoords extends BaseModel {
    @Column('int')
    scene_id!: number;

    @Column('varchar')
    from!: string;

    @Column('varchar')
    to!: string;

    @ManyToOne(() => VideoScene, la => la.detections)
    scene!: VideoScene;
}
