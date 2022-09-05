import argparse
import concurrent.futures
import itertools
import os
import pathlib

import ffmpeg_normalize
import magic


def is_valid_directory(ptr: str) -> pathlib.Path:
    path = pathlib.Path(ptr).absolute()
    if path.is_dir():
        return path
    raise argparse.ArgumentTypeError("Invalid path")


def create_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
        type=is_valid_directory
    )
    return parser


def is_valid_file(file_path: pathlib.Path) -> bool:
    return "video/" in magic.from_buffer(
        open(file_path, "rb").read(2048), mime=True
    )


def create_file_list(vals: argparse.Namespace) -> list[pathlib.Path]:
    path = vals.path
    files = []
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            file_path = pathlib.Path(dirpath, filename)
            if is_valid_file(file_path):
                files.append(file_path)
        break
    return files


def process_video_file(data: tuple[pathlib.Path, pathlib.Path]) -> None:
    file, output = data
    normalize = ffmpeg_normalize.FFmpegNormalize(
        normalization_type="ebu",
        target_level=-20.0,
        loudness_range_target=10.0,
        true_peak=-1.0,
        audio_codec="libopus",
        sample_rate="48000"
    )
    output = output / f'{file.stem}.mkv'
    normalize.add_media_file(
        file.as_posix(),
        output.as_posix()
    )
    normalize.run_normalization()


def process_video_files(file_list: list[pathlib.Path], output: pathlib.Path) -> None:
    with concurrent.futures.ThreadPoolExecutor() as pool:
        pool.map(process_video_file, itertools.product(file_list, [output]))


def create_output_folder(vals: argparse.Namespace) -> pathlib.Path:
    path: pathlib.Path = vals.path.parent
    output_path = pathlib.Path(path, "normalized")
    if not output_path.exists():
        output_path.mkdir(exist_ok=True)
    return output_path


def run():
    parser = create_argument_parser()
    vals = parser.parse_args()
    file_list = create_file_list(vals)
    output_path = create_output_folder(vals)
    process_video_files(file_list, output_path)


if __name__ == '__main__':
    run()
