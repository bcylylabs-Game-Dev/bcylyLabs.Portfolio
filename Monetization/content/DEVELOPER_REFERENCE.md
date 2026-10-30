# Developer Reference & API Examples

Runtime namespace: `bcylyLabs.Monetization`. The examples below use the shipped public facade. Example components are separate scripts; adjust their filenames to match their class names.

## 1. Architecture and startup

```text
Game bootstrap / UI
    -> MonetizationManager
       -> MonetizationSettings + selected ProviderContainer
       -> IAdProviderHandler
          -> Dummy / AdMob / MAX / LevelPlay / Unity Ads
       -> RewardedSessionTracker + watchdog
       -> NoAdsManager / ConsentManager / SafeAreaAdapter
       -> MainThreadDispatcher
```

InitializeAsync sets up common utilities, constructs the selected handler, gathers registered consent, initializes the provider and optionally loads initial ads. The current implementation does not enforce the consent result; that integration needs correction before live requests.

There is no shared in-flight initialization task, shutdown API or complete static reset. Use one startup owner; avoid concurrent initialization or runtime network switching. If the selected adapter is unavailable, initialization returns false rather than automatically selecting another network. Native initialization exceptions can propagate to the caller.

### Bootstrap example

This component initializes the package once from an Inspector reference. It does not implement the missing native consent integration.

```csharp
using System;
using UnityEngine;
using bcylyLabs.Monetization;

public sealed class MonetizationBootstrap : MonoBehaviour
{
    [SerializeField] private MonetizationSettings settings;

    private async void Start()
    {
        if (settings == null)
        {
            Debug.LogError("Assign MonetizationSettings in the Inspector.");
            return;
        }

        if (MonetizationManager.IsInitialized) return;

        try
        {
            bool ready = await MonetizationManager.InitializeAsync(settings);
            Debug.Log(ready
                ? "Ads ready: " + MonetizationManager.ActiveProviderName
                : "Ad initialization failed.");
        }
        catch (Exception error)
        {
            Debug.LogException(error);
        }
    }
}
```

Attach one instance to your startup scene and assign settings. The IsInitialized check avoids a completed duplicate initialization, but does not guard two callers starting at the same time. Centralize that ownership in your application.

## 2. Public API reference

| Member | Contract |
| --- | --- |
| IsInitialized | Manager and active handler report initialized |
| Settings | Current settings reference; may be null before startup |
| ActiveProviderName | Handler name or None |
| InitializeAsync(settings) | Task of bool; explicit startup |
| ShowBanner() | Shows/creates banner if enabled and no-ads permits it |
| HideBanner() | Hides banner and resets reported banner layout |
| DestroyBanner() | Destroys banner and resets reported banner layout |
| CanShowInterstitial() | Checks initialization, enable flag, no-ads, pacing and provider readiness |
| ShowInterstitial(callback, placement, ignorePacing) | Requests interstitial show; false when blocked/not ready |
| ShowInterstitialAsync(placement, ignorePacing) | Task wrapper for the same callback semantics |
| ResetInterstitialCooldown(seconds) | Replaces the shared next-allowed timestamp |
| IsRewardedVideoLoaded() | Checks rewarded enable/readiness |
| RequestRewardedVideo() | Explicit preload request when initialized/enabled |
| ShowRewardedVideo(callback, placement) | Starts rewarded session; bool reports earned outcome |
| ShowRewardedVideoAsync(placement) | Task wrapper for rewarded callback |
| IsAppOpenLoaded() | Checks manager gates and provider readiness |
| ShowAppOpenAd() | Requests provider app-open presentation |
| IsNoAdsActive | Permanent/timed state query |
| SetNoAds(active) | Enables permanent state, or clears all no-ads when false |
| SetTimedNoAds(durationSeconds) | Extends expiry to at least now plus duration |
| DisableNoAds() | Clears permanent and timed state |
| ShowPrivacyOptions(onClosed) | Routes privacy-form request to the first registered consent provider |

There is no public RequestInterstitial facade method, cancellation token overload, global fullscreen-busy property or built-in reward wallet. Provider interfaces expose lower-level requests, but bypassing the facade also bypasses its policies.

## 3. Interstitial integration

Place interstitials at deliberate transitions in your own game. A readiness query is a snapshot and is not a reservation.

```csharp
using UnityEngine;
using bcylyLabs.Monetization;

public sealed class InterstitialExample : MonoBehaviour
{
    public void TryShowAtTransition()
    {
        if (!MonetizationManager.IsInitialized) return;

        MonetizationManager.ShowInterstitial(accepted =>
        {
            Debug.Log("Interstitial result: " + accepted);
        }, "level_transition");
    }
}
```

