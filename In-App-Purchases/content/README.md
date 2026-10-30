# bcylyLabs IAP Documentation

Documentation for the source included in this implementation, reviewed 29 October 2026.

Start with the user guide to configure products and shop UI. Use the developer reference for scripting and fulfillment. Use the testing guide before moving from simulated purchases to a store build.

| Document | Contents |
| --- | --- |
| [User Guide](#user-guide) | Setup, Hub, products, simulator, buttons, prices, restore and no-ads |
| [Developer Reference](#developer) | Architecture, APIs, events, custom fulfillment, validation and persistence |
| [Testing and Troubleshooting](#testing) | Test scenarios, store transition, diagnostics and known limitations |

## Scope and support

The included README identifies this package as version 1.0.0. The source reviewed for this guide uses Unity 6000.3.6f1 and Unity Purchasing 5.4.3. These are the reviewed environment versions, not a minimum-version guarantee. The older README's Unity 2021.3+ compatibility claim has not been verified by this documentation work.

The implemented providers are Dummy and Unity Purchasing. The Unity adapter selects Google Play or Apple based on compile target. Amazon catalog export is available; Amazon runtime billing is not implemented here. Unity IAP 5 does not support Amazon: see the [official migration guide](https://docs.unity.com/en-us/iap/upgrade-to-iap-v5).

Live subscriptions are disabled by default and have documented implementation gaps. Treat their current support as experimental. This manual describes existing behavior; they do not imply the package passed device/store certification or that the identified code gaps have been fixed.

## Quick start

1. Open **Tools > Bcyly Labs > Bcyly In-Apps Purchases > IAP Hub**.
2. Confirm the selected settings asset and select **EditorAndUnsupportedOnly** for editor simulation.
3. Add a product with a stable key and appropriate fulfillment mode.
4. Add `BcylyIAPButton` to a Unity UI Button and enter the same key.
5. Enter Play Mode and test the simulator purchase.

For a first isolated demonstration, use **Create or Open IAP Demo Scene** from the same menu. The demo can reference starter keys that differ from your catalog; check its configured product keys.
