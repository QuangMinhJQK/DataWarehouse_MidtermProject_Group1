# Data Flow Diagram Design System

Use this visual style when turning a supplied data system flow into a draw.io diagram. The architecture and technologies will be provided separately for each project.

## Overall appearance

- Clean, compact, and professional.
- Use a white canvas with generous outer margins.
- Organize the system into clearly separated layers or functional regions.
- Use pale background colors so icons and flow lines remain easy to read.
- Keep the diagram dense enough to scan quickly without crowding.
- Prefer a landscape layout.

## Layout

- Show the main data flow from left to right.
- Place data sources on the left.
- Place ingestion, transformation, storage, and serving components in the center.
- Place reports, applications, and other consumers on the right.
- Place governance, security, monitoring, and development tools in a shared band along the bottom.
- Align related components in rows or columns.
- Keep equal spacing and consistent card sizes.

## Shapes

- Use rounded rectangles for services and tools.
- Use large, lightly tinted containers for major platform areas.
- Use a subtle dashed border for broad system boundaries.
- Use white inner panels inside colored platform areas.
- Use official product icons with a short label.
- Avoid shadows, gradients, decorative effects, and oversized icons.

## Color style

Use a small pastel palette:

- Light blue for orchestration and integration.
- Light orange for processing and transformation.
- Light green for the central data platform.
- Light purple for governance, metadata, and analytics.
- Light red for monitoring and alerts.
- Light gray for neutral services and source control.

Use dark gray for text, borders, and connectors. Keep official icons in their original colors.

## Typography

- Use a clean sans-serif font.
- Use bold labels for services and section titles.
- Keep labels short and centered.
- Use consistent text sizes throughout the diagram.
- Avoid paragraphs inside diagram shapes.

## Connectors

- Use dark gray orthogonal connectors.
- Use solid arrows for the primary data flow.
- Use dashed arrows for orchestration, metadata, security, lineage, or dependency relationships.
- Keep the main flow visually dominant.
- Avoid crossing connectors and text.
- Use arrow labels only when the relationship is unclear without one.

## Fabric diagrams

- Use official Microsoft Fabric and Azure icons.
- Group Fabric workloads inside one clear Fabric platform boundary.
- Keep sources, Fabric processing, storage, semantic models, and consumers visually distinct.
- Show shared governance and monitoring services as supporting layers.
- Choose the final layout from the supplied system flow rather than copying the old architecture.

## Codex drawing rules

When a system flow is provided:

1. Identify sources, processing stages, storage layers, consumers, and shared services.
2. Arrange them into a clear left-to-right flow.
3. Apply this appearance consistently.
4. Use official icons and automatic draw.io layout.
5. Keep the result compact, aligned, and free of overlaps.
6. Validate and visually inspect the diagram before delivery.
