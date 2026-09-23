# Haemily — Product and Technical Requirements

**Document type:** Product requirements and implementation architecture  
**Audience:** Product, design, frontend, backend, data, security, and HSS operations teams  
**Source:** Final Haemily HTML/CSS/JavaScript prototype in `hss-community-phase-1`  
**Status:** Engineering handoff draft  
**Product owner:** Haemophilia Society of Singapore (HSS)  
**Primary audience:** Adults with haemophilia and adult caregivers of children and young people, from diagnosis through National Service  
**Initial language:** English

---

## 1. Purpose

Haemily is a private HSS community platform that brings together:

- trusted HSS information and healthcare-reviewed resources;
- lived experiences, questions, and discussions from community members;
- AMAs and community-sharing threads;
- HSS events, webinars, talks, recordings, meetups, and open jios;
- life-stage and topic-based discovery;
- WhatsApp-based caregiver groups;
- a controlled way to request or offer non-emergency, non-medical practical help.

The current prototype demonstrates the intended information architecture, content hierarchy, responsive behaviour, and key interactions. It does **not** contain a working backend, persistent database, real authentication, notification delivery, search index, external integrations, AI service, or complete operational controls.

This document converts the prototype into an implementation-facing product definition. It describes what the production system must do while avoiding unnecessary prescription of programming language, framework, cloud vendor, or messaging provider.

---

## 2. Product goals

1. Help members find trustworthy information and relevant lived experiences quickly.
2. Clearly distinguish verified information from community experience without making either feel unimportant.
3. Reduce friction by organising the same content by both life stage and topic.
4. Support safe community participation under a pseudonym.
5. Make events and community activities easy to discover, join, and revisit.
6. Help caregivers form ongoing connections without building in-app private chat in the first release.
7. Enable limited, privacy-conscious, non-emergency practical-help coordination.
8. Give HSS appropriate publishing, access, safety, and audit controls.
9. Preserve a consistent design system and familiar interaction patterns across mobile, tablet, and desktop.

### Non-goals for the initial production release

- In-app direct messaging or group chat.
- Clinical consultation, diagnosis, triage, treatment advice, or emergency response.
- Medication or treatment-product exchange, infusion assistance, regulated-device lending, or medical-safety decisions through ordinary community volunteers.
- Child accounts or direct participation by minors.
- Family-planning, ageing, or adult-care-transition content pathways.
- Public access outside the HSS-approved member list.
- A volunteer rating or public reputation system.

---

## 3. Product principles

### Trust must be visible

HSS-verified and healthcare-reviewed material must carry a consistent source label. Community content must also carry a consistent, quieter source label. A verification label is source metadata, not an action button.

### Private identity, public pseudonym

HSS may know the member's registered phone number, but other members see only the chosen username and avatar. Private identity and public profile data must be stored and authorised separately.

### One content system, multiple ways to find it

Home, Search, Explore by life stage, and Explore by topic must query the same canonical content records. They are views of one repository, not duplicated content stores.

### Safety before speed

The practical-help workflow must disclose its boundaries before a request is published or an offer is made. Exact locations and contact details stay private until both parties explicitly agree to connect.

### External handoffs must be explicit

Before opening WhatsApp or another third-party service, explain what information may become visible and that Haemily privacy controls no longer apply there.

### Consistent behaviour

The same component must behave the same way everywhere: buttons, source labels, statuses, filters, cards, save actions, forms, dialogs, empty states, and responsive layouts.

---

## 4. Users and roles

| Role | Description | Key permissions |
|---|---|---|
| Eligible visitor | Phone number exists in the HSS access list but no active session exists | Request OTP, complete onboarding |
| Community member | Authenticated adult using a pseudonymous profile | Read, search, post, comment, react, save, report, register, join activities and groups |
| Volunteer | Community member who has opted into approved practical-help categories, areas, and times | View eligible matched requests, offer help, withdraw or decline |
| Verified contributor / AMA guest | Named or role-based contributor confirmed by HSS | Provide attributed answers or reviewed content through an HSS-controlled workflow |
| Moderator | HSS-appointed operator responsible for safety and review | Review reports, act on content or access, review AI-summary reports, oversee practical-help incidents |
| Maintainer / publisher | HSS-appointed content administrator | Create, edit, review, publish, archive, or remove verification from official resources |
| Service administrator | Restricted technical/operations role | Manage configuration, providers, service availability, and operational recovery; no routine content authority by default |

Roles may overlap, but permissions must be assigned explicitly through role-based access control. The UI must never be the only enforcement layer.

---

## 5. Information architecture

### Primary navigation

1. **Home** — personalised priorities and the latest content.
2. **Explore** — browse the shared repository by life stage or topic.
3. **Connect** — community WhatsApp groups and non-emergency practical help.
4. **Events** — HSS events and member-organised community activities in one discovery list.

### Account navigation

- Profile and activity
- Saved content
- My posts
- My comments
- Preferences and interests
- Notification preferences
- Moderator tools, shown only to authorised roles
- Sign out

### Content taxonomy

**Life stages**

- Newly diagnosed
- Infants and toddlers
- Preschool and kindergarten
- Primary school
- Secondary school and teenage years
- National Service

