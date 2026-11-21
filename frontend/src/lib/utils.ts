// Class-name helper used by every shadcn component: joins conditionals, then dedupes Tailwind.
// Later classes win conflicts (e.g. "px-2 px-4" → "px-4"), so pass overrides last.
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
