import Foundation

struct APIConfiguration: Sendable {
    let baseURL: URL
    private static let defaultBaseURL = URL(string: "http://localhost:8000")!

    static func load(bundle: Bundle = .main) -> APIConfiguration {
        let rawValue = bundle.object(forInfoDictionaryKey: "API_BASE_URL") as? String
        let configuredURL = URL(string: rawValue ?? "")
        let resolvedURL = configuredURL ?? defaultBaseURL
        return APIConfiguration(baseURL: resolvedURL)
    }
}
