import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

/**
 * Utility function to merge Tailwind CSS classes with conflict resolution.
 * Combines clsx for conditional classes and twMerge for Tailwind class merging.
 * 
 * @param inputs - Variable number of class values (strings, objects, arrays, etc.)
 * @returns A string of merged and deduplicated class names
 * 
 * @example
 * ```typescript
 * cn("px-2 py-1", "px-4") // Returns "py-1 px-4" (px-2 is overridden by px-4)
 * cn("bg-red-500", { "bg-blue-500": isActive }) // Conditionally applies classes
 * ```
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