**Topics**

- Travel
- Sports and exercise
- Treatment and infusion
- Bleeds and everyday safety
- School and childcare
- Caregiver wellbeing
- Financial and practical support
- Understanding haemophilia
- AMAs and community sharing

Each life-stage card exposes its top subtopics directly on Explore so a member can judge relevance without first opening the category.

---

## 6. Page catalogue

| Page / view | Purpose | Principal content and actions | Production data required |
|---|---|---|---|
| Access: phone | Confirm that the visitor belongs to the HSS-approved community | Singapore phone input, eligibility check, request OTP, HSS contact path if ineligible | Access-list record, request limits, OTP challenge |
| Access: OTP | Verify control of an eligible phone number | Six-digit code, resend and expiry behaviour, error handling | OTP challenge status, attempt count, expiry |
| Access: profile setup | Create the public identity | Pseudonymous username, avatar, privacy explanation | Member and profile records, username uniqueness |
| Home | Show the most useful current information | Search entry, Help needed, next joined/registered activity, latest content, sort, source filters, detailed filters, create-post action | Personalisation, eligible help matches, registrations, joined activities, feed query |
| Global search | Find content and activities across the app | Search suggestions, recent searches, all results, sort, source/type/stage/topic filters, empty states | Search index, taxonomy, optional private search history |
| Explore | Browse the repository in two complementary ways | Life stages with visible subtopics; topic directory; search entry | Topic and life-stage taxonomy, content counts/order |
| Collection | Show all records for a life stage, subtopic, or topic | Breadcrumb, introduction, sort, quick filters, detailed filters, result list | Canonical content/activity query with taxonomy joins |
| Content detail | Read a verified resource or community post | Source, author, metadata, original-post AI summary, body, reactions, save/share/report, discussion AI summary, comments, related content | Content, version, source/review data, interactions, summaries, recommendations |
| Create post | Publish a community contribution | Choose Question/Discussion/Lived experience; compose; classify; privacy review; publish | Draft/post records, taxonomy joins, validation, audit event |
| AMA directory | Browse AMAs and community-sharing threads | Open/upcoming/closed states, guest attribution, counts, filters and sort | AMA thread, guest, question and answer records |
| AMA detail | Read or participate in an AMA | Ask question when open, read guest answers, open scheduled event, AI recap for closed AMA | Thread lifecycle, moderation state, Q&A, event relation, recap |
| Events | See plans and discover all upcoming activity | Your plans; unified HSS/community list; All/HSS/Community source filter; detailed filters; sort; past recordings | Events, community activities, registrations, joins, capacity and availability |
| Event detail | Understand and act on an HSS event | Status, host, time, mode, audience, register/join live/add calendar, AMA link, recordings and resources | Event, registration, external meeting link, materials |
| Community-activity detail | Understand and join a meetup/open jio | Host, general location, time, audience, capacity, WhatsApp handoff, save/share/report | Activity, host, participation, protected external link, reports |
| Create activity | Publish a meetup or open jio | Choose type; enter details, general area, capacity, audience and external link; safety notice; publish | Activity and link records, validation, lifecycle, audit event |
| Connect | Find ongoing groups and practical help | WhatsApp caregiver groups, capacity, join handoff, help safety boundary, request and volunteer entry points, member's requests | Groups, protected links, memberships, support-service configuration and requests |
| Create help request | Request approved non-emergency practical assistance | Emergency stop check; approved category, broad area, timing, preferred contact, description; privacy review; publish | Policy/category configuration, request, expiry, matching and consent records |
| Volunteer preferences | Opt into practical-help matching | Approved categories, broad areas, availability, alert preference | Volunteer profile, categories, areas, schedule and consent |
| Volunteer matches | Review requests matched to preferences | Minimal request preview, offer help, decline privately | Matching result, access policy, offer/decline records |
| Help-request status | Track a request through its lifecycle | Open, offer received, connected, fulfilled, cancelled or expired; accept/decline; reveal contact after mutual consent; report concern | Request, offers, status history, protected contact release, reports |
| Notifications | Configure delivery | WhatsApp/SMS/email channels and categories; privacy-safe preview | Channel verification, preference matrix, templates and delivery records |
| Profile | Manage personal activity and preferences | Saved, posts, comments, public profile, interests, life stages, notifications | Profile, content ownership, saves, comments, preferences |
| Moderation / operations | Protect trust and safety | Reports, verified publishing, access review, stale-resource review, AI-summary reports, practical-help oversight, service pause | Moderation cases, publishing workflow, audit log, access and configuration controls |

### Page-level responsive contract

- **Mobile, below 768 px:** bottom navigation; context-sensitive floating create action; cards and form actions stack; full-width primary actions where needed.
- **Tablet and desktop, 768 px and above:** desktop top navigation; create actions in the page header; two-column layouts where specified; inline actions where space permits.
- **Home “For you”:** two equal-width, equal-height white cards on tablet/desktop; stacked on mobile. Help needed appears first and gains emphasis through its icon and action hierarchy, not through a different background or width.
- Cards, controls, and lists must fill their available container. Avoid unexplained fixed widths or empty card space.

