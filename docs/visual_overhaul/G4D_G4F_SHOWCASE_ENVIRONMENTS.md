# G4D–G4F — Showcase Environment Passes

Status: source-applied; runtime inspection pending.

## G4D — Spear Pillar

Spear Pillar, its distorted variant, Hall of Origin, and the Dialga/Palkia summit
rooms retain Platinum's geometry, collision, camera, weather, props, and ancient
stone identity. The area family now uses dedicated lighting_set_012, derived
from set 008 with a small cool high-altitude daylight lift.

## G4E — Sinnoh lakes

Lake Verity, Lake Valor, and Sendoff Spring use dedicated lighting_set_013,
derived from set 000. Daylight receives a restrained green-blue lift that
strengthens water/foliage atmosphere without replacing shore geometry or the
native warm evening transition.

## G4F — Turnback Cave

Turnback Cave previously shared area_data_056 with Solaceon Ruins and Celestic
Town Cave. G4 isolates Turnback into area_data_076 with a cloned texture slot
(map_texture_set_075) and dedicated lighting_set_014. Only Turnback Cave headers
are redirected.

Turnback lighting is darker and slightly cooler than the shared cave baseline.
Its texture bank is intentionally left pixel/palette-identical for now because
the dump contains bright green values likely used as key/transparency colors.
Changing those without material-level runtime evidence would be unsafe.

Across all three passes, map matrices, collision, scripts, encounters, camera
logic, weather, event progression, room randomization, and legendary logic are
unchanged.
