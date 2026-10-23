#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROOT_VIEW = ROOT / "SmartTubeIOS/Sources/SmartTubeIOS/Views/RootView.swift"
INNER_TUBE = ROOT / "SmartTubeIOS/Sources/SmartTubeIOSCore/InnerTubeAPI.swift"
HOME_VIEW = ROOT / "SmartTubeIOS/Sources/SmartTubeIOS/Views/Home/HomeView.swift"
SEARCH_VIEW = ROOT / "SmartTubeIOS/Sources/SmartTubeIOS/Views/Search/SearchView.swift"
PLAYLIST_VIEW = ROOT / "SmartTubeIOS/Sources/SmartTubeIOS/Views/Browse/PlaylistView.swift"


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        print(f"{label}: already applied")
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly 1 match, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"{label}: applied")


# Use the tvOS-only YouTube TV style navigation shell.
replace_once(
    ROOT_VIEW,
    """            #if os(tvOS)\n            MainTVTabView()\n""",
    """            #if os(tvOS)\n            TVYouTubeRootView()\n""",
    "tvOS root shell",
)

# Player presentation must escape the custom sidebar NavigationStack on tvOS.
home_old = '''            contentArea
                #if !os(iOS)
            .navigationDestination(item: $selectedVideo) { video in
                #if os(macOS)
                if store.settings.useTOSPlayerOnMac && tosPlayerFallbackVideoId != video.id {
                    TOSPlayerView(video: video, api: api) {
                        tosPlayerFallbackVideoId = video.id
                    }
                    .environment(store)
                    .onDisappear { tosPlayerFallbackVideoId = nil }
                } else {
                    PlayerView(video: video, api: api)
                }
                #else
                PlayerView(video: video, api: api)
                #endif
            }
                #endif
                .navigationDestination(item: $selectedPlaylist) { stub in'''
home_new = '''            contentArea
                #if os(tvOS)
            .fullScreenCover(item: $selectedVideo) { video in
                PlayerView(video: video, api: api)
                    .ignoresSafeArea()
            }
                #elseif os(macOS)
            .navigationDestination(item: $selectedVideo) { video in
                if store.settings.useTOSPlayerOnMac && tosPlayerFallbackVideoId != video.id {
                    TOSPlayerView(video: video, api: api) {
                        tosPlayerFallbackVideoId = video.id
                    }
                    .environment(store)
                    .onDisappear { tosPlayerFallbackVideoId = nil }
                } else {
                    PlayerView(video: video, api: api)
                }
            }
                #endif
                .navigationDestination(item: $selectedPlaylist) { stub in'''
replace_once(HOME_VIEW, home_old, home_new, "Home tvOS full-screen player")

search_old = '''        #if os(tvOS)
        .toolbar(.hidden, for: .navigationBar)
        .navigationDestination(item: $selectedVideo) { video in
            PlayerView(video: video, api: api)
        }
        #elseif os(iOS)'''
search_new = '''        #if os(tvOS)
        .toolbar(.hidden, for: .navigationBar)
        .fullScreenCover(item: $selectedVideo) { video in
            PlayerView(video: video, api: api)
                .ignoresSafeArea()
        }
        #elseif os(iOS)'''
replace_once(SEARCH_VIEW, search_old, search_new, "Search tvOS full-screen player")

playlist_old = '''        #if os(tvOS)
        .navigationDestination(item: $selectedVideo) { video in
            PlayerView(video: video, api: api)
        }
        #endif'''
playlist_new = '''        #if os(tvOS)
        .fullScreenCover(item: $selectedVideo) { video in
            PlayerView(video: video, api: api)
                .ignoresSafeArea()
        }
        #endif'''
replace_once(PLAYLIST_VIEW, playlist_old, playlist_new, "Playlist tvOS full-screen player")

api = INNER_TUBE.read_text(encoding="utf-8")
helper_marker = 'private let tubeLog = Logger(subsystem: appSubsystem, category: "InnerTube")\n'
helper_code = r'''

/// Language sent to YouTube browse endpoints. This follows the Apple TV preferred
/// language so localized video titles match the official YouTube app more closely.
private func smartTubeMetadataLanguage() -> String {
    let preferred = Locale.preferredLanguages.first ?? "en-US"
    let normalized = preferred.replacingOccurrences(of: "_", with: "-")
    let lower = normalized.lowercased()

    if lower.hasPrefix("zh-hant") || lower.hasPrefix("zh-tw")
        || lower.hasPrefix("zh-hk") || lower.hasPrefix("zh-mo")
    {
        return "zh-TW"
    }
    if lower.hasPrefix("zh") {
        return "zh-CN"
    }

    let parts = normalized.split(separator: "-")
    if parts.count >= 2, parts[1].count == 2 {
        return "\(parts[0])-\(parts[1])"
    }
    return parts.first.map(String.init) ?? "en"
}

/// Region remains independent from UI language, matching the official app's
/// language + region behaviour (for example zh-CN language with US region).
private func smartTubeMetadataRegion() -> String {
    Locale.current.region?.identifier ?? "US"
}
'''

if "private func smartTubeMetadataLanguage()" not in api:
    if helper_marker not in api:
        raise SystemExit("locale helper insertion marker not found")
    api = api.replace(helper_marker, helper_marker + helper_code, 1)
    print("metadata locale helpers: applied")
else:
    print("metadata locale helpers: already applied")

web_old = '''    let webClientContext: [String: Any] = [
        "client": [
            "hl": "en",
            "gl": "US",
            "clientName": InnerTubeClients.Web.name,'''
web_new = '''    let webClientContext: [String: Any] = [
        "client": [
            "hl": smartTubeMetadataLanguage(),
            "gl": smartTubeMetadataRegion(),
            "clientName": InnerTubeClients.Web.name,'''

if web_new not in api:
    count = api.count(web_old)
    if count != 1:
        raise SystemExit(f"WEB metadata context: expected exactly 1 match, found {count}")
    api = api.replace(web_old, web_new, 1)
    print("WEB metadata locale: applied")
else:
    print("WEB metadata locale: already applied")

tv_old = '''    let tvClientContext: [String: Any] = [
        "client": [
            "hl": "en",
            "gl": "US",
            "clientName": InnerTubeClients.TV.name,'''
tv_new = '''    let tvClientContext: [String: Any] = [
        "client": [
            "hl": smartTubeMetadataLanguage(),
            "gl": smartTubeMetadataRegion(),
            "clientName": InnerTubeClients.TV.name,'''

if tv_new not in api:
    count = api.count(tv_old)
    if count != 1:
        raise SystemExit(f"TV metadata context: expected exactly 1 match, found {count}")
    api = api.replace(tv_old, tv_new, 1)
    print("TV metadata locale: applied")
else:
    print("TV metadata locale: already applied")

INNER_TUBE.write_text(api, encoding="utf-8")
print("tvOS YouTube UI + metadata locale + full-screen patch complete")
