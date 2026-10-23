# GP Refresh — Our World (Landing Page)

The branded landing page for the existing draft page **https://www.gprefresh.com/our-world/** (WordPress page ID 17225): upcoming conferences, testimonial videos and group discounts.

## Files

| File | Purpose |
|---|---|
| `our-world-elementor-template.json` | Elementor template to import and insert into page 17225. It includes the page settings (Full Width template, hidden title, custom CSS). |
| `our-world.css` | Page-scoped CSS. The same CSS is embedded in the template's `custom_css`. Kept here as the source of truth. |
| `build.py` | Builds both the JSON and the preview from one content definition. Edit the copy here and rebuild. |
| `preview/our-world.html` | Local preview. The live site's real Gala Dinner page shell (header, footer, theme CSS, scripts) with only the page body swapped. |
| `preview/social.html` | Source of the testimonial videos section. The build embeds it as-is, with its global CSS rules scoped to the section. |
| `preview/assets/melbourne.jpeg`, `sydney.jpeg`, `brisbane.jpeg` | Supplied city photos used by the conference cards. The preview reads these local files; the Elementor export embeds them. |
| `preview/assets/background image.jpeg` | Supplied cream, green and gold background for the compact social section. Embedded in the Elementor export. |

Rebuild: `python build.py path/to/saved/gala-dinner.html`

To keep the current preview's shell (including the trimmed navbar), use the preview itself as the shell: `python build.py preview/our-world.html`

## Page sections (top to bottom)

1. **Hero** (unchanged).
2. **Upcoming Conferences:** Melbourne, Sydney and Brisbane in city photo cards, followed by Int'l Cruises (TBC) and Dubai (TBC). Dates and venues are copied from the homepage block. Edit `EVENTS` in `build.py`; the `image`, `image_alt`, `image_width` and `image_height` fields control each photo. Local image paths are relative to `preview/`. The layout stacks on mobile.
   - **Countdown:** sits to the right of the section heading on desktop and below it on tablet/mobile. Shows days, hours, minutes and seconds until **15 May 2027 at midnight in Melbourne (AEST, UTC+10)**, the beginning of the conference date rather than a confirmed session start time. Edit `COUNTDOWN_TARGET`, `COUNTDOWN_LABEL` and `COUNTDOWN_DATE` in `build.py` to change it. It stops at zero with a completion message; it does not automatically switch events. The date remains visible if JavaScript is unavailable.
3. **Social / delegate experiences:** `preview/social.html`, with four compact quote cards on the supplied background. Four columns on desktop, two on tablet and a swipeable row on mobile. The four original Instagram reels open on demand in a native viewing dialog, with an Instagram link as a fallback. Closing the dialog removes the player and restores keyboard focus. No Instagram player is loaded until a reel is selected. Cards reveal as they enter view; decorative gold rings drift with scroll where scroll timelines are supported. Both respect reduced-motion preferences.
   - **Reel popup:** emerald portrait frame with a compact header, gold accents and a direct Instagram link. It scales the complete 360px-wide embed to fit the screen instead of squeezing it into a short wide viewport. The fallback embed height is 900px; validated Instagram height messages adjust it when available. Opening and resizing fit the player, and closing clears it. Cross-origin Instagram content and its reported height cannot be visually verified here.
4. **Group Discounts:** the "2nd Release" tiers from `/pricing/`. Edit `GROUP_TIERS` in `build.py`, and keep it in step with the admin panel.
   - **BLT group discount artwork:** add images to `BLT_VISUALS` in `build.py`. Nothing renders until they're added.
5. **Refresh | Reframe | Reignite** (unchanged).

## Install on WordPress (needs wp-admin, Elementor Pro)

1. **Templates → Saved Templates → Import Templates**, then upload `our-world-elementor-template.json`.
2. Open **Pages → Our World → Edit with Elementor**. In the folder icon (*My Templates*), insert "Our World — Landing Page". Accept the prompt to apply the template's page settings.
3. Check **Page Settings**:
   - Page Layout should be **Elementor Full Width**, the same as Gala Dinner.
   - **Hide Title** should be on.
   - **Advanced → Custom CSS** should contain `our-world.css`. If the import didn't carry it, paste it in.
4. Publish, then view at 1440 / 768 / 390.

Dates, venues and prices on the page are copied from the live homepage and /pricing/ (23 Oct 2026). Update them in build.py when they change.

## Audit findings: the design system used (verified from the live site, 15 Oct 2026)

- **Stack:** WordPress 7.1.3, Blocksy 2.1.50 (header, transparent on dark heroes), Elementor 4.3.5 + Elementor Pro 4.3.2 (page content, footer template 592).
- **Palette** (Blocksy `global.css`): `#020a0a` ink, `#1f443d` green (top bar), `#be9a5e` gold, `#ECECEA` / `#F2F2F0` / `#F5F4EE` warm neutrals (`#F5F4EE` = body).
  - The Elementor kit globals (`#6EC1E4`, Roboto…) are Elementor defaults that the site doesn't use, so they were ignored.
