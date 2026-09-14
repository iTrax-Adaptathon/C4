# TrackFab

**TrackFab** is a browser-based production and goods-control dashboard for small manufacturing operations. It helps a user record production work, manage material batches, track goods movements, and keep a simple audit trail of operational updates.

The interface uses a glassmorphism-style control-room design and starts with no sample business data. Everything shown in the dashboard is created by the user.

## What it does

- Create and track production runs from planning through completion.
- Add material batches with quantity, unit, storage location, and quality status.
- Put a material batch on hold or release it when it is safe to use again.
- Create goods trips for supplier, warehouse, or customer movements.
- Track a trip's origin, destination, carrier, ETA, current location, and delivery stage.
- Update trips through `Created → Picked up → In transit → Delivered`.
- View operational totals, including active production, goods in transit, material holds, and deliveries due today.
- Maintain an append-only activity log for user actions.
- Reset all prototype data when needed.

## Screens

| Screen | Purpose |
| --- | --- |
| **Overview** | A high-level view of production, materials, deliveries, and latest records. |
| **Production runs** | Create work orders and move them from `Planned` to `Active` and `Completed`. |
| **Materials** | Record material batches and control their `Available` / `On hold` status. |
| **Live trips** | Select a goods movement, inspect its route, and update location and status. |
| **Activity log** | Review every production, material, and trip update recorded in the browser. |

## Run locally

No build tool, package installation, or server is required.

1. Open [index.html](./index.html) in a modern browser.
2. Select **Add material**, **Production run**, or **New trip**.
3. Enter your operational data.
4. Use **Live trips** to update a shipment as it moves.

> Tip: A lightweight local server can make development more convenient, for example `python3 -m http.server` from this folder. It is optional.

## Data storage

This prototype stores data in the browser using `localStorage` under the key `forgeos-data`.

- Data persists when the page is refreshed.
- Data is private to the browser and device on which it was entered.
- Data is not shared with other users, browsers, or devices.
- **Reset my data** deletes the local ForgeOS data after confirmation.

This is appropriate for a front-end demo. It is not a replacement for a shared, authenticated production database.

## Project structure

```text
.
├── index.html   # Application structure and screens
├── styles.css   # Responsive glassmorphism visual system
├── app.js       # State, forms, local storage, and interactions
├── schema.sql   # PostgreSQL model for a production implementation
└── README.md    # Project documentation
```

## Trip tracking workflow

1. Create a trip with a reference, origin, destination, carrier, ETA, and initial location.
2. Open **Live trips** and select the trip from the list.
3. Use **Update trip location or status** whenever the goods move.
4. Enter the latest location and choose the current stage.
5. The route view, status chip, dashboard totals, and activity log update immediately.

## Production and material workflow

1. Add a material batch with its lot number, available quantity, and location.
2. Create a production run with its work order, product, quantity, and due date.
3. Start the run when production begins.
4. Complete the run when it is finished.
5. If material fails inspection, place that batch on hold; release it only after review.

## Database foundation

[schema.sql](./schema.sql) provides the PostgreSQL model for evolving the prototype into a multi-user production system. It includes tables for:

- Material batches, machines, operators, qualifications, and production runs.
- Material, machine, and operator reservations.
- Quality holds and output batches.
- Goods trips and trip location updates.
- Immutable production events and genealogy edges for traceability.

It also defines partial unique indexes to prevent active double-booking of materials, machines, and operators.

## Moving to real-time production use

To turn ForgeOS into a shared live system, replace browser storage with an API and PostgreSQL database, then add:

1. Authentication and role-based access (operator, planner, supervisor, quality).
2. Transactional reservation APIs with row locking.
3. WebSocket updates after a successful transaction commits.
4. GPS, carrier, barcode, RFID, or IoT integrations for automatic trip and machine updates.
5. Alerts for material holds, equipment faults, allocation risks, missed output targets, and overdue runs.
6. Audit retention, backups, monitoring, and deployment controls.

## License

Licensed under the Apache License 2.0. See [LICENSE](./LICENSE).
