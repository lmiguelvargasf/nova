import SwiftUI

struct UserHomeView: View {
    let user: User
    let onLogout: () -> Void

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                VStack(alignment: .leading, spacing: 6) {
                    Text("Nova 🌟")
                        .font(.largeTitle)
                        .bold()
                    Text("Hello, \(user.firstName)")
                        .font(.title2)
                        .bold()
                    Text(user.email)
                        .foregroundStyle(.secondary)
                }
                .frame(maxWidth: .infinity, alignment: .leading)

                VStack(spacing: 12) {
                    Button("Log Out", action: onLogout)
                        .foregroundStyle(.red)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 10)
                        .background(.thinMaterial)
                        .clipShape(.rect(cornerRadius: 18))
                }
            }
            .padding(24)
        }
        .scrollIndicators(.hidden)
        .navigationTitle("")
        .navigationBarTitleDisplayMode(.inline)
    }
}
