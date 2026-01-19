import SwiftUI

struct SessionErrorView: View {
    let message: String
    let retry: () -> Void

    var body: some View {
        VStack(spacing: 20) {
            VStack(spacing: 8) {
                Text("Nova 🌟")
                    .font(.largeTitle)
                    .bold()
                Text("We hit a snag")
                    .foregroundStyle(.secondary)
            }

            VStack(spacing: 12) {
                Image(systemName: "exclamationmark.triangle.fill")
                    .imageScale(.large)
                    .foregroundStyle(.orange)
                Text(message)
                    .multilineTextAlignment(.center)
                    .foregroundStyle(.secondary)
            }
            .padding(20)
            .background(.thinMaterial)
            .clipShape(.rect(cornerRadius: 20))

            Button("Try Again", action: retry)
                .buttonStyle(.borderedProminent)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .padding(24)
    }
}

#Preview {
    SessionErrorView(message: "We couldn’t restore your session.") { }
}
