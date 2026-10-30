# bcylyLabs IAP User Guide

## 1. What the package does

bcylyLabs IAP connects your product catalog and Unity shop UI to a simulated store or Unity Purchasing. It provides a setup Hub, purchase/restore buttons, localized price binding, transaction processing and local ownership storage.

There are three separate responsibilities:

- **Store catalog:** products and actual prices configured in Google Play Console or App Store Connect.
- **Package catalog:** developer keys, store IDs, display fallbacks and fulfillment settings.
- **Game rewards:** your game's coins, boosters, lives and other effects, connected through a custom fulfillment handler when needed.

A fallback price is display text. Changing it does not change the actual store price. The built-in counter is separate from your game's wallet.

## 2. Open the setup tools

Use **Tools > Bcyly Labs > Bcyly In-Apps Purchases > IAP Hub**. The Hub contains:

| Tab | Purpose |
| --- | --- |
| Overview | Select/create settings, inspect provider installation and configure runtime options |
| Products | Add and edit products, store IDs and reward modes |
| Simulator Sandbox | Run Play Mode purchase simulations and clear test profiles |
| Diagnostics | Inspect available package diagnostics |

The Hub is also accessible from **Project Settings > bcylyLabs IAP**. **Select IAP Settings** selects the resolved asset in the Project window.

### Select the correct settings asset

The Hub supports an active settings asset and registers it in Player Settings' Preloaded Assets. This ensures the asset is loaded in a player build. Use the Hub's settings selector rather than assuming that an asset named `BcylyIAPSettings` is active.

If no settings exist, the editor creator writes `Assets/Resources/bcylyLabs/IAP/BcylyIAPSettings.asset` with starter no-ads, coins and subscription products.

Keep one intended active catalog. Runtime fallback loading includes project-specific filenames and can choose a different asset when several catalogs exist. Verify the selected profile in the Hub before editing or building.

## 3. Configure simulation

| Sandbox mode | Actual behavior |
| --- | --- |
| Disabled | Requests the native provider, including in the Editor |
| EditorAndUnsupportedOnly | Uses Dummy in Editor and WebGL; native provider elsewhere |
| AlwaysSimulate | Uses Dummy on every target, including mobile devices |

Despite the enum name, `EditorAndUnsupportedOnly` does not test every unsupported desktop platform. Its implementation explicitly checks Editor and WebGL.

Keep **Auto Initialize On Awake** enabled for the standard workflow. With it disabled, your bootstrap must call `BcylyIAP.Initialize()` once before registering custom handlers or purchasing.

**Allow Sandbox Demo Build** bypasses the release build guard for intentional simulated demos. It does not enable real billing. A non-development build with AlwaysSimulate normally fails the package's pre-build check.

Change settings before starting Play Mode. Repeated runtime initialization is not a supported profile-switching workflow in this version.

## 4. Add products

In Products, use a preset or add a custom product.

| Field | Meaning |
| --- | --- |
| Key | Stable identifier used by game code and UI, for example `no_ads` |
| Type | Consumable, NonConsumable or Subscription |
| Default Store ID | Store-facing product identifier used when no override exists |
| Google/Apple/Amazon override | Optional store-specific identifier; Amazon has no runtime adapter here |
| Fallback Title | Title displayed by package UI |
| Fallback Price | Test/fallback text shown before live price metadata is available |
| Description / Icon | Product metadata and optional image |
| Fulfillment | BuiltInEntitlement, SimpleCounter or CustomHandler |
| Counter Amount | Increment for a consumable using SimpleCounter |

ID resolution is: provider override -> default store ID -> developer key. The key and store ID may differ. Match store IDs exactly to products configured in the store console. Keep keys and IDs stable after release; renaming a key does not migrate saved ownership.

### Choose a fulfillment mode

| Use case | Recommended setup |
| --- | --- |
| Permanent feature such as no-ads | NonConsumable + BuiltInEntitlement; connect ownership to the feature |
| Simple isolated demo counter | Consumable + SimpleCounter |
| Existing game wallet or reward bundle | CustomHandler with durable transaction deduplication |
| Subscription | Simulator experiments only until the live implementation gaps are resolved |

