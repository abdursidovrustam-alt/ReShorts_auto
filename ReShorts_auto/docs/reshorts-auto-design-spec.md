# ReShorts Auto — Дизайн-спецификация
## Система автоматизации создания вирусных видео

---

## 1. Дизайн-направление и обоснование

**Выбранный стиль:** Modern Tech Dark

**Визуальная суть:** Профессиональный темный интерфейс для работы с большими объемами данных — чистая функциональность, технологичные акценты, максимальная читаемость. Вдохновлен лучшими практиками Linear, VS Code, Vercel, GitHub Dark.

**Стратегическое обоснование:**

1. **Data-heavy интерфейс требует идеальной читаемости** — темный фон снижает утомляемость глаз при долгой работе с дашбордами, таблицами, графиками статистики. Высокий контраст белого текста на темном фоне обеспечивает максимальную читаемость цифр и метрик.

2. **Профессиональный tech-стандарт индустрии** — конкуренты (OpusClip, Descript, Riverside.fm) используют темные интерфейсы для видео-редакторов. Это ожидаемый паттерн для power users, работающих с контентом.

3. **Многослойная архитектура создает визуальную иерархию** — 4 уровня глубины (background → surface → elevated → modal) четко разделяют функциональные зоны без перегрузки цветом. Cyan-акценты направляют внимание на ключевые действия.

**Ключевые характеристики:**
- **Цвет:** 90% нейтральные темные оттенки, 10% cyan tech-акценты
- **Глубина:** Многослойность через контраст surface/background (минимум 5% разница)
- **Радиусы:** 8-12px — технологичные, не детские
- **Тени:** Subtle с cyan glow на интерактивных элементах
- **Типографика:** Inter (geometric sans-serif) — четкость для метрик и данных
- **Анимации:** 250-300ms плавные переходы

**Референсы:** Linear.app (dark mode), GitHub (dark theme), Vercel Dashboard, VS Code interface

---

## 2. Дизайн-токены

### Цветовая палитра

| Название | Значение | Применение | WCAG |
|----------|----------|------------|------|
| **Primary (Cyan Tech-акцент)** |
| primary-400 | `#22D3EE` | Glow эффекты, подсветка |
| primary-500 | `#06B6D4` | Основной акцент, кнопки, иконки | ✓ 7.2:1 с neutral-950 |
| primary-600 | `#0891B2` | Hover состояния |
| primary-700 | `#0E7490` | Active состояния |
| primary-900 | `#164E63` | Subtle backgrounds |
| **Neutral (Структура)** |
| neutral-50 | `#FAFAFA` | Белый текст (высокий контраст) | ✓ 18.5:1 с neutral-950 |
| neutral-100 | `#F5F5F5` | Заголовки, primary текст | ✓ 16.8:1 с neutral-950 |
| neutral-400 | `#A3A3A3` | Secondary текст, лейблы | ✓ 7.1:1 с neutral-950 |
| neutral-500 | `#737373` | Disabled текст, плейсхолдеры | ✓ 4.6:1 с neutral-950 |
| neutral-700 | `#404040` | Elevated поверхности, модалы |
| neutral-800 | `#262626` | Surface слой (карточки, панели) |
| neutral-900 | `#171717` | Background основной |
| neutral-950 | `#0A0A0A` | Deep background (sidebar, header) |
| **Background (Слои глубины)** |
| bg-base | `neutral-900` | Основной фон страницы |
| bg-surface | `neutral-800` | Карточки, панели (контраст 6% с base) |
| bg-elevated | `neutral-700` | Поднятые элементы, dropdowns |
| bg-modal | `neutral-700` | Модальные окна |
| **Semantic (Статусы)** |
| success-500 | `#10B981` | Успех, completed | ✓ 5.8:1 с neutral-950 |
| warning-500 | `#F59E0B` | Предупреждения, pending | ✓ 5.2:1 с neutral-950 |
| error-500 | `#EF4444` | Ошибки, failed | ✓ 5.5:1 с neutral-950 |
| info-500 | `#3B82F6` | Информация, processing | ✓ 6.1:1 с neutral-950 |

### Типографика

| Название | Шрифт | Размер | Вес | Line Height | Применение |
|----------|-------|--------|-----|-------------|------------|
| display-lg | Inter | 48px | 700 | 1.2 | Hero заголовки (редко) |
| heading-xl | Inter | 32px | 700 | 1.3 | Заголовки страниц |
| heading-lg | Inter | 24px | 600 | 1.4 | Заголовки секций |
| heading-md | Inter | 20px | 600 | 1.4 | Заголовки карточек |
| body-lg | Inter | 18px | 400 | 1.6 | Крупный текст |
| body-base | Inter | 16px | 400 | 1.6 | Основной текст |
| body-sm | Inter | 14px | 400 | 1.5 | Secondary текст |
| caption | Inter | 12px | 500 | 1.4 | Метки, подписи |
| label | Inter | 14px | 500 | 1.5 | Лейблы форм |
| mono | JetBrains Mono | 14px | 400 | 1.6 | Код, технические данные |

### Отступы (8px-based)

