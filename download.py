# author: Chengrui Zhang
# This script is used to download MUSIC dataset from youtube

import json
import os
import rich
from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
import yt_dlp


def preprocessing():
    """
    Function used for check needed files:
        data: a folder, contains downloaded videos encoded with mp4 format.
        idx.out: a text file, contains a number which represents the index of the
                 last downloaded video, used for restore download.
        errors.txt: a text file, contains a list of error url.
    """
    if not os.path.exists("./data"):
        os.makedirs("./data")
        print("Created data folder")
    if not os.path.exists("./idx.out"):
        f = open("./idx.out", "w")
        f.write("0")
        f.close()
        print("Created Idx file: used for restore download")
    if not os.path.exists("./errors.txt"):
        f = open("./errors.txt", "w")
        f.close()
        print("Created error list file: used for verify unavailable videos")


def load_json(filename="./MUSIC_dataset/MUSIC_solo_videos.json"):
    """
    Load json file provided by MUSIC dataset maintainer which includes tail url link of videos

    :param filename str: relative path of json file that contains video urls
    """
    json_file_input = open(filename)
    json_file_data = json.load(json_file_input)

    video_url_list = []
    kinds = json_file_data["videos"]
    video_cnt = 0
    for kind in kinds:
        for video in kinds[kind]:
            video_cnt = video_cnt + 1

    with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            TimeElapsedColumn(),
    ) as progress:
        url_proc_rich = progress.add_task(
            description="Loading json file progress", total=video_cnt)
        for kind in kinds:
            for video in kinds[kind]:
                raw_url = "https://youtube.com/watch?v=" + str(video)
                video_url_list.append(raw_url)
                progress.advance(url_proc_rich, advance=1)
    return video_url_list, video_cnt


class MUSIC_Download(object):

    def __init__(self, tot) -> None:
        """
        initializaton function

        :param tot int: total number of videos
        :rtype None: self
        """
        self.idx = 1
        self.tot = tot
        self.download_error_list = []
        with open("./idx.out", "r") as f:
            text = f.read()
            self.idx_start = int(text)
        f.close()

        rich.print(
            "[bold magenta]Total Video Counts (include available and unavailable videos)[/bold magenta]: {}"
            .format(self.tot),
            ":vampire:",
        )

        rich.print(
            "[bold red]Remaining Counts[/bold red]: {}".format(self.tot -
                                                               self.idx_start),
            ":vampire:",
        )

        rich.print(
            "Start download from video with index: [red]{}[/red]".format(
                self.idx_start + 1))

    def rename_hook(self, d):
        """
        Rename hook

        :param d arr: information about downloaded video
        """
        if d["status"] == "finished":
            file_name = "data/{}.mp4".format(self.idx)
            os.rename(d["filename"], file_name)
            rich.print(
                "\nDownload finished, file name is: [green]{}[/green]".format(
                    file_name))
            with open("./idx.out", "w") as f:
                f.write(str(self.idx))
            f.close()

    def rename_hook_2(self, d):
        """
        Rename hook

        :param d arr: information about downloaded video
        """
        video_name = d["filename"]
        if d["status"] == "finished":
            file_name = "data/{}.mp4".format(video_name[:-3])
            os.rename(d["filename"], file_name)
            rich.print(
                "\nDownload finished, file name is: [green]{}[/green]".format(
                    file_name))
            with open("./idx.out", "w") as f:
                f.write(str(self.idx))
            f.close()

    def single_download(self, url=None, use_proxy=None, rename=None):
        """
        Download youtube videos by youtube_dl

        :param url str: video url
        :param use_proxy bool: use proxy or not (for users in China)
        """

        def check_rename():
            rename_obj = None
            if rename:
                rename_obj = [self.rename_hook]
            else:
                rename_obj = [self.rename_hook_2]
            return rename_obj

        if use_proxy:
            ydl_opts = {
                "proxy": "http://127.0.0.1:7890",
                "outtmpl": "%(id)s%(ext)s",
                "progress_hooks": check_rename(),
                "no_warnings": True,
                "format": "best",
                # "external_downloader": "aria2c",
                # "external_downloader_args": [
                #     "--max-connection-per-server=16",
                #     "--all-proxy=http://127.0.0.1:7890",
                # ],
                "quiet": True,
                "noplaylist": True,
            }
        else:
            ydl_opts = {
                "outtmpl": "%(id)s%(ext)s",
                # "progress_hooks": check_rename(),
                "progress_hooks": check_rename(),
                "no_warnings": True,
                "format": "best",
                # "external_downloader": "aria2c",
                # "external_downloader_args": [
                #     "--max-connection-per-server=16",
                # ],
                "noplaylist": True,
                "quiet": True,
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            rich.print(
                "Try to download video with idx: [red]{}[/red], url: [blue]{}[/blue]"
                .format(self.idx, url))

            # rich.inspect(url)
            # rich.inspect(ydl_opts)
            try:
                ydl.download([url])
            except Exception as e:
                self.download_error_list.append(url)
                self.video_failed_cnt = len(self.download_error_list)
                rich.print("Failed Video counts: [red]{}[/red]".format(
                    self.video_failed_cnt))
                f = open("./errors.txt", "w")
                for line in self.download_error_list:
                    f.write(line + "\n")
                f.close()
                rich.print(
                    "Download Failed, Exception: [red]{}[/red]".format(e))

    def download(self, url_list, use_proxy=True, rename=False):
        for single_url in url_list:
            if self.idx > self.idx_start:
                self.single_download(url=single_url,
                                     use_proxy=use_proxy,
                                     rename=rename)
            self.idx = self.idx + 1


if __name__ == "__main__":
    preprocessing()
    url_list, tot = load_json()
    Download = MUSIC_Download(tot)
    Download.download(url_list)
