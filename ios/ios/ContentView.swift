//
//  ContentView.swift
//  ios
//
//  Created by M on 1/19/26.
//

import Observation
import SwiftUI

struct ContentView: View {
    @Bindable var sessionStore: SessionStore

    var body: some View {
        SessionRootView(sessionStore: sessionStore)
    }
}

#Preview {
    let store = SessionStore(apiClient: .live(), tokenStore: InMemoryTokenStore())
    store.status = .unauthenticated
    return ContentView(sessionStore: store)
}
