# Testing, Release Preparation and Troubleshooting

## Test environments

| Environment | What it can establish |
| --- | --- |
| Dummy simulator | Catalog/UI flow, callbacks, built-in storage and custom game integration |
| Editor verification runners | Specific mocked regression scenarios |
| Device store sandbox/test track | Real product fetch, receipts, payment/deferred events and restore behavior |
| Release configuration review | Intended catalog/provider/validation settings are shipped |

A simulated success does not verify store configuration. This guide describes the implementation; run the verification steps against your own build and test accounts.

## Existing verification menus

Development test sources are guarded by `BCYLY_DEV_TESTS`. On a test branch/configuration, add that scripting define for the relevant Editor compilation target if the menus are absent, allow recompilation, then use **Tools > Bcyly Labs > Bcyly In-Apps Purchases**.

Available runners include Phase 1 Storage, Phase 2 Simulator, Phase 3 UI, Phase 4 Store, Phase 5 Release, all phases, and the 12-case production verification runner. They use custom menu execution and Console output rather than conventional discoverable NUnit/UnityTest cases. Keep this define out of normal distribution builds unless needed for development.

The tests manipulate service/static state and test storage. Run in a controlled development session. A broad success message from a mock runner is not evidence that Google/Apple device flows passed.

## Manual test matrix

| Scenario | Expected result |
| --- | --- |
| Approve a consumable | Exactly one complete durable reward grant |
| Cancel purchase | No grant; shop becomes usable again |
| Double-click one button | One request from that component |
| Two controls request the same product | Earlier callbacks are not silently lost; current service needs improvement here |
| Buy an owned non-consumable | Owned state preserved; no second reward grant |
| Restart after fulfillment | Ownership/counter still present |
| Kill app after external wallet grant but before journal save | Redelivery does not grant twice; requires an idempotent application handler |
| Missing inventory/game manager during recovery | Defer delivery rather than acknowledge missing rewards |
| Temporary validation outage | No premature grant; successful retry eventually delivers once |
| Acknowledgment outage beyond retry limit | Same-session reconnect eventually confirms; current implementation needs improvement here |
| Deferred/Ask-to-Buy payment | Pending feedback, then eventual success/rejection; native callback wiring needs improvement |
| Fresh-install restore | Permanent access restored without replaying spent consumables |
| Corrupt storage | Diagnostic/quarantine path; no blind consumable regrant |
| Expired or malformed subscription receipt | No unsupported access grant; current implementation needs improvement |

Record device, build, target store, product key, transaction ID, callback status, resulting reward and journal state. Keep full receipts out of shared screenshots/log attachments unless access is appropriately controlled.

## Moving to Google Play / Apple

1. Confirm the intended active/preloaded catalog and stable product IDs.
2. Configure matching products, actual prices and test accounts in the store console.
3. Verify Unity Purchasing is installed and the native adapter compiles for the target.
4. Use native mode on the device. `EditorAndUnsupportedOnly` still uses Dummy in the Editor.
5. For LocalSignature Google validation, configure the public key. For CustomServer, deploy and test the expected JSON endpoint.
6. Complete durable, idempotent custom rewards before using paid purchases.
7. Run real sandbox/test-track purchase, cancellation, deferred, restart and restore scenarios.
8. Confirm release settings again after testing. Keep live subscriptions disabled until their access/expiry implementation is corrected.

Store-specific operational instructions change; use [Unity's purchasing documentation](https://docs.unity.com/en-us/iap) and the target store's current console documentation for account/submission procedures.

## Existing pre-build checks

The package blocks AlwaysSimulate in a non-development build unless Allow Sandbox Demo Build is enabled. It also checks empty/duplicate developer keys and duplicate nonempty default store IDs.

It does not fully validate store override collisions, provider availability, public keys, server configuration or reward durability. Passing this check is one configuration check, not complete release approval.

## Troubleshooting

| Symptom | Likely cause | Next step |
| --- | --- | --- |
| Real device shows simulator | Active settings use AlwaysSimulate | Inspect Hub selection and preloaded catalog |
| Settings edits have no effect | Another settings asset is active or cached | Select intended catalog in Hub; restart Play Mode |
| Store not initialized | Startup still in progress, manual init omitted, adapter/configuration failure | Observe init events and Console; initialize once if manual |
| No provider warning | Resolver/adapter unavailable | Inspect installed package, assembly defines and target |
| MissingConfiguration / pending validation | Google key or server URL absent | Configure active settings and retry |
| Product unavailable/not found | Wrong key/store ID, store product unavailable or missing metadata | Compare effective ID with target-store product |
| Price shows `[Test]` | Dummy active or live metadata unavailable | Inspect provider and product fetch; fallback is not actual store price |
| TMP fields missing | Assembly version define/dependency not satisfied | Inspect UI asmdef and installed TMP/UGUI packages |
| Dummy request never completes | No simulator UI delegate and headless auto-approve is false | Use demo/simulator UI or Hub simulation controls |
| Button remains disabled | No completion event, missing deferred wiring or exception | Inspect provider events, callback lifecycle and Console |
| Pending purchase fires failure feedback | Current UI treats Pending as non-success | Separate pending UX in integration code |
| Coins counter changes but wallet does not | SimpleCounter is independent of your game wallet | Use a custom wallet handler |
| Custom order waits indefinitely | Handler not registered on current journal | Initialize before registration; check catalog key and manager startup |
| Paid bundle loses items | Missing gameplay dependencies were silently skipped | Implement explicit grant outcomes and transactional delivery |
| Duplicate coins after restart | Handler lacks durable transaction deduplication | Commit rewards and transaction identity together |
| Restore button hidden on Android | Auto visibility mode | Choose AlwaysShow if a manual reconciliation control is desired |
| Restore says success but ownership is delayed | Async processing continues after callback | Observe entitlement changes and verify final journal state |
| Consumables blocked after corruption | Unresolved consumable quarantine | Reconcile with authoritative wallet/history; avoid arbitrary resets |
| Acknowledgment stuck after reconnect | Retry attempts exhausted | Inspect pending journal; current runtime requires retry scheduler improvements |
| Release build aborts | AlwaysSimulate without demo override or catalog validation failure | Read build error and correct intended configuration |

## Known limitations

- Amazon runtime billing is absent; JSON export is only a catalog tool. Unity IAP 5 does not support Amazon.
- Custom reward crash safety depends on a correctly implemented external handler. An application handler must persist its own transaction deduplication.
- Native deferred callbacks are declared but not connected by the adapter.
- Acknowledgment retry exhaustion waits for a future initialization rather than a periodic durable queue sweep.
- Subscription parsing can fail open, offline fallback does not enforce cached expiry, and built-in fulfillment assumes a one-month period.
- Reinitialization can replace handlers/journal without full old-provider cleanup.
- One pending callback per product and one restore callback can be overwritten by concurrent callers.
- Validation/custom pending queues before fulfillment are not persisted; store redelivery is required after restart.
- Local storage checksum/obfuscation does not prevent intentional tampering.

## Support evidence

When reporting an issue, include Unity and Purchasing versions, target platform, active settings name, sandbox/validation mode, product key/effective store ID, relevant Console errors and reproduction steps. Include whether it occurred in Dummy or a real store test. Preserve transaction IDs for controlled debugging and avoid sharing public-key configuration screenshots alongside private backend credentials.
