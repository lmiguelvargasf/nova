import SwiftUI

struct UserHomeView: View {
    let user: User
    let onLogout: () -> Void

    var body: some View {
        List {
            Section {
                VStack(alignment: .leading, spacing: 6) {
                    Text("Hello, \(user.firstName)")
                        .font(.title2)
                        .bold()
                    Text(user.email)
                        .foregroundStyle(.secondary)
                }
                .padding(.vertical, 4)
            }

            Section {
                Button("Log Out", action: onLogout)
                    .foregroundStyle(.red)
            }
        }
        .navigationTitle("Nova")
    }
}
