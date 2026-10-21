# Habr publication metadata

**Status: RELEASE CANDIDATE**

Checked against Habr help/hub pages: **2026-10-21**.

## Title

**CTR ≠ пользовательская ценность: как рекомендательная система может идеально оптимизировать не то**

## Publication type

**Статья**

Recommended difficulty: **Средний**.

Do not mark as a tutorial: the article explains and reproduces an experiment, but is
not primarily a step-by-step lesson.

## Feed annotation / lead

Представим удачный A/B-тест: CTR вырос, watch time тоже, пользователи продолжают взаимодействовать с лентой. Можно праздновать? Не обязательно. Если метрика — лишь proxy, модель может стать лучше именно в неправильной цели. Я собрал воспроизводимый synthetic experiment и сравнил две ranking policies: одну, оптимизирующую short-term engagement, и другую — более широкий proxy пользовательской ценности.

## “Read more” button

**Разобрать эксперимент**

Alternative: **Посмотреть, что получилось**

## Hubs

Habr currently allows **1–5 hubs** per publication.

Recommended four:

1. **Машинное обучение** — primary;
2. **Искусственный интеллект**;
3. **Алгоритмы**;
4. **Python**.

Optional fifth only if the editor/relevance still makes sense at publication time:

5. **Data Mining**.

Do not add a hub merely for reach; the first four describe the article more precisely.

## Tags

Recommended compact set:

- recommender systems
- рекомендательные системы
- ranking
- objective function
- proxy metrics
- feedback loops
- multi-objective optimization
- user satisfaction
- ablation study
- Python

## Cover / КДПВ

Canonical vector source: [`article/assets/habr-cover.svg`](assets/habr-cover.svg).

A 1600×900 PNG export is prepared for upload to Habr. The cover deliberately avoids platform logos and alarmist imagery: one objective function branches into CTR and long-term value.

## Images

The release-candidate Markdown currently references stable GitHub raw URLs so preview works.

Before final publication, preferably upload all images through Habr’s editor and replace
the remote URLs with Habr-hosted versions:

1. cover / КДПВ;
2. `01_pareto_ctr_vs_satisfaction.png`;
3. `02_alpha_vs_mean_sessions.png`;
4. `05_delta_satisfaction.png`.

Captions are already included in `habr-release-candidate.md`.

## Cut

`habr-release-candidate.md` contains `<cut />` immediately after the introductory hook.
The title itself is not duplicated in the Markdown body because Habr has a separate
title field.

## Final editor checklist

- paste `article/habr-release-candidate.md` in Habr Markdown mode;
- set the title from this file;
- add the cover image;
- set the four recommended hubs;
- set difficulty to “Средний”;
- add tags;
- verify all three tables on mobile-width preview;
- upload the three plots through the editor;
- verify DOI/arXiv links;
- keep the section “Что эксперимент не доказывает” intact;
- use Preview before publishing.
