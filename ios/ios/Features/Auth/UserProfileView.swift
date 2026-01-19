import SwiftUI

struct UserProfileView: View {
    let user: User

    var body: some View {
        List {
            Section("Profile") {
                ProfileRow(label: "First name", value: user.firstName)
                ProfileRow(label: "Last name", value: user.lastName)
                ProfileRow(label: "Email", value: user.email)
            }
        }
        .navigationTitle("Profile")
    }
}
