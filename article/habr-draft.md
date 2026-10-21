# CTR ≠ пользовательская ценность: почему рекомендательные системы могут идеально оптимизировать не то

Есть неприятный класс инженерных ошибок, в котором система работает **слишком хорошо**.

Модель не деградировала. Инфраструктура не упала. A/B-тест показывает статистически значимый рост. CTR растёт. Watch time растёт. Пользователь продолжает нажимать.

Проблема в другом: мы могли очень качественно оптимизировать **не ту величину**.

Эта статья — не попытка доказать, что «рекомендательные алгоритмы вредны» или что конкретная социальная сеть кем-то манипулирует. Вопрос гораздо уже и, на мой взгляд, технически интереснее:

> если наблюдаемое поведение пользователя — лишь proxy для того результата, который нам действительно нужен, что происходит, когда мы начинаем aggressively оптимизировать именно proxy?

Я собрал небольшой воспроизводимый synthetic experiment, чтобы посмотреть на этот механизм не только на уровне рассуждений, но и в коде.

Репозиторий с моделью, тестами, sensitivity analysis и ablation study:  
https://github.com/True-Ruslan/recommender-objective-lab

---

## Проблема начинается не с ML, а с objective function

В рекомендательной системе удобно измерять то, что происходит прямо сейчас:

- click;
- dwell time;
- like;
- share;
- продолжение сессии;
- просмотр следующего объекта.

Это хорошие сигналы. Но из того, что метрика **наблюдаема**, ещё не следует, что она совпадает с конечной целью.

Например, ранжирующая функция может выглядеть примерно так:

```python
engagement_score = (
    0.58 * p_click
    + 0.42 * normalized_dwell
)
```

Внутри такой функции нет ничего заведомо плохого. Она отвечает на вполне осмысленный вопрос: какой объект с большей вероятностью вызовет взаимодействие прямо сейчас?

Сложность появляется, когда мы незаметно меняем формулировку:

> «вероятнее всего вызовет взаимодействие»

на

> «лучше всего для пользователя».

Это уже два разных утверждения.

Smitha Milli, Luca Belli и Moritz Hardt в работе **From Optimizing Engagement to Measuring Value** описывают проблему именно как проблему измерения: engagement наблюдаем, а интересующий нас «value» — латентная конструкция, которую ещё нужно корректно определить и операционализировать.

Есть и совсем production-oriented пример. В RecSys 2024 команда Google описала Learned Ranking Function — подход, который принимает short-term behavior predictions, но оптимизирует ranking уже относительно **long-term user satisfaction**. Авторы отдельно отмечают, что система была проверена live experiments и развёрнута на YouTube.

То есть разделение «short-term behavior» и «long-term satisfaction» — не философская фантазия. Это вполне реальная инженерная постановка задачи.

---

## Но пользователь же сам кликает. Разве это не означает, что он этого хочет?

Не обязательно.

Классическая модель recommender system часто неявно опирается на revealed preference:

> человек выбрал X → значит, X соответствует его предпочтениям.

Для большого количества задач это полезное приближение. Но в динамических системах оно может ломаться.

Kleinberg, Mullainathan и Raghavan формализовали ситуацию, в которой пользователь имеет внутренне несовместимые предпочтения, а платформа видит только engagement. Даже если платформа **искренне хочет максимизировать utility пользователя**, одного поведения может быть недостаточно, чтобы восстановить эту utility.

Есть и экспериментальные данные. В работе **Tailoring recommendation algorithms to ideal preferences makes users better off** исследователи Stanford/UCLA построили рекомендации под два типа предпочтений:

- actual — что человеку хочется выбрать прямо сейчас;
- ideal — что человек хотел бы хотеть / выбирать в соответствии со своими более рефлексивными предпочтениями.

В preregistered experiment на 6488 участниках рекомендации по actual preferences дали больше кликов. Но ideal-preference recommendations повысили оценки вроде «эта рекомендация сделает меня лучше» и «время было потрачено не зря».

Это важное наблюдение:

**больше кликов и больше субъективной ценности не обязаны быть одной и той же оптимизационной задачей.**

---

## Второй источник проблемы — feedback loop

Recommender — не статический классификатор.

Если сегодня показать пользователю объект, завтра пользователь уже немного другой:

1. он что-то увидел;
2. что-то нажал;
3. получил или не получил удовлетворение;
4. устал от категории;
5. возможно, изменил привычку или текущие предпочтения;
6. вернулся или не вернулся в следующую сессию.

То есть policy влияет на future state, а future state влияет на следующие observations.

В самом простом виде:

