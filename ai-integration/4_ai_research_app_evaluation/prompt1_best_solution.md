<!-- === PROMPT 1: ARCHITECTURE === -->

# AILens Backend Architecture Overview

## Core Concept

AILens automatically aggregates AI research papers/news, intelligently summarizes them using an LLM, and delivers personalized digests to users.

## Data Flow

**Ingestion Pipeline:**

- Cron jobs periodically fetch from RSS feeds (arXiv, Papers with Code, etc.)
- Raw content stored in `articles` table
- LLM service (OpenAI/Claude API) generates summaries + extracts topics/tags
- Enriched data persists to database

**User Layer:**

- Users authenticate (Auth.js) and set preferences (topics, frequency)
- `user_preferences` table stores digest schedule, interest tags, etc.

**Digest Generation:**

- Daily/weekly cron job queries relevant articles based on user preferences
- Batches similar articles by topic
- Generates personalized digest (either pre-rendered or on-demand)
- Stores digest snapshot for reproducibility

**Delivery:**

- Email service (Resend/SendGrid) sends digest to subscribers
- Web dashboard shows current + archived digests

## Database Schema (Essential Tables)

- `users` (auth, preferences)
- `articles` (raw content, source)
- `summaries` (LLM-generated content, embeddings)
- `digests` (compiled digest snapshots per user)
- `user_preferences` (topics, frequency)

## Key Architectural Decisions

1. **Separation of concerns:** Ingestion, summarization, and digest generation as separate cron jobs
2. **Caching summaries:** Avoid re-LLM-calling the same article
3. **Batch processing:** Digest generation groups articles intelligently (by topic/relevance)
4. **Snapshot storage:** Digests stored immutably for audit trail + offline access

This keeps things lean while handling async heavy-lifting elegantly.

=== PROMPT 2: DATABASE SCHEMA ===

```prisma
// prisma/schema.prisma

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

model User {
  id            String    @id @default(cuid())
  email         String    @unique
  name          String?
  emailVerified DateTime?
  image         String?
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt

  accounts      Account[]
  sessions      Session[]
  preferences   UserPreferences?
  digests       Digest[]
}

model Account {
  id                 String  @id @default(cuid())
  userId             String
  type               String
  provider           String
  providerAccountId  String
  refresh_token      String? @db.Text
  access_token       String? @db.Text
  expires_at         Int?
  token_type         String?
  scope              String?
  id_token           String? @db.Text
  session_state      String?

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([provider, providerAccountId])
}

model Session {
  id        String   @id @default(cuid())
  sessionToken String @unique
  userId    String
  expires   DateTime

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)
}

model UserPreferences {
  id              String   @id @default(cuid())
  userId          String   @unique
  topics          String[] @default([])
  digestFrequency String   @default("weekly")
  emailNotifications Boolean @default(true)
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)
}

model Article {
  id        String   @id @default(cuid())
  title     String
  content   String   @db.Text
  url       String   @unique
  source    String
  publishedAt DateTime
  createdAt DateTime @default(now())

  summary   Summary?
  digests   Digest[]
}

model Summary {
  id        String   @id @default(cuid())
  articleId String   @unique
  summary   String   @db.Text
  topics    String[]
  embedding Float[]?
  createdAt DateTime @default(now())

  article Article @relation(fields: [articleId], references: [id], onDelete: Cascade)
}

model Digest {
  id        String   @id @default(cuid())
  userId    String
  articles  Article[]
  content   String   @db.Text
  sentAt    DateTime?
  createdAt DateTime @default(now())

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)
}
```

=== PROMPT 3: ARXIV & CLAUDE LOGIC ===

