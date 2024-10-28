import {App, IProvider} from "framework";
import {VideoModule} from "../../modules/video";

export class StartApp extends App {

    override useVault(): boolean {
        return false;
    }

    getName(): string {
        return "hackaton-vmarkup-app";
    }

    public getProviders(): IProvider[] {
        return [
            new VideoModule(this.container)
        ];
    }
}
