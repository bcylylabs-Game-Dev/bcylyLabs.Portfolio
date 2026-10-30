# Developer Reference

Namespace: `BcylyLabs.IAP`. UI namespace: `BcylyLabs.IAP.UI`. Ads bridge namespace: `BcylyLabs.IAP.Integrations`.

## Architecture and lifecycle

```text
UI / game code
    -> BcylyIAP static facade
    -> BcylyIAPService
    -> IStoreProvider (Dummy or Unity Purchasing)
    -> BcylyIAPOrder
    -> BcylyTransactionJournal
        -> IValidationPolicy
        -> built-in fulfillment OR IFulfillmentHandler
        -> BcylyIAPStorage commit
        -> success/entitlement events
        -> background store acknowledgment
```

`BcylyIAPService` creates a persistent GameObject on demand. Auto-bootstrap runs before scene load when settings enable it. Providers register factory delegates during subsystem registration. Provider initialization triggers startup acknowledgment recovery and a foreground validation/custom retry loop approximately every 15 seconds. Focus regain also requests a validation/custom retry sweep.

Use one initialization per application session. `InitializeService` currently has no idempotent initialization guard or full provider disposal. Calling `Initialize()` repeatedly rebuilds the journal and can discard handler registrations.

Adding facade event listeners can create the service object; that alone does not initialize its store or journal. Read-only facade queries generally use the existing service and do not bootstrap it.

## Public facade

| Member | Purpose / result |
| --- | --- |
| `bool IsInitialized` | Active provider reports initialized |
| `bool IsSimulationActive` | Service selected simulation |
| `void Initialize()` | Initialize with resolved settings; call once if auto-init is disabled |
| `void Purchase(string key, Action<PurchaseResult> callback = null)` | Request a purchase |
| `void RestorePurchases(Action<bool, string> callback = null)` | Request provider restoration/reconciliation |
| `bool IsPurchased(string key)` | Read local entitlement ownership; intended for permanent products |
| `int GetCounter(string key)` | Read built-in product counter; zero if unavailable |
| `string GetLocalizedPrice(string key)` | Provider price or display fallback |
| `SubscriptionInfo GetSubscriptionInfo(string key)` | Subscription information; may be null without a service |
| `bool HasSubscriptionAccess(string key)` | True when returned info grants access |
| `RegisterFulfillmentHandler(string key, IFulfillmentHandler handler)` | Register custom delivery on the current journal |
| `RegisterFulfillmentHandler(string key, Func<BcylyIAPOrder, Task<FulfillmentResult>> callback)` | Register an inline async custom handler |

Product keys must match the catalog. Although catalog searches ignore case, not every storage/callback dictionary uses the same comparison behavior. Use consistent exact key spelling throughout the game.

### Purchase example

Attach this script to a GameObject and connect `BuyCoins` to a UI action. Choose either this approach or the package's purchase button listener for an individual button.

```csharp
using BcylyLabs.IAP;
using UnityEngine;

public sealed class ShopPurchaseExample : MonoBehaviour
{
    public void BuyCoins()
    {
        if (!BcylyIAP.IsInitialized)
        {
            Debug.Log("Store is still initializing.");
            return;
        }

        BcylyIAP.Purchase("coins_500", result =>
        {
            switch (result.Status)
            {
                case PurchaseStatus.Success:
                    Debug.Log("Purchase fulfilled: " + result.ProductKey);
                    break;
                case PurchaseStatus.Cancelled:
                    Debug.Log("Purchase cancelled.");
                    break;
                case PurchaseStatus.Pending:
                    Debug.Log("Purchase pending: " + result.ErrorMessage);
                    break;
                case PurchaseStatus.Failed:
                    Debug.LogWarning(result.ErrorMessage);
                    break;
            }
        });
    }
}
```

Do not grant coins again inside the completion callback. Success means the pipeline considers fulfillment complete; it does not mean background store acknowledgment has finished.

