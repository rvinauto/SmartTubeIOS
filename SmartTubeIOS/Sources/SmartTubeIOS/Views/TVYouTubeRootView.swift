import SmartTubeIOSCore
import SwiftUI

#if os(tvOS)
/// tvOS-only shell that keeps SmartTube's existing screens and playback stack,
/// while presenting them with a YouTube TV-inspired left navigation rail.
struct TVYouTubeRootView: View {
    @Environment(\.innerTubeAPI) private var api
    @State private var selectedSection: AppSection = .home
    @State private var searchVM = SearchViewModel()
    @FocusState private var focusedSection: AppSection?

    private var sidebarExpanded: Bool { focusedSection != nil }

    var body: some View {
        HStack(spacing: 0) {
            sidebar

            Rectangle()
                .fill(Color.white.opacity(0.055))
                .frame(width: 1)
                .ignoresSafeArea()

            NavigationStack {
                selectedContent
                    .id(selectedSection)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
        .background(Color.black.ignoresSafeArea())
        .environment(searchVM)
        .animation(.easeInOut(duration: 0.16), value: sidebarExpanded)
    }

    @ViewBuilder
    private var selectedContent: some View {
        switch selectedSection {
        case .home:
            HomeView(api: api)
        case .search:
            SearchView()
        case .library:
            LibraryView()
        case .settings:
            SettingsView()
                // Settings is a root screen in the custom shell. Without handling
                // Menu/Back here, tvOS treats it as an app-level exit.
                .onExitCommand {
                    selectedSection = .home
                    focusedSection = .home
                }
        }
    }

    private var sidebar: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 10) {
                Image(systemName: "play.rectangle.fill")
                    .font(.system(size: 25, weight: .semibold))
                    .foregroundStyle(.red)
                    .frame(width: 34)

                if sidebarExpanded {
                    Text("SmartTube")
                        .font(.headline.weight(.semibold))
                        .lineLimit(1)
                        .minimumScaleFactor(0.82)
                        .transition(.opacity)
                }
            }
            .frame(height: 48, alignment: .leading)
            .padding(.horizontal, 14)

            ForEach(AppSection.allCases) { section in
                sidebarButton(section)
            }

            Spacer(minLength: 0)
        }
        .padding(.top, 22)
        .padding(.bottom, 22)
        .frame(width: sidebarExpanded ? 228 : 76, alignment: .leading)
        .background(Color.black.opacity(0.985))
        .focusSection()
        .accessibilityIdentifier("tv.sidebar")
    }

    private func sidebarButton(_ section: AppSection) -> some View {
        let isSelected = selectedSection == section
        let isFocused = focusedSection == section
        let title = sidebarTitle(section)

        return Button {
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
        .accessibilityIdentifier("tv.sidebar.\(section.rawValue.lowercased())")
    }

    /// The Swift package catalogue is not always selected by the host tvOS app for
    /// root navigation labels. Keep a deterministic Chinese fallback for this shell.
    private func sidebarTitle(_ section: AppSection) -> String {
        guard Locale.preferredLanguages.first?.lowercased().hasPrefix("zh") == true else {
            return section.localizedTitle
        }
        switch section {
        case .home: return "首页"
        case .search: return "搜索"
        case .library: return "资料库"
        case .settings: return "设置"
        }
    }
}
#endif