| Название | Значение | Применение |
|----------|----------|------------|
| spacing-xs | 4px | Иконка-текст, tight spacing |
| spacing-sm | 8px | Внутренние отступы малых элементов |
| spacing-md | 16px | Стандартные отступы элементов |
| spacing-lg | 24px | Отступы внутри карточек |
| spacing-xl | 32px | Padding карточек |
| spacing-2xl | 48px | Секции между группами |
| spacing-3xl | 64px | Большие секции |
| spacing-4xl | 96px | Разделение major секций |

### Border Radius

| Название | Значение | Применение |
|----------|----------|------------|
| radius-sm | 4px | Badges, мелкие элементы |
| radius-md | 8px | Inputs, небольшие кнопки |
| radius-lg | 12px | Карточки, кнопки, панели |
| radius-xl | 16px | Крупные контейнеры |
| radius-full | 9999px | Круглые элементы, pills |

### Тени

| Название | Значение | Применение |
|----------|----------|------------|
| shadow-sm | `0 1px 2px rgba(0,0,0,0.3)` | Subtle elevation |
| shadow-md | `0 4px 6px rgba(0,0,0,0.4)` | Карточки default |
| shadow-lg | `0 10px 15px rgba(0,0,0,0.5)` | Elevated элементы |
| shadow-glow | `0 0 20px rgba(6,182,212,0.3)` | Cyan glow для hover/focus |
| shadow-glow-strong | `0 0 30px rgba(6,182,212,0.5)` | Интенсивный glow для active |

### Анимации

| Название | Duration | Easing | Применение |
|----------|----------|--------|------------|
| fast | 150ms | ease-out | Микро-интерактивность |
| normal | 250ms | ease-out | Стандартные переходы |
| smooth | 300ms | ease-out | Hover эффекты |
| slow | 400ms | ease-in-out | Модалы, drawer |

---

## 3. Спецификации компонентов

### 3.1 Stat Card (Статистическая карточка)

**Структура:**
- Container: bg-surface, padding xl (32px), radius-lg (12px), shadow-md
- Иконка: 24×24px, primary-500, слева от заголовка
- Лейбл: body-sm, neutral-400, uppercase, letter-spacing +0.05em
- Значение: display-lg (48px), neutral-50, font-weight 700
- Изменение: body-sm с иконкой тренда (↑↓), success-500/error-500
- Border: 1px solid transparent

**Состояния:**
- Default: shadow-md
- Hover: border primary-900, shadow-glow (250ms)

**Пример использования:** Дашборд — "1,247 Скачано видео", "89% Успешных обработок"

---

### 3.2 Video Card (Карточка видео)

**Структура:**
- Container: bg-surface, padding lg (24px), radius-lg (12px), shadow-md
- Thumbnail: aspect-ratio 16:9, radius-md (8px), overflow hidden, с duration badge
- Badge (duration): absolute top-right, bg neutral-950/80, body-sm, padding sm (8px)
- Title: heading-md (20px), neutral-100, margin-top md (16px)
- Meta-row: flex, gap md, body-sm, neutral-400
  - Platform icon: 16×16px
  - Views, Likes, Comments (иконка + число)
- Viral Score: progress bar, primary-500, height 4px, radius-full
- Actions: flex gap sm, margin-top lg
  - Button primary: "Скачать"
  - Button secondary: иконки (queue, info)

**Состояния:**
- Default: shadow-md
- Hover: translateY(-4px), shadow-lg + shadow-glow, scale(1.02) (300ms)
- Selected: border 2px primary-500, shadow-glow-strong

**Responsive:**
- Desktop: 3 колонки grid
- Tablet: 2 колонки
- Mobile: 1 колонка, padding md (16px)

---

### 3.3 Button

**Primary:**
- Background: primary-500
- Text: neutral-950 (темный текст на cyan для контраста)
- Padding: 12px 24px (height 48px)
- Radius: radius-lg (12px)
- Font: label (14px, 500)
- Hover: background primary-600, shadow-glow (250ms)
- Active: background primary-700, scale(0.98)
- Disabled: opacity 0.5, cursor not-allowed

**Secondary (Ghost):**
- Background: transparent
- Border: 1px solid neutral-700
- Text: neutral-100
- Hover: border primary-500, text primary-400, shadow-glow
- Active: background primary-900/20

**Icon Button:**
- Size: 40×40px (touch target)
- Padding: 8px (icon 24×24px)
- Radius: radius-md (8px)
- Background: transparent
- Hover: background neutral-700, color primary-400

---

### 3.4 Input / Search Field

**Структура:**
- Container: bg-elevated (neutral-700), border 1px neutral-600, radius-md (8px)
- Padding: 12px 16px (height 48px)
- Text: body-base, neutral-100
- Placeholder: neutral-500
- Icon (optional): 20×20px, neutral-400, слева с margin-right sm (8px)

**Состояния:**
- Default: border neutral-600
- Focus: border primary-500, shadow-glow, outline none
- Error: border error-500, shadow-glow (red tint)
- Disabled: opacity 0.6, cursor not-allowed

**Search Field вариант:**
- Height: 56px (крупнее для prominence)
- Icon search: слева
- Button "Искать": справа внутри (integrated)

