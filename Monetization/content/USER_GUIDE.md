# User Guide

## 1. Open the Monetization Hub

Open **Tools > Bcyly Labs > Bcyly Monetization > Monetization Hub**. The Hub creates or loads a MonetizationSettings asset, ensures provider containers exist and presents these tabs:

| Tab | Purpose |
| --- | --- |
| General & Pacing | Enabled formats, startup loads, cooldowns and rewarded watchdog settings |
| Dummy (Mock) | Simulator banner, timing and delayed reward controls |
| AdMob | SDK setup, app IDs, unit IDs and app-open configuration |
| AppLovin MAX | SDK setup, banner options and per-platform unit IDs |
| LevelPlay | SDK installation, app keys and per-platform unit IDs |
| Unity Ads | SDK installation, game IDs, placement IDs and test mode |
| Diagnostics | Configuration checks and setup hints |

Opening a network tab does not activate it. The **Active Monetization Provider** dropdown selects the runtime provider. An SDK Missing badge means the editor did not detect the expected dependency; filling IDs does not install an SDK.

### Settings asset selection

The default asset path is `Assets/bcylyLabs/Monetization/MonetizationSettings.asset`. The Hub and several build utilities choose the first asset returned by an editor type search. If you keep multiple settings assets, verify which one the Hub edits and which one your bootstrap references.

Runtime initialization requires an explicit settings asset. There is no automatic Core bootstrap that discovers the Hub asset. Assign it to your own startup component; a complete example appears in the developer chapter.

## 2. Configure formats and pacing

Use General & Pacing to choose the ad experience before selecting a live provider.

| Setting | Effect |
| --- | --- |
| Debug Mode | Stored configuration flag; most logging and SDK test behavior are not controlled by it in this version |
| Load Ads On Start | After successful initialization, requests enabled rewarded/interstitial ads and shows an enabled banner when allowed |
| Banner Enabled | Allows banner show through the manager |
| Interstitial Enabled | Allows interstitial requests through the show workflow |
| Rewarded Video Enabled | Allows rewarded requests/shows |
| App Open Enabled | Gates manager app-open API; AdMob's internal foreground path currently bypasses this gate |
| First Launch Delay | Initial interstitial cooldown after each initialization, not a persisted once-per-install delay |
| Interstitial Interval | Shared minimum interstitial pacing interval |
| Rewarded Shield Delay | Interstitial cooldown applied when a rewarded session resolves, including a false result |
| Show-to-Display Timeout | Resolves an unpresented rewarded session as false after the configured interval |
| Post-Close Grace Window | Waits briefly for out-of-order native reward callbacks after close |

The source defaults for first delay, interval and rewarded shield are 45, 30 and 45 seconds respectively. Those defaults are not universal UX recommendations. The screenshot uses short demonstration values so behavior is easy to test.

Do not interpret the Hub's “frequency capping” label as persisted per-user or per-placement impression caps. Core pacing uses one runtime timestamp; any level/session caps must be implemented in your game or mediation configuration.

With Load Ads On Start disabled, call RequestRewardedVideo when you need to preload rewarded. There is no public facade RequestInterstitial method: calling ShowInterstitial while not ready returns false and requests one for a later attempt.

## 3. Use the Dummy simulator

Choose **Dummy** in the active-provider dropdown and open **Dummy (Mock)**. No native ad SDK or network credentials are required.

| Control | Purpose |
| --- | --- |
| Banner Position / Height | Controls the mock banner and reported layout height |
| Interstitial Countdown | Delay before the mock interstitial can be closed |
| Rewarded Duration | Mock rewarded progress timing |
| Simulate Late Reward | Exposes a delayed-reward outcome in the mock UI |

Enter Play Mode with an initialized manager, then call the runtime APIs from your controls or use the supplied demo scene. Show an interstitial, complete a rewarded ad and close one early. When late simulation is enabled, select the late-reward outcome and inspect both the initial callback and late-reward event.

Dummy creates an interactive Canvas simulator. It does not prove real SDK installation, fill rates, native threading, privacy forms or build compatibility. Its consent provider is currently registered after the initial consent gather, so Dummy privacy behavior is not evidence that native consent startup is correct.

## 4. Configure Google AdMob

Open the AdMob tab. The Hub offers a Google Mobile Ads Unity package download/import, official sample IDs and an action to synchronize app IDs into Google Mobile Ads settings.

1. Import a supported Google Mobile Ads SDK and its required native dependencies.
2. Use sample ad units or properly configured test devices while developing.
3. Set Android and iOS **App IDs** separately; these identify the application and use the `~` separator.
4. Set per-platform banner, interstitial and rewarded **Ad Unit IDs**, which use the `/` separator.
5. Synchronize app IDs to the SDK's settings asset and inspect the generated native configuration.
6. Configure consent before native initialization and test it on devices.
7. Select AdMob as active only when the adapter compiles and its requirements are satisfied.

### App-open controls

The AdMob container has its own **Use App Open Ad** setting in addition to the global format flag. App-open units and expiration duration are available when configured.