---

## 7. End-to-end flows

### 7.1 Access and onboarding

1. Visitor enters a Singapore phone number.
2. Backend normalises the number and checks the active HSS access list.
3. If eligible and within rate limits, the OTP service sends a code through the approved channel.
4. Visitor submits the code before expiry.
5. Backend verifies the challenge and creates an authenticated session.
6. A first-time member selects a unique pseudonymous username and avatar.
7. Member reaches Home. Their phone number and registered identity are never exposed publicly.

Failure paths must cover ineligible number, invalid or expired OTP, resend cooldown, too many attempts, blocked access, provider failure, and HSS contact guidance.

### 7.2 Find and read information

1. Member enters through Home, Search, or Explore.
2. Member sorts or filters by source, content type, topic, or life stage.
3. Member opens a content record.
4. System shows its source and review state before the content body.
5. Member may read the AI summary, inspect referenced source material, react, save, share, report, comment, or open related content.

Home returns content records only in its latest-community feed; events and activities remain in their own page and in the personal “next event” card. Search and collection pages may return multiple supported record types.

### 7.3 Publish a community post

1. Member chooses Question, Discussion, or Lived experience.
2. Member adds title and body.
3. Member assigns one or more topics and life stages.
4. UI warns against child-identifying, health-identifying, location, or contact information.
5. Member reviews the final source label and classification.
6. Backend validates, stores, and publishes the post as community content.
7. The post becomes queryable on Home, Search, and relevant Explore collections.

Community members cannot apply HSS or healthcare verification labels.

### 7.4 Participate in a discussion

1. Member opens a content or AMA thread.
2. Member adds a comment, reply, question, or supported reaction.
3. Backend checks authentication, access status, rate limits, and content state.
4. Interaction is stored and counters are updated transactionally or asynchronously.
5. Relevant participants receive privacy-safe notifications according to preferences.
6. A member may edit or report permitted records; moderators may act through an auditable process.

### 7.5 Register for an HSS event

1. Member opens an upcoming HSS event.
2. Member registers once; the operation must be idempotent.
3. Event appears under Your plans.
4. Confirmation and reminders are delivered through opted-in channels without sensitive details.
5. When live, the join action opens the authorised event room.
6. After the event, recording and HSS materials may be attached to the same record.

### 7.6 Join or create a community activity

1. Member discovers a meetup or open jio in Events.
2. Member opens the detail page and sees the community source, host, broad area, date, audience, capacity, and safety notice.
3. Member joins or follows the explicit WhatsApp handoff.
4. Joined activity appears under Your plans.

For creation, a member selects Meetup or Open jio, enters activity details and only a general area/MRT, confirms that it is social rather than medical assistance, and publishes. The activity remains reportable to HSS.

### 7.7 Join a caregiver group

1. Member reviews group purpose, audience, and availability.
2. Member selects Join group.
3. Haemily explains what WhatsApp will expose.
4. Member confirms the handoff.
5. Backend generates or returns an authorised, short-lived redirect where feasible; raw group invitation links should not be embedded in public page data.

### 7.8 Request non-emergency practical help

1. Member starts with a mandatory emergency-safety question.
2. “Yes” or “unsure” stops the flow and shows official emergency guidance.
3. “No” continues to HSS-approved non-medical categories.
4. Member provides a broad area, timing, contact preference, and sanitised description.
5. Member reviews what volunteers will see and explicitly confirms the boundary.
6. Backend publishes an expiring request and matches only eligible opted-in volunteers.
7. A volunteer may offer, decline privately, or later withdraw before acceptance.
8. Requester accepts or declines an offer.
9. Contact information is revealed only after mutual agreement.
10. Either person can end contact or report a concern. The requester can mark the request fulfilled or cancel it.
11. Unanswered requests expire automatically.

The exact Home pinning and volunteer-visibility rules remain a policy decision. The backend should support configurable eligibility, priority, expiry, and presentation without hard-coding them into clients.

### 7.9 Moderate a safety or accuracy concern

1. Member submits a structured report against content, a comment, activity, connection, or AI summary.
2. Backend creates an immutable case with the target snapshot and reporter access controls.
3. Authorised moderator reviews context and history.
4. Moderator keeps, corrects, hides, removes, closes, or escalates the case.
5. The system records actor, reason, before/after state, time, and any member communication.
6. Access suspension or verification removal requires explicit permissions and a recorded reason.

---

## 8. Consolidated feature set

### Membership and identity

- HSS-managed phone allowlist.
- OTP verification with expiry, retry limits, resend cooldown, and abuse protection.
- Pseudonymous username and avatar.
- Private/public identity separation.
- Role-based access and session management.
- Sign out, session expiry, access suspension, and audit history.

### Repository and forum

- Shared content model for HSS resources and community threads.
- Content types: guide/resource, question, discussion, lived experience/story.
- Multiple topics and life stages per record.
- Source labels: Verified by HSS, Healthcare reviewed, Community experience.
- Author, publication date, review date, lifecycle state, and revision history.
- Comments and nested replies.
- Empathetic reactions: Helpful, I relate, Support.
- Save, share, view, and report.
- Related verified guidance and related lived experience.