The callback meaning is currently provider-dependent: AdMob/MAX/LevelPlay invoke success after dispatch, while Unity Ads/Dummy generally invoke it after completion. Do not treat true as a universal “ad has closed” barrier. AdMob's current immediate callback also triggers premature reload/destruction through the manager; fix lifecycle semantics before shipping this flow.

If not loaded, ShowInterstitial returns false and requests one for a future opportunity. `ignorePacing: true` skips the timestamp check but still respects initialization, format enable and no-ads. The placement string is not forwarded to provider APIs or used for per-placement caps in this implementation.

## 4. Rewarded integration

Offer an explicit player choice and grant a reward only when the earned callback is true. Use a gameplay method that knows the offered reward; the package does not persist application rewards.

```csharp
using UnityEngine;
using UnityEngine.Events;
using bcylyLabs.Monetization;

public sealed class RewardedOfferExample : MonoBehaviour
{
    [SerializeField] private UnityEvent onRewardEarned;
    private bool requestPending;

    public void ShowOffer()
    {
        if (requestPending) return;

        if (!MonetizationManager.IsRewardedVideoLoaded())
        {
            MonetizationManager.RequestRewardedVideo();
            Debug.Log("Rewarded ad is not ready. Try later.");
            return;
        }

        requestPending = true;
        MonetizationManager.ShowRewardedVideo(earned =>
        {
            requestPending = false;
            if (earned) onRewardEarned?.Invoke();
            else Debug.Log("Reward was not confirmed by this callback.");
        }, "optional_reward_offer");
    }
}
```

The local requestPending flag prevents repeated taps on this component. It does not fix the shared tracker's session bugs, provide durable transaction deduplication or recover callbacks across app exit. Handle view destruction and changing reward context in your application.

### Reward lifecycle

```text
Idle -> Requested -> Showing -> Closed -> Completed
             |                    |
             -> Failed            -> wait briefly for reward
```

Reward before close is remembered; close resolves success. Close before reward starts a configurable grace timer. After that timer expires, the normal callback is false. A later native reward can emit a separate LateRewardData event.

Current limitations: Closed is not treated as busy, native events carry no session token, mismatched provider events are accepted, and duplicate late rewards can emit repeatedly. Correct these before relying on once-only reward guarantees. The show-to-display watchdog stops after display; a missing close event can leave a session unresolved.

## 5. Events and late rewards

| Event | Signature | Use |
| --- | --- | --- |
| OnAdLoaded | Action of AdType | Refresh readiness indicators |
| OnAdDisplayed | Action of AdType | Observe a reported presentation |
| OnAdClosed | Action of AdType | Observe format close notifications |
| OnAdSuppressed | Action of AdType and string | Report no-ads suppression; not every blocked request emits it |
| OnNoAdsStateChanged | Action of bool | Refresh entitlement-dependent UI |
| OnLateRewardReceived | Action of LateRewardData | Reconcile a delayed native reward after initial false outcome |

AdType values are Banner, Interstitial, RewardedVideo and AppOpen. App-open event coverage is incomplete, and some provider events are posted to the main thread while others are invoked directly. Keep observers exception-safe and centralize Unity-thread delivery when extending adapters.

```csharp
using UnityEngine;
using bcylyLabs.Monetization;

public sealed class AdEventExample : MonoBehaviour
{
    private void OnEnable()
    {
        MonetizationManager.OnAdLoaded += HandleLoaded;
        MonetizationManager.OnLateRewardReceived += HandleLateReward;
    }

    private void OnDisable()
    {
        MonetizationManager.OnAdLoaded -= HandleLoaded;
        MonetizationManager.OnLateRewardReceived -= HandleLateReward;
    }

    private void HandleLoaded(AdType type)
    {
        Debug.Log("Loaded: " + type);
    }

    private void HandleLateReward(LateRewardData data)
    {
        Debug.Log("Reconciliation needed: " + data.SessionToken.Id);
        // Resolve a retained offer context and compensate exactly once.
        // This logging example deliberately does not grant a second reward.
    }
}
```

LateRewardData contains SessionToken, Placement, ProviderName, DelaySeconds and TimestampUtc. AdSessionToken contains Id, Placement and CreationTimestamp. Normal public earned callbacks expose only bool; they do not expose the token created internally. A complete offer-context ledger needs an API extension or application-level integration, not just the logging example.

Local late-reward notifications are not authenticated server-side verification. No SSV endpoint, signed reward validation or durable reward ledger is implemented here.

## 6. No-ads and persistence

```csharp
MonetizationManager.SetNoAds(true);      // Permanent no-ads.
MonetizationManager.SetTimedNoAds(3600); // At least one hour from now.
bool active = MonetizationManager.IsNoAdsActive;
// MonetizationManager.DisableNoAds(); // Clears BOTH permanent and timed state.
```

