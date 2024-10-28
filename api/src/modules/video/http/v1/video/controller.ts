import {Get, getConnection, getRepository, JsonController, Params, Query,} from "framework";
import {Video} from "../../../entities/video";
import {GetVideoListDto} from "./requests/get-list";
import {VideoScene} from "../../../entities/video-scene";

@JsonController("/api/v1/video")
export class VideoController {
    constructor() {
    }

    @Get("/")
    public async index(@Query dto: GetVideoListDto) {
        const limit = dto.limit > 0 ? dto.limit : undefined;
        const videos = getRepository(Video)

        let items = [];

        if (dto.search && dto.search !== '') {
            items = await getConnection().createQueryRunner().query('' +
                'select distinct \n' +
                '\tvs.video_id "id",\n' +
                '\tv."name"\n' +
                'from video_scenes vs\n' +
                '\tleft join video_scenes_audios vsa ON vs.id = vsa.scene_id\n' +
                '\tleft join videos v on vs.video_id = v.id\n' +
                `where vsa.transcription like '%${dto.search}%'
                 limit $1 offset $2`, [limit, dto.offset]);
        } else {
            items = await videos.find({
                take: limit,
                skip: dto.offset,
            });
        }


        const count = await videos.count();
        return {
            meta: {
                total: count,
                limit: dto.limit,
            },
            items: items
        };
    }

