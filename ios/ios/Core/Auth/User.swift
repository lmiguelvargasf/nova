import Foundation

struct User: Codable, Hashable, Identifiable {
    let id: Int
    let email: String
    let firstName: String
    let lastName: String
}
