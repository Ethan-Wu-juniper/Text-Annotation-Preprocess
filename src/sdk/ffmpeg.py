import subprocess
from gfs.store import local
from gfs import temp


def execute_ffmpeg_cmd(cmd: list[str], output_path: str):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode != 0:
            raise Exception(f"FFmpeg 錯誤: {result.stderr}")

        return output_path
    except Exception as e:
        raise Exception(f"處理影片時發生錯誤: {str(e)}")


def extract_frame(file: str, frame_number: int):
    input_path = local(file)
    output_path = temp.filename(".jpg")

    cmd = [
        "ffmpeg",
        "-i",
        input_path,
        "-vf",
        f"select=eq(n\\,{frame_number})",
        "-vframes",
        "1",
        "-q:v",
        "2",
        "-y",
        output_path,
    ]
    return execute_ffmpeg_cmd(cmd, output_path)
