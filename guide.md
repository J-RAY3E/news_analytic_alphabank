# Alfa Radar — User guide

A practical walkthrough of the prototype. The UI is in Russian; key labels are
quoted. Setup is in [`setup.md`](setup.md).

## 1. Sign in

- Open <http://localhost:3000> — you are redirected to the login page.
- Enter a demo account (credentials are listed in the README "Test accounts"
  table), for example `cfo` / `cfo-radar-2026`.
- There is no guest access; the login page's `×` closes it.

## 2. Select client and role (top bar)

- **«Мои компании»** — the company selector; each option shows the company name,
  industry, revenue band and group.
- **Role pills** — CEO / CFO / Казначей / Гл. бухгалтер / Другое. The same event
  is re-ranked and re-worded per role (Role Lens).

## 3. Home screen

- **Radar widget** — the top ranked event for the current company with its
  relevance score, impact chip, source and time; **«Открыть Radar»** enters the
  workspace.
- **Company profile** — industry, region/city, group (id · size · group revenue),
  scale, client type, with "нет данных" chips when a field is missing.
- **Bank tile** — mock balance and "Дела в работе" (no real data).
- **Disclaimer** — "Материалы носят аналитический характер и не являются
  инвестиционной рекомендацией."

## 4. Feed (left panel of the workspace)

- Each **feed card** shows the source + time, a **relevance score** badge, the
  event title, a company-specific reason, and chips: impact level, event type,
  macro factors, risk/opportunity, group context, external source.
- Click the **score badge** to open the weighted breakdown (7 factors incl.
  `event_quality`).
- **«Срочно»** badge marks urgent risk events.
- **Period filter**: Сегодня / Неделя / Месяц / Всё время; the caption shows
  "Обновлено N минут назад".
- **«Скрыть»** hides a card; **«Показать скрытые (N)»** restores them.
- **«История»** opens the history page.

## 5. Insight (center panel)

Six blocks: Что произошло · Почему это важно · Возможные последствия · Какие
действия актуальны · Как это оценивает банк · На чём основаны выводы.

- Every claim is labeled: **Факт**, **Позиция банка**, **Вывод ИИ**, **Гипотеза**
  (each with icon + tooltip).
- **Impact chip** (Низкое/Среднее/Высокое) with a definition tooltip.
- **Source chips** open the original source (news URL or the cited bank PDF page)
  in a side drawer.
- The **«Как это оценивает банк»** block contains only bank analytics; external
  conclusions are labeled.
- **«Следующие шаги»** actions: Связаться с менеджером · Оставить заявку ·
  Запросить обратный звонок · Открыть источник — each shows a demo toast (in
  production they lead to the bank's CRM).
- **«Реклама»** block — an apt native product offer (may be absent). It never
  affects the analysis.
- **Disclaimer** at the bottom of the insight.

## 6. Agent Trace (right panel)

Dark panel with the plan, tool calls (`get_company_profile`,
`get_graph_exposure`, `get_group_view`, `search_bank_analytics`), results,
sources, company features, and Critic checks (pass/fail with retries). Expand a
row for inputs/outputs, model and tokens.

## 7. Follow-up chat

Under the insight: ask a clarifying question or use the quick actions
(«Открыть источник», «Другой срез данных», «Объяснить подробнее»). Answers reuse
the labeled claim format.

## 8. History

`/radar/history` (or «История» in the feed) lists saved insights for the current
client and role; open one to return to its analysis, sources and trace.

## 9. Test a new news item

In the feed panel, **«Проверить новую новость»** → paste article **text** or a
**URL** → the full pipeline runs (5-step progress) and opens a fresh insight.

- Text works reliably.
- URL works for sites that allow fetching; sites that block bots show a clear
  message — paste the text instead.

## 10. Feedback

Under the insight: **Полезно / Не полезно / Неверно**; stored in
`data/feedback/feedback.jsonl` and surfaced in the metrics.

## 11. Admin metrics

`/admin/metrics` (footer link "Метрики", not linked from the client area):
daily budget meter, event/insight counts, thumbs-up ratio, source coverage,
average cost per insight, average latency.

## 12. Notes and limitations

- Without an API key the service runs in **deterministic mode** (full insight,
  no cost). With a key, A6 reasoning uses DeepSeek-V4.1-Flash with Gemma failover.
- Authentication/RBAC is design-only (demo login); see `docs/security.md`.
- The follow-up chat answers deterministically from the stored insight.