```typescript
// lib/arxiv.ts
import { parseStringPromise } from 'xml2js';

export interface ArxivArticle {
  id: string;
  title: string;
  summary: string;
  publishedAt: Date;
  url: string;
}

export async function fetchArxivArticles(): Promise<ArxivArticle[]> {
  const ARXIV_FEED_URL = 'http://export.arxiv.org/rss/list/cs.AI';

  try {
    const response = await fetch(ARXIV_FEED_URL, {
      headers: {
        'User-Agent': 'AILens/1.0 (+https://ailens.ai)',
      },
    });

    if (!response.ok) {
      throw new Error(`ArXiv fetch failed: ${response.statusText}`);
    }

    const xml = await response.text();
    const parsed = await parseStringPromise(xml);

    const items = parsed.rss.channel[0].item || [];

    const articles: ArxivArticle[] = items.map((item: any) => ({
      id: item.link[0].split('/abs/')[1],
      title: item.title[0],
      summary: item.description[0],
      publishedAt: new Date(item.pubDate[0]),
      url: item.link[0],
    }));

    return articles;
  } catch (error) {
    console.error('Error fetching ArXiv articles:', error);
    throw error;
  }
}
```

```typescript
// lib/claude.ts
import Anthropic from '@anthropic-ai/sdk';

export interface EnrichedArticle {
  themeArea: 'Web Development' | 'Software Development' | 'Data Science' | 'Other';
  hashtags: string[];
  simplifiedExplanation: string;
  mermaidSchema: string;
  promptExamples: string[];
}

const client = new Anthropic();

const CLAUDE_PROMPT = `Analyze the following AI research abstract and respond with ONLY valid JSON (no markdown, no extra text). 

Abstract:
{ABSTRACT}

Return strictly this JSON structure:
{
  "themeArea": "Web Development" | "Software Development" | "Data Science" | "Other",
  "hashtags": ["tag1", "tag2", "tag3"],
  "simplifiedExplanation": "Clear 2-3 sentence explanation for non-technical users",
  "mermaidSchema": "flowchart TD; A[Input] --> B[Process] --> C[Output]",
  "promptExamples": ["Example prompt 1", "Example prompt 2", "Example prompt 3"]
}`;

export async function enrichArticleWithClaude(
  abstract: string,
): Promise<EnrichedArticle> {
  try {
    const message = await client.messages.create({
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 1024,
      messages: [
        {
          role: 'user',
          content: CLAUDE_PROMPT.replace('{ABSTRACT}', abstract),
        },
      ],
    });

    const responseText =
      message.content[0].type === 'text' ? message.content[0].text : '';

    const jsonMatch = responseText.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      throw new Error('No JSON found in Claude response');
    }

    const enriched: EnrichedArticle = JSON.parse(jsonMatch[0]);

    return enriched;
  } catch (error) {
    console.error('Error enriching article with Claude:', error);
    throw error;
  }
}
```

```typescript
// app/api/cron/fetch-arxiv/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { fetchArxivArticles } from '@/lib/arxiv';
import { enrichArticleWithClaude } from '@/lib/claude';

export async function POST(request: NextRequest) {
  // Verify cron secret
  const authHeader = request.headers.get('authorization');
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    console.log('Starting ArXiv fetch cron job...');

    // Fetch articles from ArXiv
    const arxivArticles = await fetchArxivArticles();
    console.log(`Fetched ${arxivArticles.length} articles from ArXiv`);

    let successCount = 0;
    let errorCount = 0;

    // Process each article
    for (const arxivArticle of arxivArticles) {
      try {
        // Check if article already exists
        const existingArticle = await prisma.article.findUnique({
          where: { url: arxivArticle.url },
        });

        if (existingArticle) {
          console.log(`Article already exists: ${arxivArticle.id}`);
          continue;
        }

        // Enrich with Claude
        const enriched = await enrichArticleWithClaude(arxivArticle.summary);

        // Save article to database
        const article = await prisma.article.create({
          data: {
            title: arxivArticle.title,
            content: arxivArticle.summary,
            url: arxivArticle.url,
            source: 'arxiv',
            publishedAt: arxivArticle.publishedAt,
          },
        });

        // Save summary
        await prisma.summary.create({
          data: {
            articleId: article.id,
            summary: enriched.simplifiedExplanation,
            topics: enriched.hashtags,
          },
        });

        // Store enriched data as metadata (optional: extend Summary model if needed)
        console.log(`Processed: ${arxivArticle.id}`);
        successCount++;

        // Rate limiting: small delay between Claude API calls
        await new Promise((resolve) => setTimeout(resolve, 1000));
      } catch (error) {
        console.error(
          `Error processing article ${arxivArticle.id}:`,
          error,
        );
        errorCount++;
      }
    }

    return NextResponse.json({
      success: true,
      processed: successCount,
      errors: errorCount,
      total: arxivArticles.length,
    });
  } catch (error) {
    console.error('Cron job failed:', error);
    return NextResponse.json(
      { error: 'Cron job failed', details: String(error) },
      { status: 500 },
    );
  }
}
```