Do not configure a coin purchase as BuiltInEntitlement and assume coins will appear. A SimpleCounter increment is stored under the product key and can be read through `GetCounter`; it does not automatically update your game wallet or provide a spending API.

## 5. Add a purchase button

1. Create or select a Unity UI Button.
2. Add **bcylyLabs > IAP > bcylyLabs IAP Button**.
3. Set **Product Key** to the catalog key.
4. Optionally assign price/title labels and an icon image.
5. Enable **Disable If Purchased** or **Hide If Purchased** for owned permanent products.
6. Connect feedback events to sound, animation or purchase messages.

The component registers its own click listener. Do not additionally wire the Button's OnClick to a second purchase call.

`onPurchaseSuccess` and `onPurchaseFailed` are feedback hooks. Deliver paid rewards in the fulfillment pipeline, not these UI events. Otherwise another scene, restore or duplicate event may deliver rewards inconsistently.

The component prevents repeated clicks on that button while processing. Multiple buttons or scripted requests for the same product are not globally serialized by this version.

## 6. Display a price

Either assign the purchase button's price label or add **bcylyLabs IAP Price Text** to a separate label and set its Product Key.

The package tries initialized provider metadata first, then the catalog fallback. Unknown keys return a generic `$0.99` fallback through the facade, so a displayed price alone does not prove the key exists.

TextMeshPro fields compile when the assembly's `TMP_PRESENT` package version define is satisfied. Legacy Unity UI Text fields are also available. The settings UI framework choice controls custom inspector presentation; it does not install dependencies or change actual store metadata.

## 7. Add restore purchases

Add **bcylyLabs IAP Restore Button** to a Button.

| Mode | Behavior |
| --- | --- |
| Auto | Visible in simulation and Apple targets; hidden on other targets |
| AlwaysShow | Forces visibility |
| AlwaysHide | Forces hiding |

Apple uses the store extension restore request. Other targets scan cached receipt-bearing non-consumables/subscriptions. Dummy restore only reports simulated success; it does not reconstruct purchases after deleting local storage.

Restore is for recoverable ownership, not replaying spent consumable balances. A successful restore callback does not guarantee that all asynchronous custom reward validation/fulfillment has finished. Refresh final ownership using entitlement events.

## 8. Connect no-ads

A purchased entitlement does not automatically configure your advertising SDK. Use your game integration or subscribe to `BcylyIAPAdsBridge.OnNoAdsStatusChanged` in code. The bridge defaults to product key `no_ads`; set its `NoAdsProductKey` if yours differs.

The bridge emits state changes and has Unknown, Owned and NotOwned states. It does not directly call an ad manager. For bundles granting no-ads, connect the bundle's reward/ownership explicitly; one default bridge key does not represent every bundle.

## 9. Test a purchase

1. Set an appropriate simulation mode and enter Play Mode.
2. Confirm the service/provider initialized.
3. Click the shop button and approve or cancel the simulator sheet.
4. Check the expected entitlement, built-in counter or custom game reward.
5. For permanent products, verify the button disables/hides as configured.
6. Stop/restart Play Mode and verify persisted state.

The Hub also provides **Simulate Buy** and simulated restore in Play Mode when Dummy is active. Simulations do not prove native store setup or receipt verification.

Use **Clear Sandbox Profile Data** for isolated test resets. This clears package ownership/journal data, not your game's separate wallet or PlayerPrefs. Clearing the live profile can remove local transaction deduplication history; reserve it for controlled test accounts/devices.

## 10. Move to real stores

Configure products and test access in the target store, install/verify Unity Purchasing, select the correct target and replace simulation with native mode. For Google local validation, supply the public key. For custom-server validation, supply a working receipt validation endpoint.

Run the device scenarios in [Testing and Troubleshooting](#testing). Fix the documented reward and provider gaps before treating this integration as production ready.
