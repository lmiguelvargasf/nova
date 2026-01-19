import Foundation

struct LoginRequest: Codable, Sendable {
    let email: String
    let password: String
}