```typescript
// lib/prisma.ts
import { PrismaClient } from '@prisma/client';

const globalForPrisma = globalThis as unknown as { prisma: PrismaClient };

export const prisma =
  globalForPrisma.prisma ||
  new PrismaClient({
    log: ['error', 'warn'],
  });

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma;
```

**Setup Instructions:**

1. Install dependencies:

```bash
npm install xml2js @anthropic-ai/sdk
```

1. Add to `.env.local`:

```bash
ANTHROPIC_API_KEY=your_key_here
CRON_SECRET=your_secret_here
```

1. Call via cron (Vercel Cron):

```json
// vercel.json
{
  "crons": [
    {
      "path": "/api/cron/fetch-arxiv",
      "schedule": "0 9 * * *"
    }
  ]
}
```

=== PROMPT 4: VALIDATION LOGIC ===

```typescript
// lib/validation.ts
import { z } from 'zod';

// Mermaid diagram keywords that are valid
const VALID_MERMAID_KEYWORDS = [
  'flowchart',
  'graph',
  'sequenceDiagram',
  'classDiagram',
  'stateDiagram',
  'erDiagram',
  'journey',
  'gantt',
  'pie',
  'gitGraph',
];

// Zod schema for enriched article validation
export const EnrichedArticleSchema = z.object({
  themeArea: z.enum(['Web Development', 'Software Development', 'Data Science', 'Other']),
  hashtags: z.array(z.string().min(1)).min(1).max(10),
  simplifiedExplanation: z.string().min(10).max(500),
  mermaidSchema: z
    .string()
    .min(1, 'Mermaid schema cannot be empty')
    .refine(
      (schema) => {
        const trimmed = schema.trim().toLowerCase();
        return VALID_MERMAID_KEYWORDS.some((keyword) =>
          trimmed.startsWith(keyword),
        );
      },
      {
        message: `Mermaid schema must start with a valid keyword: ${VALID_MERMAID_KEYWORDS.join(', ')}`,
      },
    )
    .refine(
      (schema) => {
        // Basic syntax validation: should contain at least one semicolon or arrow
        return /[;>-]/.test(schema);
      },
      {
        message: 'Mermaid schema must contain valid diagram syntax',
      },
    ),
  promptExamples: z.array(z.string().min(5)).min(1).max(5),
});

export type EnrichedArticle = z.infer<typeof EnrichedArticleSchema>;

/**
 * Validates enriched article data from Claude
 * @throws ZodError if validation fails
 */
export function validateEnrichedArticle(data: unknown): EnrichedArticle {
  return EnrichedArticleSchema.parse(data);
}

/**
 * Safe validation wrapper that returns validation result object
 */
export function validateEnrichedArticleSafe(
  data: unknown,
): { success: boolean; data?: EnrichedArticle; error?: string } {
  try {
    const validated = EnrichedArticleSchema.parse(data);
    return { success: true, data: validated };
  } catch (error) {
    return {
      success: false,
      error: error instanceof z.ZodError
        ? error.errors.map((e) => `${e.path.join('.')}: ${e.message}`).join('; ')
        : 'Validation failed',
    };
  }
}

/**
 * Validates Mermaid schema independently
 */
export function validateMermaidSchema(schema: string): boolean {
  if (!schema || typeof schema !== 'string') {
    return false;
  }

  const trimmed = schema.trim();
  if (trimmed.length === 0) {
    return false;
  }

  const lowerTrimmed = trimmed.toLowerCase();
  const hasValidKeyword = VALID_MERMAID_KEYWORDS.some((keyword) =>
    lowerTrimmed.startsWith(keyword),
  );

  if (!hasValidKeyword) {
    return false;
  }

  // Check for basic syntax
  return /[;>-]/.test(trimmed);
}
```