### Discovery

- Home feed with Latest, Top, and Most discussed sort options.
- Quick source filters and detailed multi-select filters.
- Browse by life stage with exposed top subtopics.
- Browse by topic.
- Global search across supported content and activities.
- Suggestions, recent searches, empty states, and result counts.
- Personal interests used to improve relevance.

### AI summaries

- Summary of the original post/resource.
- Summary of a discussion and unresolved questions.
- AMA and event recaps.
- Updated timestamp, source/reference links, report-inaccuracy action, hide/correct workflow, and generation status.
- Clear AI label; summaries must not inherit a verification label from source content.

### AMAs and community sharing

- Open, Upcoming, and Closed lifecycle states.
- Verified guest identity/role.
- Moderated question submission.
- Guest answers and community replies.
- Link to scheduled event.
- Closed-thread recap and continued read access.

### Events and activities

- Unified discovery list for HSS events and community activities.
- Quick filters: All, HSS events, Community activities.
- Filters for format, date, area, topic, type, availability, and participation state.
- Sort by upcoming, recently added, or popularity.
- Your plans combines registered events and joined community activities.
- Live, upcoming, joined/registered, closed, and recording states.
- Event registration, calendar export, live-room link, recordings, slides, and related resources.
- Member-created meetups and open jios with broad-location privacy and reporting.

### Connect and external groups

- Ongoing caregiver groups by audience/life stage.
- Capacity or availability state.
- Explicit WhatsApp privacy interstitial.
- Protected external invitation links.

### Non-emergency practical help

- HSS-controlled service availability switch.
- Emergency stop gate.
- Configurable approved categories and safety wording.
- Broad-area and time-based volunteer matching.
- Volunteer availability and alert preferences.
- Request expiry and full status history.
- Private decline and withdrawal.
- Mutual consent before contact disclosure.
- Fulfil, cancel, end-contact, and report flows.
- Privacy-safe notifications and operations oversight.

### Notifications

- Opt-in WhatsApp, SMS, and email channels.
- Categories for replies/mentions, registration confirmation, event reminders, meetup changes, AMA answers, followed topics, major HSS announcements, and eligible help matches.
- Per-channel and per-category preference checks.
- Non-sensitive message templates.
- Retry, failure, suppression, unsubscribe, and delivery audit.

### HSS operations

- Report queue.
- Verified-resource publishing and review.
- Stale-resource reminders and removal of verification.
- AI-summary accuracy review.
- Member access review and suspension.
- Practical-help oversight and service pause.
- Policy/configuration change approval and audit trail.

---

## 9. Recommended logical architecture

The implementation may be a modular monolith initially, provided module boundaries and data ownership are explicit. This reduces early operational complexity while preserving a clean path to split high-volume or high-risk services later.

```text
Responsive web client
        |
        v
Application API / backend-for-frontend
        |
        +-- Identity and access
        +-- Profiles and preferences
        +-- Content, taxonomy and interactions
        +-- Search and discovery
        +-- AMAs
        +-- Events and community activities
        +-- Groups and external-link handoff
        +-- Practical-help matching and consent
        +-- Moderation, publishing and audit
        +-- Notification orchestration
        +-- AI-summary orchestration
        |
        +-- Relational database
        +-- Search index
        +-- Object/file storage
        +-- Job queue and scheduler
        +-- Cache / rate-limit store
        |
        +-- OTP / WhatsApp / SMS / email providers
        +-- Event and calendar integrations
        +-- AI model provider
```

### Architectural requirements

- The application API is the sole authority for permissions and state transitions.
- Use a transactional relational database for identity, content, participation, and help workflows. PostgreSQL is a suitable default, not a mandatory vendor choice.
- Use an asynchronous queue for notifications, indexing, AI generation, counters, expiry, reminders, and scheduled review tasks.
- Keep provider integrations behind internal adapters so OTP, messaging, event, or AI vendors can change.
- Store uploaded files outside the relational database, with access-controlled metadata and malware scanning.
- Introduce a search service when database search no longer meets relevance or scale needs; preserve canonical IDs from the main database.
- All sensitive and privileged state changes must generate audit records.
- All dates must be stored as timezone-aware timestamps. Display in Asia/Singapore by default and never derive production logic from hard-coded dates.

---

## 10. Domain model and database requirements

The table names below are illustrative. Engineering may adjust naming and normalisation, but must retain the relationships and controls.

### Identity and access

| Entity | Important fields / relationships |
|---|---|
| `access_list_entries` | Normalised phone hash/encrypted phone, eligibility status, source, valid-from/to, HSS reference, suspension state |
| `otp_challenges` | Phone reference, provider, code hash, requested/expiry/verified times, attempts, resend count, status, IP/device risk metadata |
| `users` | Internal ID, access-list reference, status, created/last-login times |
| `profiles` | User ID, unique username, avatar, public bio if introduced; contains no phone number |
| `sessions` | User ID, token hash or session identifier, issued/expiry/revoked times, device metadata |
| `roles`, `user_roles` | Role, scope, grantor, granted/expiry times |
| `user_interests` | User-to-topic and user-to-life-stage preferences |