---

### 3.5 Filter Panel (Горизонтальная панель фильтров)

**Структура:**
- Container: bg-surface, padding xl (32px), radius-lg (12px), shadow-md
- Layout: Grid 2-3 колонки (responsive)
- Filter Group:
  - Label: label, neutral-400, margin-bottom sm (8px)
  - Control: Input, Select, Range slider
- Pills (platform select): 
  - Background: neutral-700, padding 8px 16px, radius-full
  - Selected: background primary-900, border primary-500, text primary-400
  - Hover: background neutral-600

**Actions Row:**
- Margin-top 2xl (48px)
- Button primary "Искать" + Button secondary "Сбросить"
- Справа: "Сохранить пресет" (ghost button)

---

### 3.6 Chart Container (Контейнер графика)

**Структура:**
- Container: bg-surface, padding xl (32px), radius-lg (12px), shadow-md
- Header:
  - Title: heading-lg, neutral-100
  - Subtitle: body-sm, neutral-400
  - Actions: dropdown справа (period select)
- Chart Area: margin-top lg (24px)
- Grid lines: neutral-700, 1px
- Axis labels: caption, neutral-500
- Data line: primary-500, 2px, с gradient fill (primary-900/20 to transparent)
- Data points: 6px circle, primary-400, с hover tooltip

**Tooltip:**
- Background: neutral-700, padding md, radius-md, shadow-lg
- Text: body-sm, neutral-100
- Value: body-lg, primary-400

---

## 4. Макет и адаптивность

### Breakpoints

| Название | Значение | Применение |
|----------|----------|------------|
| sm | 640px | Mobile landscape |
| md | 768px | Tablet portrait |
| lg | 1024px | Tablet landscape / Small desktop |
| xl | 1280px | Desktop |
| 2xl | 1536px | Large desktop |

### Структура приложения

**Layout (все страницы):**
- Sidebar: 240px фиксированная ширина, bg-neutral-950, border-right 1px neutral-800
  - Mobile: drawer (overlay), закрыт по умолчанию
- Main Content: flex-1, bg-base (neutral-900), padding 2xl (48px)
  - Mobile: padding md (16px)
- Header: height 64px, bg-neutral-950, border-bottom 1px neutral-800
  - Search глобальный, notifications, user menu

### Grid системы

**Dashboard:**
- Stat Cards: grid 4 колонки (xl), 2 колонки (md), 1 колонка (sm)
- Gap: lg (24px)
- Chart: full-width, height 400px (desktop), 300px (mobile)

**Search Results:**
- Video Cards: grid 3 колонки (xl), 2 колонки (md), 1 колонка (sm)
- Gap: xl (32px)

**Video Manager:**
- Table на desktop (>lg)
- Cards на tablet/mobile (<lg)

### Адаптивные принципы

**Stack:** Горизонтальные элементы становятся вертикальными на <md
**Hide:** Secondary информация скрывается на <sm (показывается через expand)
**Enlarge:** Touch targets минимум 44×44px на mobile
**Simplify:** Sidebar → hamburger menu, таблицы → карточки

---

## 5. Принципы интерактивности

### Стандарты анимаций

**Все переходы:**
- Duration: 250ms (normal) — стандарт для большинства
- Easing: ease-out — естественное ускорение
- Properties: transform, opacity ТОЛЬКО (GPU-accelerated, не layout shift)

**Специальные случая:**
- Micro-interactions (checkbox, toggle): 150ms fast
- Modals/Drawer открытие: 300ms smooth
- Chart animations: 400ms ease-in-out

### Hover эффекты

**Карточки:**
- translateY(-4px) + shadow-glow + scale(1.02)
- Transition: 300ms smooth

**Кнопки:**
- Primary: background shift + shadow-glow
- Secondary: border color + text color + shadow-glow
- Icon: background fill + icon color

**Ссылки/Text:**
- Underline decoration-primary-500
- Color shift neutral-400 → primary-400

### Focus states

**Клавиатурная навигация:**
- Outline: 2px solid primary-500, offset 2px
- Shadow-glow добавляется
- Visible только при keyboard focus (не mouse click)

### Loading состояния

**Skeleton screens:**
- Background: neutral-800
- Shimmer: linear-gradient анимация neutral-700 → neutral-750 → neutral-700
- Duration: 1.5s infinite
- Radius/размеры совпадают с финальным контентом

**Progress bars:**
- Background: neutral-800
- Fill: primary-500 с gradient
- Indeterminate: animated shimmer

**Spinners:**
- Border: 3px, neutral-700 с primary-500 accent
- Size: 24px (inline), 48px (page-level)
- Animation: rotate 1s linear infinite

### Reduced motion

**Fallback при prefers-reduced-motion:**
- Все durations → 50ms
- Transform/translate → opacity fade только
- Infinite animations → static

### Звуковые состояния (опционально)

**Success/Error feedback:**
- Subtle sound cues для завершения операций
- Отключаемо в настройках
- Не критично для функциональности

---

**Автор:** MiniMax Agent  
**Дата:** 2025-10-17  
**Версия:** 1.0