```typescript
// lib/claude.ts (UPDATED)
import Anthropic from '@anthropic-ai/sdk';
import { validateEnrichedArticleSafe } from '@/lib/validation';

const client = new Anthropic();

const CLAUDE_PROMPT = `Analyze the following AI research abstract and respond with ONLY valid JSON (no markdown, no extra text). 

Abstract:
{ABSTRACT}

Return strictly this JSON structure:
{
  "themeArea": "Web Development" | "Software Development" | "Data Science" | "Other",
  "hashtags": ["tag1", "tag2", "tag3"],
  "simplifiedExplanation": "Clear 2-3 sentence explanation for non-technical users",
  "mermaidSchema": "flowchart TD; A[Input] --> B[Process] --> C[Output]",
  "promptExamples": ["Example prompt 1", "Example prompt 2", "Example prompt 3"]
}`;

export async function enrichArticleWithClaude(abstract: string) {
  try {
    const message = await client.messages.create({
      model: 'claude-3-5-sonnet-20241022',
      max_tokens: 1024,
      messages: [
        {
          role: 'user',
          content: CLAUDE_PROMPT.replace('{ABSTRACT}', abstract),
        },
      ],
    });

    const responseText =
      message.content[0].type === 'text' ? message.content[0].text : '';

    const jsonMatch = responseText.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      throw new Error('No JSON found in Claude response');
    }

    const parsed = JSON.parse(jsonMatch[0]);

    // Validate against schema
    const validation = validateEnrichedArticleSafe(parsed);
    if (!validation.success) {
      throw new Error(`Validation failed: ${validation.error}`);
    }

    return validation.data;
  } catch (error) {
    console.error('Error enriching article with Claude:', error);
    throw error;
  }
}
```

```typescript
// app/api/cron/fetch-arxiv/route.ts (UPDATED)
import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';
import { fetchArxivArticles } from '@/lib/arxiv';
import { enrichArticleWithClaude } from '@/lib/claude';

export async function POST(request: NextRequest) {
  const authHeader = request.headers.get('authorization');
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    console.log('Starting ArXiv fetch cron job...');

    const arxivArticles = await fetchArxivArticles();
    console.log(`Fetched ${arxivArticles.length} articles from ArXiv`);

    let successCount = 0;
    let errorCount = 0;
    const errors: string[] = [];

    for (const arxivArticle of arxivArticles) {
      try {
        const existingArticle = await prisma.article.findUnique({
          where: { url: arxivArticle.url },
        });

        if (existingArticle) {
          console.log(`Article already exists: ${arxivArticle.id}`);
          continue;
        }

        // Enrich with Claude (validation happens inside)
        const enriched = await enrichArticleWithClaude(arxivArticle.summary);

        // Save article to database
        const article = await prisma.article.create({
          data: {
            title: arxivArticle.title,
            content: arxivArticle.summary,
            url: arxivArticle.url,
            source: 'arxiv',
            publishedAt: arxivArticle.publishedAt,
          },
        });

        // Save summary with validated data
        await prisma.summary.create({
          data: {
            articleId: article.id,
            summary: enriched.simplifiedExplanation,
            topics: enriched.hashtags,
          },
        });

        console.log(`Processed: ${arxivArticle.id}`);
        successCount++;

        await new Promise((resolve) => setTimeout(resolve, 1000));
      } catch (error) {
        const errorMsg = `Error processing article ${arxivArticle.id}: ${error instanceof Error ? error.message : String(error)}`;
        console.error(errorMsg);
        errors.push(errorMsg);
        errorCount++;
      }
    }

    return NextResponse.json({
      success: true,
      processed: successCount,
      errors: errorCount,
      total: arxivArticles.length,
      errorDetails: errors,
    });
  } catch (error) {
    console.error('Cron job failed:', error);
    return NextResponse.json(
      { error: 'Cron job failed', details: String(error) },
      { status: 500 },
    );
  }
}
```