### Taxonomy and content

| Entity | Important fields / relationships |
|---|---|
| `topics` | Stable key, name, description, icon key, display order, active state |
| `life_stages` | Stable key, name, description, display order, active state |
| `life_stage_subtopics` | Life stage, label, linked topic/query rule, display order |
| `content_items` | Author, type, source type, title, body, excerpt, status, published/updated times, current revision |
| `content_topics`, `content_life_stages` | Many-to-many classifications |
| `content_revisions` | Immutable body/metadata snapshot, editor, change reason, timestamp |
| `source_verifications` | Content, verification type, named source/contributor, reviewer, review date, next review date, state |
| `attachments` | Owner record, object key, MIME type, size, scan status, access policy |
| `content_views` | Content, viewer or anonymous aggregate key, timestamp; used with privacy-aware retention |
| `saves` | Unique user/content pair, timestamp |
| `reactions` | Unique user/target/reaction-type record; target can be content or comment |
| `comments` | Content/thread, author, parent comment, body, state, edit timestamps |
| `reports` | Reporter, target type/ID, reason, details, status, target snapshot, timestamps |
| `moderation_actions` | Report/target, actor, action, reason, before/after state, timestamp |

### AI summaries

| Entity | Important fields / relationships |
|---|---|
| `ai_summaries` | Target type/ID, summary type, text, model/config version, status, generated/updated times, moderation state |
| `ai_summary_sources` | Summary, source content/comment/answer, quoted range or reference metadata |
| `ai_summary_reports` | Summary, reporter, reason, resolution and moderator |

Only one active summary per target and summary type should be presented. Regeneration must keep prior versions for audit and rollback.

### AMAs

| Entity | Important fields / relationships |
|---|---|
| `ama_threads` | Title, topic, life stage, guest, status, opens/closes times, linked event |
| `ama_guests` | Public attribution, verification state, HSS approver, optional user link |
| `ama_questions` | Thread, author, body, moderation state, submitted/published times |
| `ama_answers` | Question, guest/author, body, state, published time |

### Events and community activities

| Entity | Important fields / relationships |
|---|---|
| `events` | HSS owner, type, title, description, start/end, timezone, mode, audience, life stage, capacity, status |
| `event_registrations` | Unique event/user pair, status, registered/cancelled/check-in times, external-provider reference |
| `event_resources` | Event, resource type, protected URL/file, display order, availability |
| `community_activities` | Host user, Meetup/Open jio, title, description, broad area, start/end, audience, capacity, status, external-link reference |
| `activity_participations` | Unique activity/user pair, joined/withdrawn state and timestamps |
| `external_links` | Encrypted/protected destination, owner, purpose, active/expiry state, access policy |

HSS events and community activities remain different entities because ownership, trust, registration, and moderation rules differ. A backend read model can merge them into the unified Events list.

### Groups

| Entity | Important fields / relationships |
|---|---|
| `groups` | Name, description, kind, audience/life stage, capacity, state, external-link reference |
| `group_membership_events` | User, group, handoff/join/leave state when known, timestamp |

### Practical help

| Entity | Important fields / relationships |
|---|---|
| `help_service_config` | Service availability, approved wording/version, default expiry, policy owner, effective date |
| `help_categories` | HSS-approved category, description, allowed state, matching rules, policy version |
| `volunteer_profiles` | User, active/paused state, consent/policy version, contact preference |
| `volunteer_categories` | Volunteer/category opt-in |
| `volunteer_areas` | Volunteer/broad-area opt-in; never exact residential location |
| `volunteer_availability` | Time windows or coarse availability labels, notification state |
| `help_requests` | Requester, category, sanitised description, broad area, urgency window, expiry, preferred contact, status, policy version |
| `help_request_matches` | Request, volunteer, match reason, eligibility snapshot, notified/viewed/declined times |
| `help_offers` | Request, volunteer, message, offer state, created/withdrawn/accepted times |
| `help_connections` | Accepted offer, consent from both parties, contact-release time, ended time |
| `help_status_history` | Request, previous/new status, actor/system, reason, timestamp |
| `help_incidents` | Request/connection, reporter, concern type, safety action, resolution |

Private contact data should be fetched through a narrowly authorised endpoint only after a valid active connection exists. Do not copy phone numbers into request, offer, match, notification, analytics, or search records.

### Notifications and audit

| Entity | Important fields / relationships |
|---|---|
| `notification_preferences` | User, channel, category, enabled state, quiet hours if introduced |
| `notifications` | Recipient, category, template, safe payload, related entity, scheduled/sent/read state |
| `delivery_attempts` | Notification, provider, attempt, response code, status, retry time |
| `audit_logs` | Actor, action, entity type/ID, reason, before/after references, time, security metadata |

---

## 11. State models

### Content

`draft -> published -> archived`  
Exceptional states: `hidden`, `removed`, `outdated`  
Verification: `unverified -> pending review -> verified -> review due -> renewed | verification removed`

### AMA

`upcoming -> open -> closed -> archived`

### Event

`draft -> published/upcoming -> live -> completed -> recording available -> archived`  
Cancellation may occur from upcoming or live with participant notification.

