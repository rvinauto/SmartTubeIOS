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
                .fill(Color.white.opacity(0.08))
                .frame(width: 1)
                .ignoresSafeArea()

            NavigationStack {
                selectedSection.destination(api: api)
                    .id(selectedSection)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
        .background(Color.black.ignoresSafeArea())
        .environment(searchVM)
        .animation(.easeInOut(duration: 0.18), value: sidebarExpanded)
    }

    private var sidebar: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack(spacing: 12) {
                Image(systemName: "play.rectangle.fill")
                    .font(.system(size: 30, weight: .semibold))
                    .foregroundStyle(.red)

                if sidebarExpanded {
                    Text("SmartTube")
                        .font(.title3.weight(.semibold))
                        .lineLimit(1)
                        .transition(.opacity.combined(with: .move(edge: .leading)))
                }
            }
            .frame(height: 58, alignment: .leading)
            .padding(.horizontal, 18)

            ForEach(AppSection.allCases) { section in
                sidebarButton(section)
            }

            Spacer(minLength: 0)
        }
        .padding(.top, 28)
        .padding(.bottom, 28)
        .frame(width: sidebarExpanded ? 300 : 104, alignment: .leading)
        .background(Color.black.opacity(0.98))
        .focusSection()
        .accessibilityIdentifier("tv.sidebar")
    }

    private func sidebarButton(_ section: AppSection) -> some View {
        let isSelected = selectedSection == section
        let isFocused = focusedSection == section

        return Button {
            selectedSection = section
        } label: {
            HStack(spacing: 18) {
                Image(systemName: section.icon)
                    .font(.system(size: 26, weight: .semibold))
                    .frame(width: 40, height: 40)

                if sidebarExpanded {
                    Text(section.localizedTitle)
                        .font(.headline)
                        .lineLimit(1)
                        .transition(.opacity.combined(with: .move(edge: .leading)))
                }
            }
            .foregroundStyle(isSelected || isFocused ? Color.white : Color.white.opacity(0.70))
            .padding(.horizontal, 16)
            .frame(width: sidebarExpanded ? 276 : 80, height: 64, alignment: .leading)
            .background(
                RoundedRectangle(cornerRadius: 14, style: .continuous)
                    .fill(isSelected || isFocused ? Color.white.opacity(0.14) : Color.clear)
            )
            .overlay(alignment: .leading) {
                if isSelected {
                    Capsule()
                        .fill(Color.red)
                        .frame(width: 5, height: 34)
                        .padding(.leading, 2)
                }
            }
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .focusEffectDisabled()
        .scaleEffect(isFocused ? 1.04 : 1.0, anchor: .leading)
        .animation(.easeInOut(duration: 0.12), value: isFocused)
        .focused($focusedSection, equals: section)
        .accessibilityLabel(section.localizedTitle)
        .accessibilityAddTraits(isSelected ? [.isSelected] : [])
        .accessibilityIdentifier("tv.sidebar.\(section.rawValue.lowercased())")
    }
}
#endif
