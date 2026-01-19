import Foundation

struct APIConfiguration: Sendable {
    let baseURL: URL

    static func load(bundle: Bundle = .main) -> APIConfiguration {
        let rawValue = bundle.object(forInfoDictionaryKey: "API_BASE_URL") as? String
        let configuredURL = URL(string: rawValue ?? "")
        let fallbackURL = URL(string: "http://localhost:8000")
        let resolvedURL = configuredURL ?? fallbackURL ?? URL(fileURLWithPath: "/")
        return APIConfiguration(baseURL: resolvedURL)
    }
}
