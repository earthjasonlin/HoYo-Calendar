"""
生成日历
"""
import json
import os
from datetime import datetime
from icalendar import Calendar, Event
import pytz


def load_json(filepath):
    """加载JSON文件"""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_time(time_str):
    """将时间字符串转换为datetime对象（上海时区）"""
    if not time_str or len(time_str) < 8:
        return None
    try:
        shanghai_tz = pytz.timezone("Asia/Shanghai")
        naive_dt = datetime.strptime(time_str, "%Y%m%d%H%M")
        return shanghai_tz.localize(naive_dt)
    except ValueError:
        return None


def create_event(title, description, start_time, end_time, categories):
    """创建日历事件"""
    event = Event()
    event.add("summary", title)
    if description:
        event.add("description", description)
    event.add("dtstart", start_time)
    event.add("dtend", end_time)
    event.add("categories", [categories])
    return event


def generate_calendar(data, game_name, version_key):
    """生成日历"""
    cal = Calendar()

    game_names = {"ys": "原神", "hsr": "崩坏：星穹铁道", "zzz": "绝区零"}
    display_name = game_names.get(game_name, game_name)
    cal.add("prodid", f"-//Game Calendar//{game_name}//CN")
    cal.add("version", "2.0")
    cal.add("X-WR-CALNAME", f"{display_name}-{version_key}")
    cal.add("X-WR-CALDESC", f"{display_name}活动日历-{version_key}")
    cal.add("x-wr-TIMEZONE", "Asia/Shanghai")

    if "version" in data:
        for item in data["version"]:
            start_time = parse_time(item["timefrom"])
            end_time = parse_time(item["timeto"])
            if start_time and end_time:
                title = f"🆕版本-{item['title']}"
                event = create_event(
                    title, item["description"], start_time, end_time, "版本"
                )
                cal.add_component(event)

    if "media" in data:
        for item in data["media"]:
            start_time = parse_time(item["timefrom"])
            end_time = parse_time(item["timeto"])
            if start_time and end_time:
                title = f"📺媒体-{item['title']}"
                event = create_event(
                    title, item["description"], start_time, end_time, "媒体"
                )
                cal.add_component(event)

    if "abyss" in data:
        for item in data["abyss"]:
            start_time = parse_time(item["timefrom"])
            end_time = parse_time(item["timeto"])
            if start_time and end_time:
                title = f"⚔️深渊-{item['title']}"
                event = create_event(
                    title, item["description"], start_time, end_time, "深渊"
                )
                cal.add_component(event)

    if "gacha" in data:
        for item in data["gacha"]:
            start_time = parse_time(item["timefrom"])
            end_time = parse_time(item["timeto"])
            if start_time and end_time:
                title = f"💫卡池-{item['title']}"
                event = create_event(
                    title, item["description"], start_time, end_time, "卡池"
                )
                cal.add_component(event)

    if "events" in data:
        for item in data["events"]:
            start_time = parse_time(item["timefrom"])
            end_time = parse_time(item["timeto"])
            if start_time and end_time:
                event_type = item.get("type", "")
                if event_type == "main":
                    prefix = "🎡大活动-"
                elif event_type == "mini":
                    prefix = "🎡小活动-"
                elif event_type == "double":
                    prefix = "🎡翻倍活动-"
                else:
                    prefix = "🎡活动-"

                title = f"{prefix}{item['title']}"
                event = create_event(
                    title, item["description"], start_time, end_time, "活动"
                )
                cal.add_component(event)

    return cal


def main():
    """主函数"""
    src_dir = "src"
    generate_path = os.path.join(src_dir, "generate.json")
    generate_data = load_json(generate_path)
    for game_key, version_key in generate_data.items():
        filename = f"{game_key}.json"
        filepath = os.path.join(src_dir, filename)
        if os.path.exists(filepath):
            data = load_json(filepath)
            if version_key in data:
                cal = generate_calendar(data[version_key], game_key, version_key)
                ics_filename = f"{game_key}-calendar-{version_key}.ics"
                with open(ics_filename, "wb") as f:
                    f.write(cal.to_ical())
                print(f"已生成: {ics_filename}")
            else:
                print(f"在{filename}中未找到版本{version_key}")
        else:
            print(f"文件{filepath}不存在")


if __name__ == "__main__":
    main()