    @Get("/:id")
    public async show(@Params('id') id: number) {
        const runner = getConnection().createQueryRunner();
        const detections: Array<{ id: number, class: string | null, avg: number | null }> = await runner.query(
            "select\n" +
            "\tvs.id,\n" +
            "\tvsd.\"class\",\n" +
            "\tavg(vsd.confidence)\n" +
            "from video_scenes vs \n" +
            "\tleft join video_scenes_detections vsd ON vs.id = vsd.scene_id \n" +
            `where video_id = ${id}\n` +
            "group by vs.id, vsd.\"class\" \n" +
            "order by vs.id, avg(vsd.confidence) desc"
        )

        const scenes: Record<number, {
            id: number,
            original_id: number,
            detections: Array<{ class: string | null, avg: number | null }>,
            events: Array<{ name: string | null, probability: number | null }>,
            faces: Array<{ emotion_label: string | null, emotion_probability: number | null }>,
            transcription: string,
            summary: string,
            sentiment_label: string,
            sentiment_confidence: number,
            clap_labels: string,
            labeled_transcriptions: string,
            time_from: string,
            time_to: string,
        }> = {}

        for (const item of detections) {
            if (scenes[item.id] === undefined) {
                scenes[item.id] = {
                    id: item.id,
                    original_id: 1,
                    detections: [],
                    events: [],
                    faces: [],
                    transcription: '',
                    summary: '',
                    sentiment_label: '',
                    sentiment_confidence: 1,
                    clap_labels: '',
                    labeled_transcriptions: '',
                    time_from: '',
                    time_to: '',
                }
            }

            if (scenes[item.id].detections === undefined) {
                scenes[item.id].detections = []
            }

            if (item.avg === null) {
                continue;
            }

            scenes[item.id].detections.push({
                avg: Math.round(item.avg * 100) / 100,
                class: item.class
            });
        }

        const events: Array<{ scene_id: number, name: string | null, probability: number | null }> = await runner.query(
            "select\n" +
            "\tvs.id \"scene_id\",\n" +
            "\tvse.\"name\",\n" +
            "\tmax(vse.probability) \"probability\"\n" +
            "from video_scenes vs \n" +
            "\tleft join video_scenes_events vse ON vs.id = vse.scene_id\n" +
            `where video_id = ${id}\n` +
            "group by vs.id, vse.\"name\" \n" +
            "order by vs.id, max(vse.probability) desc"
        )

        for (const item of events) {
            if (scenes[item.scene_id] === undefined) {
                scenes[item.scene_id] = {
                    id: item.scene_id,
                    original_id: 1,
                    detections: [],
                    events: [],
                    faces: [],
                    transcription: '',
                    summary: '',
                    sentiment_label: '',
                    sentiment_confidence: 1,
                    clap_labels: '',
                    labeled_transcriptions: '',
                    time_from: '',
                    time_to: '',
                }
            }

            if (item.name === null || item.probability === null) {
                continue;
            }

            if (scenes[item.scene_id].events === undefined) {
                scenes[item.scene_id].events = []
            }

            scenes[item.scene_id].events.push({
                name: item.name,
                probability: Math.round(item.probability * 100) / 100
            });
        }

        const faces: Array<{ scene_id: number, emotion_label: string | null, emotion_probability: number | null }> = await runner.query(
            "select\n" +
            "\tvs.id \"scene_id\",\n" +
            "\tvsf.emotion_label \"emotion_label\",\n" +
            "\tmax(vsf.emotion_probability) \"emotion_probability\"\n" +
            "from video_scenes vs \n" +
            "\tleft join video_scenes_faces vsf ON vs.id = vsf.scene_id\n" +
            `where video_id = ${id}\n` +
            "group by vs.id, vsf.emotion_label \n" +
            "order by vs.id, max(vsf.emotion_probability) desc"
        )

        for (const item of faces) {
            if (scenes[item.scene_id] === undefined) {
                scenes[item.scene_id] = {
                    id: item.scene_id,
                    original_id: 1,
                    detections: [],
                    events: [],
                    faces: [],
                    transcription: '',
                    summary: '',
                    sentiment_label: '',
                    sentiment_confidence: 1,
                    clap_labels: '',
                    labeled_transcriptions: '',
                    time_from: '',
                    time_to: '',
                }
            }

            if (item.emotion_probability === null) {
                continue;
            }

            if (scenes[item.scene_id].faces === undefined) {
                scenes[item.scene_id].faces = []
            }

            scenes[item.scene_id].faces.push({
                emotion_label: item.emotion_label,
                emotion_probability: Math.round(item.emotion_probability * 100) / 100
            });
        }


        const audios: Array<{
            scene_id: number,
            transcription: string,
            summary: string,
            sentiment_label: string,
            sentiment_confidence: number,
            clap_labels: string,
            labeled_transcriptions: string,
        }> = await runner.query(
            "select \n" +
            "\t*\n" +
            "from video_scenes_audios vsa \n" +
            "\tleft join video_scenes vs ON vsa.scene_id = vs.id \n" +
            `where vs.video_id = ${id}`
        )

        for (const item of audios) {
            if (scenes[item.scene_id] === undefined) {
                scenes[item.scene_id] = {
                    id: item.scene_id,
                    original_id: 1,
                    detections: [],
                    events: [],
                    faces: [],
                    transcription: '',
                    summary: '',
                    sentiment_label: '',
                    sentiment_confidence: 1,
                    clap_labels: '',
                    labeled_transcriptions: '',
                    time_from: '',
                    time_to: '',
                }
            }

            scenes[item.scene_id].transcription = item.transcription
            scenes[item.scene_id].summary = item.summary
            scenes[item.scene_id].sentiment_label = item.sentiment_label
            scenes[item.scene_id].sentiment_confidence = Math.round(item.sentiment_confidence * 100) / 100
            scenes[item.scene_id].clap_labels = item.clap_labels
            scenes[item.scene_id].labeled_transcriptions = item.labeled_transcriptions
        }

        const coords: Array<{
            scene_id: number,
            from: string,
            to: string,
        }> = await runner.query(
            "select \n" +
            "\t*\n" +
            "from video_scenes_coords t\n" +
            "\tleft join video_scenes vs ON t.scene_id = vs.id \n" +
            `where vs.video_id = ${id}`
        )

        for (const item of coords) {
            if (scenes[item.scene_id] === undefined) {
                scenes[item.scene_id] = {
                    id: item.scene_id,
                    original_id: 1,
                    detections: [],
                    events: [],
                    faces: [],
                    transcription: '',
                    summary: '',
                    sentiment_label: '',
                    sentiment_confidence: 1,
                    clap_labels: '',
                    labeled_transcriptions: '',
                    time_from: '',
                    time_to: '',
                }
            }

            scenes[item.scene_id].time_from = item.from
            scenes[item.scene_id].time_to = item.to
        }

        for (const id in scenes) {
            const fromDb = await getRepository(VideoScene).findOneOrFail({
                where: {
                    id: id,
                }
            })

            scenes[id].original_id = fromDb.original_id
        }

        return {
            scenes: Object.values(scenes)
                .filter(s => s.time_to !== '')
                .sort((a, b) => a.original_id > b.original_id ? 1 : -1)
        };
    }
}
