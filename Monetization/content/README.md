# bcylyLabs Monetization Documentation

Package manual · Version 1.0.0 · Reviewed 30 October 2026.

Configure advertising from one Hub, integrate a provider-neutral runtime API and test the player experience with an interactive simulator. This manual covers the package itself and can be used with any Unity game.

## Documentation map

| Chapter | What you will learn |
| --- | --- |
| [User Guide](#user-guide) | Hub setup, provider configuration, ad formats, pacing, simulator and privacy controls |
| [Developer Reference](#developer) | Initialization, runtime APIs, events, rewards, no-ads, consent and custom adapters |
| [Testing and Troubleshooting](#testing) | Reproducible scenarios, build checks, error diagnosis and implementation limitations |

## Quick start

1. Open **Tools > Bcyly Labs > Bcyly Monetization > Monetization Hub**.
2. Keep **Dummy** selected while building and testing your game integration.
3. Configure enabled formats and pacing under **General & Pacing**.
4. Configure the simulator under **Dummy (Mock)**.
5. Assign the MonetizationSettings asset to your bootstrap and initialize the manager once.
6. Use the public API to show a banner, request an interstitial or offer a rewarded ad.
7. Verify outcomes and no-ads behavior before integrating a native network SDK.

## Package structure

| Area | Responsibility |
| --- | --- |
| Core | Settings, facade, provider contracts, consent, no-ads, session tracking and common utilities |
| Adapters | Dummy, AdMob, AppLovin MAX, LevelPlay and Unity Ads implementations |
| Hub | Network setup, SDK installers, requirement checks and diagnostics |
| Demo | Example runtime controls and interactive simulator usage |

Only one provider is active at a time. Multiple available adapters do not constitute an internal waterfall or automatic network fallback. Mediation is supplied by the selected third-party SDK where configured.

## Provider and format support

| Provider | Banner | Interstitial | Rewarded | App open |
| --- | --- | --- | --- | --- |
| Dummy | Simulated | Simulated | Simulated | Simulated |
| AdMob | Implemented | Implemented; lifecycle fixes needed | Implemented; shared session caveats | Partial lifecycle; fixes needed |
| AppLovin MAX | Implemented; position/adaptive limitations | Implemented; callback caveats | Implemented; shared session caveats | Not implemented |
| LevelPlay | Implemented in source | Implemented in source | Implemented in source | Not implemented |
| Unity Ads | Implemented | Implemented | Implemented; shared session caveats | Not implemented |

LevelPlay currently has a conditional namespace/class collision that must be corrected before enabling its SDK adapter. “Implemented” describes source coverage, not certification or successful device testing.

## Scope and compatibility

The source was reviewed in Unity 6000.3.6f1. The package README declares Unity 2021.3 LTS or higher, but that broad compatibility range has not been verified here. Native SDK versions have their own requirements and must be compiled/tested explicitly.

Screenshots show the supplied editor tools and sample configuration. The pictured 2-second pacing values, missing-SDK badges, placeholder IDs and test IDs are examples, not a recommended live configuration.

This documentation describes existing behavior. Important consent, session attribution and native lifecycle gaps are explained where relevant and collected in the testing chapter. They are not fixed by creating this manual.