```text
user state
   ↓
candidate generation
   ↓
ranking objective
   ↓
recommended item
   ↓
click / dwell / satisfaction
   ↓
fatigue + preference update
   ↓
return probability
   └──────────────→ next session
```

Если оптимизировать только instant reward, можно не увидеть стоимость, которая проявляется позже.

Saig и Rosenfeld в ICML 2023 рассматривают очень похожую по духу идею: recommendation dynamics состоят одновременно из positive и negative feedback, а иногда даже временное снижение engagement — например, предложенный break — может увеличивать устойчивое long-term engagement.

---

# Собираем минимальную модель

Я специально не хотел строить «симулятор YouTube».

Такой claim был бы практически невозможно защитить: у нас нет production data, реальных моделей user state, настоящих coefficients и causal identification.

Поэтому задача эксперимента скромнее:

> можно ли построить явную синтетическую среду, в которой две разумные objective functions систематически выбирают разные trajectories?

В модели:

- 400 synthetic users на seed;
- 20 random seeds;
- 8 content categories;
- 1200 items;
- до 12 sessions на пользователя;
- 5 recommendation opportunities на session;
- 20 candidate items на каждый ranking step.

У каждого item есть независимо сгенерированные:

- category;
- quality;
- stimulus.

Это важно: я **не** зашивал в модель предположение «всё стимулирующее автоматически низкого качества».

У пользователя есть два distribution:

- `actual` — текущие, непосредственные предпочтения;
- `ideal` — более рефлексивные предпочтения.

Это тоже не утверждение о человеческой природе. Это одна из modelling assumptions, которую затем можно отключить или менять через sensitivity analysis.

---

## Две objective functions

### 1. Engagement-first

```python
engagement_score = (
    0.58 * p_click
    + 0.42 * normalized_dwell
)
```

Ranker смотрит на хорошо измеримые immediate signals.

### 2. Value-aware

```python
value_score = (
    0.38 * p_click
    + 0.47 * latent_satisfaction
    + 0.15 * novelty
)
```

Здесь мы искусственно разрешаем ranker смотреть на broader synthetic outcome.

Это, разумеется, сильное допущение: в production latent satisfaction нельзя просто прочитать из памяти. Её пришлось бы оценивать через survey signals, learned reward model, delayed outcomes и т.д.

Именно поэтому результат эксперимента нельзя читать как «вторая формула правильная».

Она нужна как **контрольная policy**, оптимизирующая другую цель.

---

## Что происходит после рекомендации

В модели есть два delayed mechanism.

### Fatigue

Повторное потребление одной категории создаёт decaying cost.

Это попытка представить очень общий класс эффектов: насыщение, усталость, потерю интереса.

### Preference drift

Потреблённый контент немного сдвигает текущие preferences.

Я отдельно подчёркиваю: это не модель «алгоритм переписывает личность». Сдвиг здесь — технический state transition, который можно полностью отключить в ablation.

В конце session рассчитывается synthetic return probability, зависящая от satisfaction, dwell и accumulated fatigue.

И после этого цикл повторяется.

---

# Результат: выигрыш по CTR действительно оказался выигрышем по CTR

Reference run: 20 seeds × 400 users.

| Metric | Engagement-first | Value-aware |
|---|---:|---:|
| CTR | **0.702** | 0.607 |
| Satisfaction | 0.682 | **0.908** |
| Mean sessions | 7.53 | **8.83** |
| Diversity | 0.358 | **0.498** |
| Fatigue | 0.153 | **0.129** |
| Preference drift | 0.254 | **0.147** |

Самое важное здесь — не абсолютные значения.

Это synthetic units. Число `0.908` нельзя интерпретировать как «90,8% реальной удовлетворённости пользователей».

Интереснее структура результата:

- engagement-first получает примерно **+9.5 п.п. CTR**;
- value-aware получает примерно **+0.226 synthetic satisfaction**;
- средняя жизнь пользователя в модели увеличивается примерно на **1.30 session**;
- diversity становится выше;
- fatigue и preference drift — ниже.

Иначе говоря, первая policy делает именно то, что от неё просили.

Она не «сломалась».

Она **успешно оптимизирует локальную метрику**, за которую её награждают.

![CTR vs satisfaction](../results/reference/figures/01_pareto_ctr_vs_satisfaction.png)

---

## Это не бинарный переключатель

Чтобы не сравнивать только две крайности, я добавил параметр:

```python
score = (
    (1 - alpha) * engagement_score
    + alpha * value_score
)
```

где:

- `alpha = 0` — чистый engagement-first;
- `alpha = 1` — чистый value-aware.

