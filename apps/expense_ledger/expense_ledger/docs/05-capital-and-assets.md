# Capital contributions and assets

## Capital contributions

A **Capital Contribution** records money a person has put into the company, tagged to the financial year (April to March) of its date.

- **From a claim:** approve a claim with the settlement *Capital Contribution* and the contribution is created and confirmed for you.
- **By hand:** open *Capital Contribution*, choose New, and enter the contributor, date and amount. It stays a draft until an Accounts Manager submits it.

The **Capital Contributions** report lists them, filtered by financial year (for example 2026-27) or contributor.

## Turning something you built into an asset

When the company builds a product or creates IP, the costs sit as ordinary expenses until it is ready and deployed. A **Capitalization** record gathers those costs and creates the asset.

1. Choose New in *Capitalization*. Give it a title, say whether it is a Product or IP, and pick the Asset Category, Cost Center and the Location it is deployed to.
2. Fill in the dates. **Ready on** is when it was finished. **Deployed on** is when it went into use; it becomes the asset's available-for-use date.
3. Add the **costs**. For a purchase, pick the confirmed bill. Its taxable value is filled in because recoverable GST is not part of an asset's cost, and you can edit the amount. For anything with no bill, such as in-house labour, leave the bill empty and describe the cost.
4. Write the **narrative**: what was built, what it is for, where it is deployed. Attach a document if you have one.
5. **Submit** once it is ready and deployed. The system creates and submits the Asset for the total cost, links it back to this record, and marks the bills as capitalized so they cannot be used again.

The rule is deliberately simple: no submit until it is ready and deployed. Tell your administrator if you want a different trigger.

Cancelling the record cancels the asset and frees the bills. The *Asset Register* report from ERPNext lists everything capitalized.

## Before the first one

ERPNext needs an **Asset Category** (add an intangible one for IP) and a **Location** to exist. The asset is created as an existing asset with no depreciation schedule; set depreciation up in ERPNext if your accountant wants it.