`PurchaseResult` exposes `Status`, `ProductKey`, `TransactionId`, `ErrorMessage` and `IsSuccess`. Pending is not a terminal payment rejection. The current service removes a request callback after delivering a Pending result; later fulfillment is observed through global events rather than a second invocation of that callback.

### Events

| Event | Signature | Meaning |
| --- | --- | --- |
| `OnInitialized` | `Action` | Provider initialization completed |
| `OnInitializeFailed` | `Action<string>` | Provider initialization reported an error |
| `OnPurchaseSuccess` | `Action<BcylyIAPProduct>` | A new journal fulfillment emitted success |
| `OnPurchaseFailed` | `Action<BcylyIAPProduct, string>` | Non-success pipeline outcome; currently includes Pending |
| `OnEntitlementsChanged` | `Action` | Refresh ownership/access UI |

Subscribe in `OnEnable` and unsubscribe in `OnDisable` for ordinary scene components. Also read current state when enabling; initialization can precede subscription. Keep observers short and exception-safe. These events are notifications, not a durable reward delivery mechanism.

Some early validation failures returned directly by `Purchase` invoke only the request callback. Do not assume every failure also generates the global failed event.

### Restore example

```csharp
BcylyIAP.RestorePurchases((success, message) =>
{
    UnityEngine.Debug.Log($"Restore request: {success}; {message}");
});
```

Do not interpret this callback as a barrier for asynchronous validation/custom delivery. Listen for entitlement changes and read the resulting ownership.

## Catalog model

`BcylyIAPProduct` contains `key`, `type`, `defaultStoreId`, per-store overrides, fallback display metadata, `icon`, `fulfillment` and `counterAmount`. `Id` is an internal GUID and `RegenerateInternalId()` creates another GUID. Saved ownership currently uses keys, so the GUID does not make key renames safe.

`GetEffectiveStoreId(provider)` chooses override, then default ID, then key. `BcylyIAPSettings` supports `FindProductByKey`, `FindProductById` and `FindProductByStoreId`.

Settings resolution uses the cached instance; Editor preloaded assets and active EditorPrefs selection; loaded settings objects; project-specific Resources filenames; the default Resources path; then a Resources-wide fallback. Prefer one deliberate preloaded catalog over relying on fallback order.

## Custom fulfillment contract

Use CustomHandler for rewards stored outside the package's counter/entitlement file. Register after the journal is created. With auto-init enabled this is normally possible in scene startup; with manual initialization call Initialize once first. Missing handlers cause orders to defer until registration.

```csharp
public interface IFulfillmentHandler
{
    System.Threading.Tasks.Task<FulfillmentResult> FulfillAsync(
        BcylyIAPOrder order, BcylyIAPProduct product);
}
```

| Result | Handler must mean |
| --- | --- |
| Success | Rewards and transaction identity were durably committed |
| AlreadyApplied | The same transaction was previously durably applied |
| RetryableFailure | No completed delivery can be asserted; retry later |
| TerminalFailure | Permanently reject delivery with an understood reason |

The journal calls the handler before committing its own fulfillment record. Therefore **the handler must provide its own durable idempotency**. An in-memory HashSet or a separate PlayerPrefs flag written after granting rewards does not close the crash window.

### Required wallet integration pattern

The following is an integration template. `DurableWallet.ApplyBundleOnceAsync` is an application API you must implement; it is not part of this package.

```text
ApplyBundleOnceAsync(transactionIdentity, rewardBundle):
    start durable wallet transaction
    if transactionIdentity already exists:
        return AlreadyApplied
    validate that the entire bundle can be delivered
    update every wallet/inventory value in the bundle
    insert transactionIdentity into the processed-order ledger
    commit wallet values and processed identity together
    return Success
```

Pass `order.CompoundTransactionId` as the identity. For a server wallet, enforce a unique transaction identity and authorize the reward from verified store/product information. For local storage, one atomic persisted snapshot must include both balances and processed IDs. Report temporary failures rather than acknowledging a partial grant.

Never register a handler that always returns Success without actually delivering and persisting the reward.

## Order identity and processing

