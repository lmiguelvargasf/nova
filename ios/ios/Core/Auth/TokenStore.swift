import Foundation

protocol TokenStore {
    func readToken() throws -> String?
    func saveToken(_ token: String) throws
    func clearToken() throws
}
