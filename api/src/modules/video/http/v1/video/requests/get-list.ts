import {ApiProperty} from "framework";

export class GetVideoListDto {
    @ApiProperty({type: 'number'})
    limit!: number;

    @ApiProperty({type: 'number'})
    offset!: number;

    @ApiProperty({type: 'string', optional: true})
    search!: string | undefined;

}