### Community activity

`draft -> published -> full | upcoming -> completed`  
Exceptional states: `cancelled`, `hidden`, `removed`.

### Registration or participation

`not joined -> registered/joined -> withdrawn`  
Optional later states: `waitlisted`, `attended`, `no-show`.

### Help request

`draft -> open -> offer received -> connected -> fulfilled`

Terminal alternatives from eligible states: `cancelled`, `expired`, `reported/closed by HSS`. An offer has its own states: `offered -> accepted | declined | withdrawn | expired`.

Every transition must be validated server-side and written to history. Client-supplied statuses must not be trusted.

---

## 12. API capability map

Exact URL style may follow the team's API standards. The production API must expose at least these capabilities:

### Authentication and profile

- Check eligibility and request OTP.
- Verify OTP, refresh/revoke session, and sign out.
- Create/read/update pseudonymous profile.
- Read/update interests and notification preferences.

### Content and discovery

- List Home feed, filtered collections, related content, and personalised priorities.
- Search across content, AMA threads, events, and activities with facets.
- Read content with source/review metadata.
- Create/update/delete the current member's permitted community content.
- Save/unsave; react/unreact; share-link resolution; record privacy-safe views.
- Create/edit/report comments and replies.

### AMAs

- List/read threads and linked sessions.
- Submit questions.
- Publish guest answers through authorised workflow.
- Read/generate/report recaps.

### Events and activities

- List unified activities and Your plans.
- Register/cancel event registration.
- Join/withdraw from community activity.
- Create/update/cancel member-hosted activity.
- Retrieve authorised live, calendar, recording, resource, or WhatsApp handoff links.

### Groups

- List eligible groups and availability.
- Request an authorised external handoff.

### Practical help

- Read effective policy, service availability, and approved categories.
- Create/read/cancel/republish request.
- Update volunteer preferences.
- List eligible matches; decline, offer, or withdraw.
- Accept/decline offer and retrieve contact only after mutual agreement.
- Mark fulfilled, end contact, or submit incident report.

### Moderation and publishing

- List and resolve reports.
- Create/review/publish verified resources.
- Renew or remove verification.
- Hide/correct AI summary.
- Review or suspend member access.
- Pause/reopen practical-help service and version its policy.
- Read immutable audit history.

All mutation endpoints need validation, authorisation, idempotency where double submission is plausible, and structured error responses suitable for inline UI recovery.

---

## 13. Sorting, filtering, and feed rules

### Home

- Home's main feed contains content threads/resources, not the full event/activity list.
- Default sort: latest published activity.
- Top: reaction-weighted ranking with time decay to be defined.
- Most discussed: comment/reply activity with anti-gaming and time-window rules to be defined.
- Quick filters: All, Verified, Community.
- Detailed filters: source, content type, life stage, topic.

### Home “For you”

- **Help needed:** only requests the member is eligible to see; exact eligibility and prominence rules are configurable and require HSS approval.
- **Your next event:** nearest future event/activity that the member registered for or joined and that occurs within seven days.
- If one card is absent, the remaining card fills the available width.
- The current prototype's fixed reference date must be replaced by server-derived current time.

### Events

- Your plans includes both HSS registrations and community activities joined by the member.
- Discovery uses one list with source filters: All, HSS events, Community activities.
- Default sort: live first, then ascending start time.
- Other sorts: recently added and popularity. Popularity requires an explicit formula rather than prototype constants.

### Explore

- Life-stage and topic browsing query the same records.
- A record may appear in several collections without duplication in storage.
- Display order for life stages, topics, and highlighted subtopics is HSS-configurable.

---

## 14. Notification events

| Trigger | Potential recipients | Default privacy-safe content |
|---|---|---|
| Reply or mention | Parent author / mentioned member | “You have a new reply in Haemily.” |
| Event registration | Registrant | Confirmation without condition, stage, or child information |
| Event reminder/change/cancellation | Active registrants | Event name may be configurable; avoid health details in lock-screen preview |
| Community activity change | Joined members | Generic activity update with link back to Haemily |
| AMA question answered | Question author | “A question you follow has an update.” |
| Followed-topic update | Opted-in member | Generic new-content message |
| Eligible help match | Opted-in volunteer | Broad category/area only; no diagnosis, exact address, or requester contact |
| Help offer | Requester | “Someone offered to help with your request.” |
| Offer accepted | Volunteer and requester | Ask each party to return to Haemily; do not put contact details in notification |
| Help expiry/cancellation/report action | Relevant member(s) | Minimal status message and in-app link |
| Significant HSS announcement | Eligible opted-in members | HSS-approved template |

Notification production must be event-driven, preference-aware, deduplicated, retryable, and auditable.

---

## 15. AI-summary requirements

1. Generate only from content the requesting member is authorised to view.
2. Keep original content/comments as the source of truth.
3. Store model, prompt/configuration version, generation time, and referenced records.
4. Regenerate when source material changes beyond an agreed threshold or when explicitly requested.
5. Show generation/update status and allow the member to open referenced passages.
6. Separate verified facts from lived experience and unverified suggestions in wording and structure.
7. Never present individual medical advice or infer diagnoses, treatment safety, or emergency status.
8. Support report, hide, correct, regenerate, and rollback workflows.
9. Exclude deleted, hidden, or unauthorised source material from future generations.
10. Define retention and provider-training controls before sending health-related community text to an external model provider.

