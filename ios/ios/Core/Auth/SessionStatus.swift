import Foundation

enum SessionStatus: Hashable {
    case checking
    case unauthenticated
    case authenticated(User)
    case error(String)
}
