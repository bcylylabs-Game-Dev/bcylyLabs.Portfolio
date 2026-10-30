# Testing & Troubleshooting

## 1. Verification levels

| Environment | What it establishes |
| --- | --- |
| Dummy in Play Mode | Game controls, simulated outcomes and integration behavior |
| Deterministic tracker tests | Specific event-order and callback-state behavior |
| Vendor SDK compile | Adapter API compatibility with the chosen SDK version |
| Native test ads on device | Real callback timing, format rendering, privacy flow and platform lifecycle |
| Release/IL2CPP build | Actual selected configuration and linker preservation |

This manual describes source behavior and known issues; it does not certify native ad delivery. No dedicated discoverable NUnit/UnityTest suite was found in the package. The demo and diagnostics are development tools, not a substitute for regression tests.

## 2. Simulator walkthrough

1. Select Dummy and verify your bootstrap references the intended settings asset.
2. Enable the formats needed for your test and initialize once in Play Mode.
3. Show/hide/destroy a banner and verify layout changes.
4. Attempt an interstitial before the initial cooldown; it should be suppressed.
5. Show one after the delay, close it and verify pacing before the next attempt.
6. Complete a rewarded ad and verify exactly the offered reward is delivered once.
7. Close a rewarded ad early and verify no earned reward is granted.
8. Enable late-reward simulation; inspect the initial false callback followed by the late event.
9. Activate permanent/timed no-ads and verify non-rewarded suppression.
10. Restart the application session and verify expected no-ads persistence.

The late-reward path currently needs fixes for duplicate notification and session attribution. A functioning mock button demonstrates the event path, not once-only reward correctness.

## 3. Regression test matrix

| Scenario | Required result / current caveat |
| --- | --- |
| Repeated rewarded taps | One unresolved operation; current Closed grace state allows overwrite |
| Reward before close | One earned completion |
| Close then reward within grace | One earned completion for that original session |
| Reward after grace | One compensation for the original offer |
| Duplicate delayed reward | No duplicate compensation; current tracker emits repeatedly |
| Old reward after a new offer | Must not credit the new offer; identity is missing today |
| Different provider callback | Ignore mismatched origin; current tracker accepts it |
| Native show failure | One failure result; no permanently blocked gameplay |
| Interstitial request accepted then native failure | Do not report definitive successful completion at dispatch |
| Interstitial closes | Reload next object after lifecycle completion |
| No native close callback | Explicit recovery policy rather than an indefinitely stuck session |
| Concurrent initialization | One shared operation/provider; current manager lacks this guard |
| Load button spam | One load per format; ignore stale responses |
| No-ads activates during banner load | No late banner reappearance or null callback access |
| Timed no-ads expires | Correct state/UI transition; event restoration needs implementation |
| App-open global flag disabled | No resume ad, including internal native handler |
| Resume after rewarded/interstitial | No app-open overlay on an active fullscreen ad |
| App-open consumed/expired | Replacement can load; current handler does not replenish |
| Privacy update disallows requests | No premature initialization/request |
| Privacy options change | Eligibility and presentation state refresh appropriately |
| IL2CPP stripping | Selected reflection-created adapter survives and initializes |

Use fake providers for deterministic state assertions, then real test ads for SDK-specific behavior. Do not infer native callback threading/order solely from Dummy.

## 4. Diagnostics and build preparation

The Diagnostics tab checks detected SDKs, selected credentials, platform settings, script defines and presence of build helpers. Treat results as hints and inspect the actual build target.

Current limitations include Android-biased ID checks, SDK detection by folder/manifest heuristics and target-API passing messages without a required-version comparison. A postprocessor file existing does not prove its generated output is correct.

Before release:

1. Resolve consent, reward attribution, callback and app-open issues that affect the formats you will ship.
2. Pin a deliberately tested SDK version and compile each intended adapter.
3. Fix the LevelPlay namespace collision before enabling its define.
4. Confirm the runtime asset matches the one edited by the Hub/build tools.
5. Confirm live app/unit/game IDs for the correct platform; configure test traffic on development devices.
6. Check generated Android/iOS configuration and native dependency resolution.
7. Run stripping-enabled Android/iOS device tests and repeated foreground/background cycles.
8. Verify reward persistence/compensation and no-ads restoration in your own game.
9. Verify your build process rejects unintended Dummy/placeholder configuration.

The supplied release validator only warns for Dummy in batch mode. Interactive warnings can be suppressed through EditorPrefs. It does not provide a fail-closed production gate.

## 5. Native network checks

