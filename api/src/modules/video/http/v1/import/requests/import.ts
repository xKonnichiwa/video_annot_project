import {ApiProperty} from "framework";

export class ImportVideoDto {
    @ApiProperty({type: 'string'})
    name!: string;
}