Получается достаточно плавный trade-off:

| alpha | CTR | Satisfaction | Mean sessions |
|---:|---:|---:|---:|
| 0.0 | 0.702 | 0.682 | 7.53 |
| 0.2 | 0.696 | 0.732 | 7.83 |
| 0.5 | 0.672 | 0.813 | 8.37 |
| 0.8 | 0.636 | 0.880 | 8.70 |
| 1.0 | 0.607 | 0.908 | 8.83 |

Мне этот график кажется важнее сравнения endpoints.

Он показывает, что вопрос обычно не выглядит как:

> CTR или добро?

Реальная инженерная задача больше похожа на поиск Pareto frontier между несколькими conflicting objectives.

---

# Самая полезная часть — ablation study

Если synthetic model даёт красивый результат, первый вопрос должен быть не «как здорово», а:

> какой assumption его создаёт?

Поэтому я по очереди отключил основные механизмы.

Смотрим разницу `value-aware − engagement-first`:

| Ablation | Δ CTR | Δ Satisfaction | Δ Mean sessions |
|---|---:|---:|---:|
| Baseline | -0.095 | **+0.226** | **+1.295** |
| No fatigue | -0.049 | **+0.062** | **+0.281** |
| No novelty | -0.052 | +0.195 | +1.151 |
| No preference drift | -0.056 | +0.140 | +0.883 |
| Actual = ideal | -0.104 | +0.224 | +1.270 |

И вот здесь появляется действительно полезный вывод.

Я первоначально ожидал, что главным объяснением окажется difference between actual and ideal preferences или preference drift.

Но сильнее всего результат проседает при удалении **fatigue**.

Без fatigue:

- advantage по satisfaction падает с `+0.226` до `+0.062`;
- advantage по mean sessions — с `+1.295` до `+0.281`.

То есть в этой конкретной среде divergence между short-term и long-term objectives в значительной степени возникает из-за **delayed consumption cost**.

Это не доказательство, что fatigue — главный механизм реальных платформ.

Зато это хороший пример того, зачем вообще нужен ablation: он заставляет отличать красивую историю от механизма, который реально создаёт эффект внутри модели.

---

# Sensitivity analysis: эффект не держится на одном числе

Следующий вопрос — не подобрал ли я просто удобные coefficients.

Поэтому несколько параметров прогоняются отдельно:

### Strength of preference reinforcement

При reinforcement:

- `0.00` → Δ satisfaction ≈ +0.140;
- `0.04` → +0.226;
- `0.08` → +0.322.

Чем сильнее state feedback, тем сильнее divergence policies.

### Fatigue gain

- `0.00` → Δ satisfaction ≈ +0.062;
- `0.10` → +0.151;
- `0.22` → +0.226;
- `0.35` → +0.214.

Здесь зависимость уже не монотонная — хороший сигнал, что модель не сводится к одному линейному трюку.

### Actual / ideal alignment

Даже при полном `actual = ideal` gap не исчезает.

Это ещё раз показывает, что основной baseline result нельзя объяснить только историей про «истинные и импульсивные желания».

---

# Что из этого следует для production recommender system

Не «перестаньте считать CTR».

CTR, dwell time, conversion и другие immediate metrics крайне полезны.

Вывод другой:

## 1. Proxy должен оставаться proxy

Если бизнес-цель — long-term value, нельзя молча считать, что один observable signal полностью её представляет.

Нужно явно написать:

```text
business / user objective
        ↓
measurable constructs
        ↓
metrics and learned signals
        ↓
ranking objective
```

И периодически проверять каждую стрелку.

---

## 2. Ranking objective — отдельный продуктовый интерфейс

В зрелой системе полезно относиться к objective function почти как к API-контракту.

Нужно понимать:

- какие signals входят;
- за какой horizon они отвечают;
- какие trade-offs допустимы;
- какие guardrails нельзя нарушать;
- кто имеет право менять weights;
- чем измеряется регрессия.

Именно поэтому multi-objective ranking значительно интереснее формулы вида:

```text
score = 5 * click + 3 * watch_time + 7 * like
```

Такая формула тоже может работать. Но тогда её assumptions должны быть явными.

---

## 3. Нужны delayed metrics

Если побочный эффект проявляется через неделю, offline AUC модели клика его не покажет.

Минимальный набор уровней выглядит примерно так:

**Immediate**
- CTR;
- dwell;
- conversion.

**Session**
- satisfaction proxy;
- diversity;
- abandonment;
- explicit negative feedback.

**Long horizon**
- return quality;
- retention;
- survey-based value;
- repeated-regret / hide / unsubscribe signals.

