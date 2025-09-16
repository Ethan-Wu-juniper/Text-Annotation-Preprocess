from pydantic import BaseModel
import xml.etree.ElementTree as ET


class Task(BaseModel):
    url: str
    frame_count: int
    start_frame: int
    width: int
    height: int


class Box(BaseModel):
    id: int
    frame: int
    xtl: float
    ytl: float
    xbr: float
    ybr: float


tree = ET.parse("./annotation/cvat_for_video.xml")
root = tree.getroot()
tasks = root.find("meta").find("project").find("tasks").findall("task")
tracks = root.findall("track")

acc_frame = 0
result_tasks = {}

for task in tasks:
    frame_count = int(task.find("size").text)
    ratio = task.find("original_size")
    result_tasks[task.find("id").text] = Task(
        url=f"https://creative-assets.gliacloud.com/{task.find('name').text}",
        frame_count=frame_count,
        start_frame=acc_frame,
        width=ratio.find("width").text,
        height=ratio.find("height").text,
    )
    acc_frame += frame_count

result_boxes = [
    Box(
        id=track.get("id"),
        frame=box.get("frame"),
        xtl=box.get("xtl"),
        ytl=box.get("ytl"),
        xbr=box.get("xbr"),
        ybr=box.get("ybr"),
    )
    for track in tracks
    for box in track.findall("box")
]

print("result boxes", result_boxes)