`BcylyIAPOrder` contains ProductKey, StoreTransactionId, Provider, Environment, Receipt, TimestampUtc, RawProviderPayload and IsNativeStoreVerified.

Compound identity format:

```text
{Provider}:{Environment}:{StoreTransactionId}
```

`RawProviderPayload` is not serialized. `FromCompoundTransactionId` reconstructs identity for acknowledgment recovery; it does not restore a full receipt/native payload. A valid stable native transaction identity is essential for deduplication.

Journal processing checks quarantine and duplicates, validates, fulfills, persists FulfilledAckPending, schedules acknowledgment and emits success. On successful/already-finalized acknowledgment it attempts CompletedAcked persistence. Deferred validation/custom queues are memory-only; restart recovery before fulfillment depends on store redelivery.

## Validation

| Mode | Implementation |
| --- | --- |
| None | Passthrough accepts the order |
| LocalSignature / Google | RSA signature verification with configured Google public key, plus selected receipt identity checks |
| LocalSignature / Apple | Checks wrapper fields/identity and trusts the adapter's native-verification flag |
| LocalSignature / other provider | Falls back to passthrough |
| CustomServer | POST receipt data to configured URL |

Dummy always uses the dummy-only validation policy. Google supports SHA-256 or SHA-1 verification in this implementation. Local Google validation does not currently compare packageName to Application.identifier. Apple wrapper checks are not independent cryptographic verification of the receipt.

### Custom server protocol

The request body is JSON:

```json
{
  "productKey": "coins_500",
  "storeTransactionId": "store-transaction-id",
  "provider": "GooglePlay",
  "environment": "Live",
  "receipt": "store receipt payload"
}
```

A successful HTTP response must contain:

```json
{ "valid": true, "reason": "" }
```

For rejection return a successful HTTP response with `valid: false` and a reason. The implementation treats HTTP 5xx, network errors and timeouts as temporary; other non-success HTTP statuses are rejection. Consequently 429 is currently not retried as a temporary error. Default timeout is 10 seconds.

The client has no configurable authentication headers or account identifier in this protocol. Add the required account/authentication integration for your backend. The server must actually verify store data and identity; echoing valid=true is not receipt validation. The response does not carry wallet rewards, subscription expiry or authoritative balances.

## Persistence

Default files under `Application.persistentDataPath`:

- `bcyly_iap_sandbox.dat`
- `bcyly_iap_live.dat`
- Associated `.bak`, `.tmp` and quarantined `.corrupt.*` files when applicable.

Schema version is 2. The 48-byte binary header contains magic, version, generation and SHA-256 checksum. Payload data is XOR-obfuscated JSON. The checksum detects corruption; it is not keyed authentication or encryption.

Built-in reward effects and journal records share a file commit with memory rollback on save failure. External wallet effects do not share this transaction. Corruption recovery can quarantine consumables; inspect `Storage.HasUnresolvedConsumables` and reconcile from an authoritative source. There is no complete support/reconciliation UI in this version.

`GetCounter` reads a cumulative built-in counter. There is no public spending/decrement API in the facade. Do not substitute it for a complete game currency wallet without extending the design.

## Ads bridge

`BcylyIAPAdsBridge` exposes `Initialize(customNoAdsKey)`, `NoAdsProductKey`, `CurrentState`, `IsNoAdsActive`, `OnNoAdsStatusChanged` and `OnNoAdsStateChanged`.

It automatically initializes after scene load and emits ownership changes; subscribers configure their own ad managers. It tracks one product key and does not itself combine all no-ads bundles. Unknown startup state suppresses false revocation notifications.

## Extension boundaries

`IStoreProvider` supplies initialization, purchase, acknowledgment, restore, price and subscription queries plus lifecycle/order events. `ProviderFactory` uses resolver delegates so Core does not directly reference provider assemblies.

The shipped Unity adapter mixes legacy initialization/listener APIs with v5 purchase-service confirmation. Its existence does not establish support for older Unity IAP versions. Consult [Testing and Troubleshooting](#testing) before extending or releasing it.
