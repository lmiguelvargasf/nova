import Foundation

struct User: Codable, Hashable, Identifiable, Sendable {
    let id: Int
    let email: String
    let firstName: String
    let lastName: String
}
