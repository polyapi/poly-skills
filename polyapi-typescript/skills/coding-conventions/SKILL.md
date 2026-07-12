---
name: coding-conventions
description: Use when writing or reviewing TypeScript in PolyAPI workflows, CLI tooling, or utilities and the task needs concrete conventions for poly.*, vari.*, schemas.*, artifact alignment, and boundary handling.
---

# TypeScript Coding Conventions

## Overview

This skill contains the concrete PolyAPI-oriented TypeScript conventions that
sit underneath the broader `coding-standards` guidance.

The local [`CONVENTIONS.md`](./CONVENTIONS.md) file is the canonical reference
for the detailed rules used by this skill.

## When to Use

- Editing TypeScript in a PolyAPI codebase
- Reviewing whether code matches the expected PolyAPI style
- Changing `poly.*`, `vari.*`, `schemas.*`, JSON artifacts, or error handling
- Deciding whether a helper, custom type, or defensive branch is justified

Do not use this skill:
- For generic TypeScript advice with no PolyAPI context
- When a repo has stronger local rules that intentionally override these

## Quick Reference

- Keep one readable main function per file
- Call `poly.*` directly; do not shadow or re-cast platform namespaces
- Deploy missing platform constructs and regenerate the SDK before referencing
  new generated paths
- Use `schemas.*` directly when it already represents the contract
- Treat `poly.*`, `vari.*`, env, files, HTTP, and webhook payloads as
  boundaries
- Fail fast on untrusted input; avoid "just in case" logic for guaranteed
  contracts
- Keep TypeScript, JSON artifacts, and tests aligned in the same change

## Implementation

Follow [`CONVENTIONS.md`](./CONVENTIONS.md). If the active repo has its own
`AGENTS.md`, `CONVENTIONS.md`, or stronger local workflow docs, those should
override this generalized reference.

## Common Mistakes

- Hiding platform calls behind generic wrappers
- Introducing alias chains for types that already exist
- Using local `.d.ts` shims, `@ts-expect-error`, or `as unknown as` to bypass
  generated SDK drift
- Normalising trusted `vari.*` values without a contract reason
- Updating TypeScript without the matching artifact or test changes

## Real-World Impact

These conventions keep PolyAPI code predictable to review, safer to debug, and
less likely to drift away from platform contracts.