**Key Validation Features:**

1. **Zod Schema:** Type-safe validation with clear error messages
2. **Mermaid Keywords:** Whitelist of valid diagram types
3. **Syntax Check:** Ensures schema contains diagram syntax (`;`, `>`, `-`)
4. **Safe Validation:** `validateEnrichedArticleSafe()` returns structured result
5. **Error Tracking:** Cron endpoint logs validation failures for debugging

=== PROMPT 5: INTERNATIONALIZATION ===

```typescript
// locales/en.json
{
  "common": {
    "appName": "AILens",
    "appDescription": "Your daily AI research digest",
    "loading": "Loading...",
    "error": "An error occurred",
    "success": "Success",
    "cancel": "Cancel",
    "save": "Save",
    "delete": "Delete",
    "edit": "Edit",
    "back": "Back"
  },
  "navigation": {
    "home": "Home",
    "digest": "Digest",
    "preferences": "Preferences",
    "account": "Account",
    "signIn": "Sign In",
    "signOut": "Sign Out"
  },
  "home": {
    "title": "Welcome to AILens",
    "subtitle": "Stay updated with the latest AI research",
    "latestArticles": "Latest Articles",
    "noArticles": "No articles available yet",
    "readMore": "Read More",
    "viewDigest": "View Digest"
  },
  "digest": {
    "title": "Your AI Research Digest",
    "frequency": "Frequency",
    "topics": "Topics",
    "generatedOn": "Generated on",
    "articles": "Articles",
    "noDigests": "No digests generated yet",
    "nextDigest": "Next digest on"
  },
  "preferences": {
    "title": "Your Preferences",
    "selectTopics": "Select Topics of Interest",
    "digestFrequency": "Digest Frequency",
    "weekly": "Weekly",
    "daily": "Daily",
    "biweekly": "Bi-weekly",
    "emailNotifications": "Email Notifications",
    "enabled": "Enabled",
    "disabled": "Disabled",
    "saveChanges": "Save Changes",
    "preferencesUpdated": "Preferences updated successfully"
  },
  "articles": {
    "themeArea": "Theme Area",
    "webDevelopment": "Web Development",
    "softwareDevelopment": "Software Development",
    "dataScience": "Data Science",
    "other": "Other",
    "hashtags": "Tags",
    "explanation": "Simplified Explanation",
    "promptExamples": "Prompt Examples",
    "schema": "Technical Schema",
    "source": "Source",
    "publishedAt": "Published"
  },
  "errors": {
    "notFound": "Page not found",
    "unauthorized": "You are not authorized",
    "serverError": "Server error occurred",
    "fetchFailed": "Failed to fetch data",
    "saveFailed": "Failed to save changes"
  }
}
```

