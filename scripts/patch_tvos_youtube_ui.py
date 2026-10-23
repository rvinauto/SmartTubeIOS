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
chip_button_new = '''        // Pre-compute styling with explicit types so the Swift type checker does not time out.
        let chipHighlighted: Bool = isSelected || isFocused
        let chipFont: Font = .callout.weight(isSelected ? .semibold : .medium)
        let chipForeground: Color = Color.white.opacity(chipHighlighted ? 1.0 : 0.72)
        let chipFillOpacity: Double = isSelected ? 0.16 : (isFocused ? 0.10 : 0.045)
        let chipFill: Color = Color.white.opacity(chipFillOpacity)
        let chipStroke: Color = isFocused ? Color.white.opacity(0.34) : Color.clear
        let chipScale: CGFloat = isFocused ? 1.025 : 1.0
        let chipTitle: String = section.title
        let chipLabel: AnyView = AnyView(
            Text(chipTitle)
                .font(chipFont)
                .lineLimit(1)
                .padding(.horizontal, 18)
                .frame(height: 44)
                .foregroundStyle(chipForeground)
                .background(Capsule().fill(chipFill))
                .overlay(Capsule().stroke(chipStroke, lineWidth: 1.5))
                .focusEffectDisabled()
        )
        let chipCore: AnyView = AnyView(
            Button(action: action) { chipLabel }
                .buttonStyle(.plain)
                .focusEffectDisabled()
                .scaleEffect(chipScale)
        )
        return chipCore
        .animation(.easeOut(duration: 0.10), value: focusedSection)
        .animation(.easeInOut(duration: 0.12), value: selectedSection)
        .accessibilityAddTraits(isSelected ? [.isSelected] : [])
        .accessibilityLabel(chipTitle)
        .accessibilityIdentifier("chip.\\(chipTitle)")
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

# ---------------------------------------------------------------------------------------
# tvOS 4K experiment (approved): only active on tvOS when the requested quality is >1080p.
# Default / <=1080p paths are untouched. All diagnostics are logged with the `[4k-exp]` prefix.
# ---------------------------------------------------------------------------------------
CORE_DIR = ROOT / "SmartTubeIOS/Sources/SmartTubeIOSCore"
UI_DIR = ROOT / "SmartTubeIOS/Sources/SmartTubeIOS"
HLS_PARSER = CORE_DIR / "HLSManifestParser.swift"
FALLBACK = UI_DIR / "ViewModels/PlaybackViewModel+Fallback.swift"
PLAYER_LIFECYCLE = UI_DIR / "Views/Player/PlayerView+Lifecycle.swift"

(CORE_DIR / "TVFourKExperiment.swift").write_text(r"""import Foundation
import os
#if canImport(VideoToolbox)
import CoreMedia
import VideoToolbox
#endif

/// tvOS-only 4K playback experiment. Active only when the requested quality is above 1080p.
public enum TVFourKExperiment {
    /// Sentinel passed as `requiredVideoCodec` to the HLS master filter: keep every codec
    /// except AV1 when the device cannot hardware-decode AV1.
    public static let excludeUnsupportedAV1Codec = "!4kexp-no-unsupported-av01"
    /// Height cap used by the HLS proxy filter while the experiment is active (effectively none).
    public static let uncappedHeight = 4320

    private static let logger = Logger(subsystem: "com.void.smarttube", category: "4k-exp")

    public static func isActive(requestedMaxHeight: Int?) -> Bool {
        #if os(tvOS)
        guard let h = requestedMaxHeight else { return false }
        return h > 1080
        #else
        return false
        #endif
    }

    public static let av1HardwareDecodeSupported: Bool = {
        #if canImport(VideoToolbox)
        return VTIsHardwareDecodeSupported(kCMVideoCodecType_AV1)
        #else
        return false
        #endif
    }()

    nonisolated(unsafe) public static var lastClientLabel: String = ""

    public static func log(_ message: String) {
        logger.notice("[4k-exp] \(message, privacy: .public)")
        print("[4k-exp] \(message)")
    }

    /// Codec gate for an HLS `#EXT-X-STREAM-INF` line / codecs string.
    public static func isVariantCodecAllowed(_ codecs: String) -> Bool {
        if codecs.localizedCaseInsensitiveContains("av01") { return av1HardwareDecodeSupported }
        return true
    }

    /// Option 2: on tvOS hide AV1 formats above 1080p when AV1 cannot be hardware decoded.
    public static func isFormatDecodable(height: Int, mimeType: String) -> Bool {
        #if os(tvOS)
        if height > 1080, mimeType.contains("av01"), !av1HardwareDecodeSupported { return false }
        #endif
        return true
    }

    /// Human-readable list of master manifest variants (resolution / codecs / bandwidth).
    public static func describeVariants(_ manifest: String) -> [String] {
        var out: [String] = []
        for raw in manifest.components(separatedBy: .newlines) {
            let line = raw.trimmingCharacters(in: .whitespaces)
            guard line.hasPrefix("#EXT-X-STREAM-INF") else { continue }
            let res = line.range(of: #"RESOLUTION=[0-9x]+"#, options: .regularExpression).map { String(line[$0]) } ?? "RESOLUTION=?"
            let codecs = line.range(of: #"CODECS="[^"]*""#, options: .regularExpression).map { String(line[$0]) } ?? "CODECS=?"
            let bw = line.range(of: #"BANDWIDTH=[0-9]+"#, options: .regularExpression).map { String(line[$0]) } ?? "BANDWIDTH=?"
            let allowed = isVariantCodecAllowed(codecs) ? "ok" : "dropped(av01 no HW)"
            out.append("\(res) \(codecs) \(bw) \(allowed)")
        }
        return out
    }
}

/// 4K-experiment variant of `parseHLSMasterManifest`: heights above 1080p prefer VP9, then
/// HEVC, then AV1 (only with hardware decode); <=1080p keeps H.264 first. Unsupported AV1 is dropped.
public func parseHLSMasterManifestFourK(_ manifestText: String, baseURL: URL) -> [Int: URL] {
    var variants: [Int: URL] = [:]
    var ranks: [Int: Int] = [:]
    var pendingHeight: Int? = nil
    var pendingCodecs: String = ""
    func rank(_ codecs: String, height: Int) -> Int {
        let c = codecs.lowercased()
        if height > 1080 {
            if c.contains("vp09") { return 0 }
            if c.contains("hvc1") || c.contains("hev1") { return 1 }
            if c.contains("av01") { return 2 }
            return 3
        }
        if c.contains("avc1") { return 0 }
        if c.contains("vp09") { return 1 }
        return 2
    }
    for line in manifestText.components(separatedBy: .newlines) {
        let trimmed = line.trimmingCharacters(in: .whitespaces)
        if trimmed.hasPrefix("#EXT-X-STREAM-INF") {
            pendingHeight = nil
            pendingCodecs = trimmed.range(of: #"CODECS="[^"]*""#, options: .regularExpression).map { String(trimmed[$0]) } ?? ""
            if let r = trimmed.range(of: #"RESOLUTION=\d+x(\d+)"#, options: .regularExpression),
                let h = String(trimmed[r]).components(separatedBy: "x").last.flatMap({ Int($0) })
            {
                pendingHeight = h
            }
        } else if !trimmed.hasPrefix("#"), !trimmed.isEmpty, let height = pendingHeight {
            let url: URL? = trimmed.hasPrefix("http")
                ? URL(string: trimmed)
                : URL(string: trimmed, relativeTo: baseURL).map { $0.absoluteURL }
            if let url, TVFourKExperiment.isVariantCodecAllowed(pendingCodecs) {
                let r = rank(pendingCodecs, height: height)
                if let existing = ranks[height], existing <= r {
                    // keep better-ranked variant
                } else {
                    variants[height] = url
                    ranks[height] = r
                }
            }
            pendingHeight = nil
            pendingCodecs = ""
        } else if trimmed.hasPrefix("#") {
            pendingHeight = nil
        }
    }
    return variants
}
""", encoding="utf-8")
print("tvOS 4K experiment core helper: written")

(UI_DIR / "Views/Player/TVFourKDebug.swift").write_text(r"""#if os(tvOS)
import AVFoundation
import CoreMedia
import SmartTubeIOSCore
import SwiftUI

/// Runtime monitor for the tvOS 4K experiment. Logs with `[4k-exp]` and feeds the overlay.
@MainActor
enum TVFourKMonitor {
    /// HLS config (maxHeight, requiredCodec) saved before a 4K quality switch so a later
    /// <=1080p selection restores the exact previous behaviour.
    static var savedHLSConfig: (maxHeight: Int?, codec: String?)? = nil
    static var lastError: String = ""

    static func videoCodec(_ item: AVPlayerItem) -> String {
        for track in item.tracks {
            guard let asset = track.assetTrack, asset.mediaType == .video else { continue }
            for raw in asset.formatDescriptions {
                let desc = raw as! CMFormatDescription
                let code = CMFormatDescriptionGetMediaSubType(desc)
                let chars: [UInt8] = [
                    UInt8((code >> 24) & 0xFF), UInt8((code >> 16) & 0xFF),
                    UInt8((code >> 8) & 0xFF), UInt8(code & 0xFF),
                ]
                return String(bytes: chars, encoding: .ascii) ?? "?"
            }
        }
        return "?"
    }

    static func describe(_ item: AVPlayerItem?) -> String {
        guard let item else { return "no item" }
        let size = item.presentationSize
        let event = item.accessLog()?.events.last
        let indicated = Int((event?.indicatedBitrate ?? 0) / 1000)
        let observed = Int((event?.observedBitrate ?? 0) / 1000)
        let uri = event?.uri.map { String($0.suffix(60)) } ?? "-"
        return "size=\(Int(size.width))x\(Int(size.height)) codec=\(videoCodec(item)) indicated=\(indicated)kbps observed=\(observed)kbps uri=…\(uri)"
    }

    static func attach(to item: AVPlayerItem, context: String) {
        TVFourKExperiment.log(
            "attach context=\(context) client=\(TVFourKExperiment.lastClientLabel) av1HW=\(TVFourKExperiment.av1HardwareDecodeSupported) maxRes=\(Int(item.preferredMaximumResolution.width))x\(Int(item.preferredMaximumResolution.height)) peak=\(Int(item.preferredPeakBitRate / 1000))kbps"
        )
        lastError = ""
        Task { @MainActor [weak item] in
            var reportedError = false
            for tick in 0..<24 {
                try? await Task.sleep(for: .seconds(5))
                guard let item else { return }
                TVFourKExperiment.log("[\(context)] t=\((tick + 1) * 5)s status=\(item.status.rawValue) \(describe(item))")
                if !reportedError {
                    if let err = item.error {
                        lastError = "\(err)"
                        TVFourKExperiment.log("[\(context)] item.error=\(err)")
                        reportedError = true
                    } else if let ev = item.errorLog()?.events.last {
                        lastError = "\(ev.errorDomain) \(ev.errorStatusCode) \(ev.errorComment ?? "")"
                        TVFourKExperiment.log("[\(context)] errorLog: \(lastError)")
                        reportedError = true
                    }
                }
            }
        }
    }
}

/// Small on-screen debug text shown in the player only while the 4K experiment is active.
struct TVFourKDebugOverlay: View {
    let player: AVPlayer
    let requestedMaxHeight: Int?

    var body: some View {
        if TVFourKExperiment.isActive(requestedMaxHeight: requestedMaxHeight) {
            TimelineView(.periodic(from: .now, by: 1.0)) { _ in
                let text: String = overlayText()
                Text(text)
                    .font(.system(size: 18, weight: .medium, design: .monospaced))
                    .foregroundStyle(Color.yellow)
                    .padding(10)
                    .background(Color.black.opacity(0.65))
                    .clipShape(RoundedRectangle(cornerRadius: 8))
            }
            .padding(40)
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topTrailing)
            .allowsHitTesting(false)
            .accessibilityHidden(true)
        }
    }

    private func overlayText() -> String {
        let req: String = requestedMaxHeight.map { "\($0)p" } ?? "auto"
        var lines: [String] = []
        lines.append("[4k-exp] req=\(req) client=\(TVFourKExperiment.lastClientLabel)")
        lines.append(TVFourKMonitor.describe(player.currentItem))
        lines.append("AV1 HW=\(TVFourKExperiment.av1HardwareDecodeSupported ? "yes" : "no")")
        if !TVFourKMonitor.lastError.isEmpty {
            lines.append("err=\(String(TVFourKMonitor.lastError.prefix(120)))")
        }
        return lines.joined(separator: "\n")
    }
}
#endif
""", encoding="utf-8")
print("tvOS 4K experiment monitor/overlay: written")

# HLS master filter: support the "drop unsupported AV1 only" sentinel.
replace_once(
    HLS_PARSER,
    "            let codecMatches = trimmed.localizedCaseInsensitiveContains(requiredVideoCodec)\n",
    "            let codecMatches: Bool =\n"
    "                requiredVideoCodec == TVFourKExperiment.excludeUnsupportedAV1Codec\n"
    "                ? TVFourKExperiment.isVariantCodecAllowed(trimmed)\n"
    "                : trimmed.localizedCaseInsensitiveContains(requiredVideoCodec)\n",
    "4k-exp HLS master filter sentinel",
)

# Initial load: relax HLS policy only in 4K mode.
replace_once(
    FALLBACK,
    "        let hlsPolicy = HLSPlaybackPolicy.resolve(label: label, isHLS: isHLSManifest)\n",
    """        let basePolicy = HLSPlaybackPolicy.resolve(label: label, isHLS: isHLSManifest)
        let fourKActive: Bool = isHLSManifest && TVFourKExperiment.isActive(requestedMaxHeight: effectiveQuality.maxHeight)
        let hlsPolicy: HLSPlaybackPolicy =
            fourKActive
            ? HLSPlaybackPolicy(
                userAgent: basePolicy.userAgent,
                maximumHeight: nil,
                filtersMasterManifest: basePolicy.filtersMasterManifest,
                requiresH264: false
            )
            : basePolicy
        if fourKActive {
            TVFourKExperiment.lastClientLabel = label
            TVFourKExperiment.log(
                "attemptURL client=\\(label) requested=\\(effectiveQuality.maxHeight ?? 0)p base(maxH=\\(basePolicy.maximumHeight ?? 0) h264=\\(basePolicy.requiresH264)) → relaxed (no cap, no H.264 requirement, av1HW=\\(TVFourKExperiment.av1HardwareDecodeSupported))"
            )
        }
""",
    "4k-exp relaxed HLS policy",
)
replace_once(
    FALLBACK,
    """            qualityManager.configureHLSPlayback(
                userAgent: hlsPolicy.userAgent,
                maximumHeight: hlsPolicy.maximumHeight,
                requiredVideoCodec: hlsPolicy.requiresH264 ? "avc1" : nil
            )
""",
    """            if fourKActive {
                qualityManager.configureHLSPlayback(
                    userAgent: hlsPolicy.userAgent,
                    maximumHeight: TVFourKExperiment.uncappedHeight,
                    requiredVideoCodec: TVFourKExperiment.excludeUnsupportedAV1Codec
                )
            } else {
                qualityManager.configureHLSPlayback(
                    userAgent: hlsPolicy.userAgent,
                    maximumHeight: hlsPolicy.maximumHeight,
                    requiredVideoCodec: hlsPolicy.requiresH264 ? "avc1" : nil
                )
            }
""",
    "4k-exp HLS proxy config",
)
replace_once(
    FALLBACK,
    """        player.replaceCurrentItem(with: item)
        itemObserverTask?.cancel()

        for await status in item.statusStream {
""",
    """        player.replaceCurrentItem(with: item)
        #if os(tvOS)
        if fourKActive { TVFourKMonitor.attach(to: item, context: label) }
        #endif
        itemObserverTask?.cancel()

        for await status in item.statusStream {
""",
    "4k-exp monitor on initial load",
)

replace_once(
    FALLBACK,
    "            } else if let cached = PlaybackQualityManager.cachedHLSVariants(for: videoId) {\n",
    "            } else if !fourKActive, let cached = PlaybackQualityManager.cachedHLSVariants(for: videoId) {\n",
    "4k-exp bypass HLS variant cache",
)

# Manifest parsing / variant logging in 4K mode.
replace_once(
    QUALITY_MANAGER,
    """        let variants = parseHLSMasterManifest(text, baseURL: url.deletingLastPathComponent())
""",
    """        let fourKActive: Bool = TVFourKExperiment.isActive(requestedMaxHeight: effectiveQuality.maxHeight)
        if fourKActive {
            let described: [String] = TVFourKExperiment.describeVariants(text)
            TVFourKExperiment.log("manifest variants (\\(described.count)):")
            for line in described { TVFourKExperiment.log("  variant \\(line)") }
        }
        let variants: [Int: URL] =
            fourKActive
            ? parseHLSMasterManifestFourK(text, baseURL: url.deletingLastPathComponent())
            : parseHLSMasterManifest(text, baseURL: url.deletingLastPathComponent())
""",
    "4k-exp manifest parse + log",
)

# Option 2: composition never picks undecodable AV1 >1080p on tvOS.
replace_once(
    QUALITY_MANAGER,
    """        let videoOnly = formats.filter {
            $0.mimeType.hasPrefix("video/mp4") && !$0.mimeType.contains(", ") && $0.url != nil
        }
        func sortKey(""",
    """        let videoOnly = formats.filter {
            $0.mimeType.hasPrefix("video/mp4") && !$0.mimeType.contains(", ") && $0.url != nil
                && TVFourKExperiment.isFormatDecodable(height: $0.height, mimeType: $0.mimeType)
        }
        func sortKey(""",
    "4k-exp hide undecodable AV1 from composition",
)

# Monitor quality-switch HLS items in 4K mode.
replace_once(
    QUALITY_MANAGER,
    """        player.replaceCurrentItem(with: item)
        delegate?.isSwappingItem = false
    }

    func configureHLSPlayback(""",
    """        player.replaceCurrentItem(with: item)
        delegate?.isSwappingItem = false
        #if os(tvOS)
        if TVFourKExperiment.isActive(requestedMaxHeight: quality.maxHeight) {
            TVFourKMonitor.attach(to: item, context: "quality-switch-HLS")
        }
        #endif
    }

    func configureHLSPlayback(""",
    "4k-exp monitor on quality switch",
)

replace_once(
    QUALITY_MANAGER,
    """        hlsPlaybackMaximumHeight = nil
        hlsRequiredVideoCodec = nil
        nativeHLSProxyLoader = nil
        isMuxedFallback = false
""",
    """        hlsPlaybackMaximumHeight = nil
        hlsRequiredVideoCodec = nil
        nativeHLSProxyLoader = nil
        #if os(tvOS)
        TVFourKMonitor.savedHLSConfig = nil
        #endif
        isMuxedFallback = false
""",
    "4k-exp reset saved HLS config",
)

# Quality switch routing: >1080p on tvOS goes through the relaxed HLS master when available;
# <=1080p restores the exact previous HLS configuration.
replace_once(
    QUALITY_MANAGER,
    quality_route_new,
    """            #if os(tvOS)
            if let format, format.height > 1080 {
                if let hlsURL = self.delegate?.playerInfo?.hlsURL {
                    if TVFourKMonitor.savedHLSConfig == nil {
                        TVFourKMonitor.savedHLSConfig = (self.hlsPlaybackMaximumHeight, self.hlsRequiredVideoCodec)
                    }
                    TVFourKExperiment.log(
                        "quality switch → \\(format.height)p via relaxed HLS master client=\\(TVFourKExperiment.lastClientLabel) prev(maxH=\\(self.hlsPlaybackMaximumHeight ?? 0) codec=\\(self.hlsRequiredVideoCodec ?? "nil"))"
                    )
                    self.hlsPlaybackMaximumHeight = TVFourKExperiment.uncappedHeight
                    self.hlsRequiredVideoCodec = TVFourKExperiment.excludeUnsupportedAV1Codec
                    self.nativeHLSProxyLoader = nil
                    _ = await self.fetchHLSVariantURLs(url: hlsURL, userAgent: self.hlsPlaybackUserAgent)
                    await self.reloadHLSItem(seekTo: savedTime, quality: quality)
                    return
                }
                TVFourKExperiment.log(
                    "quality switch → \\(format.height)p: no HLS URL, using adaptive DASH composition codec=\\(format.mimeType)"
                )
                await self.reloadDASHItem(seekTo: savedTime, format: format)
                return
            }
            if let saved = TVFourKMonitor.savedHLSConfig {
                TVFourKExperiment.log("quality switch → <=1080p: restoring HLS config maxH=\\(saved.maxHeight ?? 0) codec=\\(saved.codec ?? "nil")")
                self.hlsPlaybackMaximumHeight = saved.maxHeight
                self.hlsRequiredVideoCodec = saved.codec
                self.nativeHLSProxyLoader = nil
                TVFourKMonitor.savedHLSConfig = nil
            }
            #endif
            if self.delegate?.playerInfo?.hlsURL != nil {
                await self.reloadHLSItem(seekTo: savedTime, quality: quality)
            } else {
                await self.reloadDASHItem(seekTo: savedTime, format: format)
            }""",
    "4k-exp tvOS quality routing",
)

# Picker: hide undecodable AV1 >1080p; when an HLS master exists, offer 1440p/2160p entries.
replace_once(
    QUALITY_VM,
    """        #if os(tvOS)
        if let info = playerInfo {
            let adaptive = Self.deduplicatedVideoFormats(info.formats)
            let adaptiveMax = adaptive.map(\\.height).max() ?? 0
            let hlsMax = availableFormats.map(\\.height).max() ?? 0
            if adaptiveMax > hlsMax {
                return adaptive
            }
        }
        #endif
        return availableFormats""",
    """        #if os(tvOS)
        guard let info = playerInfo else { return availableFormats }
        let adaptive: [VideoFormat] = Self.deduplicatedVideoFormats(info.formats)
        let adaptiveMax: Int = adaptive.map(\\.height).max() ?? 0
        let hlsMax: Int = availableFormats.map(\\.height).max() ?? 0
        let base: [VideoFormat] = adaptiveMax > hlsMax ? adaptive : availableFormats
        var result: [VideoFormat] = base.filter {
            TVFourKExperiment.isFormatDecodable(height: $0.height, mimeType: $0.mimeType)
        }
        guard let hlsURL = info.hlsURL else { return result }
        let present: Set<Int> = Set(result.map(\\.height))
        var highHeights: Set<Int> = []
        for f in info.formats where f.height > 1080 && f.mimeType.hasPrefix("video/") {
            if AppSettings.VideoQuality.from(height: f.height) != nil { highHeights.insert(f.height) }
        }
        var synthesized: [VideoFormat] = []
        for h in highHeights.sorted(by: >) where !present.contains(h) {
            let src: VideoFormat? = info.formats.first { $0.height == h && $0.mimeType.contains("vp09") }
                ?? info.formats.first { $0.height == h }
            synthesized.append(
                VideoFormat(
                    label: "\\(h)p HLS",
                    width: src?.width ?? (h * 16 / 9),
                    height: h,
                    fps: src?.fps ?? 30,
                    mimeType: "application/x-mpegURL",
                    url: hlsURL,
                    bitrate: src?.bitrate
                )
            )
        }
        if !synthesized.isEmpty {
            let higher: [VideoFormat] = result.filter { $0.height > 1080 }
            let lower: [VideoFormat] = result.filter { $0.height <= 1080 }
            var merged: [VideoFormat] = higher + synthesized
            merged.sort { $0.height > $1.height }
            result = merged + lower
        }
        return result
        #else
        return availableFormats
        #endif""",
    "4k-exp tvOS picker formats",
)

# On-screen debug text in the tvOS player while the experiment is active.
replace_once(
    PLAYER_LIFECYCLE,
    """                PlayerAVLayerView(player: vm.player, videoGravity: store.settings.videoGravityMode.avGravity)
                    .ignoresSafeArea()
                    .accessibilityHidden(true)
                if vm.isAudioOnlyMode {
                    audioOnlyThumbnailOverlay
                }
                #elseif os(macOS)""",
    """                PlayerAVLayerView(player: vm.player, videoGravity: store.settings.videoGravityMode.avGravity)
                    .ignoresSafeArea()
                    .accessibilityHidden(true)
                if vm.isAudioOnlyMode {
                    audioOnlyThumbnailOverlay
                }
                TVFourKDebugOverlay(player: vm.player, requestedMaxHeight: vm.effectiveQuality.maxHeight)
                #elseif os(macOS)""",
    "4k-exp tvOS debug overlay",
)

print("tvOS YouTube UI + Chinese titles + 4K quality routing + metadata locale patch complete")
