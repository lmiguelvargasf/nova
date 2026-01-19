import SwiftUI

struct SessionRootView: View {
    @Environment(SessionStore.self) private var sessionStore
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            switch sessionStore.status {
            case .checking:
                LoadingView()
            case .unauthenticated:
                LoginView(sessionStore: sessionStore)
            case .authenticated(let user):
                UserHomeView(user: user) {
                    sessionStore.logout()
                }
            case .error(let message):
                SessionErrorView(message: message) {
                    Task {
                        await sessionStore.restoreSession()
                    }
                }
            }
        }
        .navigationDestination(for: SessionRoute.self) { route in
            switch route {
            case .profile(let user):
                UserProfileView(user: user)
            }
        }
    }
}

#Preview {
    let store = SessionStore(apiClient: .live(), tokenStore: InMemoryTokenStore())
    store.status = .unauthenticated
    return SessionRootView()
        .environment(store)
}
