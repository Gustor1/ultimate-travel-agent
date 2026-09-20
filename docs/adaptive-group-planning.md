# Adaptive and Group Planning

`adaptive-day` creates four deterministic variants from sourced activity candidates:

- `essential`: essential activities only;
- `balanced`: the fullest plan within duration and walking limits;
- `rain`: non-essential outdoor activities removed;
- `low_energy`: non-essential high-energy activities removed with a reduced duration cap.

Essential conflicts are never silently removed; they become visible issues.

`group-decide` requires every participant to score every option. It combines weighted average satisfaction with the lowest individual score, while hard vetoes make an option ineligible. This prevents a majority from silently overriding medical, accessibility, dietary, or other non-negotiable constraints.

`route-optimize` evaluates every ordering for up to eight visits using sourced door-to-door travel times, opening windows, visit duration, and fixed appointments. It minimizes travel plus waiting time and fails visibly when the travel matrix is incomplete or no feasible order exists.