```typescript
// locales/uk.json
{
  "common": {
    "appName": "AILens",
    "appDescription": "Ваш щоденний дайджест досліджень в галузі ШІ",
    "loading": "Завантаження...",
    "error": "Сталася помилка",
    "success": "Успішно",
    "cancel": "Скасувати",
    "save": "Зберегти",
    "delete": "Видалити",
    "edit": "Редагувати",
    "back": "Назад"
  },
  "navigation": {
    "home": "Головна",
    "digest": "Дайджест",
    "preferences": "Налаштування",
    "account": "Профіль",
    "signIn": "Увійти",
    "signOut": "Вийти"
  },
  "home": {
    "title": "Ласкаво просимо в AILens",
    "subtitle": "Залишайтесь в курсі найновіших досліджень ШІ",
    "latestArticles": "Останні статті",
    "noArticles": "Статей ще немає",
    "readMore": "Читати далі",
    "viewDigest": "Переглянути дайджест"
  },
  "digest": {
    "title": "Ваш дайджест досліджень ШІ",
    "frequency": "Частота",
    "topics": "Теми",
    "generatedOn": "Створено",
    "articles": "Статті",
    "noDigests": "Дайджестів ще не створено",
    "nextDigest": "Наступний дайджест"
  },
  "preferences": {
    "title": "Ваші налаштування",
    "selectTopics": "Виберіть теми, які вас цікавлять",
    "digestFrequency": "Частота дайджесту",
    "weekly": "Щотижня",
    "daily": "Щодня",
    "biweekly": "Раз на два тижні",
    "emailNotifications": "Сповіщення електронною поштою",
    "enabled": "Увімкнено",
    "disabled": "Вимкнено",
    "saveChanges": "Зберегти зміни",
    "preferencesUpdated": "Налаштування успішно оновлено"
  },
  "articles": {
    "themeArea": "Область застосування",
    "webDevelopment": "Веб-розробка",
    "softwareDevelopment": "Розробка програмного забезпечення",
    "dataScience": "Наука про дані",
    "other": "Інше",
    "hashtags": "Теги",
    "explanation": "Спрощене пояснення",
    "promptExamples": "Приклади запитів",
    "schema": "Технічна схема",
    "source": "Джерело",
    "publishedAt": "Опубліковано"
  },
  "errors": {
    "notFound": "Сторінку не знайдено",
    "unauthorized": "Ви не авторизовані",
    "serverError": "Сталася помилка сервера",
    "fetchFailed": "Не вдалося завантажити дані",
    "saveFailed": "Не вдалося зберегти зміни"
  }
}
```

```typescript
// lib/i18n/settings.ts
export const LANGUAGES = {
  EN: 'en',
  UK: 'uk',
} as const;

export type Language = (typeof LANGUAGES)[keyof typeof LANGUAGES];

export const DEFAULT_LANGUAGE: Language = LANGUAGES.EN;

export const LANGUAGE_NAMES: Record<Language, string> = {
  en: 'English',
  uk: 'Українська',
};
```

```typescript
// lib/i18n/translations.ts
import en from '@/locales/en.json';
import uk from '@/locales/uk.json';
import { Language } from './settings';

const translations: Record<Language, typeof en> = {
  en,
  uk,
};

export function getTranslations(language: Language) {
  return translations[language] || translations.en;
}

export function t(
  language: Language,
  key: string,
  defaultValue: string = key,
): string {
  const keys = key.split('.');
  let value: any = translations[language] || translations.en;

  for (const k of keys) {
    value = value?.[k];
    if (!value) return defaultValue;
  }

  return typeof value === 'string' ? value : defaultValue;
}
```

```typescript
// context/i18n-context.tsx
'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { Language, DEFAULT_LANGUAGE, LANGUAGES } from '@/lib/i18n/settings';
import { getTranslations } from '@/lib/i18n/translations';

interface I18nContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
  translations: ReturnType<typeof getTranslations>;
}

const I18nContext = createContext<I18nContextType | undefined>(undefined);

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguageState] = useState<Language>(DEFAULT_LANGUAGE);
  const [mounted, setMounted] = useState(false);

  // Hydrate from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem('language') as Language | null;
    if (stored && Object.values(LANGUAGES).includes(stored)) {
      setLanguageState(stored);
    }
    setMounted(true);
  }, []);

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem('language', lang);
  };

  const translations = getTranslations(language);

  const t = (key: string): string => {
    const keys = key.split('.');
    let value: any = translations;

    for (const k of keys) {
      value = value?.[k];
      if (!value) return key;
    }

    return typeof value === 'string' ? value : key;
  };

  // Prevent hydration mismatch
  if (!mounted) {
    return <>{children}</>;
  }

  return (
    <I18nContext.Provider value={{ language, setLanguage, t, translations }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useI18n must be used within I18nProvider');
  }
  return context;
}
```