- **Type:** Urbanist throughout, letter-spacing 0.3px.
  - Gala hero: H1 80/60/41px at weight 400; eyebrow 14px/600/5px tracking, uppercase.
  - Section H2: 50/65px. Body: 17.6px/1.65.
- **Layout:**
  - Container 1300px. Side padding 70 / 30 / 20px.
  - Interior heroes are 900px (800px mobile) full-bleed photos under the transparent header.
  - Gala overlay: `rgb(25,25,23)` gradient.
- **Buttons:** pill radius. The hero uses the header's outline "Register Now" style; hover fills gold with ink text.

### Why the page needs an image hero
The site header is transparent, with white text. On the current blank `/our-world/` page, the logo and navigation are invisible on the cream background. A dark full-bleed hero, as on Home and Gala Dinner, fixes this.

## Assets

Conference photos use the supplied `preview/assets/melbourne.jpeg`, `preview/assets/sydney.jpeg` and `preview/assets/brisbane.jpeg`. They show the city skylines, with descriptive alt text and intrinsic dimensions, in the existing fixed-aspect-ratio frames. The local preview loads these files directly. The Elementor JSON embeds the same JPEG bytes as data URLs in its HTML widget, so these three photos do not require local paths on WordPress. This adds roughly 1.8 MB to the export. Check the images after importing into Elementor; the live import has not been verified. Cruises and Dubai retain text-only TBC entries.

- **Hero:** `2026/03/conference-8.webp` (homepage *GP Refresh Highlights → Conference* gallery). Two delegates in GP Refresh lanyards talking at a break; it fits the "community / connections" message.
  - Subjects are on the right, so text sits on the left (desktop) or the lower half (tablet/mobile) without covering faces.
  - Served with `srcset` from WordPress's existing 768 / 1536 / 2304 crops, plus `fetchpriority="high"` and width/height attributes (no layout shift).
- **Supporting section:** `2026/03/conference-6.webp` (delegates at round tables), lazy-loaded.
- The hero and supporting image remain linked to existing site uploads in Elementor HTML widgets. The three conference photos are embedded in the export; no files have been uploaded to WordPress.

## Copy
- Hero copy is taken from the website: the homepage headline "Join the 6-Minute GP Refresh CPD Revolution" and its four pillars (77 six-minute talks, up to 53 CPD hours, no sponsored talks, Gala Dinner). The gold line under the copy lists the 2027 cities. There's no "Coming Soon" wording.
- "Refresh | Reframe | Reignite" and the three lines ("Refresh the basics." / "Reframe the evidence." / "Reignite your passion for patient care.") are existing homepage headings.
- Hero button: **Register Now → https://events.gprefresh.com/** (verified 200).

## QA performed (local preview inside the live page shell, Chrome)

- **Overflow:** none at 1440, 1280, 768, 390 or 320. The only element extending past the viewport is the site's own scrolling date bar.
- **Headings:** a single H1, then one H2. The eyebrow and status are `<p>`, so the heading order has no gaps.
- **Images:** alt text on both; correct `srcset` candidate chosen at each width.
- **Keyboard:** the button is reachable, with a visible 2px focus outline. Touch target 214×44.
- **Contrast** (WCAG, conservative background estimate):
  - Gold status on hero: 5.5:1.
  - Eyebrow: 12:1.
  - Lede: 9.7:1.
  - Ink on cream: 18:1.
  - Button hover (ink on gold): 7.6:1.
  - The site's white-on-gold button (2.6:1) was deliberately not used.
- **Responsive refinements made after review:**
  - Headline kept off the subject's face at 1280 and 768.
  - Hero CTA kept clear of the site's global floating "Register Now / 1300 GP REFRESH" buttons on tablet and mobile.
- **Motion:** short, once-per-element fade-and-rise entrances for the hero copy, section headings, countdown, conference cards, discount tiers and closing section. Desktop hover gently lifts cards and buttons and zooms conference photos. New effects respect `prefers-reduced-motion`, including changes while the page is open. Content stays visible when JavaScript or animation APIs are unavailable; keyboard focus cancels entrance motion on the focused element. No animation library is required. Browser playback has not been verified in this environment.
- **Scope:** all CSS is under `.gpr-ow-*` classes. Shared header, footer, theme and kit are untouched.

## Limitations

- No wp-admin access from here, so nothing has been imported or published. The live page is still blank until the steps above are done.
- The preview approximates Elementor's generated per-element CSS. The custom CSS sets layout explicitly so it doesn't depend on that CSS, but confirm once in Elementor's own preview.
- In the local preview, the footer's icon-font glyphs show as boxes. This is a cross-origin font restriction when served from localhost; they render normally on gprefresh.com.
