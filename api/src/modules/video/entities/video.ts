import {Column, Entity, OneToMany} from 'typeorm';
import {BaseModel} from "framework";
import {VideoScene} from "./video-scene";


@Entity('videos')
export class Video extends BaseModel {
    @Column('int')
    name!: string;

    @OneToMany(() => VideoScene, la => la.video)
    scenes!: VideoScene[];
}