| Network | Additional checks |
| --- | --- |
| AdMob | Actual app ID synchronization, registered UMP, CanRequestAds eligibility, test ads, close/failure reload and real banner pixel height |
| MAX | SDK application setup, valid unit IDs, event ad-unit filtering, consistent callback semantics and banner options |
| LevelPlay | SDK alias/namespace fix, modern API compatibility, valid platform app key/units and fullscreen/load sequencing |
| Unity Ads | Correct platform game ID, test mode, correct placement IDs and completion/failure callbacks |

Consult current vendor documentation for dashboard/account/platform requirements. The package's installers select particular releases or unpinned UPM dependencies; they do not establish a maintained compatibility matrix.

## 6. Troubleshooting reference

| Symptom | Likely cause | What to inspect |
| --- | --- | --- |
| No ads on a device | Dummy active, initialization failure, no fill or missing native setup | ActiveProviderName, bootstrap result, SDK logs and target configuration |
| Hub shows SDK Missing | Expected dependency not detected | Actual imported SDK, package manifest, assembly references and symbols |
| Hub edits have no effect | Different settings asset used at runtime | Bootstrap reference versus first asset selected by Hub |
| Nothing initializes automatically | No Core auto-bootstrap | Add one initialization owner and assign settings |
| Reflection handler cannot be created | Missing define/assembly/type/constructor, or stripping | HandlerTypeName, Console and linker preservation |
| LevelPlay CS0234 | Package namespace shadows SDK class | Use explicit SDK type alias/qualification |
| SDK setup looks green but native build fails | Folder detection is not API/version verification | Compile against chosen SDK and inspect native dependencies |
| AdMob app ID error | App ID absent or not synchronized to SDK settings | App IDs versus ad unit IDs and native generated output |
| Consent screen never appears | Native consent providers not registered before gather | Bootstrap/provider registration and eligibility gating |
| Ads proceed after denied gather | Manager ignores gather result | Implement request eligibility gate |
| Privacy button does not open UMP | First provider is not form-capable or no native provider | Consent registration order and requirement status |
| First rewarded attempt returns false | Not initialized/enabled/loaded | Explicit RequestRewardedVideo and readiness |
| Rewarded callback never returns | Overwritten grace session or missing native close | Session IDs/state and native event sequence |
| Wrong/duplicate delayed reward | No origin identity or late deduplication | Retained offer context and once-only compensation |
| Interstitial callback occurs immediately | Adapter dispatch-success semantics | Native close/failure lifecycle rather than callback as a close barrier |
| AdMob ad destroyed near show | Immediate callback triggers preload/destroy | Manager/provider completion ordering |
| App-open ignores resume rules | Adapter-level foreground subscription bypasses game flow | Single foreground policy owner and global guards |
| App-open only works once | No next-ad reload/expiry refresh | Fullscreen close/failure and load lifecycle |
| Banner appears at bottom despite top selection | Adapter ignores/maps position | Native handler position mapping |
| Safe area is too small/invalid | Mixed pixels/density units or zero DPI | Native pixel height, finite checks and canvas conversion |
| Expired no-ads UI remains unchanged | No automatic expiration event | Add explicit expiry transition handling |
| Timed grant does not stack | Uses max(old expiry, now + duration) | Intended entitlement extension semantics |
| SDK removal breaks another plugin | Shared resolver tooling removed | Restore dependency manager and adopt ownership-aware uninstall |
| Removed network remains active | UPM removal skips settings reset | Select Dummy and verify symbols/references |
| Strange keys in generated Info.plist | Global string replacement inserts into nested dicts | Structured root-dictionary edit |

## 7. Known implementation boundaries

- Consent classes and UI exist, but normal native startup does not register/enforce them.
- Rewarded callback attribution and late-event deduplication have reproduced failures.
- Interstitial completion semantics differ across adapters; AdMob reload happens prematurely.
- App-open is partial for AdMob and absent for MAX/LevelPlay/Unity Ads.
- Initialization, provider disposal, static reset and per-format request cancellation are incomplete.
- No durable reward ledger, authenticated SSV, internal network waterfall or automatic fallback exists.
- No-ads is local PlayerPrefs state and timed access uses the device wall clock.
- Several banner options, height units and expiry notifications need corrections.
- SDK installation/removal and green diagnostic messages are not proof of a release-ready build.

These boundaries should guide testing and implementation planning. They are not additional hidden setup switches that can be enabled in the Hub.

## 8. Useful support evidence

Record Unity version, SDK/plugin version, target device/OS, build configuration, active provider, enabled formats, ad unit/placement, result, event order and reproduction steps. For rewarded issues, retain the offer context and session/token details where available.

Include whether the failure occurred with Dummy or real test ads. Share relevant logs without private account credentials. A screenshot of the Hub helps diagnose configuration, but event logs and native build output are necessary for lifecycle issues.