```typescript
// app/layout.tsx
import { I18nProvider } from '@/context/i18n-context';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'AILens - AI Research Digest',
  description: 'Stay updated with the latest AI research',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <I18nProvider>{children}</I18nProvider>
      </body>
    </html>
  );
}
```

```typescript
// components/language-switcher.tsx
'use client';

import { useI18n } from '@/context/i18n-context';
import { Language, LANGUAGES, LANGUAGE_NAMES } from '@/lib/i18n/settings';

export function LanguageSwitcher() {
  const { language, setLanguage } = useI18n();

  return (
    <div className="flex gap-2">
      {Object.entries(LANGUAGES).map(([_, lang]) => (
        <button
          key={lang}
          onClick={() => setLanguage(lang as Language)}
          className={`px-3 py-1 rounded ${
            language === lang
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-800'
          }`}
        >
          {LANGUAGE_NAMES[lang as Language]}
        </button>
      ))}
    </div>
  );
}
```

```typescript
// app/page.tsx
'use client';

import { useI18n } from '@/context/i18n-context';
import { LanguageSwitcher } from '@/components/language-switcher';

export default function HomePage() {
  const { t } = useI18n();

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <nav className="flex justify-between items-center p-6 bg-white shadow">
        <h1 className="text-2xl font-bold">{t('common.appName')}</h1>
        <LanguageSwitcher />
      </nav>

      <div className="container mx-auto px-6 py-12 text-center">
        <h2 className="text-4xl font-bold mb-4">{t('home.title')}</h2>
        <p className="text-xl text-gray-600 mb-8">{t('home.subtitle')}</p>

        <div className="grid md:grid-cols-2 gap-8 mt-12">
          <section className="bg-white p-8 rounded-lg shadow">
            <h3 className="text-2xl font-semibold mb-4">
              {t('home.latestArticles')}
            </h3>
            <p className="text-gray-600">{t('home.noArticles')}</p>
          </section>

          <section className="bg-white p-8 rounded-lg shadow">
            <h3 className="text-2xl font-semibold mb-4">{t('digest.title')}</h3>
            <p className="text-gray-600">{t('digest.noDigests')}</p>
          </section>
        </div>
      </div>
    </main>
  );
}
```

```typescript
// app/preferences/page.tsx
'use client';

import { useI18n } from '@/context/i18n-context';
import { LanguageSwitcher } from '@/components/language-switcher';

export default function PreferencesPage() {
  const { t } = useI18n();

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <nav className="flex justify-between items-center p-6 bg-white shadow">
        <h1 className="text-2xl font-bold">{t('common.appName')}</h1>
        <LanguageSwitcher />
      </nav>

      <div className="container mx-auto px-6 py-12 max-w-2xl">
        <h2 className="text-3xl font-bold mb-8">{t('preferences.title')}</h2>

        <div className="bg-white p-8 rounded-lg shadow space-y-8">
          <section>
            <label className="block text-lg font-semibold mb-4">
              {t('preferences.digestFrequency')}
            </label>
            <div className="space-y-2">
              {['daily', 'weekly', 'biweekly'].map((freq) => (
                <label key={freq} className="flex items-center">
                  <input type="radio" name="frequency" value={freq} />
                  <span className="ml-2">{t(`preferences.${freq}`)}</span>
                </label>
              ))}
            </div>
          </section>

          <section>
            <label className="flex items-center gap-3">
              <input type="checkbox" defaultChecked />
              <span className="text-lg font-semibold">
                {t('preferences.emailNotifications')}
              </span>
            </label>
          </section>

          <button className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700">
            {t('preferences.saveChanges')}
          </button>
        </div>
      </div>
    </main>
  );
}
```

```json
// package.json (add these dependencies)
{
  "dependencies": {
    "react": "^18.2.0",
    "next": "^14.0.0"
  }
}
```

**Setup Instructions:**

1. Place translation files:
   - `locales/en.json`
   - `locales/uk.json
