import Foundation

struct LoginResponse: Codable, Sendable {
    let token: String
    let user: User
    let reactivated: Bool
}