---

## 16. Design-system contract

### Foundation

- Typeface: Inter with system sans-serif fallbacks.
- Background: warm off-white `#F8F6F0`.
- Surface: white.
- Primary teal: `#0D5C5B`; reserved for principal navigation, actions, focus, and HSS trust cues.
- Secondary blue: `#3F6F9F`; used intentionally for community-led cues and supporting emphasis.
- Navy text: `#152F3E`.
- Muted text: `#5D7480`.
- Amber is for attention; red is for destructive or danger states.
- Default card radius: 14 px; small control radius: 9 px.
- Minimum interactive target: 44 by 44 px.

### Component rules

- Filled teal buttons are primary actions; outlined buttons are secondary; ghost/text buttons are tertiary.
- Do not use underlines as the default interaction style.
- Source labels and status labels are compact metadata, never button-like.
- Verified source labels use a soft teal treatment and shield icon.
- Community source labels use a soft blue treatment and people icon.
- Status badges use semantic tones and must not replace source labels.
- Filter chips, selectable chips, and static metadata must remain visually distinguishable.
- Use one consistent filter pattern: Sort by, Filters, then quick source filters; detailed filters open in a modal sheet/drawer.
- Desktop/tablet page-level create actions appear at the top right; mobile uses a bottom-right floating action. Card-specific actions such as Reply, Join, Register, or Offer help remain inside their card/context.
- Dialogs trap focus, close with Escape, restore focus to their trigger, and prevent background scrolling.
- Support reduced motion and visible keyboard focus.

### Content design

- Lead with plain-language titles and the action or status most relevant to the member.
- Keep trust/source metadata near the title.
- Avoid repeating the same label in title, badge, metadata, and button.
- Use concise card excerpts and compact padding; details belong on the destination page.
- Make empty, loading, error, permission-denied, expired, and offline states explicit.

---

## 17. Security, privacy, and safety requirements

- Treat phone numbers, HSS membership, contact information, help-request data, and health-related text as sensitive.
- Encrypt data in transit and sensitive data at rest; manage secrets outside source code.
- Authorise every record read and mutation server-side.
- Separate public profile data from private identity and contact data.
- Hash phone numbers for lookup where practical and retain encrypted values only where delivery requires them.
- Use rate limits and abuse detection for OTP, posting, reactions, reports, registrations, external-link access, and help offers.
- Prevent common web vulnerabilities including injection, cross-site scripting, request forgery, broken object authorisation, unsafe redirects, and file-upload abuse.
- Sanitise user-generated rich text and external links.
- Do not index private contacts, exact locations, draft records, or restricted moderation data.
- Keep tamper-evident audit history for verification, policy, access, moderation, AI-summary, and practical-help actions.
- Define retention, deletion, export, incident-response, and backup-restoration policies with HSS's data-protection owner.
- Complete a Singapore privacy and legal review, including PDPA obligations, consent language, volunteer terms, and liability wording, before launch.
- Provide an operational emergency/escalation page maintained by HSS. Haemily must not attempt clinical triage.

---

## 18. Accessibility and quality requirements

- Target WCAG 2.2 AA.
- All functions must work with keyboard alone.
- Controls require programmatic names, roles, states, and error associations.
- Do not encode source, status, or urgency by colour alone.
- Preserve logical heading order and landmarks.
- Announce async success/failure through an accessible live region.
- Maintain minimum touch targets and sufficient contrast.
- Test screen-reader use, focus order, zoom to 200%, text reflow, reduced motion, and common mobile viewport sizes.
- Test tablet at 768 px and above using desktop navigation and layout rules.

---

## 19. Performance, reliability, and operations

- Define service-level targets before build; recommended starting targets are fast first content on typical mobile networks and API p95 below one second for standard reads under normal load.
- Paginate feeds, comments, searches, moderation queues, and audit views.
- Use optimistic UI only where rollback is clear; high-risk transitions such as registration, connection consent, contact reveal, suspension, and publishing must wait for authoritative server confirmation.
- Implement idempotency for OTP request, registration, join, publish, offer, accept, fulfil, cancel, and notification jobs.
- Provide structured logs, metrics, traces, alerting, dead-letter queues, and provider-health dashboards.
- Back up transactional data and test restoration regularly.
- Allow HSS to pause risky services such as practical help without redeploying the application.
- Provide feature flags and staged rollout for AI summaries, notification channels, practical help, and moderator tools.

---

## 20. Analytics and product measurement

Collect the minimum data needed to improve the product. Avoid placing phone numbers, free-text health content, exact location, or child information in analytics payloads.

Suggested measures:

