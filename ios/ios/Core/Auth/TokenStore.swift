import Foundation

protocol TokenStore: Sendable {
    func readToken() throws -> String?
    func saveToken(_ token: String) throws
    func clearToken() throws
}
