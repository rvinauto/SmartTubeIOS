#!/usr/bin/env python3
"""Fill missing Simplified Chinese translations used by the tvOS build.

The upstream project already ships a large Localizable.xcstrings catalog with
zh-Hans support. New UI strings occasionally land before their Simplified
Chinese translations. Keeping this small overlay in the self-build branch lets
us fill only those gaps without rewriting the entire upstream catalog by hand.

The script is intentionally idempotent: an existing non-empty zh-Hans
translation is never overwritten.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "SmartTubeIOS" / "Sources" / "SmartTubeIOS" / "Localizable.xcstrings"

ZH_HANS: dict[str, str] = {
    "%@ — Undo": "%@ — 撤销",
    "Added to Playlist": "已添加到播放列表",
    "All Channels": "所有频道",
    "Change PIN": "更改 PIN",
    "Chapters": "章节",
    "Clear Watch History on This Device": "清除此设备上的观看记录",
    "Copy to Playlist": "复制到播放列表",
    "Could Not Load Playlists": "无法加载播放列表",
    "Could Not Report": "无法提交报告",
    "Could Not Update Playlist": "无法更新播放列表",
    "Disable Analytics & Crash Reporting": "关闭分析与崩溃报告",
    "Disable Liquid Glass": "禁用液态玻璃",
    "Hide Watched Videos": "隐藏已观看的视频",
    "Loop": "循环播放",
    'Missing playlist entry information for "%@".': '缺少“%@”的播放列表条目信息。',
    "Move to Playlist": "移动到播放列表",
    "No chapters available.": "暂无章节。",
    "No Playlists": "没有播放列表",
    "Parental Controls": "家长控制",
    "Play Incognito": "无痕播放",
    "Remove PIN": "移除 PIN",
    "Reported": "已报告",
    "Restart the app for this to take effect.": "重新启动应用后此设置才会生效。",
    "Set PIN": "设置 PIN",
    "Thanks for the feedback — this segment has been reported to SponsorBlock.": "感谢反馈——此片段已报告给 SponsorBlock。",
    "The report couldn't be sent. Please try again later.": "报告无法发送，请稍后再试。",
    "Watch history is saved on this device. SmartTube also tries to report watches to your YouTube account, but YouTube may not always record them.": "观看记录会保存在此设备上。SmartTube 也会尝试将观看记录同步到您的 YouTube 账号，但 YouTube 不一定每次都能记录。",
    "Watched threshold: %lld%%": "已观看阈值：%lld%%",
    "When a PIN is set, it must be entered every time this Settings screen is opened.": "设置 PIN 后，每次打开“设置”页面都必须输入该 PIN。",
}


def has_translation(entry: dict) -> bool:
    zh = entry.get("localizations", {}).get("zh-Hans", {})
    unit = zh.get("stringUnit", {})
    return bool(str(unit.get("value", "")).strip())


def main() -> None:
    with CATALOG.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    strings = data.get("strings")
    if not isinstance(strings, dict):
        raise SystemExit(f"Invalid strings catalog: {CATALOG}")

    added: list[str] = []
    already_present: list[str] = []
    missing_keys: list[str] = []

    for key, value in ZH_HANS.items():
        entry = strings.get(key)
        if not isinstance(entry, dict):
            missing_keys.append(key)
            continue

        if has_translation(entry):
            already_present.append(key)
            continue

        localizations = entry.setdefault("localizations", {})
        localizations["zh-Hans"] = {
            "stringUnit": {
                "state": "translated",
                "value": value,
            }
        }
        added.append(key)

    if missing_keys:
        print("WARNING: localization keys no longer present in catalog:")
        for key in missing_keys:
            print(f"  - {key}")

    # Keep Xcode-compatible JSON and UTF-8 Chinese characters.
    with CATALOG.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    # Audit remaining gaps so CI logs make newly introduced untranslated strings visible.
    remaining: list[str] = []
    for key, entry in strings.items():
        if not key or not isinstance(entry, dict):
            continue
        if not has_translation(entry):
            remaining.append(key)

    print(f"zh-Hans patch complete: added={len(added)}, existing={len(already_present)}, missing_keys={len(missing_keys)}")
    if added:
        print("Added Simplified Chinese translations:")
        for key in added:
            print(f"  + {key}")
    if remaining:
        print(f"Remaining catalog entries without zh-Hans: {len(remaining)}")
        for key in remaining:
            print(f"  ? {key}")
    else:
        print("All non-empty catalog keys have a zh-Hans translation.")


if __name__ == "__main__":
    main()
