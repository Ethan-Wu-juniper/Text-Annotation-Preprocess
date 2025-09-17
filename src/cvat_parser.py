from pydantic import BaseModel
import xml.etree.ElementTree as ET
from collections import defaultdict
import numpy as np
from PIL import Image

from gfs import temp
from sdk.ffmpeg import extract_frame


class Task(BaseModel):
    url: str
    frame_count: int
    start_frame: int
    width: int
    height: int


class Box(BaseModel):
    task_id: str
    xtl: float
    ytl: float
    xbr: float
    ybr: float


class FluxData(BaseModel):
    image: str
    mask: str
    frame_number: int


def create_mask_from_boxes(boxes: list[Box], width: int, height: int):
    """處理多個 boxes"""
    mask = np.zeros((height, width), dtype=np.uint8)

    for box in boxes:
        x1 = int(box.xtl)
        y1 = int(box.ytl)
        x2 = int(box.xbr)
        y2 = int(box.ybr)

        x1 = max(0, min(x1, width - 1))
        y1 = max(0, min(y1, height - 1))
        x2 = max(0, min(x2, width))
        y2 = max(0, min(y2, height))

        mask[y1:y2, x1:x2] = 255

    output_path = temp.filename(".jpg")
    image = Image.fromarray(mask)
    image.save(output_path)
    return output_path


class FluxDataset:
    def __init__(self):
        tree = ET.parse("./annotation/cvat_for_video.xml")
        root = tree.getroot()
        tasks = root.find("meta").find("project").find("tasks").findall("task")
        tracks = root.findall("track")
        acc_frame = 0

        self.tasks: dict[str, Task] = {}  # key : task id
        self.boxes: dict[int, list[Box]] = defaultdict(list)  # key : frame number

        for task in tasks:
            frame_count = int(task.find("size").text)
            ratio = task.find("original_size")
            self.tasks[task.find("id").text] = Task(
                url=f"https://creative-assets.gliacloud.com/{task.find('name').text}",
                frame_count=frame_count,
                start_frame=acc_frame,
                width=ratio.find("width").text,
                height=ratio.find("height").text,
            )
            acc_frame += frame_count

        for track in tracks:
            for box in track.findall("box"):
                frame_number = int(box.get("frame"))
                box = Box(
                    task_id=track.get("task_id"),
                    xtl=box.get("xtl"),
                    ytl=box.get("ytl"),
                    xbr=box.get("xbr"),
                    ybr=box.get("ybr"),
                )
                self.boxes[frame_number].append(box)

        self._frame_keys = sorted(self.boxes.keys())
        self._current_frame_index = 0

    def _fetch(self, index: int) -> FluxData:
        current_frame = self._frame_keys[index]
        boxes = self.boxes[current_frame]
        task = self.tasks.get(boxes[0].task_id)
        mask = create_mask_from_boxes(boxes, task.width, task.height)
        image = extract_frame(task.url, current_frame - task.start_frame)

        return FluxData(image=image, mask=mask, frame_number=current_frame)

    def __iter__(self):
        return self

    def __next__(self) -> FluxData:
        if self._current_frame_index >= len(self._frame_keys):
            raise StopIteration

        data = self._fetch(self._current_frame_index)
        self._current_frame_index += 1
        return data

    def __len__(self):
        return len(self._frame_keys)

    def __getitem__(self, key: int):
        return self._fetch(key)


if __name__ == "__main__":
    dataset = FluxDataset()
    # item = next(dataset)
    # print(item)
    print(len(dataset))
    print(dataset[2])
