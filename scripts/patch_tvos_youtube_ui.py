#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROOT_VIEW = ROOT / "SmartTubeIOS/Sources/SmartTubeIOS/Views/RootView.swift"
TV_ROOT_VIEW = ROOT / "SmartTubeIOS/Sources/SmartTubeIOS/Views/TVYouTubeRootView.swift"
INNER_TUBE = ROOT / "SmartTubeIOS/Sources/SmartTubeIOSCore/InnerTubeAPI.swift"
VIDEO_GROUP = ROOT / "SmartTubeIOS/Sources/SmartTubeIOSCore/VideoGroup.swift"
HOME_VIEW = ROOT / "SmartTubeIOS/Sources/SmartTubeIOS/Views/Home/HomeView.swift"
SEARCH_VIEW = ROOT / "SmartTubeIOS/Sources/SmartTubeIOS/Views/Search/SearchView.swift"
PLAYLIST_VIEW = ROOT / "SmartTubeIOS/Sources/SmartTubeIOS/Views/Browse/PlaylistView.swift"
QUALITY_VM = ROOT / "SmartTubeIOS/Sources/SmartTubeIOS/ViewModels/PlaybackViewModel+Quality.swift"
QUALITY_MANAGER = ROOT / "SmartTubeIOS/Sources/SmartTubeIOS/ViewModels/Managers/PlaybackQualityManager.swift"
PICKER_OVERLAYS = ROOT / "SmartTubeIOS/Sources/SmartTubeIOS/Views/Player/PlayerView+PickerOverlays.swift"


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

# Keep browse section titles localized even though they are runtime Strings. SwiftUI's
# Text(String) does not resolve the string catalog automatically, which is why the first
# tvOS build still showed Home / Recommended while the sidebar was Chinese.
section_titles_old = '''        public var defaultTitle: String {
            switch self {
            case .home: return "Home"
            case .recommended: return "Recommended"
            case .subscriptions: return "Subscriptions"
            case .history: return "History"
            case .playlists: return "Playlists"
            case .channels: return "Channels"
            case .shorts: return "Shorts"
            case .music: return "Music"
            case .news: return "News"
            case .gaming: return "Gaming"
            case .live: return "Live"
            case .sports: return "Sports"
            case .watchLater: return "Watch Later"
            case .settings: return "Settings"
            }
        }'''
section_titles_new = '''        public var defaultTitle: String {
            let useSimplifiedChinese = Locale.preferredLanguages.first?.lowercased().hasPrefix("zh") == true
            switch self {
            case .home: return useSimplifiedChinese ? "首页" : "Home"
            case .recommended: return useSimplifiedChinese ? "推荐" : "Recommended"
            case .subscriptions: return useSimplifiedChinese ? "订阅" : "Subscriptions"
            case .history: return useSimplifiedChinese ? "历史记录" : "History"
            case .playlists: return useSimplifiedChinese ? "播放列表" : "Playlists"
            case .channels: return useSimplifiedChinese ? "频道" : "Channels"
            case .shorts: return useSimplifiedChinese ? "短视频" : "Shorts"
            case .music: return useSimplifiedChinese ? "音乐" : "Music"
            case .news: return useSimplifiedChinese ? "新闻" : "News"
            case .gaming: return useSimplifiedChinese ? "游戏" : "Gaming"
            case .live: return useSimplifiedChinese ? "直播" : "Live"
            case .sports: return useSimplifiedChinese ? "体育" : "Sports"
            case .watchLater: return useSimplifiedChinese ? "稍后观看" : "Watch Later"
            case .settings: return useSimplifiedChinese ? "设置" : "Settings"
            }
        }'''
replace_once(VIDEO_GROUP, section_titles_old, section_titles_new, "browse section Simplified Chinese titles")

# Make the top section selector closer to the compact SmartTube / YouTube TV treatment:
# horizontal scrolling, dark rail, subtle focus ring, and no oversized white tvOS pill.
chip_bar_old = '''        HStack(spacing: 8) {
            ForEach(visibleSections) { section in
                chipButton(section: section)
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 10)
        .background(.ultraThinMaterial)
        .focusSection()
        .defaultFocus($focusedSection, selectedSection)
        .accessibilityElement(children: .contain)
        .accessibilityIdentifier("home.chipBar")'''
chip_bar_new = '''        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 10) {
                ForEach(visibleSections) { section in
                    chipButton(section: section)
                }
            }
            .padding(.horizontal, 18)
            .padding(.vertical, 9)
        }
        .background(Color.black.opacity(0.96))
        .focusSection()
        .defaultFocus($focusedSection, selectedSection)
        .accessibilityElement(children: .contain)
        .accessibilityIdentifier("home.chipBar")'''
replace_once(HOME_VIEW, chip_bar_old, chip_bar_new, "compact tvOS home chip bar")