The current internal foreground handler can bypass the global flag and your own resume policy. It also lacks complete close/failure/reload handling. Correct those lifecycle paths and choose one owner for resume policy before using app-open in a live build.

### Under-age tag and test configuration

The under-age field is forwarded by AdMobUMPProvider when that provider is actually created and registered. It does not wire consent automatically or replace your audience configuration. Debug Mode does not put AdMob into test traffic mode; sample IDs/test-device configuration do that.

The included installer points to a specific SDK release rather than guaranteeing compatibility with every newer release. Validate the chosen SDK version instead of treating the installed badge as an API compatibility check.

## 5. Configure AppLovin MAX

Use the MAX tab to import the SDK and enter real ad unit IDs separately for Android and iOS. Values such as `banner`, `interstitial` and `rewarded` in the screenshot are placeholders.

Complete SDK account/application setup, initialization requirements and any mediated network setup using MAX's own integration tools. This package's container only supplies its exposed unit IDs/options; it is not a full mediation dashboard or SDK-key manager.

The current handler always creates its banner at BottomCenter, and Use Adaptive Banner is stored but unused. Do not assume choosing a different position or enabling that option changes native rendering until the handler is updated and tested.

Interstitial callbacks currently report dispatch rather than close. Follow the lifecycle notes in the developer chapter before using completion callbacks to resume a game flow.

## 6. Configure Unity LevelPlay

The LevelPlay tab offers installation through Package Manager. Configure Android/iOS app keys and the banner, interstitial and rewarded unit IDs corresponding to the correct application.

The adapter targets the modern Unity.Services.LevelPlay API. Detecting an old IronSource folder does not establish compatibility with this API.

The current source also has a LevelPlay namespace collision: static SDK calls must use an explicit alias or fully qualified SDK class. Fix that conditional compile blocker before activating the provider, then compile against a deliberate SDK version and validate native callbacks.

App-open is not implemented by this adapter. Empty keys/unit fields in the screenshot are configuration examples, not a functioning network setup.

## 7. Configure Unity Ads

The Unity Ads tab installs `com.unity.ads` through Package Manager. Enter the Android and iOS game IDs and the placements corresponding to your dashboard.

Test Mode is passed to the Unity Ads initialization API. Banner/interstitial/rewarded placement fields are shared across the container; they are not separate Android/iOS pairs. Select the values appropriate to your target or maintain a deliberate per-platform configuration workflow.

Unity Ads implements banners, interstitials and rewarded video here. App-open queries return false and show calls do nothing. Avoid configuring identical interstitial/rewarded placement IDs: callback routing distinguishes these by the configured IDs.

## 8. Add a bootstrap and game controls

Create a component that references MonetizationSettings and calls `await MonetizationManager.InitializeAsync(settings)` once. Keep a single startup owner and observe the result before requesting ads.

Use `ShowBanner`, `HideBanner` and `DestroyBanner` for banner controls. Use `CanShowInterstitial` before a natural transition, and `IsRewardedVideoLoaded` before showing an optional reward offer. A false result must leave the player able to continue without assuming an ad was watched.

Do not add gameplay rewards to both the completion callback and a second general ad-closed listener. A closed ad is not proof that a reward was earned. See the runnable scripting examples in [Developer Reference](#developer).

## 9. Configure no-ads and safe area

`SetNoAds(true)` enables permanent no-ads. `SetTimedNoAds(seconds)` enables a temporary period. Both preserve voluntary rewarded availability while suppressing banners, interstitials and app-open through the manager.

`SetNoAds(false)` and `DisableNoAds()` clear both permanent and timed access. A timed grant extends to the later of the existing expiry and now plus duration; it does not add the duration to the old expiry.

When no-ads becomes active, the package destroys the visible banner and resets its layout state. Expiration currently changes the getter result without emitting an automatic expiry event or restoring the banner. Your integration must account for this limitation.

SafeAreaAdapter exposes banner height, position, a change event and an adjusted screen Rect. It does not automatically attach a layout component to your Canvas. Native height units and some position options currently need correction; test real high-DPI devices before relying on banner avoidance.

## 10. Privacy controls and diagnostics

Add PrivacyOptionsButton to a Unity UI Button or call `ShowPrivacyOptions` from your own settings UI. The component disables itself while the form request runs and re-enables on callback. It does not perform consent registration or automatically reflect whether the network requires an entry point.

Native UMP/ATT classes exist but are not registered by normal package startup, and the manager ignores the gather result. Wire and enforce the intended eligibility flow before live SDK requests. An editor fallback success is only a simulation.

Use Diagnostics for SDK/configuration hints. Green checks do not establish correct consent, current platform submission requirements, successful native output or working rewards. Follow [Testing and Troubleshooting](#testing) before release.

## 11. Manage SDKs carefully

The Hub can install/import and remove supported dependencies. Back up your project and check dependency ownership before removing an SDK: the current uninstaller can delete resolver folders shared by other plugins.

UPM removal paths for Unity Ads and LevelPlay can leave the active provider pointing at the removed SDK. After a removal, explicitly recheck the active setting, symbols, assembly references and Console. Do not rely on “zero compile errors” messaging as verification.