**Guardrails**
- safety;
- fairness;
- content quality;
- creator/ecosystem health.

---

## 4. User state нельзя считать константой

Как только recommendations влияют на future interactions, ranking становится sequential decision problem.

Не обязательно сразу выкатывать full RL.

Но хотя бы в offline evaluation полезно задавать вопрос:

> что изменится в данных, если эту policy применять долго?

Это уже другой взгляд, чем обычное «насколько точно мы предскажем следующий click?».

---

## 5. Satisfaction тоже proxy

Есть соблазн закончить статью фразой:

> значит, надо оптимизировать satisfaction.

Нет.

Это просто перенос проблемы на следующий уровень.

Как мы измеряем satisfaction?

- survey?
- explicit rating?
- return behavior?
- regret?
- willingness to pay?
- time well spent?

Каждая из этих величин снова является operationalization.

В этом и состоит неприятная рекурсия: невозможно полностью избавиться от proxy. Можно только делать его связь с настоящей целью более явной, проверяемой и корректируемой.

---

# Что эксперимент НЕ показывает

Я специально вынес это в отдельный раздел репозитория, потому что без него synthetic simulation очень легко превратить в красивое, но некорректное доказательство.

Эксперимент **не показывает**, что:

- YouTube, TikTok или другая конкретная платформа работает по этим equations;
- engagement optimization обязательно причиняет вред;
- preference drift в реальности имеет такую форму;
- моя synthetic satisfaction — правильное определение welfare;
- coefficients в формулах близки к production;
- value-aware objective всегда лучше.

Он показывает только более узкую вещь:

> если measurable proxy не совпадает с desired long-term outcome, оптимизация proxy может систематически выбрать другую policy.

И чем сильнее feedback loops и delayed costs, тем важнее становится эта разница.

---

# Небольшое философское послесловие

У этой проблемы есть старая форма, не связанная ни с ML, ни с рекомендательными системами:

**средство легко перепутать с целью.**

У Аристотеля различие между инструментальными благами и конечной целью — базовая часть разговора о практической рациональности: некоторые вещи мы выбираем ради чего-то ещё.

CTR почти идеальный пример инструментальной величины.

Мы хотим не «клика как такового». Клик нужен потому, что через него мы пытаемся узнать что-то о более важном результате.

Есть и неожиданная параллель с христианской антропологией: непосредственное желание человека не автоматически тождественно тому, что он сам после размышления назвал бы благом. Для технической статьи это, конечно, не evidence и не спецификация objective function. Но как интеллектуальная рамка мысль полезна: **наблюдаемый импульс и осознанная цель — не обязательно одно и то же**.

Инженерная версия этой идеи гораздо прозаичнее:

> модель не знает, чего мы хотели. Она знает только то, что мы записали в loss / reward / objective.

И если записали не то — высокий quality score лишь быстрее приведёт нас туда, куда мы на самом деле не собирались.

---

# Вместо вывода

Самый опасный recommender — не обязательно тот, который плохо предсказывает.

Иногда гораздо интереснее система, которая **очень хорошо предсказывает и оптимизирует**, но целевая функция постепенно становится самостоятельной реальностью.

Поэтому вопрос «какая у нас модель?» я бы ставил после другого:

> **что именно считается успехом этой модели — и почему мы уверены, что именно это хотели оптимизировать?**

Код эксперимента, методология, ограничения claims, sensitivity analysis и reference outputs:  
https://github.com/True-Ruslan/recommender-objective-lab

## Литература

1. Wu Y. et al. _Learned Ranking Function: From Short-term Behavior Predictions to Long-term User Satisfaction._ RecSys 2024. DOI: 10.1145/3640457.3688184.
2. Milli S., Belli L., Hardt M. _From Optimizing Engagement to Measuring Value._ FAccT 2021. DOI: 10.1145/3442188.3445933.
3. Stray J. et al. _What are you optimizing for? Aligning Recommender Systems with Human Values._ 2021.
4. Kleinberg J., Mullainathan S., Raghavan M. _The Challenge of Understanding What Users Want: Inconsistent Preferences and Engagement Optimization._ 2022.
5. Khambatta P. et al. _Tailoring recommendation algorithms to ideal preferences makes users better off._ Scientific Reports, 2023. DOI: 10.1038/s41598-023-34192-x.
6. Saig E., Rosenfeld N. _Learning to Suggest Breaks: Sustainable Optimization of Long-Term User Engagement._ ICML 2023.
7. Lindström B. et al. _A computational reward learning account of social media engagement._ Nature Communications, 2021. DOI: 10.1038/s41467-020-19607-x.
