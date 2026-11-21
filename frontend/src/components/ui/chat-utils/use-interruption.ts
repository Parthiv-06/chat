// Tracks whether the user just scrolled by hand, so auto-scroll can back off for a moment.
// interruptedRef stays true for `ms` after the last interrupt() call, then clears itself.
import * as React from "react"

export function useUserInterruption(ms: number) {
  const interruptedRef = React.useRef(false)
  const timerRef = React.useRef<ReturnType<typeof setTimeout> | null>(null)

  const interrupt = React.useCallback(() => {
    interruptedRef.current = true
    if (timerRef.current) clearTimeout(timerRef.current)
    timerRef.current = setTimeout(() => {
      interruptedRef.current = false
    }, ms)
  }, [ms])

  React.useEffect(() => () => {
    if (timerRef.current) clearTimeout(timerRef.current)
  }, [])

  return { interruptedRef, interrupt }
}
