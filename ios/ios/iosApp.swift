//
//  iosApp.swift
//  ios
//
//  Created by M on 1/19/26.
//

import SwiftUI

@main
struct NovaApp: App {
    @State private var sessionStore = SessionStore()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(sessionStore)
                .task {
                    await sessionStore.restoreSession()
                }
        }
    }
}