chip_button_old = '''        return Button(action: action) {
            Text(section.title)
                .font(.headline)
                .padding(.horizontal, 24)
                .padding(.vertical, 12)
                .background(
                    (isSelected || isFocused) ? Color.primary : Color.secondary.opacity(0.15),
                    in: Capsule()
                )
                .foregroundStyle(
                    (isSelected || isFocused)
                        ? Color(white: colorScheme == .dark ? 0 : 1)
                        : Color.primary
                )
                .focusEffectDisabled()
        }
        .buttonStyle(.borderless)
        .scaleEffect(isFocused ? 1.12 : 1.0)
        .animation(.easeInOut(duration: 0.15), value: focusedSection)
        .animation(.easeInOut(duration: 0.15), value: selectedSection)
        .accessibilityAddTraits(isSelected ? [.isSelected] : [])
        .accessibilityLabel(section.title)
        .accessibilityIdentifier("chip.\\(section.title)")
        .focused($focusedSection, equals: section)'''
chip_button_new = '''        return Button(action: action) {
            Text(section.title)
                .font(.callout.weight(isSelected ? .semibold : .medium))
                .lineLimit(1)
                .padding(.horizontal, 18)
                .frame(height: 44)
                .foregroundStyle(Color.white.opacity(isSelected || isFocused ? 1.0 : 0.72))
                .background(
                    Capsule()
                        .fill(
                            isSelected
                                ? Color.white.opacity(0.16)
                                : (isFocused ? Color.white.opacity(0.10) : Color.white.opacity(0.045))
                        )
                )
                .overlay(
                    Capsule()
                        .stroke(isFocused ? Color.white.opacity(0.34) : Color.clear, lineWidth: 1.5)
                )
                .focusEffectDisabled()
        }
        .buttonStyle(.plain)
        .focusEffectDisabled()
        .scaleEffect(isFocused ? 1.025 : 1.0)
        .animation(.easeOut(duration: 0.10), value: focusedSection)
        .animation(.easeInOut(duration: 0.12), value: selectedSection)
        .accessibilityAddTraits(isSelected ? [.isSelected] : [])
        .accessibilityLabel(section.title)
        .accessibilityIdentifier("chip.\\(section.title)")
        .focused($focusedSection, equals: section)'''
replace_once(HOME_VIEW, chip_button_old, chip_button_new, "compact tvOS home chips")

# Tighten the left navigation rail and take full ownership of the button style so tvOS does
# not draw the giant system focus capsule seen on the first real-device build.
sidebar_width_old = '''        .frame(width: sidebarExpanded ? 228 : 76, alignment: .leading)
        .background(Color.black.opacity(0.985))'''
sidebar_width_new = '''        .frame(width: sidebarExpanded ? 212 : 68, alignment: .leading)
        .background(Color.black.opacity(0.985))'''
replace_once(TV_ROOT_VIEW, sidebar_width_old, sidebar_width_new, "compact tvOS sidebar width")

sidebar_button_old = '''        return Button {
            selectedSection = section
        } label: {
            HStack(spacing: 12) {
                Image(systemName: section.icon)
                    .font(.system(size: 23, weight: .semibold))
                    .frame(width: 34, height: 34)

                if sidebarExpanded {
                    Text(title)
                        .font(.headline)
                        .lineLimit(1)
                        .transition(.opacity)
                }
            }
            .foregroundStyle(isSelected || isFocused ? Color.white : Color.white.opacity(0.68))
            .padding(.horizontal, 12)
            .frame(width: sidebarExpanded ? 212 : 62, height: 54, alignment: .leading)
            .background(
                RoundedRectangle(cornerRadius: 11, style: .continuous)
                    .fill(isFocused ? Color.white.opacity(0.15) : (isSelected ? Color.white.opacity(0.08) : Color.clear))
            )
            .overlay(alignment: .leading) {
                if isSelected {
                    Capsule()
                        .fill(Color.red)
                        .frame(width: 4, height: 28)
                        .padding(.leading, 1)
                }
            }
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .focusEffectDisabled()
        .scaleEffect(isFocused ? 1.018 : 1.0, anchor: .leading)
        .animation(.easeInOut(duration: 0.10), value: isFocused)
        .focused($focusedSection, equals: section)
        .accessibilityLabel(title)
        .accessibilityAddTraits(isSelected ? [.isSelected] : [])
        .accessibilityIdentifier("tv.sidebar.\\(section.rawValue.lowercased())")'''