- Successful and failed access attempts by reason.
- Search success, zero-result queries, filter usage, and content opens.
- Content saves, reactions, comments, and reports.
- Explore usage by life stage versus topic.
- Event detail views, registrations, joins, cancellations, and recording opens.
- Group handoff confirmation, without tracking activity inside WhatsApp.
- Help-request funnel: safety stop, draft, publish, match, offer, connect, fulfill, expire, cancel, report.
- Notification opt-in, delivery, failure, and return-to-app.
- AI-summary open, referenced-source open, and inaccurate-summary report rates.

Analytics events need a versioned dictionary, lawful basis/consent review, role-limited access, and a retention period.

---

## 21. Prototype-to-production gaps

| Prototype behaviour | Production requirement |
|---|---|
| Authentication stored in `sessionStorage` | Secure server session or equivalent token lifecycle with revocation |
| Any valid-length phone/OTP succeeds | HSS allowlist, real OTP provider, expiry, throttling, risk controls |
| All content is hard-coded JavaScript | Persistent canonical database with lifecycle and revisions |
| State resets on reload | Per-user durable state and server-authoritative workflows |
| Routes are internal render states | Real deep-linkable, guarded URLs with not-found and permission states |
| Counts and popularity are constants | Stored interactions and documented ranking formulas |
| Filters/search run in memory | Paginated API queries and search index/facets |
| Buttons use timeouts and toasts | Real async requests, loading, retry, conflict and error handling |
| Current date is hard-coded to 22 Sep 2026 | Timezone-aware server clock and testable time abstraction |
| WhatsApp “would open” | Protected, audited external handoff with safe redirect |
| AI summaries are static copy | Authorised generation pipeline, sources, versions, moderation and reporting |
| Reports/moderation are demonstrations | Persistent case management, permissions, reasons and audit history |
| Help matching is simulated | Configurable eligibility, matching, expiry, consent, privacy and incident workflows |
| No real file or event integration | Protected resources, calendar export, live-room and recording integration |
| No failure/loading/offline states | Full state coverage and observability |

---

## 22. Delivery recommendation

### Release 1 — Platform foundation

- HSS access list, OTP, sessions, pseudonymous profiles, roles.
- Taxonomy, repository/forum, source labels, comments, reactions, saves, reports.
- Home, Search, Explore, content detail, create post, profile.
- Basic moderation and verified publishing.
- Responsive design system and accessibility baseline.

### Release 2 — Events and structured community participation

- AMAs, HSS events, registrations, Your plans, recordings/resources.
- Community meetups/open jios, joins, WhatsApp handoff, reporting.
- Notification preferences and initial delivery channels.

### Release 3 — Intelligence and operational maturity

- AI summaries with references, reporting, versioning, and review.
- Search relevance, personalisation, followed-topic notifications, analytics.
- Resource review reminders and richer moderator tooling.

### Release 4 — Practical-help pilot

- Launch only after HSS confirms permitted categories, safety wording, volunteer eligibility, visibility/pinning rules, liability terms, contact-release model, escalation ownership, and operating hours.
- Roll out behind a feature flag to a limited cohort.
- Include pause control, incident queue, expiry jobs, privacy-safe notifications, and an exit/rollback plan from day one.

This sequencing treats the practical-help feature as a separately governed service rather than a normal forum feature.

---

## 23. Decisions required before implementation

1. Who owns and synchronises the HSS phone allowlist, and how quickly are additions/removals reflected?
2. Which provider and channel send the initial OTP?
3. Are members required to accept community rules and privacy terms, and how are term versions recorded?
4. Which moderator functions are required at first production launch versus a later back-office release?
5. What evidence, reviewer, and review interval are required for each verification type?
6. What content editing/deletion window applies to members and what remains in audit history?
7. What exact ranking formulas define Top, Most discussed, Most popular, and Recently added?
8. Which event registration, live-session, and recording systems will HSS use?
9. Are WhatsApp group links static, approval-based, expiring, or regenerated per member?
10. Which notification categories use WhatsApp, SMS, or email by default, and what are reminder timings?
11. Which AI provider, data-retention setting, model, review process, and fallback are approved?
12. For practical help: approved categories, volunteer eligibility, coverage areas, operating hours, request expiry, visibility, Home pinning, contact release, incident escalation, and legal wording.
13. Who maintains emergency and HSS contact guidance?
14. What data-retention and deletion periods apply to OTP data, community content, reports, help requests, contacts, notifications, analytics, and audit logs?

---

## 24. Definition of done for production features

A feature is not complete solely because its page matches the prototype. It is complete when:

- its happy path and documented failure paths work against persistent backend data;
- server-side authentication, authorisation, validation, and lifecycle rules are enforced;
- responsive mobile, tablet, and desktop behaviour matches the design-system contract;
- loading, empty, error, expired, unavailable, and permission states are implemented;
- accessibility checks pass;
- security/privacy review is complete for the data involved;
- analytics and audit events are defined without leaking sensitive data;
- notifications and scheduled jobs are idempotent and observable;
- automated tests cover core business rules and permissions;
- operational ownership, support procedures, and rollback behaviour are documented;
- HSS has approved all member-facing safety, privacy, verified-source, and external-handoff wording.

---

The prototype remains the visual reference. This PRD is the behavioural, data, safety, and production-architecture reference. If they conflict, product/design should resolve the intended behaviour before engineering implements it.
