/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

export function AuthFooter() {
  return (
    <div className="flex flex-col items-center gap-2 text-13 text-tertiary">
      <span>Team 2 · Applied Project · 2026</span>
      <a
        href="https://github.com/shaxaydev/sakura-team"
        target="_blank"
        rel="noreferrer"
        className="hover:text-primary"
      >
        Powered by Plane
      </a>
    </div>
  );
}
