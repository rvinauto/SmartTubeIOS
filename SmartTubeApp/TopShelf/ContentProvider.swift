import Foundation
import TVServices

/// Minimal Top Shelf provider for the sideloaded tvOS build.
///
/// Phase 1 deliberately uses static public thumbnails. This proves that the nested
/// Top Shelf extension can be built, packaged, re-signed by ATVLoadly/plumesign,
/// installed, and rendered by tvOS before wiring in SmartTube's real feed data.
final class ContentProvider: TVTopShelfContentProvider {
    override func loadTopShelfContent(
        completionHandler: @escaping (TVTopShelfContent?) -> Void
    ) {
        let cards: [(id: String, title: String, videoID: String)] = [
            ("topshelf-ready", "SmartTube Top Shelf 已启用", "M7lc1UVf-VE"),
            ("featured-one", "推荐视频", "aqz-KE-bpKQ"),
            ("featured-two", "SmartTube", "jNQXAC9IVRw"),
        ]

        let items: [TVTopShelfSectionedItem] = cards.compactMap { card in
            guard let imageURL = URL(
                string: "https://i.ytimg.com/vi/\(card.videoID)/hqdefault.jpg"
            ) else {
                return nil
            }

            let item = TVTopShelfSectionedItem(identifier: card.id)
            item.title = card.title
            item.imageShape = .hdtv
            item.setImageURL(imageURL, for: .screenScale1x)
            item.setImageURL(imageURL, for: .screenScale2x)
            return item
        }

        guard !items.isEmpty else {
            completionHandler(nil)
            return
        }

        let section = TVTopShelfItemCollection(items: items)
        section.title = "SmartTube"
        completionHandler(TVTopShelfSectionedContent(sections: [section]))
    }
}