NoAdsSaveData is stored as JSON under PlayerPrefs key `bcylyLabs_Monetization_NoAds`. It contains a permanent flag and a UTC Unix expiry timestamp. Initialization loads it lazily. It is a local entitlement cache, not receipt verification or tamper-proof storage.

Activating no-ads destroys the banner and resets SafeAreaAdapter layout. Rewarded is intentionally allowed. The timed getter can return false after expiry without raising an event; no automatic banner restoration is implemented. If integrating purchases, keep purchase ownership authoritative and define how restored ownership updates this cache.

## 7. Consent and privacy extension

IConsentProvider exposes Name, CurrentStatus, CanRequestAds, RequestConsentAsync and ShowPrivacyOptionsForm. ConsentManager.RegisterProvider adds a provider; GatherAllConsentAsync visits registered providers and returns a combined result. CanRequestAds returns true when none are registered.

Normal native startup currently does not construct/register AdMobUMPProvider or AppleATTProvider, and MonetizationManager ignores the gather result. Register providers before gathering and modify orchestration to enforce eligibility before SDK initialization or load. Do not simply paste a provider registration after InitializeAsync; that is too late for startup requests.

Keep ATT tracking authorization separate from whether nontracking ad requests are allowed. The shipped ATT provider's denied state is modeled as CanRequestAds=false; design a suitable platform/network eligibility model rather than treating all privacy signals as interchangeable.

ShowPrivacyOptionsForm only selects the first registered provider. Choose a form-capable provider deliberately, expose requirement status, marshal native callbacks before Unity UI work and refresh eligibility after changes. Handle update errors without assuming an exception means permission.

For native SDK behavior, consult the [Google UMP guide](https://developers.google.com/admob/unity/privacy).

## 8. Provider contract and registration

```csharp
public interface IAdProviderHandler
{
    string ProviderName { get; }
    bool IsInitialized { get; }
    System.Threading.Tasks.Task<bool> InitializeAsync();
    void ShowBanner();
    void HideBanner();
    void DestroyBanner();
    void RequestInterstitial();
    bool IsInterstitialLoaded();
    void ShowInterstitial(System.Action<bool> callback);
    void RequestRewardedVideo();
    bool IsRewardedVideoLoaded();
    void ShowRewardedVideo(System.Action<bool> callback);
    bool IsAppOpenLoaded();
    void ShowAppOpenAd();
}
```

ProviderContainer supplies ProviderName, HandlerTypeName and CreateHandler(settings). Its default factory resolves a type by name/reflection and invokes a constructor taking the container and settings. MonetizationSettings stores containers through SerializeReference and selects one by its provider name.

Native adapter compilation is conditional on BCYLY_ADMOB_INSTALLED, BCYLY_APPLOVIN_INSTALLED, BCYLY_LEVELPLAY_INSTALLED or BCYLY_UNITYADS_INSTALLED. The editor symbol manager updates defines and assembly references using dependency detection heuristics.

For a new adapter, keep it in a separate assembly, provide a serializable container, wire a deliberate factory/preservation mechanism, marshal callbacks, track request generations and clean up native subscriptions/resources. The current interface lacks Dispose and session-token parameters; extend it consistently if implementing reliable lifecycle ownership.

Reflection-created handler types/constructors need explicit factories or linker preservation for stripping-enabled IL2CPP builds. An Editor success is not sufficient evidence.

## 9. Main-thread dispatch and layout

MainThreadDispatcher creates a DontDestroyOnLoad host, queues Action delegates for Update and hosts watchdog/retry coroutines. Post itself only enqueues; it requires a live initialized host to execute. Avoid calling Unity object APIs directly from SDK worker callbacks.

SafeAreaAdapter exposes BannerHeight, CurrentBannerPosition, OnSafeAreaAdjusted, SetBannerLayout, ResetBannerLayout and GetAdjustedSafeArea. Use a consistent screen-pixel convention when consuming its Rect. Current native adapters mix units and do not honor all positions, so validate and correct those paths before using the adjusted Rect as a layout authority.

## 10. Native lifecycle requirements

Interstitial completion must have a consistent definition across adapters and execute once. AdMob should not destroy the current fullscreen object immediately after dispatch; reload after close/failure. App-open needs one foreground owner, enabled/no-ads/fullscreen guards, real closed/failed events, expiration handling and replenishment.

Use per-format isLoading/isShowing state, operation identity and cancellation/cleanup. Current startup has no shared initialization task, provider disposal or full domain-reload-disabled reset. Treat runtime network switching as unsupported until those lifecycles are added.

See the [Google interstitial lifecycle](https://developers.google.com/admob/unity/interstitial) and [app-open lifecycle](https://developers.google.com/admob/unity/app-open) when implementing the AdMob fixes.