sidebar_button_new = '''        return Button {
            selectedSection = section
        } label: {
            HStack(spacing: 10) {
                Image(systemName: section.icon)
                    .font(.system(size: 21, weight: .semibold))
                    .frame(width: 32, height: 32)

                if sidebarExpanded {
                    Text(title)
                        .font(.callout.weight(isSelected ? .semibold : .medium))
                        .lineLimit(1)
                        .transition(.opacity)
                }
            }
            .foregroundStyle(isSelected || isFocused ? Color.white : Color.white.opacity(0.66))
            .padding(.horizontal, 10)
            .frame(width: sidebarExpanded ? 196 : 56, height: 50, alignment: .leading)
            .background(
                RoundedRectangle(cornerRadius: 9, style: .continuous)
                    .fill(isFocused ? Color.white.opacity(0.10) : (isSelected ? Color.white.opacity(0.055) : Color.clear))
            )
            .overlay(
                RoundedRectangle(cornerRadius: 9, style: .continuous)
                    .stroke(isFocused ? Color.white.opacity(0.28) : Color.clear, lineWidth: 1.25)
            )
            .overlay(alignment: .leading) {
                if isSelected {
                    Capsule()
                        .fill(Color.red)
                        .frame(width: 3, height: 25)
                        .padding(.leading, 1)
                }
            }
            .contentShape(RoundedRectangle(cornerRadius: 9, style: .continuous))
            .focusEffectDisabled()
        }
        .buttonStyle(TVSidebarButtonStyle())
        .focusEffectDisabled()
        .animation(.easeOut(duration: 0.10), value: isFocused)
        .focused($focusedSection, equals: section)
        .accessibilityLabel(title)
        .accessibilityAddTraits(isSelected ? [.isSelected] : [])
        .accessibilityIdentifier("tv.sidebar.\\(section.rawValue.lowercased())")'''
replace_once(TV_ROOT_VIEW, sidebar_button_old, sidebar_button_new, "custom tvOS sidebar focus style")

sidebar_style_old = '''}
#endif
'''
sidebar_style_new = '''}

private struct TVSidebarButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .opacity(configuration.isPressed ? 0.78 : 1.0)
    }
}
#endif
'''
replace_once(TV_ROOT_VIEW, sidebar_style_old, sidebar_style_new, "tvOS sidebar custom button style")

# The initial HLS manifest is commonly capped at 1080p. Keep adaptive MP4 formats from the
# successful player response available to the tvOS picker so 1440p/2160p do not disappear.
quality_formats_old = '''extension PlaybackViewModel {

    public func selectFormat(_ format: VideoFormat?) {'''
quality_formats_new = '''extension PlaybackViewModel {

    /// Formats shown by the quality picker. On tvOS the native HLS master commonly tops out
    /// at 1080p, while the same PlayerInfo contains higher adaptive MP4 (typically AV1) video.
    /// Preserve those higher tiers so selecting 1440p/2160p can switch through DASH composition.
    public var selectableVideoFormats: [VideoFormat] {
        #if os(tvOS)
        if let info = playerInfo {
            let adaptive = Self.deduplicatedVideoFormats(info.formats)
            let adaptiveMax = adaptive.map(\\.height).max() ?? 0
            let hlsMax = availableFormats.map(\\.height).max() ?? 0
            if adaptiveMax > hlsMax {
                return adaptive
            }
        }
        #endif
        return availableFormats
    }

    public func selectFormat(_ format: VideoFormat?) {'''
replace_once(QUALITY_VM, quality_formats_old, quality_formats_new, "tvOS adaptive 4K quality list")

replace_once(
    PICKER_OVERLAYS,
    "                        ForEach(vm.availableFormats) { fmt in",
    "                        ForEach(vm.selectableVideoFormats) { fmt in",
    "quality picker uses adaptive tvOS formats",
)

# 1440p/2160p selected on tvOS must not be sent back through the 1080p HLS master. The
# project already has a tested DASH composition path that combines adaptive video + audio;
# route high-resolution selections through it and retain all existing rqh/CDN recovery logic.
quality_route_old = '''            if self.delegate?.playerInfo?.hlsURL != nil {
                await self.reloadHLSItem(seekTo: savedTime, quality: quality)
            } else {
                await self.reloadDASHItem(seekTo: savedTime, format: format)
            }'''
quality_route_new = '''            #if os(tvOS)
            if let format, format.height > 1080 {
                playerLog.notice(
                    "[quality] tvOS high-resolution selection \\(format.height)p — switching via adaptive DASH composition"
                )
                await self.reloadDASHItem(seekTo: savedTime, format: format)
                return
            }
            #endif
            if self.delegate?.playerInfo?.hlsURL != nil {
                await self.reloadHLSItem(seekTo: savedTime, quality: quality)
            } else {
                await self.reloadDASHItem(seekTo: savedTime, format: format)
            }'''
replace_once(QUALITY_MANAGER, quality_route_old, quality_route_new, "tvOS 1440p/2160p DASH routing")

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
print("tvOS YouTube UI + Chinese titles + 4K quality routing + metadata locale patch complete")
